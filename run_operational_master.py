#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Run the safe, non-destructive stages documented in VesselFramework_Agent.md."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from vessell.app.defense_planning import build_defense_plan, load_asset_inventory, write_defense_plan
from vessell.app.pipeline import run_case_pipeline
from vessell.app.reporting import write_outputs
from vessell.app.sources.cisa_kev import build_case_from_kev, fetch_kev_catalog


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_operational_master")
    parser.add_argument("--inventory", type=Path, default=Path("example_asset_inventory.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    if args.run_tests:
        result = subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False)
        if result.returncode:
            return result.returncode

    try:
        catalog = fetch_kev_catalog()
        case = build_case_from_kev(catalog)
        case_result = run_case_pipeline(case)
        assets = load_asset_inventory(args.inventory)
        defense_plan = build_defense_plan(assets, catalog)
    except (OSError, TypeError, ValueError) as error:
        print(f"RUN FAILED: {error}")
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    case_directory = args.output_dir / "case_runs"
    defense_directory = args.output_dir / "defense_plans"
    report_path, case_json_path = write_outputs(case_result, case_directory, f"{timestamp}_operational-master-kev")
    plan_path = write_defense_plan(defense_plan, defense_directory / f"{timestamp}_operational-master-plan.json")

    print("OPERATIONAL MASTER COMPLETE")
    print(f"- live_kev_report: {report_path}")
    print(f"- live_kev_data: {case_json_path}")
    print(f"- defense_plan: {plan_path}")
    print(f"- remediation_actions: {defense_plan['matched_action_count']}")
    print("- next_step: import scanner-confirmed CVEs before any approval or dispatch.")
    if case_result.harm_gate is None or not case_result.harm_gate.cleared:
        print("RUNNER STATUS: REVIEW REQUIRED (Harm Gate)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())