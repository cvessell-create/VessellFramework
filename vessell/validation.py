# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Schema validation helpers for machine-readable framework records."""

import json
from pathlib import Path
from typing import Any

SCHEMA_ROOT = Path(__file__).with_name("schemas")


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_ROOT / name
    if path.parent != SCHEMA_ROOT or path.suffix != ".json":
        raise ValueError(f"Unknown schema: {name}")
    with path.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    if not isinstance(schema, dict):
        raise TypeError(f"Schema must be a JSON object: {path}")
    return schema


def validate_record(record: Any, schema_name: str) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise RuntimeError(
            "Schema validation needs jsonschema: pip install 'vessell-framework[core]'"
        ) from error
    validator = Draft202012Validator(load_schema(schema_name))
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(details)


# Fields every provenance-tagged intake must carry before a record is
# accepted for validation (doctrine: tag at intake, or do not intake).
REQUIRED_PROVENANCE_FIELDS = ("source", "source_tier", "observed_at", "status")


def require_provenance_fields(record: dict[str, Any]) -> dict[str, Any]:
    """Enforce provenance tagging at validation time.

    Every record accepted for downstream use must name its source, its
    source tier, when it was observed, and its corroboration standing.
    Missing or blank fields raise ValueError naming the gaps — the
    record is rejected at the boundary instead of entering the system
    untagged.
    """
    missing = [
        field
        for field in REQUIRED_PROVENANCE_FIELDS
        if not isinstance(record.get(field), str) or not record[field].strip()
    ]
    if missing:
        raise ValueError(
            "Record rejected: missing provenance fields: " + ", ".join(missing)
        )
    return record
