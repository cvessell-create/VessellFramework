# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Schema validation helpers for machine-readable framework records."""

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_ROOT = Path(__file__).parents[1] / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_ROOT / name
    with path.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    if not isinstance(schema, dict):
        raise TypeError(f"Schema must be a JSON object: {path}")
    return schema


def validate_record(record: Any, schema_name: str) -> None:
    validator = Draft202012Validator(load_schema(schema_name))
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(details)
