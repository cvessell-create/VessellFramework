"""Local deterministic replay lab; no target contact or operational remediation."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from vessell.app.pipeline import run_case_pipeline
from vessell.app.reporting import verify_outputs, write_outputs
from vessell.data_evidence import audit_data, verify_catalog
from vessell.evaluation import (
    score_cdc,
    sha256,
    verify_reports,
    write_reports,
)
from vessell.harm_gate import REQUIRED_FIELDS, evaluate_harm_gate


def stress_gate(workers: int, repetitions: int) -> dict[str, Any]:
    if not 1 <= workers <= 16 or not 1 <= repetitions <= 256:
        raise ValueError("Use 1-16 workers and 1-256 repetitions.")
    complete = [
        dict(zip(REQUIRED_FIELDS, values, strict=True))
        for values in product((False, True), repeat=len(REQUIRED_FIELDS))
    ]
    partial = [
        {name: False for name in REQUIRED_FIELDS if name != omitted}
        for omitted in REQUIRED_FIELDS
    ]
    payloads = (complete + partial + [{}]) * repetitions
    original = [dict(payload) for payload in payloads]
    serial = [evaluate_harm_gate(payload) for payload in payloads]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        parallel = list(executor.map(evaluate_harm_gate, payloads))
    incomplete_cleared = sum(
        result.cleared for payload, result in zip(payloads, parallel, strict=True)
        if set(payload) != set(REQUIRED_FIELDS)
    )
    clearance_mismatches = sum(
        result.cleared != (payload.get("benefit_proportionate") is True)
        for payload, result in zip(payloads, parallel, strict=True)
        if set(payload) == set(REQUIRED_FIELDS)
    )
    return {
        "name": "parallel_harm_gate_replay",
        "passed": (parallel == serial and payloads == original
                   and incomplete_cleared == 0 and clearance_mismatches == 0),
        "workers": workers, "repetitions": repetitions, "evaluations": len(payloads),
        "complete_truth_table_cases": len(complete),
        "incomplete_inputs_cleared": incomplete_cleared,
        "clearance_rule_mismatches": clearance_mismatches,
        "serial_parallel_agreement": parallel == serial,
        "inputs_unchanged": payloads == original,
        "evidence_role": "SYNTHETIC_POLICY_AND_CONCURRENCY_TEST",
    }


def report_fault_test(output_dir: Path) -> dict[str, Any]:
    result = run_case_pipeline({
        "title": "Synthetic missing-intake replay", "evidence": [],
    }, track_provenance=False)
    markdown, machine = write_outputs(result, output_dir, "missing_gate_case")
    verify_outputs(result, markdown, machine)
    with TemporaryDirectory(prefix="vf-report-fault-", dir=output_dir) as temp:
        bad_markdown = Path(temp) / "case.md"
        bad_machine = Path(temp) / "case.json"
        shutil.copyfile(markdown, bad_markdown)
        shutil.copyfile(machine, bad_machine)
        bad_markdown.write_text(bad_markdown.read_text() + "\nInjected drift.\n")
        drift_rejected = False
        try:
            verify_outputs(result, bad_markdown, bad_machine)
        except ValueError as error:
            if "do not match" not in str(error):
                raise
            drift_rejected = True
    gate_blocked = (
        result.harm_gate is not None and not result.harm_gate.cleared
        and result.harm_gate.exposure == "UNKNOWN"
    )
    return {
        "name": "missing_intake_and_report_drift",
        "passed": gate_blocked and drift_rejected,
        "missing_gate_blocked": gate_blocked, "output_drift_rejected": drift_rejected,
        "evidence_role": "SYNTHETIC_END_TO_END_NEGATIVE_TEST",
    }


def corruption_test(data_dir: Path, output_dir: Path) -> dict[str, Any]:
    with TemporaryDirectory(prefix="vf-source-fault-", dir=output_dir) as temp:
        replay = Path(temp)
        for name in (
            "download_manifest.json", "cdc_ensemble_state_part1.csv",
            "cdc_ensemble_state_part2.csv", "cdc_observed_state.csv",
            "cdc_forecast_archive_metadata.json",
        ):
            shutil.copyfile(data_dir / name, replay / name)
        with (replay / "cdc_observed_state.csv").open("a", encoding="utf-8") as file:
            file.write("\nInjected corruption.\n")
        rejected = False
        try:
            score_cdc(replay)
        except ValueError as error:
            if "checksum mismatch" not in str(error):
                raise
            rejected = True
    return {
        "name": "source_corruption_rejected_before_scoring",
        "passed": rejected, "checksum_rejection": rejected,
        "evidence_role": "COPIED_SOURCE_FAULT_INJECTION",
    }


def run_lab(
    data_dir: Path, catalog_path: Path, output_dir: Path, *,
    workers: int = 4, repetitions: int = 32, decode_sources: bool = True,
) -> dict[str, Any]:
    if not 1 <= workers <= 16 or not 1 <= repetitions <= 256:
        raise ValueError("Use 1-16 workers and 1-256 repetitions.")
    source = data_dir.resolve(strict=True)
    output = output_dir.resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError("Lab outputs and source data must be separate non-nested directories.")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    frozen = verify_catalog(source, catalog["sources"])
    actual_names = {
        path.name for path in source.iterdir()
        if path.is_file() and path.name != "download_manifest.json"
    }
    if actual_names != set(frozen):
        raise ValueError("Frozen catalog does not cover the exact current source-file population.")
    manifest_hash = sha256(source / "download_manifest.json")
    output.mkdir(parents=True, exist_ok=True)
    checks = [stress_gate(workers, repetitions), report_fault_test(output)]
    checks.append(corruption_test(source, output))
    audit = audit_data(source, catalog_path, decode_sources=decode_sources)
    write_reports(audit, output / "data_audit")
    forecast = score_cdc(source)
    write_reports(forecast, output / "forecast")
    counts = forecast["counts"]
    partition = (
        counts["scored"] + counts["exact_duplicate_forecasts_excluded"]
        + counts["nonfuture_targets_excluded"] + counts["unmatched_observation"]
        + counts["missing_baseline"]
    )
    checks.append({
        "name": "real_forecast_population_accounting",
        "passed": (counts["selected"] == partition and counts["scored"] > 0
                   and counts["scored"] == counts["interval_scored"] + counts["missing_interval"]),
        "selected": counts["selected"], "accounted": partition,
        "scored": counts["scored"], "metrics": forecast["metrics"],
        "evidence_role": "EXTERNAL_FORECAST_REPLAY_NOT_FRAMEWORK_PREDICTION",
    })
    after = verify_catalog(source, catalog["sources"])
    checks.append({
        "name": "original_sources_unchanged",
        "passed": frozen == after and manifest_hash == sha256(source / "download_manifest.json"),
        "verified_source_files": len(frozen),
        "evidence_role": "LOCAL_INPUT_IDENTITY_CHECK",
    })
    return {
        "evaluation": "Isolated local public-data replay lab",
        "independent_external_validation": False,
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
        "runtime": {"python": platform.python_version(), "executable": sys.executable},
        "catalog_sha256": sha256(catalog_path),
        "frozen_source_hashes": frozen, "download_manifest_sha256": manifest_hash,
        "implementation_hashes": {
            name: sha256(Path(__file__).parent / name) for name in (
                "replay_lab.py", "data_evidence.py", "evaluation.py", "harm_gate.py",
                "source_readers.py", "app/pipeline.py", "app/reporting.py",
            )
        },
        "limitations": [
            "Python venv isolates dependencies, not OS resources, filesystem or network privileges.",
            "This runner requests no downloads, target scans or remediation; setup installs packages.",
            "Faults use copies in temporary folders; public source files remain unchanged.",
            "Synthetic gate/report tests are not incident or intervention efficacy outcomes.",
            "CDC metrics concern externally produced forecasts, not framework forecasts.",
            "Unknown/withheld data does not become a negative label.",
            "Operational control outcomes, posting-level labels and prospective studies remain needed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--repetitions", type=int, default=32)
    parser.add_argument("--skip-source-decoding", action="store_true",
                        help="Explicitly skip optional full PDF/Parquet decoding.")
    args = parser.parse_args()
    try:
        result = run_lab(
            args.data_dir, args.catalog, args.output_dir,
            workers=args.workers, repetitions=args.repetitions,
            decode_sources=not args.skip_source_decoding,
        )
        machine, human = write_reports(result, args.output_dir)
        verify_reports(machine, human)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(f"REPLAY LAB FAILED: {error}", file=sys.stderr)
        return 2
    print(f"Replay results saved and synchronized: {machine}, {human}")
    print(f"REPLAY LAB: {'PASS' if result['passed'] else 'FAIL'}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
