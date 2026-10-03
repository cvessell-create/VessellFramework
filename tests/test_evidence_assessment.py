import copy
from pathlib import Path

import pytest

from vessell.evidence_assessment import IMPLEMENTATION_LINKS, combine_assessment


def test_all_declared_implementation_links_resolve():
    root = Path(__file__).resolve().parents[1]
    for source, targets in IMPLEMENTATION_LINKS.items():
        assert (root / source).is_file()
        assert all((root / target).is_file() for target in targets)


def test_evidence_extension_preserves_original_scores_and_unresolved_gaps():
    historical = {"file_scores": [
        {"path": "vesselframework_case_runner.py", "gap": "No behavior tests",
         "evidence_support": 0.1},
        {"path": "unreviewed.py", "gap": "No labels", "evidence_support": 0.2},
    ], "bottom_up": {"old_mean": 0.15}}
    prior = copy.deepcopy(historical)
    evidence = {"independent_external_validation": False}
    result = combine_assessment(
        historical, evidence, evidence, {"tests/test_harm_gate.py": "hash"}
    )
    assert historical == prior
    assert result["historical_assessment"] == prior
    links = result["validation_extension"]["artifact_gap_links"]
    assert links[0]["status"] == "CURRENT_LOCAL_EVIDENCE_LINKED"
    assert links[1]["status"] == "NOT_REASSESSED"
    assert all(link["score_changed"] is False for link in links)
    result["historical_assessment"]["file_scores"][0]["evidence_support"] = 1
    assert historical == prior


@pytest.mark.parametrize("claim", [True, None, "false"])
def test_extension_rejects_missing_or_overstated_external_validation(claim):
    with pytest.raises(ValueError, match="external efficacy"):
        combine_assessment(
            {"file_scores": []}, {"independent_external_validation": claim},
            {"independent_external_validation": False}, {},
        )


def test_duplicate_historical_artifact_is_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        combine_assessment(
            {"file_scores": [{"path": "same"}, {"path": "same"}]},
            {"independent_external_validation": False},
            {"independent_external_validation": False}, {},
        )
