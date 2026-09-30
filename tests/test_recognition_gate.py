import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "VesselFramework_SingleFile_EvilTwin_v0.2.py"
SPEC = importlib.util.spec_from_file_location("vessel_single_file_v02", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)


def test_name_only_match_is_quarantined() -> None:
    result = RUNTIME.recognition_gate(
        "Alex Cvessell",
        [{
            "identity": "Alex Cvessell",
            "class": "INDEPENDENT-MENTION",
            "root_id": "root-1",
        }],
    )

    assert result["identity_match_count"] == 0
    assert result["quarantined_identity_count"] == 1
    assert result["stage"] == "NOT-ESTABLISHED"


def test_derivative_items_share_one_independent_root() -> None:
    evidence = [
        {
            "identity": "Alex Cvessell",
            "class": "INDEPENDENT-MENTION",
            "root_id": "root-1",
            "corroborating_attributes": ["occupation", "location"],
            "title": "Mention",
        },
        {
            "identity": "Alex Cvessell",
            "class": "INDEPENDENT-EVALUATION",
            "root_id": "root-1",
            "corroborating_attributes": ["occupation", "location"],
            "title": "Derivative evaluation",
        },
    ]

    result = RUNTIME.recognition_gate("Alex Cvessell", evidence)

    assert result["raw_item_count"] == 2
    assert result["independent_root_count"] == 1
    assert result["strongest_class"] == "INDEPENDENT-EVALUATION"
