import json

import pytest

from tests.test_evaluation import data_fixture
from vessell.replay_lab import corruption_test, report_fault_test, run_lab, stress_gate


def test_parallel_lab_exercises_every_complete_combination_and_missing_fields():
    result = stress_gate(4, 2)
    assert result["passed"]
    assert result["complete_truth_table_cases"] == 128
    assert result["evaluations"] == 272
    assert result["incomplete_inputs_cleared"] == 0
    assert result["clearance_rule_mismatches"] == 0
    assert result["inputs_unchanged"]


@pytest.mark.parametrize("workers,repetitions", [(0, 1), (17, 1), (1, 0), (1, 257)])
def test_lab_rejects_unbounded_resources(workers, repetitions):
    with pytest.raises(ValueError):
        stress_gate(workers, repetitions)


def test_missing_gate_and_corrupt_output_are_rejected_end_to_end(tmp_path):
    result = report_fault_test(tmp_path)
    assert result["passed"]
    assert result["missing_gate_blocked"]
    assert result["output_drift_rejected"]
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "missing_gate_case.json", "missing_gate_case.md",
    ]


def test_source_fault_uses_copy_and_does_not_touch_original(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    data_fixture(source)
    original = (source / "cdc_observed_state.csv").read_bytes()
    output = tmp_path / "outputs"
    output.mkdir()
    assert corruption_test(source, output)["passed"]
    assert (source / "cdc_observed_state.csv").read_bytes() == original
    assert list(output.iterdir()) == []


def test_lab_rejects_output_inside_source_before_any_write(tmp_path):
    with pytest.raises(ValueError, match="non-nested"):
        run_lab(tmp_path, tmp_path / "catalog.json", tmp_path / "outputs")
    assert list(tmp_path.iterdir()) == []


def test_lab_rejects_incomplete_frozen_population(tmp_path):
    source = tmp_path / "data"
    source.mkdir()
    (source / "unlisted.csv").write_text("unlisted")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"sources": []}))
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="exact current"):
        run_lab(source, catalog, output)
    assert not output.exists()
