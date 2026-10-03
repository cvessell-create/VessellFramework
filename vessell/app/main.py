# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Executable CLI for full-program case runs."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from .pipeline import run_case_pipeline
from .reporting import write_outputs


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "case"


def main() -> int:
    parser = argparse.ArgumentParser(prog="vf-program")
    parser.add_argument(
        "--input",
        default="example_case.json",
        type=Path,
        help="Path to case input JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("outputs/case_runs"),
        type=Path,
        help="Directory where report artifacts will be written.",
    )
    args = parser.parse_args()

    try:
        with args.input.open("r", encoding="utf-8") as file:
            case = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"RUN FAILED: unable to read input JSON: {error}")
        return 1

    try:
        result = run_case_pipeline(case)
    except (KeyError, TypeError, ValueError) as error:
        print(f"RUN FAILED: invalid case payload: {error}")
        return 2

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{timestamp}_{_slugify(result.title)}"
    markdown_path, json_path = write_outputs(result, args.output_dir, stem)

    print("RUN COMPLETE")
    print(f"- markdown_report: {markdown_path}")
    print(f"- machine_report: {json_path}")
    print(f"- confidence_ceiling: {result.confidence_ceiling}")
    print(f"- unresolved_lineage: {result.counts.unresolved_lineage}")
    if result.harm_gate is None or not result.harm_gate.cleared:
        print("RUNNER STATUS: REVIEW REQUIRED (Harm Gate)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
