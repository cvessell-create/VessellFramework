# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Minimal Microsoft Intune remediation adapter for approved managed-device syncs."""

from __future__ import annotations

import os
from typing import Any

import httpx

REQUIRED_SETTINGS = (
    "MICROSOFT_TENANT_ID",
    "MICROSOFT_CLIENT_ID",
    "MICROSOFT_CLIENT_SECRET",
)


def _settings() -> dict[str, str]:
    values = {name: os.environ.get(name, "").strip() for name in REQUIRED_SETTINGS}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("Microsoft Intune configuration is missing: " + ", ".join(missing))
    return values


def _access_token(settings: dict[str, str]) -> str:
    response = httpx.post(
        f"https://login.microsoftonline.com/{settings['MICROSOFT_TENANT_ID']}/oauth2/v2.0/token",
        data={
            "client_id": settings["MICROSOFT_CLIENT_ID"],
            "client_secret": settings["MICROSOFT_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Microsoft token response did not include an access token.")
    return token


def sync_device(asset: dict[str, Any]) -> str:
    """Request an Intune device sync; device patch policy remains Intune-owned."""
    device_id = asset.get("intune_device_id")
    if not isinstance(device_id, str) or not device_id.strip():
        raise RuntimeError("Asset requires intune_device_id for Microsoft Intune remediation.")
    settings = _settings()
    token = _access_token(settings)
    response = httpx.post(
        f"https://graph.microsoft.com/v1.0/deviceManagement/managedDevices/{device_id}/syncDevice",
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    response.raise_for_status()
    return "Microsoft Intune managed-device sync requested."