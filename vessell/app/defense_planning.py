"""Correlate live CISA KEV intelligence with an authorized local asset inventory."""

from __future__ import annotations

import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def _normalise_asset(row: dict[str, Any], index: int) -> dict[str, Any]:
    prefix = f"assets[{index}]"
    return {
        "asset_id": _text(row.get("asset_id"), f"{prefix}.asset_id"),
        "vendor": _text(row.get("vendor"), f"{prefix}.vendor"),
        "product": _text(row.get("product"), f"{prefix}.product"),
        "internet_exposed": bool(row.get("internet_exposed", False)),
        "criticality": str(row.get("criticality", "standard")).strip().lower(),
        "authorized": bool(row.get("authorized", False)),
        "confirmed_cves": [
            _text(cve_id, f"{prefix}.confirmed_cves")
            for cve_id in row.get("confirmed_cves", [])
        ],
        "remediation_webhook": str(row.get("remediation_webhook", "")).strip(),
    }


def load_asset_inventory(path: Path) -> list[dict[str, Any]]:
    """Load an authorized local inventory from JSON or CSV."""
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("assets") if isinstance(payload, dict) else payload
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            rows = list(csv.DictReader(file))
    else:
        raise ValueError("Inventory must be a .json or .csv file.")

    if not isinstance(rows, list) or not rows:
        raise ValueError("Inventory must contain a non-empty assets list.")

    assets = [_normalise_asset(row, index) for index, row in enumerate(rows)]
    asset_ids = [str(asset["asset_id"]) for asset in assets]
    if len(asset_ids) != len(set(asset_ids)):
        raise ValueError("Inventory must not contain duplicate asset_id values.")
    return assets


def _match_type(asset: dict[str, Any], kev: dict[str, Any]) -> str | None:
    if kev.get("cveID") in asset.get("confirmed_cves", []):
        return "scanner_confirmed_cve"

    asset_vendor = _tokens(str(asset["vendor"]))
    kev_vendor = _tokens(str(kev.get("vendorProject", "")))
    if not asset_vendor or asset_vendor != kev_vendor:
        return None

    kev_product = _tokens(str(kev.get("product", "")))
    if kev_product == {"multiple", "products"}:
        return "vendor_only"

    if _tokens(str(asset["product"])) & kev_product:
        return "vendor_and_product"
    return None


def build_defense_plan(
    assets: list[dict[str, Any]],
    catalog: dict[str, Any],
    *,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build reviewable containment and remediation actions without executing them."""
    timestamp = generated_at or datetime.now(UTC)
    actions: list[dict[str, Any]] = []

    for kev in catalog.get("vulnerabilities", []):
        if not isinstance(kev, dict) or not kev.get("cveID"):
            continue
        for asset in assets:
            if not asset.get("authorized", False):
                continue
            match_type = _match_type(asset, kev)
            if match_type is None:
                continue

            dispatch_eligible = match_type == "scanner_confirmed_cve"
            contain = dispatch_eligible and (
                bool(asset.get("internet_exposed", False))
                or asset.get("criticality", "standard") == "critical"
            )
            actions.append(
                {
                    "action_id": f"{asset['asset_id']}:{kev['cveID']}",
                    "asset_id": asset["asset_id"],
                    "cve_id": kev["cveID"],
                    "vulnerability": kev.get("vulnerabilityName", "Unnamed vulnerability"),
                    "due_date": kev.get("dueDate", "Unknown"),
                    "match_type": match_type,
                    "priority": "CRITICAL" if contain else "REVIEW",
                    "dispatch_eligible": dispatch_eligible,
                    "status": "PENDING_APPROVAL" if dispatch_eligible else "REVIEW_REQUIRED",
                    "actions": (
                        [
                            "Restrict untrusted network access while remediation is pending.",
                            "Apply the vendor patch or CISA-listed mitigation.",
                        ]
                        if contain
                        else ["Confirm the CVE with an authorized scanner before remediation."]
                    ),
                    "verification": "Confirm the fixed version or mitigation, then rescan the asset.",
                }
            )

    actions.sort(key=lambda action: (action["priority"] != "CRITICAL", action["due_date"]))
    return {
        "generated_at": timestamp.astimezone(UTC).isoformat(timespec="seconds"),
        "source": "CISA Known Exploited Vulnerabilities catalog",
        "catalog_version": catalog.get("catalogVersion", "unknown"),
        "asset_count": len(assets),
        "matched_action_count": len(actions),
        "approval_required": True,
        "execution_status": "PENDING_APPROVAL",
        "actions": actions,
    }


def approve_plan(plan: dict[str, Any], approver: str) -> dict[str, Any]:
    """Record approval; endpoint and firewall execution requires a separate authorized adapter."""
    approved = dict(plan)
    approved["execution_status"] = "APPROVED_FOR_AUTHORIZED_DEPLOYMENT"
    approved["approved_by"] = _text(approver, "approver")
    approved["approved_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    return approved


def write_defense_plan(plan: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return output_path