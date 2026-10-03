import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from itertools import product
from pathlib import Path

import pytest

import vesselframework_case_runner as legacy
from vessell.app import main
from vessell.app.pipeline import run_case_pipeline
from vessell.app.reporting import render_markdown_report, verify_outputs, write_outputs
from vessell.harm_gate import REQUIRED_FIELDS, evaluate_harm_gate
from vessell.validation import validate_record


def complete_gate(**changes: bool) -> dict[str, bool]:
    return {**dict.fromkeys(REQUIRED_FIELDS, False), "benefit_proportionate": True, **changes}


def test_parallel_stress_matches_serial_and_does_not_mutate_intake() -> None:
    complete = [dict(zip(REQUIRED_FIELDS, values, strict=True))
                for values in product((False, True), repeat=len(REQUIRED_FIELDS))]
    partial = [{key: value for key, value in complete_gate().items() if key != field}
               for field in REQUIRED_FIELDS]
    payloads = (complete + partial + [{}]) * 32
    original = [dict(payload) for payload in payloads]
    expected = [evaluate_harm_gate(payload) for payload in payloads]
    with ThreadPoolExecutor(max_workers=4) as executor:
        actual = list(executor.map(evaluate_harm_gate, payloads))
    assert actual == expected
    assert payloads == original
    assert all(not result.cleared for payload, result in zip(payloads, actual, strict=True)
               if set(payload) != set(REQUIRED_FIELDS))


@pytest.mark.parametrize("payload", [None, {}, {"benefit_proportionate": True}])
def test_missing_assessments_are_unknown_and_not_cleared(payload) -> None:
    result = evaluate_harm_gate(payload)
    assert result.exposure == "UNKNOWN"
    assert not result.cleared
    assert result.missing_fields
    assert legacy.evaluate_harm_gate(payload) == asdict(result)


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_every_missing_field_blocks_clearance(field: str) -> None:
    gate = complete_gate()
    del gate[field]
    result = evaluate_harm_gate(gate)
    assert not result.cleared
    assert result.missing_fields == [field]


@pytest.mark.parametrize("value", ["false", 0, 1, None, [], {}])
def test_invalid_boolean_is_rejected(value) -> None:
    gate = {**complete_gate(), "accuracy_risk": value}
    with pytest.raises(ValueError, match="accuracy_risk must be a boolean"):
        evaluate_harm_gate(gate)


@pytest.mark.parametrize("payload", [False, [], ""])
def test_non_object_gate_is_rejected(payload) -> None:
    with pytest.raises(TypeError, match="must be an object"):
        evaluate_harm_gate(payload)


@pytest.mark.parametrize(
    ("changes", "exposure"),
    [
        ({}, "LOW"),
        ({"accuracy_risk": True}, "MODERATE"),
        ({"hard_to_reverse": True}, "HIGH"),
        ({"accuracy_risk": True, "academic_risk": True, "legal_risk": True}, "HIGH"),
        (
            {"hard_to_reverse": True, "accuracy_risk": True, "legal_risk": True},
            "SEVERE / IRREVERSIBLE",
        ),
    ],
)
def test_complete_gate_preserves_exposure_ladder(changes, exposure: str) -> None:
    result = evaluate_harm_gate(complete_gate(**changes))
    assert result.exposure == exposure
    assert result.cleared
    assert not evaluate_harm_gate(complete_gate(**changes, benefit_proportionate=False)).cleared


def test_runner_and_packaged_report_both_block_missing_gate() -> None:
    case = json.loads(Path("example_case.json").read_text(encoding="utf-8"))
    del case["harm_gate"]
    report, blocked = legacy.markdown_report(case, legacy.load_reference_module(Path.cwd()))
    assert blocked
    assert "Exposure: **UNKNOWN**" in report
    assert "Overall intake status: **REVIEW REQUIRED**" in report
    result = run_case_pipeline(case, track_provenance=False)
    assert result.harm_gate is not None and not result.harm_gate.cleared
    assert "Exposure: UNKNOWN" in render_markdown_report(result)


def test_cli_missing_gate_exits_review_required(tmp_path, monkeypatch, capsys) -> None:
    case = json.loads(Path("example_case.json").read_text(encoding="utf-8"))
    del case["harm_gate"]
    source = tmp_path / "input.json"
    source.write_text(json.dumps(case), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["vf-program", "--input", str(source),
                                    "--output-dir", str(tmp_path / "reports")])
    assert main.main() == 1
    assert "REVIEW REQUIRED" in capsys.readouterr().out


def test_case_schema_rejects_string_boolean() -> None:
    case = json.loads(Path("example_case.json").read_text(encoding="utf-8"))
    case["harm_gate"]["accuracy_risk"] = "false"
    with pytest.raises(ValueError):
        validate_record(case, "case.schema.json")


def test_all_128_complete_gate_boolean_combinations() -> None:
    for values in product((False, True), repeat=len(REQUIRED_FIELDS)):
        gate = dict(zip(REQUIRED_FIELDS, values))
        result = evaluate_harm_gate(gate)
        risks = sum(values[:5])
        expected = (
            "SEVERE / IRREVERSIBLE" if values[5] and risks >= 2
            else "HIGH" if values[5] or risks >= 3
            else "MODERATE" if risks
            else "LOW"
        )
        assert result.exposure == expected
        assert result.cleared is values[6]
        assert legacy.evaluate_harm_gate(gate) == asdict(result)


def test_case_outputs_are_synchronized_and_detect_tampering(tmp_path) -> None:
    case = json.loads(Path("example_case.json").read_text(encoding="utf-8"))
    result = run_case_pipeline(case, track_provenance=False)
    markdown, machine = write_outputs(result, tmp_path, "case")
    verify_outputs(result, markdown, machine)
    payload = json.loads(machine.read_text())
    payload["harm_gate"]["cleared"] = False
    machine.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="do not match"):
        verify_outputs(result, markdown, machine)
