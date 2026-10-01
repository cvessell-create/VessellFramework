#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""One-click live case run: fetches the official CISA KEV feed and produces a
VesselFramework doctrine-to-code report on currently active, US-relevant
exploited vulnerabilities.

Usage:
    python3 run_live_kev_case.py [--lookback-days N] [--limit N] [--output-dir DIR]
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from vessell.app.pipeline import run_case_pipeline
from vessell.app.reporting import write_outputs
from vessell.app.sources.cisa_kev import (
    DEFAULT_LIMIT,
    DEFAULT_LOOKBACK_DAYS,
    build_case_from_kev,
    fetch_kev_catalog,
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_live_kev_case")
    parser.add_argument("--lookback-days", type=int, default=DEFAULT_LOOKBACK_DAYS)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/case_runs"))
    parser.add_argument(
        "--save-case",
        type=Path,
        default=None,
        help="Optional path to also save the raw case JSON that was submitted to the pipeline.",
    )
    args = parser.parse_args()

    try:
        catalog = fetch_kev_catalog()
    except OSError as error:
        print(f"RUN FAILED: unable to fetch CISA KEV feed: {error}")
        return 1

    case = build_case_from_kev(catalog, lookback_days=args.lookback_days, limit=args.limit)

    if args.save_case is not None:
        args.save_case.parent.mkdir(parents=True, exist_ok=True)
        args.save_case.write_text(json.dumps(case, indent=2), encoding="utf-8")

    try:
        result = run_case_pipeline(case)
    except (KeyError, TypeError, ValueError) as error:
        print(f"RUN FAILED: invalid case payload: {error}")
        return 2

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{timestamp}_live-cisa-kev-case"
    markdown_path, json_path = write_outputs(result, args.output_dir, stem)

    print("RUN COMPLETE")
    print(f"- evidence_count: {result.counts.total_evidence}")
    print(f"- markdown_report: {markdown_path}")
    print(f"- machine_report: {json_path}")
    print(f"- confidence_ceiling: {result.confidence_ceiling}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
