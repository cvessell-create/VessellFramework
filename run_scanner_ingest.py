#!/usr/bin/env python3
"""Import authorized scanner findings into one inventory asset's confirmed CVEs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from vessell.app.scanner_adapters import authorized_asset, import_confirmed_cves, load_report, run_local_scan, write_inventory


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_scanner_ingest")
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--source", required=True, choices=("greenbone", "trivy", "osv-scanner", "wazuh"))
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--report", type=Path)
    input_group.add_argument("--local-path", type=Path)
    args = parser.parse_args()

    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        authorized_asset(inventory, args.asset_id)
        report = load_report(args.report) if args.report else run_local_scan(args.source, args.local_path)
        updated = import_confirmed_cves(inventory, asset_id=args.asset_id, source=args.source, report=report)
        write_inventory(updated, args.inventory)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"INGEST FAILED: {error}")
        return 1

    print("INGEST COMPLETE")
    print(f"- source: {args.source}")
    print(f"- asset_id: {args.asset_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())