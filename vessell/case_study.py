"""Executable, durable local correction study with an explicit comparison arm."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from vessell.evaluation import sha256, verify_reports, write_reports
from vessell.provenance import (
    ClaimRecord,
    SourceStatus,
    claim_events,
    confirm_dependent_update,
    deliver_correction,
    disavow,
    gate_for_use,
    intake_claim,
    propagate_correction,
    register_dependent,
    verify_event_chain,
)
from vessell.validation import validate_record


def write_snapshot(path: Path, claim: ClaimRecord) -> str:
    payload = claim.to_dict()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    if path.read_text(encoding="utf-8") != text:
        raise ValueError(f"Snapshot write failed read-back: {path.name}")
    return sha256(path)


def repair_snapshot(original: ClaimRecord, correction: ClaimRecord, path: Path) -> str:
    """Acknowledge only after a registered snapshot matches the delivered correction."""
    if path.is_symlink():
        raise ValueError("Managed consumer must not be a symbolic link.")
    current = json.loads(path.read_text(encoding="utf-8"))
    if current.get("id") != original.id:
        raise ValueError("Managed consumer no longer matches the originating claim.")
    dependents = propagate_correction(original.id)
    if not any(item.artifact == "managed-json" and item.location == str(path)
               for item in dependents):
        raise ValueError("Snapshot has no registered claim dependency.")
    deliver_correction(original.id, correction.id)
    digest = write_snapshot(path, correction)
    confirm_dependent_update(
        original.id, "managed-json", str(path), correction_id=correction.id,
    )
    return digest


def validate_spec(spec: dict[str, Any]) -> None:
    validate_record(spec, "case-study.schema.json")
    ids = [scenario["id"] for scenario in spec["scenarios"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Case-study scenario IDs must be unique.")
    for scenario in spec["scenarios"]:
        consumers = scenario["consumers"]
        if len(consumers) != len(set(consumers)):
            raise ValueError("Consumer names must be unique within a scenario.")
        observed = datetime.fromisoformat(scenario["observed_at"])
        corrected = datetime.fromisoformat(scenario["corrected_at"])
        if (observed.tzinfo is None or corrected.tzinfo is None or corrected < observed):
            raise ValueError("Correction dates must be timezone-aware and follow intake.")


def run_arm(spec: dict[str, Any], output: Path, mode: str) -> dict[str, Any]:
    validate_spec(spec)
    if mode not in {"framework", "snapshot-only"}:
        raise ValueError("Unknown comparison arm.")
    if output.exists():
        raise ValueError("Arm output must be a new directory; prior runs are never overwritten.")
    output.mkdir(parents=True)
    database = output / "receipts.sqlite"
    results = []
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE receipts (scenario TEXT, consumer TEXT, file TEXT, "
            "original_id TEXT, expected_id TEXT, sha256 TEXT, repaired INTEGER, "
            "PRIMARY KEY (scenario, consumer))"
        )
        connection.execute(
            "CREATE TABLE events (claim_id TEXT, seq INTEGER, payload TEXT, "
            "PRIMARY KEY (claim_id, seq))"
        )
        connection.execute(
            "CREATE TABLE claims (claim_id TEXT, stage TEXT, payload TEXT, sha256 TEXT, "
            "PRIMARY KEY (claim_id, stage))"
        )
        connection.execute(
            "CREATE TABLE population (receipts INTEGER, events INTEGER, claims INTEGER)"
        )
        for scenario in spec["scenarios"]:
            folder = output / scenario["id"]
            folder.mkdir()
            original = intake_claim(
                scenario["claim"], "Deidentified study subject", scenario["source"],
                SourceStatus.SOURCE_ESTABLISHED if scenario["official_record"]
                else SourceStatus.WORKING_HYPOTHESIS,
                is_official_record=scenario["official_record"],
                uncertainty=scenario["uncertainty"],
                note=f"Reconstructed source observation date: {scenario['observed_at']}",
            )
            intake_snapshot = original.to_dict()
            consumers = [folder / f"{name}.json" for name in scenario["consumers"]]
            for path in consumers:
                write_snapshot(path, original)
                if mode == "framework":
                    register_dependent(original.id, "managed-json", str(path),
                                       via="case-study local JSON adapter")
            decisions = [
                gate_for_use(original, "consequential")[0] if mode == "framework" else True
                for _ in consumers
            ]
            correction = disavow(
                original, "Case-study operator",
                f"{scenario['correction_reason']}; reconstructed source correction date: "
                f"{scenario['corrected_at']}",
                corrected_text=scenario["correction"],
            )
            corrected_use_allowed = gate_for_use(correction, "consequential")[0]
            repairs = 0
            for path in consumers:
                if mode == "framework":
                    repair_snapshot(original, correction, path)
                    repairs += 1
                actual = json.loads(path.read_text())
                expected_id = correction.id if mode == "framework" else original.id
                if actual["id"] != expected_id:
                    raise ValueError("Consumer read-back disagrees with expected arm behavior.")
                connection.execute("INSERT INTO receipts VALUES (?, ?, ?, ?, ?, ?, ?)", (
                    scenario["id"], path.stem, str(path.relative_to(output)),
                    original.id, expected_id, sha256(path), int(mode == "framework"),
                ))
            for record in (original, correction):
                valid, detail = verify_event_chain(record.id)
                if not valid:
                    raise ValueError(f"Lifecycle chain failed: {detail}")
                for event in claim_events(record.id):
                    connection.execute("INSERT INTO events VALUES (?, ?, ?)", (
                        record.id, event.seq, json.dumps(asdict(event), sort_keys=True),
                    ))
            for record, stage, payload in (
                (original, "intake", intake_snapshot),
                (original, "disavowed", original.to_dict()),
                (correction, "correction", correction.to_dict()),
            ):
                text = json.dumps(payload, sort_keys=True)
                connection.execute("INSERT INTO claims VALUES (?, ?, ?, ?)", (
                    record.id, stage, text, hashlib.sha256(text.encode()).hexdigest(),
                ))
            results.append({
                "scenario": scenario["id"], "consumers": len(consumers),
                "source_observed_at": scenario["observed_at"],
                "source_corrected_at": scenario["corrected_at"],
                "original_final_status": original.status.value,
                "consequential_uses_allowed": sum(decisions),
                "consequential_uses_blocked": len(decisions) - sum(decisions),
                "unverified_uses_allowed": sum(decisions) if not scenario["official_record"] else 0,
                "corroborated_uses_blocked": len(decisions) - sum(decisions)
                if scenario["official_record"] else 0,
                "correction_files_read_back": repairs,
                "original_claim_snapshots_remaining": sum(
                    json.loads(path.read_text())["id"] == original.id for path in consumers
                ),
                "corrected_claim_status": correction.status.value,
                "corrected_consequential_use_allowed": corrected_use_allowed,
            })
        connection.execute(
            "INSERT INTO population SELECT (SELECT COUNT(*) FROM receipts), "
            "(SELECT COUNT(*) FROM events), (SELECT COUNT(*) FROM claims)"
        )
    verified = verify_receipts(output)
    result = {
        "evaluation": f"Local correction case-study arm: {mode}",
        "evidence_scope": "Measured managed local files; no independent external efficacy claim.",
        "independent_external_validation": False, "arm": mode,
        "scenarios": results, "durable_receipts_verified": verified,
        "database_sha256": sha256(database),
        "limitations": [
            "Snapshot-only baseline is a specified comparator, not an observed historical system.",
            "Managed JSON consumers are actual local files; external services are not modified.",
            "Document narrative supplies a reconstructed scenario, not independent outcome labels.",
            "Correction is UNVERIFIED until independently corroborated, even after delivery.",
            "Receipts can be checked after restart; this is not a resumable distributed controller.",
        ],
    }
    write_reports(result, output)
    return result


def verify_receipts(output: Path) -> int:
    database = output / "receipts.sqlite"
    with sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro", uri=True) as connection:
        rows = connection.execute(
            "SELECT file, expected_id, sha256 FROM receipts ORDER BY scenario, consumer"
        ).fetchall()
        events = connection.execute(
            "SELECT claim_id, seq, payload FROM events ORDER BY claim_id, seq"
        ).fetchall()
        claims = connection.execute("SELECT claim_id, payload, sha256 FROM claims").fetchall()
        populations = connection.execute("SELECT receipts, events, claims FROM population").fetchall()
    if populations != [(len(rows), len(events), len(claims))]:
        raise ValueError("Durable population is incomplete or duplicated.")
    if not rows or not events or not claims:
        raise ValueError("Case-study receipts or lifecycle events are empty.")
    claim_ids = set()
    for claim_id, text, digest in claims:
        if (json.loads(text)["id"] != claim_id
                or hashlib.sha256(text.encode()).hexdigest() != digest):
            raise ValueError("Durable claim snapshot mismatch.")
        claim_ids.add(claim_id)
    root = output.resolve()
    for name, expected_id, expected_hash in rows:
        if expected_id not in claim_ids:
            raise ValueError("Consumer receipt refers to a missing durable claim.")
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Consumer receipt points outside managed workspace.")
        if sha256(path) != expected_hash or json.loads(path.read_text())["id"] != expected_id:
            raise ValueError(f"Consumer receipt mismatch: {name}")
    previous: dict[str, str] = {}
    sequences: dict[str, int] = {}
    for claim_id, sequence, text in events:
        event = json.loads(text)
        if (claim_id not in claim_ids or event["claim_id"] != claim_id or event["seq"] != sequence
                or sequence != sequences.get(claim_id, 0) + 1
                or event["prev_hash"] != previous.get(claim_id, "GENESIS")):
            raise ValueError("Durable lifecycle event order mismatch.")
        payload = {key: event[key] for key in (
            "claim_id", "event_type", "seq", "timestamp", "detail", "prev_hash",
        )}
        actual = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if actual != event["event_hash"]:
            raise ValueError("Durable lifecycle event hash mismatch.")
        previous[claim_id] = actual
        sequences[claim_id] = sequence
    machine = output / "evaluation.json"
    if machine.exists():
        verify_reports(machine, machine.with_suffix(".md"))
        if json.loads(machine.read_text())["database_sha256"] != sha256(database):
            raise ValueError("Durable database differs from synchronized report checksum.")
    return len(rows)


def compare(spec_path: Path, output: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text())
    validate_spec(spec)
    if output.exists():
        raise ValueError("Study output must be a new directory.")
    output.mkdir(parents=True)
    arms = {}
    for mode in ("snapshot-only", "framework"):
        process = subprocess.run([
            sys.executable, "-m", "vessell.case_study", "--spec", str(spec_path.resolve()),
            "--output-dir", str((output / mode).resolve()), "--arm", mode,
        ], check=False, capture_output=True, text=True)
        if process.returncode:
            raise RuntimeError(f"{mode} arm failed: {process.stdout}\n{process.stderr}")
        machine = output / mode / "evaluation.json"
        verify_reports(machine, machine.with_suffix(".md"))
        arms[mode] = json.loads(machine.read_text())
        if verify_receipts(output / mode) != arms[mode]["durable_receipts_verified"]:
            raise ValueError("Restarted receipt verification population changed.")
    outcomes = []
    for baseline, framework in zip(
        arms["snapshot-only"]["scenarios"], arms["framework"]["scenarios"], strict=True,
    ):
        if baseline["scenario"] != framework["scenario"]:
            raise ValueError("Comparison populations differ.")
        outcomes.append({
            "scenario": baseline["scenario"], "consumer_count": baseline["consumers"],
            "baseline": baseline, "framework": framework,
            "unverified_use_reduction_count": (
                baseline["unverified_uses_allowed"] - framework["unverified_uses_allowed"]
            ),
            "stale_snapshot_reduction_count": (
                baseline["original_claim_snapshots_remaining"]
                - framework["original_claim_snapshots_remaining"]
            ),
        })
    result = {
        "evaluation": "Comparative local claim-correction case study",
        "evidence_scope": "Controlled local software comparison; not independent field validation.",
        "independent_external_validation": False, "design": spec["design"],
        "specification_sha256": sha256(spec_path),
        "source_document_sha256": spec["source_document_sha256"],
        "implementation_sha256": sha256(Path(__file__)),
        "outcomes": outcomes,
        "acceptance_passed": all(
            row["framework"]["unverified_uses_allowed"] == 0
            and row["framework"]["corroborated_uses_blocked"] == 0
            and row["framework"]["original_claim_snapshots_remaining"] == 0
            and row["framework"]["correction_files_read_back"] == row["consumer_count"]
            and not row["framework"]["corrected_consequential_use_allowed"]
            for row in outcomes
        ),
        "limitations": [
            "Measured local software outcomes, not a randomized field or user-effectiveness study.",
            "Comparator deliberately omits gating and correction delivery; not a competitor benchmark.",
            "Official-record control is a constructed positive control, not a verified real event.",
            "Personal source document remains local; its hash establishes identity, not truth.",
            "No employment, application, external automation or production control outcome measured.",
            "No formal verification, SI capability certification or causal efficacy established.",
        ],
    }
    write_reports(result, output)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--arm", choices=("framework", "snapshot-only"))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.verify_only:
            if not (args.output_dir / "evaluation.json").is_file():
                raise ValueError("Verification requires a completed arm report.")
            print(f"Durable consumer receipts verified: {verify_receipts(args.output_dir)}")
            return 0
        if args.spec is None:
            raise ValueError("--spec is required for execution.")
        if args.arm:
            run_arm(json.loads(args.spec.read_text()), args.output_dir, args.arm)
            return 0
        result = compare(args.spec, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, sqlite3.Error) as error:
        print(f"CASE STUDY FAILED: {error}", file=sys.stderr)
        return 2
    print(f"CASE STUDY: {'PASS' if result['acceptance_passed'] else 'FAIL'}")
    return 0 if result["acceptance_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
