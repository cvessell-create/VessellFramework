# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Optional, read-only Azure Log Analytics adapter for bounded SOC hunt plans."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from .agentic_soc import HuntPlan, redact_secrets


@dataclass(frozen=True)
class QueryBatch:
    """Normalized telemetry returned by a read-only workspace query."""

    table: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    truncated: bool


class AzureAdapterConfigurationError(RuntimeError):
    """Raised when the optional SDK or workspace configuration is unavailable."""


def _column_name(column: Any) -> str:
    name = getattr(column, "name", column)
    return str(name)


def _table_rows(table: Any) -> QueryBatch:
    columns = tuple(_column_name(column) for column in getattr(table, "columns", ()))
    raw_rows = list(getattr(table, "rows", ()))
    rows = tuple(
        {
            column: redact_secrets(str(value))
            for column, value in zip(columns, row, strict=False)
        }
        for row in raw_rows
    )
    return QueryBatch("", columns, rows, False)


class AzureLogAnalyticsAdapter:
    """Execute only approved read-only ``HuntPlan`` queries against Azure."""

    def __init__(self, client: Any, workspace_id: str, *, max_rows: int = 5_000) -> None:
        if not workspace_id.strip():
            raise ValueError("workspace_id must be a non-empty string.")
        if max_rows <= 0:
            raise ValueError("max_rows must be positive.")
        self._client = client
        self._workspace_id = workspace_id.strip()
        self._max_rows = max_rows

    @classmethod
    def from_environment(cls, *, max_rows: int = 5_000) -> AzureLogAnalyticsAdapter:
        """Build an adapter from Azure CLI/default credentials and environment config."""
        workspace_id = os.environ.get("VESSELFRAMEWORK_LOG_ANALYTICS_WORKSPACE_ID", "")
        if not workspace_id:
            raise AzureAdapterConfigurationError(
                "Set VESSELFRAMEWORK_LOG_ANALYTICS_WORKSPACE_ID before using the Azure adapter."
            )
        try:
            identity_module = importlib.import_module("azure.identity")
            monitor_module = importlib.import_module("azure.monitor.query")
        except ImportError as error:
            raise AzureAdapterConfigurationError(
                "Install the optional 'soc' dependencies to use the Azure adapter."
            ) from error
        credential = identity_module.DefaultAzureCredential()
        return cls(monitor_module.LogsQueryClient(credential), workspace_id, max_rows=max_rows)

    def query(self, plan: HuntPlan) -> QueryBatch:
        """Run a bounded read-only query and normalize its first result table."""
        if plan.max_rows > self._max_rows:
            raise ValueError("Hunt plan exceeds the adapter row cap.")
        response = self._client.query_workspace(
            self._workspace_id,
            plan.kql,
            timespan=timedelta(hours=plan.request.hours),
        )
        tables = list(getattr(response, "tables", ()))
        if not tables:
            return QueryBatch(plan.request.table, (), (), False)
        normalized = _table_rows(tables[0])
        rows = normalized.rows[: plan.max_rows]
        return QueryBatch(
            plan.request.table,
            normalized.columns,
            rows,
            len(normalized.rows) > len(rows),
        )