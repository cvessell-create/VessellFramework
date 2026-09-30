# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Persistent approval-gated remediation orchestration for scanner-confirmed KEVs."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from .defense_planning import build_defense_plan, load_asset_inventory
from .microsoft_intune import sync_device
from .sources.cisa_kev import fetch_kev_catalog

REQUIRED_CONFIG = (
    "APPROVAL_TOKEN",
    "SCANNER_TOKEN",
    "WEBHOOK_SECRET",
    "ALLOWED_WEBHOOK_PREFIX",
)


def validate_required_configuration() -> dict[str, str]:
    values = {name: os.environ.get(name, "") for name in REQUIRED_CONFIG}
    missing = [name for name, value in values.items() if not value.strip()]
    if missing:
        raise RuntimeError("Required security configuration is missing: " + ", ".join(missing))

    allowed_prefix = values["ALLOWED_WEBHOOK_PREFIX"]
    parsed = urlparse(allowed_prefix)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("ALLOWED_WEBHOOK_PREFIX must be an absolute HTTPS URL.")
    if not allowed_prefix.endswith("/"):
        raise RuntimeError("ALLOWED_WEBHOOK_PREFIX must end with '/'.")
    return values


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class RemediationStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as database:
            database.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    action_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    cve_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    approved_by TEXT,
                    change_ticket TEXT,
                    result TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            database.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _audit(
        self, database: sqlite3.Connection, action_id: str, event: str, actor: str, details: dict[str, Any]
    ) -> None:
        database.execute(
            "INSERT INTO audit_log(action_id, event, actor, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (action_id, event, actor, json.dumps(details, sort_keys=True), _now()),
        )

    def synchronize(self, assets: list[dict[str, Any]], catalog: dict[str, Any]) -> int:
        plan = build_defense_plan(assets, catalog)
        asset_by_id = {asset["asset_id"]: asset for asset in assets}
        kev_by_cve = {entry.get("cveID"): entry for entry in catalog.get("vulnerabilities", [])}
        created = 0

        with self._connect() as database:
            for action in plan["actions"]:
                payload = {
                    "asset": asset_by_id[action["asset_id"]],
                    "cisa": kev_by_cve[action["cve_id"]],
                    # Provenance: the defense-plan claim this action was
                    # derived from, so corrections propagate to the action.
                    "plan_claim_id": plan.get("claim_id", ""),
                }
                cursor = database.execute(
                    """
                    INSERT OR IGNORE INTO actions(
                        action_id, asset_id, cve_id, status, payload, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        action["action_id"],
                        action["asset_id"],
                        action["cve_id"],
                        action["status"],
                        json.dumps(payload, sort_keys=True),
                        _now(),
                        _now(),
                    ),
                )
                if cursor.rowcount:
                    created += 1
                    self._audit(database, action["action_id"], "ACTION_CREATED", "kev-synchronizer", action)
        return created

    def list_actions(self, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM actions"
        values: tuple[str, ...] = ()
        if status:
            query += " WHERE status = ?"
            values = (status,)
        query += " ORDER BY created_at, action_id"
        with self._connect() as database:
            return [dict(row) for row in database.execute(query, values).fetchall()]

    def approve(self, action_id: str, approved_by: str, change_ticket: str) -> None:
        if not approved_by.strip() or not change_ticket.strip():
            raise ValueError("approved_by and change_ticket are required.")
        with self._connect() as database:
            row = database.execute("SELECT status FROM actions WHERE action_id = ?", (action_id,)).fetchone()
            if row is None:
                raise KeyError("Action not found.")
            if row["status"] != "PENDING_APPROVAL":
                raise ValueError(f"Action is currently {row['status']}.")
            database.execute(
                "UPDATE actions SET status = 'APPROVED', approved_by = ?, change_ticket = ?, updated_at = ? WHERE action_id = ?",
                (approved_by.strip(), change_ticket.strip(), _now(), action_id),
            )
            self._audit(database, action_id, "ACTION_APPROVED", approved_by.strip(), {"change_ticket": change_ticket})

    def verify(self, action_id: str, fixed: bool, evidence: str) -> None:
        if not evidence.strip():
            raise ValueError("verification evidence is required.")
        status = "VERIFIED" if fixed else "VERIFICATION_FAILED"
        with self._connect() as database:
            row = database.execute("SELECT status FROM actions WHERE action_id = ?", (action_id,)).fetchone()
            if row is None:
                raise KeyError("Action not found.")
            database.execute(
                "UPDATE actions SET status = ?, result = ?, updated_at = ? WHERE action_id = ?",
                (status, evidence.strip(), _now(), action_id),
            )
            self._audit(database, action_id, status, "vulnerability-scanner", {"evidence": evidence.strip()})

    def dispatch(self, action_id: str) -> str:
        configuration = validate_required_configuration()
        allowed_prefix = configuration["ALLOWED_WEBHOOK_PREFIX"]
        webhook_secret = configuration["WEBHOOK_SECRET"]
        with self._connect() as database:
            row = database.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,)).fetchone()
            if row is None:
                raise KeyError("Action not found.")
            if row["status"] != "APPROVED":
                raise ValueError(f"Action is currently {row['status']}.")
            payload = json.loads(row["payload"])
            if payload["asset"].get("remediation_provider") == "microsoft-intune":
                database.execute("UPDATE actions SET status = 'DISPATCHING', updated_at = ? WHERE action_id = ?", (_now(), action_id))
                self._audit(database, action_id, "DISPATCH_STARTED", "microsoft-intune", {})
                intune_asset = payload["asset"]
                endpoint = None
            else:
                intune_asset = None
                endpoint = payload["asset"].get("remediation_webhook", "")
            if endpoint is not None and (not endpoint.startswith("https://") or not endpoint.startswith(allowed_prefix)):
                database.execute(
                    "UPDATE actions SET status = 'BLOCKED_CONFIGURATION', result = ?, updated_at = ? WHERE action_id = ?",
                    ("Webhook is not on the HTTPS allowlist.", _now(), action_id),
                )
                self._audit(database, action_id, "DISPATCH_BLOCKED", "remediation-worker", {"endpoint": endpoint})
                return "BLOCKED_CONFIGURATION"
            if endpoint is not None:
                database.execute("UPDATE actions SET status = 'DISPATCHING', updated_at = ? WHERE action_id = ?", (_now(), action_id))
                self._audit(database, action_id, "DISPATCH_STARTED", "remediation-worker", {})

        request_payload = {
            "action_id": action_id,
            "operation": "apply_vendor_remediation",
            "asset_id": row["asset_id"],
            "cve_id": row["cve_id"],
            "change_ticket": row["change_ticket"],
            "requested_at": _now(),
        }
        try:
            if intune_asset is not None:
                status, result = "DISPATCHED", sync_device(intune_asset)
            else:
                if not isinstance(endpoint, str) or not endpoint:
                    raise RuntimeError(
                        "Remediation webhook endpoint is not configured."
                    )
                body = json.dumps(request_payload, separators=(",", ":"), sort_keys=True).encode()
                signature = hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()
                response = httpx.post(
                    endpoint,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "Idempotency-Key": action_id,
                        "X-Remediation-Signature": f"sha256={signature}",
                    },
                    timeout=60,
                )
                response.raise_for_status()
                status, result = "DISPATCHED", response.text[:4000]
        except (httpx.HTTPError, RuntimeError, OSError) as error:
            status, result = "DISPATCH_FAILED", str(error)

        with self._connect() as database:
            database.execute(
                "UPDATE actions SET status = ?, result = ?, updated_at = ? WHERE action_id = ?",
                (status, result, _now(), action_id),
            )
            self._audit(database, action_id, f"DISPATCH_{status}", "remediation-worker", {"result": result})
        return status


def create_app() -> Any:
    """Create the local remediation API from environment-based configuration."""
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse

    poll_seconds = int(os.environ.get("POLL_SECONDS", "300"))
    inventory_path = Path(os.environ.get("INVENTORY_FILE", "example_asset_inventory.json"))
    store = RemediationStore(Path(os.environ.get("DATABASE", "outputs/remediation/remediation.db")))

    def require_token(provided: str | None, name: str) -> None:
        try:
            expected = validate_required_configuration()[name]
        except RuntimeError as error:
            raise HTTPException(503, str(error)) from error
        if not provided or not hmac.compare_digest(provided, expected):
            raise HTTPException(401, "Invalid authorization token.")

    def synchronize() -> dict[str, Any]:
        assets = load_asset_inventory(inventory_path)
        catalog = fetch_kev_catalog()
        return {
            "catalog_version": catalog.get("catalogVersion", "unknown"),
            "assets_checked": len(assets),
            "actions_created": store.synchronize(assets, catalog),
        }

    async def polling_loop() -> None:
        while True:
            try:
                validate_required_configuration()
                await asyncio.to_thread(synchronize)
            except (OSError, RuntimeError, ValueError) as error:
                print(f"KEV synchronization failed: {error}", flush=True)
            await asyncio.sleep(poll_seconds)

    @asynccontextmanager
    async def lifespan(_: Any) -> AsyncGenerator[None]:
        validate_required_configuration()
        store.initialize()
        task = asyncio.create_task(polling_loop())
        yield
        task.cancel()

    app = FastAPI(title="VessellFramework KEV Remediation Orchestrator", lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return Path(__file__).with_name("remediation_dashboard.html").read_text(encoding="utf-8")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "time": _now()}

    @app.post("/sync")
    async def sync(x_approval_token: str | None = Header(default=None)) -> dict[str, Any]:
        require_token(x_approval_token, "APPROVAL_TOKEN")
        return await asyncio.to_thread(synchronize)

    @app.get("/actions")
    def actions(status: str | None = None) -> list[dict[str, Any]]:
        return store.list_actions(status)

    @app.post("/actions/{action_id}/approve")
    def approve(
        action_id: str,
        approval: dict[str, str],
        x_approval_token: str | None = Header(default=None),
    ) -> dict[str, str]:
        require_token(x_approval_token, "APPROVAL_TOKEN")
        try:
            store.approve(action_id, approval.get("approved_by", ""), approval.get("change_ticket", ""))
        except KeyError as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        asyncio.create_task(asyncio.to_thread(store.dispatch, action_id))
        return {"action_id": action_id, "status": "APPROVED"}

    @app.post("/actions/{action_id}/verify")
    def verify(
        action_id: str,
        verification: dict[str, Any],
        x_scanner_token: str | None = Header(default=None),
    ) -> dict[str, str]:
        require_token(x_scanner_token, "SCANNER_TOKEN")
        try:
            store.verify(action_id, bool(verification.get("fixed")), str(verification.get("evidence", "")))
        except KeyError as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        return {"action_id": action_id, "status": "VERIFIED" if verification.get("fixed") else "VERIFICATION_FAILED"}

    return app


def main() -> int:
    import argparse
    import sys

    import uvicorn
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(prog="vf-remediator")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    load_dotenv()
    try:
        validate_required_configuration()
    except RuntimeError as error:
        print(f"CONFIGURATION ERROR: {error}", file=sys.stderr)
        print("Copy .env.example to .env and replace every placeholder value.", file=sys.stderr)
        return 2
    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())