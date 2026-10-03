import pytest
from jsonschema import Draft202012Validator

from vessell.validation import load_schema, validate_record
from vessell.verify import (
    ClaimCheck,
    JobPosting,
    analyze_planted_news,
    detect_ghost_job,
    verify_claim,
)

EXAMPLES = {
    "evidence_product.schema.json": {
        "claim": "Illustrative contract test", "evidence_ids": ["source-1"],
        "confidence": "LOW", "validation_level": "SCHEMA_ONLY", "release_status": "DRAFT",
    },
    "forecast.schema.json": {
        "id": "f-1", "question": "Illustrative binary event", "outcome": "yes",
        "horizon": "2027-01-01", "probability": 0.5, "status": "UNRESOLVED",
    },
    "skill_record.schema.json": {
        "name": "Illustrative skill", "version": "1", "status": "DRAFT",
    },
}


@pytest.mark.parametrize("schema_name", EXAMPLES)
def test_positive_and_every_required_field_negative_contract(schema_name: str) -> None:
    schema = load_schema(schema_name)
    Draft202012Validator.check_schema(schema)
    record = EXAMPLES[schema_name]
    validate_record(record, schema_name)
    for field in schema["required"]:
        without = {key: value for key, value in record.items() if key != field}
        with pytest.raises(ValueError):
            validate_record(without, schema_name)


@pytest.mark.parametrize("probability", [-0.01, 1.01, "0.5", None])
def test_forecast_rejects_invalid_probability(probability) -> None:
    record = {**EXAMPLES["forecast.schema.json"], "probability": probability}
    with pytest.raises(ValueError):
        validate_record(record, "forecast.schema.json")


def test_evidence_product_rejects_empty_evidence() -> None:
    record = {**EXAMPLES["evidence_product.schema.json"], "evidence_ids": []}
    with pytest.raises(ValueError):
        validate_record(record, "evidence_product.schema.json")


@pytest.mark.parametrize("kind", ["verification", "planted-news", "ghost-job"])
def test_verification_schema_matches_real_serializers_and_requires_payload(kind: str) -> None:
    check = ClaimCheck("Illustrative test claim")
    payloads = {
        "verification": verify_claim(check).to_dict(),
        "planted-news": analyze_planted_news(check).to_dict(),
        "ghost-job": detect_ghost_job([
            JobPosting("Test role", "Test employer", "Test location", "Illustrative")
        ]).to_dict(),
    }
    validate_record({"record_type": kind, kind: payloads[kind]}, "verification.record.schema.json")
    with pytest.raises(ValueError):
        validate_record({"record_type": kind}, "verification.record.schema.json")
    with pytest.raises(ValueError):
        validate_record({"record_type": kind, **payloads}, "verification.record.schema.json")
