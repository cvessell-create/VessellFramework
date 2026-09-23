#!/usr/bin/env python3
"""Check whether the local VessellFramework environment is ready for live operation."""

from __future__ import annotations

import argparse
from pathlib import Path

from vessell.app.preflight import run_preflight


def main() -> int:
    parser = argparse.ArgumentParser(prog="vessell-preflight")
    parser.add_argument("--inventory", type=Path, default=Path("example_asset_inventory.json"))
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--strict", action="store_true", help="Return nonzero unless every check is ready.")
    args = parser.parse_args()

    checks = run_preflight(args.inventory, args.env_file)
    for check in checks:
        state = "READY" if check["ready"] else "BLOCKED"
        print(f"{state:7} {check['name']}: {check['detail']}")
    return 0 if not args.strict or all(check["ready"] for check in checks) else 2


if __name__ == "__main__":
    raise SystemExit(main())