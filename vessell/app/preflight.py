# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Pre-live readiness checks for the VessellFramework Control Room."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .microsoft_intune import REQUIRED_SETTINGS as INTUNE_SETTINGS
from .scanner_adapters import _scanner_executable


def _result(name: str, ready: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ready": ready, "detail": detail}


def _configured(value: str | None) -> bool:
    return bool(value and value.strip() and not value.startswith("replace-with"))


def run_preflight(inventory_path: Path, dotenv_path: Path = Path(".env")) -> list[dict[str, Any]]:
    """Return a non-secret readiness report without dispatching any action."""
    load_dotenv(dotenv_path, override=False)
    checks = [_result("python", sys.version_info >= (3, 13), f"Python {sys.version.split()[0]}")]

    dependencies = [name for name in ("fastapi", "httpx") if importlib.util.find_spec(name)]
    checks.append(_result("orchestrator_dependencies", len(dependencies) == 2, ", ".join(dependencies) or "missing"))

    scanners: list[str] = []
    for source in ("trivy", "osv-scanner"):
        try:
            scanners.append(f"{source}: {_scanner_executable(source)}")
        except RuntimeError:
            continue
    checks.append(_result("local_scanners", bool(scanners), "; ".join(scanners) or "install Trivy or OSV-Scanner"))

    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        assets = inventory.get("assets", [])
        authorized = [asset for asset in assets if asset.get("authorized")]
        placeholders = [asset for asset in authorized if str(asset.get("asset_id", "")).startswith("replace-with")]
        checks.append(
            _result(
                "authorized_inventory",
                bool(authorized) and not placeholders,
                f"{len(authorized)} authorized asset(s); {len(placeholders)} placeholder asset ID(s)",
            )
        )
        uses_intune = any(asset.get("remediation_provider") == "microsoft-intune" for asset in authorized)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        checks.append(_result("authorized_inventory", False, str(error)))
        uses_intune = False

    base_settings = ("APPROVAL_TOKEN", "SCANNER_TOKEN", "WEBHOOK_SECRET", "ALLOWED_WEBHOOK_PREFIX")
    missing = [name for name in base_settings if not _configured(os.environ.get(name))]
    checks.append(_result("control_room_secrets", not missing, ", ".join(missing) or "configured"))

    if uses_intune:
        missing_intune = [name for name in INTUNE_SETTINGS if not _configured(os.environ.get(name))]
        checks.append(_result("microsoft_intune", not missing_intune, ", ".join(missing_intune) or "configured"))
    else:
        checks.append(_result("microsoft_intune", True, "not selected by an authorized asset"))
    return checks