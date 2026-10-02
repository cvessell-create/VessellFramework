"""Public claim-lifecycle guarantees not tied to a specific integration."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from vessel import ClaimKind as CompatibilityClaimKind
from vessell import ClaimKind, ClaimStatus, SourceStatus, intake_claim
from vessell.provenance import (
    add_corroboration,
    gate_for_use,
    reset_claim_lifecycle,
)


@pytest.fixture(autouse=True)
def _reset_lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def test_ai_generated_material_stays_unverified_and_is_serialized() -> None:
    claim = intake_claim(
        "A generated assertion.",
        "subject",
        "model output",
        SourceStatus.SOURCE_ESTABLISHED,
        is_ai_generated=True,
    )

    assert claim.status is ClaimStatus.UNVERIFIED
    assert gate_for_use(claim, "consequential")[0] is False
    assert claim.to_dict()["source"]["is_ai_generated"] is True


def test_ai_output_cannot_be_labeled_an_official_record() -> None:
    with pytest.raises(ValueError, match="AI-generated"):
        intake_claim(
            "A generated assertion.",
            "subject",
            "model output",
            SourceStatus.SOURCE_ESTABLISHED,
            is_official_record=True,
            is_ai_generated=True,
        )


def test_official_corroboration_and_schema_contract() -> None:
    claim = intake_claim(
        "Claim under review.",
        "subject",
        "analyst report",
        SourceStatus.WORKING_HYPOTHESIS,
    )
    updated = add_corroboration(
        claim,
        source="primary record",
        source_tier=SourceStatus.SOURCE_ESTABLISHED,
        is_official_record=True,
    )
    assert updated.status is ClaimStatus.CORROBORATED
    schema_path = Path(__file__).parents[1] / "schemas" / "claim.record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate({"record_type": "claim", "claim": updated.to_dict()})


def test_compatibility_namespace_uses_the_active_claim_types() -> None:
    assert CompatibilityClaimKind is ClaimKind
