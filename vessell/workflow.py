"""Bounded analyst workflows adapted from observable game architecture."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any

from vessell.app.pipeline import run_case_pipeline
from vessell.case_study import repair_snapshot, write_snapshot
from vessell.evaluation import sha256, verify_reports, write_reports
from vessell.harm_gate import evaluate_harm_gate
from vessell.provenance import (
    SourceStatus,
    add_corroboration,
    claim_events,
    disavow,
    gate_for_use,
    intake_claim,
    register_dependent,
    verify_event_chain,
)
from vessell.validation import validate_record


class WorkflowState(str, Enum):
    REVIEW = "REVIEW"
    READY = "READY"
    PAUSED = "PAUSED"
    CORRECTED = "CORRECTED"
    COMPLETE = "COMPLETE"


def digest_payload(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def plan_workflow(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """A transparent local agent proposes commands; it does not grant clearance."""
    commands: list[dict[str, Any]] = [{"operation": "use"}]
    for source in spec["sources"]:
        commands.append({"operation": "observe", "source_id": source["id"]})
        commands.append({"operation": "use"})
    commands.extend([{"operation": "correct"}, {"operation": "finish"}])
    return [{"tick": tick, **command} for tick, command in enumerate(commands)]


def validate_workflow(spec: dict[str, Any]) -> list[dict[str, Any]]:
    validate_record(spec, "workflow.schema.json")
    validate_record(spec["case"], "case.schema.json")
    sources = spec["sources"]
    if len({row["id"] for row in sources}) != len(sources):
        raise ValueError("Source IDs must be unique; roots may legitimately repeat.")
    commands = plan_workflow(spec) if spec["controller"] == "agent" else copy.deepcopy(
        spec["commands"]
    )
    if spec["controller"] == "agent" and spec["commands"]:
        raise ValueError("Agent mode cannot silently ignore operator commands.")
    if len(commands) > spec["command_budget"]:
        raise ValueError("Command population exceeds the explicit workflow budget.")
    ticks = [command["tick"] for command in commands]
    if ticks != sorted(ticks):
        raise ValueError("Logical ticks must be nondecreasing; input order breaks equal-tick ties.")
    source_ids = {source["id"] for source in sources}
    for command in commands:
        if command["operation"] == "observe" and command["source_id"] not in source_ids:
            raise ValueError(f"Unknown observation source: {command['source_id']}")
    if not commands or commands[-1]["operation"] != "finish":
        raise ValueError("A bounded workflow must explicitly finish.")
    return commands


def render_narrative(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every sentence cites its producing logical event, never unsupported story lore."""
    narrative = []
    for event in trace:
        number = event["sequence"]
        operation = event["operation"]
        if operation == "use":
            sentence = (
                "Consequential local use permitted by both gates."
                if event["allowed"] else
                "Consequential use blocked: " + "; ".join(event["reasons"])
            )
        elif operation == "observe":
            sentence = (
                f"Recorded source {event['source_id']}; "
                f"{event['independent_roots']} declared independent root(s)."
            )
        elif operation == "correct":
            sentence = (
                f"Original retained and disavowed; {event['verified_consumers']} "
                "local consumers corrected and read back. Replacement remains UNVERIFIED."
            )
        else:
            sentence = f"Workflow {operation}: state {event['state']}."
        narrative.append({
            "event_sequence": number, "logical_tick": event["tick"],
            "text": sentence, "standing": "MEASURED LOCAL SOFTWARE EVENT",
        })
    return narrative


def run_workflow(spec: dict[str, Any], output: Path) -> dict[str, Any]:
    commands = validate_workflow(spec)
    if output.exists():
        raise ValueError("Output must be new; preserved runs are never overwritten.")
    frozen = copy.deepcopy(spec)
    pipeline = run_case_pipeline(copy.deepcopy(spec["case"]), track_provenance=False)
    pipeline_payload: dict[str, Any] = json.loads(json.dumps(asdict(pipeline)))
    harm = evaluate_harm_gate(spec["case"].get("harm_gate"))
    output.mkdir(parents=True)
    claim = intake_claim(
        spec["claim"]["text"], spec["case"]["subject"],
        spec["claim"]["source"], SourceStatus.WORKING_HYPOTHESIS,
        source_root=spec["claim"]["root"], uncertainty=spec["claim"]["uncertainty"],
    )
    original_intake = claim.to_dict()
    consumers = [output / f"{name}.json" for name in spec["consumers"]]
    hashes = {}
    for path in consumers:
        hashes[path.name] = write_snapshot(path, claim)
        register_dependent(claim.id, "managed-json", str(path),
                           via="workflow provisional record; not permission to operationalize")
    state = WorkflowState.REVIEW
    resume_state = state
    sources = {source["id"]: source for source in spec["sources"]}
    observed: set[str] = set()
    correction = None
    trace: list[dict[str, Any]] = []
    for sequence, command in enumerate(commands, start=1):
        operation = command["operation"]
        if state is WorkflowState.COMPLETE:
            raise ValueError("Commands after completion are invalid.")
        if state is WorkflowState.PAUSED and operation != "resume":
            raise ValueError("Paused workflows accept only resume.")
        if state is WorkflowState.CORRECTED and operation != "finish":
            raise ValueError("Corrected workflow must finish; use a new intake for further decisions.")
        for path in consumers:
            if path.is_symlink() or sha256(path) != hashes[path.name]:
                raise ValueError(f"Consumer drift before command {sequence}: {path.name}")
        event: dict[str, Any] = {
            "sequence": sequence, "tick": command["tick"], "operation": operation,
        }
        if operation == "observe":
            source_id = command["source_id"]
            if source_id in observed:
                raise ValueError("Duplicate observation command; sightings are not new sources.")
            source = sources[source_id]
            add_corroboration(
                claim, source=source["description"], source_tier=SourceStatus.SOURCE_ESTABLISHED,
                root=source["root"],
            )
            observed.add(source_id)
            event.update(source_id=source_id, independent_roots=claim.independent_roots())
        elif operation == "use":
            allowed, reason = gate_for_use(claim, "consequential")
            event["allowed"] = allowed and harm.cleared
            event["reasons"] = ([reason] if not allowed else []) + (
                harm.safeguards if not harm.cleared else []
            )
            state = WorkflowState.READY if event["allowed"] else WorkflowState.REVIEW
        elif operation == "pause":
            resume_state, state = state, WorkflowState.PAUSED
        elif operation == "resume":
            if state is not WorkflowState.PAUSED:
                raise ValueError("Resume requires a paused workflow.")
            state = resume_state
        elif operation == "correct":
            correction = disavow(
                claim, spec["operator"], spec["correction"]["reason"],
                corrected_text=spec["correction"]["text"],
            )
            for path in consumers:
                hashes[path.name] = repair_snapshot(claim, correction, path)
            state = WorkflowState.CORRECTED
            event["verified_consumers"] = len(consumers)
        elif operation == "finish":
            if state is not WorkflowState.CORRECTED:
                raise ValueError("Completion requires applied, verified correction.")
            state = WorkflowState.COMPLETE
        event["state"] = state.value
        trace.append(event)
    if correction is None or state is not WorkflowState.COMPLETE:
        raise ValueError("Workflow failed completion criteria.")
    lifecycle = {}
    for record in (claim, correction):
        valid, reason = verify_event_chain(record.id)
        if not valid:
            raise ValueError(f"Lifecycle verification failed: {reason}")
        lifecycle[record.id] = [asdict(event) for event in claim_events(record.id)]
    if spec != frozen:
        raise ValueError("Workflow mutated its specification.")
    narrative = render_narrative(trace)
    replay = {
        "specification_sha256": digest_payload(spec),
        "implementation_sha256": sha256(Path(__file__)),
        "trace": trace, "narrative": narrative,
        "pipeline": pipeline_payload,
    }
    result = {
        "evaluation": "Game-pattern analyst workflow",
        "evidence_scope": "Actual local analyst APIs and file read-back; no game score or field efficacy claim.",
        "state": state.value, "controller": spec["controller"],
        "trace": trace, "narrative": narrative,
        "replay_projection": replay, "replay_sha256": digest_payload(replay),
        "specification": frozen,
        "uses_allowed": sum(event.get("allowed") is True for event in trace),
        "uses_blocked": sum(event.get("allowed") is False for event in trace),
        "commands_executed": len(trace), "command_budget": spec["command_budget"],
        "harm_gate": asdict(harm), "pipeline": pipeline_payload,
        "original_intake": original_intake, "original_final": claim.to_dict(),
        "correction": correction.to_dict(), "lifecycle_events": lifecycle,
        "consumers": [{"file": path.name, "sha256": hashes[path.name],
                       "claim_id": correction.id} for path in consumers],
        "limitations": [
            "Declared source roots are operator-supplied lineage, not independently authenticated sources.",
            "Deterministic replay projection excludes random claim IDs and real execution timestamps.",
            "Consequential use here records a local decision only; it invokes no external action.",
            "Harm Gate clearance and source corroboration do not prove control efficacy.",
            "Narrative sentences cite local events, not fictional characters as evidence.",
            "Partial failed output remains for diagnosis; no crash-resume or multiwriter transaction.",
        ],
    }
    write_reports(result, output)
    verify_workflow(output)
    return result


def verify_workflow(output: Path) -> dict[str, Any]:
    machine = output / "evaluation.json"
    verify_reports(machine, machine.with_suffix(".md"))
    result: dict[str, Any] = json.loads(machine.read_text())
    commands = validate_workflow(result["specification"])
    trace = result["trace"]
    if len(trace) != len(commands):
        raise ValueError("Workflow trace population differs from the specified queue.")
    for number, (command, event) in enumerate(zip(commands, trace, strict=True), start=1):
        if (event["sequence"] != number or event["tick"] != command["tick"]
                or event["operation"] != command["operation"]):
            raise ValueError("Workflow trace order differs from the specified queue.")
    if render_narrative(trace) != result["narrative"]:
        raise ValueError("Narrative is not grounded in the recorded trace.")
    projection = result["replay_projection"]
    if (projection["trace"] != trace or projection["narrative"] != result["narrative"]
            or projection["specification_sha256"] != digest_payload(result["specification"])
            or projection["pipeline"] != result["pipeline"]
            or digest_payload(projection) != result["replay_sha256"]):
        raise ValueError("Replay projection or checksum mismatch.")
    if (result["state"] != "COMPLETE" or trace[-1]["state"] != "COMPLETE"
            or result["commands_executed"] != len(trace)
            or result["uses_allowed"] != sum(event.get("allowed") is True for event in trace)
            or result["uses_blocked"] != sum(event.get("allowed") is False for event in trace)
            or result["correction"]["status"] != "UNVERIFIED"
            or result["original_final"]["status"] != "DISAVOWED"
            or result["correction"]["supersedes"] != result["original_final"]["id"]):
        raise ValueError("Workflow outcome or claim lifecycle mismatch.")
    if not result["harm_gate"]["cleared"] and result["uses_allowed"]:
        raise ValueError("Uncleared Harm Gate cannot permit a local use.")
    expected_ids = {result["original_final"]["id"], result["correction"]["id"]}
    events = result["lifecycle_events"]
    if set(events) != expected_ids:
        raise ValueError("Lifecycle event population mismatch.")
    for claim_id, chain in events.items():
        previous = "GENESIS"
        if not chain:
            raise ValueError("Lifecycle event history is empty.")
        for number, event in enumerate(chain, start=1):
            payload = {key: event[key] for key in (
                "claim_id", "event_type", "seq", "timestamp", "detail", "prev_hash",
            )}
            if (event["claim_id"] != claim_id or event["seq"] != number
                    or event["prev_hash"] != previous
                    or digest_payload(payload) != event["event_hash"]):
                raise ValueError("Persisted lifecycle event integrity mismatch.")
            previous = event["event_hash"]
    expected_files = {f"{name}.json" for name in result["specification"]["consumers"]}
    receipts = result["consumers"]
    if len(receipts) != len(expected_files) or {row["file"] for row in receipts} != expected_files:
        raise ValueError("Consumer receipt population mismatch.")
    for receipt in receipts:
        path = output / receipt["file"]
        if (path.is_symlink() or sha256(path) != receipt["sha256"]
                or json.loads(path.read_text())["id"] != result["correction"]["id"]
                or receipt["claim_id"] != result["correction"]["id"]):
            raise ValueError("Consumer read-back receipt mismatch.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--compare-to", type=Path, help="Previously completed run with matching inputs.")
    args = parser.parse_args()
    try:
        if args.verify_only:
            result = verify_workflow(args.output_dir)
        else:
            if args.spec is None:
                raise ValueError("--spec is required.")
            result = run_workflow(json.loads(args.spec.read_text()), args.output_dir)
        if args.compare_to:
            previous = verify_workflow(args.compare_to)
            if previous["replay_sha256"] != result["replay_sha256"]:
                raise ValueError("Deterministic replay differs; inputs or implementation may have changed.")
        print(f"WORKFLOW VERIFIED: {result['commands_executed']} commands; "
              f"{len(result['consumers'])} corrected consumers; replay {result['replay_sha256']}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"WORKFLOW FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
