import json

import pytest

from vessell.validation import validate_record


def test_example_case_matches_schema() -> None:
    with open("example_case.json", encoding="utf-8") as file:
        validate_record(json.load(file), "case.schema.json")


def test_case_schema_rejects_missing_evidence() -> None:
    with pytest.raises(ValueError):
        validate_record({"title": "Incomplete"}, "case.schema.json")
