# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Normalize authorized scanner results into inventory-confirmed CVEs."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from vessell.provenance import (
    ClaimKind,
    SourceStatus,
    intake_claim,
    register_dependent,
)

SUPPORTED_SOURCES = {"greenbone", "trivy", "osv-scanner", "wazuh"}
CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,}")


def _cves(value: object) -> set[str]:
    return set(CVE_PATTERN.findall(json.dumps(value).upper()))


def extract_cves(source: str, report: object) -> set[str]:
    """Extract CVE IDs from exported scanner JSON; no network actions occur."""
    if source not in SUPPORTED_SOURCES:
        raise ValueError(f"Unsupported scanner source: {source}.")
    if not isinstance(report, (dict, list)):
        raise TypeError("Scanner report must be a JSON object or array.")
    return _cves(report)


def import_confirmed_cves(
    inventory: dict[str, Any],
    *,
    asset_id: str,
    source: str,
    report: object,
    track_provenance: bool = True,
) -> dict[str, Any]:
    """Add scanner-confirmed CVEs to exactly one authorized inventory asset.

    With ``track_provenance`` (default), every newly confirmed CVE is
    intaked as a provenance claim (a scanner's verdict is framework
    synthesis, not an official record) and the inventory's
    ``confirmed_cves`` list registers as its dependent — so a later
    correction of a confirmation propagates to the asset record.
    """
    asset = authorized_asset(inventory, asset_id)

    confirmed = {str(cve).upper() for cve in asset.get("confirmed_cves", [])}
    new_cves = extract_cves(source, report)
    confirmed.update(new_cves)
    asset["confirmed_cves"] = sorted(confirmed)
    asset["scanner_source"] = source
    if track_provenance:
        for cve in sorted(new_cves):
            record = intake_claim(
                text=f"{cve} confirmed on asset {asset_id} by {source} scan",
                subject=asset_id,
                source=f"vessell.app.scanner_adapters import ({source})",
                source_tier=SourceStatus.FRAMEWORK_SYNTHESIS,
                kind=ClaimKind.REPORT,
            )
            register_dependent(
                record.id,
                artifact="asset-inventory",
                location=f"{asset_id}:confirmed_cves",
            )
    return inventory


def authorized_asset(inventory: dict[str, Any], asset_id: str) -> dict[str, Any]:
    assets = inventory.get("assets")
    if not isinstance(assets, list):
        raise TypeError("Inventory must contain an assets list.")
    asset: dict[str, Any] | None = next(
        (row for row in assets if row.get("asset_id") == asset_id), None
    )
    if asset is None:
        raise ValueError("Asset ID is not present in the inventory.")
    if not asset.get("authorized", False):
        raise ValueError("Asset is not authorized for scanner-result ingestion.")
    return asset


def _scanner_executable(source: str) -> str:
    executable = shutil.which(source)
    if executable:
        return executable
    homebrew_path = Path("/opt/homebrew/bin") / source
    if homebrew_path.is_file():
        return str(homebrew_path)
    raise RuntimeError(f"{source} is not installed or available on PATH.")


def run_local_scan(source: str, target_path: Path) -> dict[str, Any]:
    """Run an installed local code or filesystem scanner without invoking a shell."""
    if source == "trivy":
        command = [_scanner_executable("trivy"), "fs", "--format", "json", str(target_path)]
    elif source == "osv-scanner":
        command = [_scanner_executable("osv-scanner"), "scan", "source", "--format", "json", "--", str(target_path)]
    else:
        raise ValueError("Local mode supports only trivy or osv-scanner; import Greenbone/Wazuh exports instead.")

    completed = subprocess.run(command, capture_output=True, check=False, text=True, timeout=900)
    if completed.returncode not in {0, 1}:
        raise RuntimeError(f"{source} scan failed: {completed.stderr.strip()}")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{source} did not produce JSON output.") from error
    if not isinstance(report, dict):
        raise TypeError(f"{source} produced an invalid JSON report.")
    return report


def load_report(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_inventory(inventory: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")