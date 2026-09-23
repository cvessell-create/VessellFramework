#!/usr/bin/env python3
"""Create an approval-gated defense plan from live CISA KEV intelligence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from vessell.app.defense_planning import approve_plan, build_defense_plan, load_asset_inventory, write_defense_plan
from vessell.app.sources.cisa_kev import fetch_kev_catalog


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_active_defense")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/defense_plans"))
    parser.add_argument("--approve", metavar="APPROVER")
    args = parser.parse_args()

    try:
        assets = load_asset_inventory(args.inventory)
        catalog = fetch_kev_catalog()
        plan = build_defense_plan(assets, catalog)
    except (OSError, ValueError) as error:
        print(f"RUN FAILED: {error}")
        return 1

    if args.approve:
        plan = approve_plan(plan, args.approve)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = write_defense_plan(plan, args.output_dir / f"{timestamp}_active-defense-plan.json")
    print("RUN COMPLETE")
    print(f"- defense_plan: {output_path}")
    print(f"- matched_actions: {plan['matched_action_count']}")
    print(f"- execution_status: {plan['execution_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())