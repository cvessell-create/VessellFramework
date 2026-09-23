"""Small command-line surface for validating framework records."""

import argparse
import json
from pathlib import Path

from .validation import validate_record


def main() -> int:
    parser = argparse.ArgumentParser(prog="vf")
    parser.add_argument("record", type=Path)
    parser.add_argument("--schema", default="case.schema.json")
    args = parser.parse_args()
    try:
        with args.record.open("r", encoding="utf-8") as file:
            record = json.load(file)
        validate_record(record, args.schema)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"VALIDATION FAILED: {error}")
        return 1
    print(f"VALIDATION PASSED: {args.record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
