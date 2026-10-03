import copy
import json
from pathlib import Path

import pytest

from vessell.evaluation import write_reports
from vessell.provenance import reset_claim_lifecycle
from vessell.workflow import plan_workflow, run_workflow, validate_workflow, verify_workflow


@pytest.fixture(autouse=True)
def isolated_claims():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def specification():
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "case_studies/game_patterns/workflow.json").read_text())


def test_agent_replay_gates_roots_and_verifies_real_consumers(tmp_path):
    spec = specification()
    before = copy.deepcopy(spec)
    first = run_workflow(spec, tmp_path / "first")
    second = run_workflow(spec, tmp_path / "second")
    assert first["replay_sha256"] == second["replay_sha256"]
    assert first["original_intake"]["id"] != second["original_intake"]["id"]
    assert first["uses_blocked"] == 3
    assert first["uses_allowed"] == 1
    assert [row["independent_roots"] for row in first["trace"]
            if row["operation"] == "observe"] == [1, 1, 2]
    assert first["pipeline"]["counts"]["independent_roots"] == 2
    assert first["state"] == "COMPLETE"
    assert first["commands_executed"] == 9
    assert spec == before
    for receipt in first["consumers"]:
        payload = json.loads((tmp_path / "first" / receipt["file"]).read_text())
        assert payload["id"] == first["correction"]["id"]
        assert payload["status"] == "UNVERIFIED"
    assert verify_workflow(tmp_path / "first") == first


def test_narrative_every_sentence_cites_event_not_game_lore(tmp_path):
    result = run_workflow(specification(), tmp_path / "run")
    assert len(result["trace"]) == len(result["narrative"])
    for event, sentence in zip(result["trace"], result["narrative"], strict=True):
        assert sentence["event_sequence"] == event["sequence"]
        assert sentence["logical_tick"] == event["tick"]
        assert "Jack Slade" not in sentence["text"]
        assert sentence["standing"] == "MEASURED LOCAL SOFTWARE EVENT"


def test_missing_harm_fields_block_even_corroborated_uses(tmp_path):
    spec = specification()
    spec["case"]["harm_gate"] = {}
    result = run_workflow(spec, tmp_path / "run")
    assert result["uses_allowed"] == 0
    assert result["uses_blocked"] == 4
    assert result["harm_gate"]["exposure"] == "UNKNOWN"


def test_operator_pause_resume_and_stable_equal_tick_order(tmp_path):
    spec = specification()
    spec["controller"] = "operator"
    spec["commands"] = [
        {"tick": 0, "operation": "pause"},
        {"tick": 0, "operation": "resume"},
        {"tick": 1, "operation": "correct"},
        {"tick": 1, "operation": "finish"},
    ]
    result = run_workflow(spec, tmp_path / "run")
    assert [row["state"] for row in result["trace"]] == [
        "PAUSED", "REVIEW", "CORRECTED", "COMPLETE",
    ]


@pytest.mark.parametrize("operations", [
    ["resume", "correct", "finish"],
    ["pause", "use", "correct", "finish"],
    ["finish"],
    ["correct", "use", "finish"],
    ["correct", "finish", "finish"],
])
def test_invalid_transitions_never_emit_success_report(tmp_path, operations):
    spec = specification()
    spec["controller"] = "operator"
    spec["commands"] = [{"tick": index, "operation": operation}
                        for index, operation in enumerate(operations)]
    with pytest.raises(ValueError):
        run_workflow(spec, tmp_path / "failed")
    assert not (tmp_path / "failed/evaluation.json").exists()


@pytest.mark.parametrize("change", [
    "budget", "unsafe-path", "unknown-source", "duplicate-source",
    "out-of-order", "agent-command", "reserved-path",
])
def test_workflow_contract_rejects_bad_configurations(change):
    spec = specification()
    if change == "budget":
        spec["command_budget"] = 2
    elif change == "unsafe-path":
        spec["consumers"] = ["../escape"]
    elif change == "reserved-path":
        spec["consumers"] = ["evaluation"]
    elif change == "duplicate-source":
        spec["sources"].append(spec["sources"][0])
    else:
        spec["commands"] = plan_workflow(spec)
        if change != "agent-command":
            spec["controller"] = "operator"
        if change == "unknown-source":
            spec["commands"][1]["source_id"] = "unknown"
        elif change == "out-of-order":
            spec["commands"][0]["tick"] = 999
    with pytest.raises(ValueError):
        validate_workflow(spec)


def test_duplicate_observation_is_not_new_evidence(tmp_path):
    spec = specification()
    spec["controller"] = "operator"
    spec["commands"] = [
        {"tick": 0, "operation": "observe", "source_id": "primary"},
        {"tick": 1, "operation": "observe", "source_id": "primary"},
        {"tick": 2, "operation": "correct"},
        {"tick": 3, "operation": "finish"},
    ]
    with pytest.raises(ValueError, match="Duplicate"):
        run_workflow(spec, tmp_path / "run")


@pytest.mark.parametrize("target", ["consumer", "narrative", "population", "lifecycle"])
def test_verification_rejects_unsynchronized_or_corrupted_results(tmp_path, target):
    output = tmp_path / "run"
    result = run_workflow(specification(), output)
    if target == "consumer":
        (output / "goals.json").write_text("{}")
    else:
        if target == "narrative":
            result["narrative"][0]["text"] = "Invented success."
        elif target == "population":
            result["consumers"].pop()
        else:
            result["lifecycle_events"][result["original_final"]["id"]][0]["detail"] = "altered"
        write_reports(result, output)
    with pytest.raises(ValueError):
        verify_workflow(output)


def test_run_never_overwrites_prior_evidence(tmp_path):
    output = tmp_path / "run"
    run_workflow(specification(), output)
    with pytest.raises(ValueError, match="never overwritten"):
        run_workflow(specification(), output)
