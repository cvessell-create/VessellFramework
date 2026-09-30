# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Safe planning primitives for an evidence-first agentic SOC workflow.

This module plans hunts and remediation proposals but never queries a workspace,
calls an LLM, changes a host, or executes a containment action.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from vessell.provenance import register_dependent

DEFAULT_MAX_HOURS: Final = 96
DEFAULT_MAX_ROWS: Final = 5_000
DEFAULT_MAX_TOKENS: Final = 100_000
DEFAULT_INPUT_COST_PER_MILLION: Final = 0.25
DEFAULT_OUTPUT_COST_PER_MILLION: Final = 2.00


@dataclass(frozen=True)
class TableDefinition:
    name: str
    fields: tuple[str, ...]
    purpose: str
    timestamp_field: str


@dataclass(frozen=True)
class HuntRequest:
    request: str
    table: str
    fields: tuple[str, ...]
    hours: int
    host: str | None
    user: str | None


@dataclass(frozen=True)
class HuntPlan:
    request: HuntRequest
    kql: str
    max_rows: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost: float
    model: str
    approval_required: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class RemediationProposal:
    action: str
    target: str
    rationale: str
    authorization_required: bool
    rollback_required: bool
    executed: bool = False
    claim_id: str = ""  # provenance claim that motivated this proposal, if any


TABLES: Final[dict[str, TableDefinition]] = {
    "DeviceLogonEvents": TableDefinition(
        "DeviceLogonEvents",
        ("Timestamp", "AccountName", "DeviceName", "ActionType", "RemoteIP"),
        "Authentication activity against managed devices.",
        "Timestamp",
    ),
    "SigninLogs": TableDefinition(
        "SigninLogs",
        ("TimeGenerated", "UserPrincipalName", "IPAddress", "Location", "ResultType"),
        "Cloud identity sign-in activity.",
        "TimeGenerated",
    ),
    "DeviceProcessEvents": TableDefinition(
        "DeviceProcessEvents",
        ("Timestamp", "AccountName", "DeviceName", "FileName", "ProcessCommandLine"),
        "Process execution telemetry from managed devices.",
        "Timestamp",
    ),
    "DeviceNetworkEvents": TableDefinition(
        "DeviceNetworkEvents",
        ("Timestamp", "DeviceName", "RemoteIP", "RemotePort", "ActionType"),
        "Network connection telemetry from managed devices.",
        "Timestamp",
    ),
}

MODEL_LIMITS: Final[dict[str, tuple[int, float, float]]] = {
    "gpt-5-mini": (272_000, 0.25, 2.00),
    "gpt-4.1": (1_000_000, 2.00, 8.00),
    "gpt-4.1-mini": (128_000, 0.40, 1.60),
}

SECRET_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[^\s,'\"]+"),
    re.compile(r"\b[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
)


def redact_secrets(value: str) -> str:
    """Redact common credential-shaped values before model submission."""
    if not isinstance(value, str):
        raise TypeError("value must be a string.")
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: match.group(0).split("=")[0] + "=[REDACTED]", redacted)
    return redacted


def _choose_table(request: str) -> str:
    lowered = request.lower()
    has_host = _extract_host(request) is not None
    if has_host and any(term in lowered for term in ("sign-in", "signin", "logged in", "logon", "login")):
        return "DeviceLogonEvents"
    if any(term in lowered for term in ("sign-in", "signin", "tenant", "azure login", "identity")):
        return "SigninLogs"
    if any(term in lowered for term in ("process", "powershell", "command line", "executed")):
        return "DeviceProcessEvents"
    if any(term in lowered for term in ("network", "firewall", "connection", "traffic")):
        return "DeviceNetworkEvents"
    return "DeviceLogonEvents"


def _extract_host(request: str) -> str | None:
    match = re.search(r"\b(?:Windows|Linux|Ubuntu|Device|Host|VM)[\w.-]*\b", request, re.IGNORECASE)
    return match.group(0) if match else None


def _extract_user(request: str) -> str | None:
    match = re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", request)
    return match.group(0) if match else None


def parse_hunt_request(request: str) -> HuntRequest:
    """Convert a natural-language request into an allowlisted hunt request."""
    if not isinstance(request, str) or not request.strip():
        raise ValueError("request must be a non-empty string.")
    table = _choose_table(request)
    definition = TABLES[table]
    hours_match = re.search(r"\b(\d+)\s*(?:hours?|hrs?|days?)\b", request, re.IGNORECASE)
    hours = int(hours_match.group(1)) if hours_match else 24
    if hours_match and "day" in hours_match.group(0).lower():
        hours *= 24
    selected_fields = definition.fields
    return HuntRequest(
        request=redact_secrets(request.strip()),
        table=table,
        fields=selected_fields,
        hours=hours,
        host=_extract_host(request),
        user=_extract_user(request),
    )


def build_kql(hunt: HuntRequest) -> str:
    """Build a constrained KQL query from an already validated hunt request."""
    definition = TABLES.get(hunt.table)
    if definition is None:
        raise ValueError(f"Table is not allowlisted: {hunt.table}")
    unknown = set(hunt.fields) - set(definition.fields)
    if unknown:
        raise ValueError(f"Fields are not allowlisted for {hunt.table}: {sorted(unknown)}")
    projections = ", ".join(hunt.fields)
    clauses = [f"{hunt.table}", f"where {definition.timestamp_field} >= ago({hunt.hours}h)"]
    if hunt.host and "DeviceName" in definition.fields:
        clauses.append(f'where DeviceName =~ "{hunt.host}"')
    if hunt.user and "UserPrincipalName" in definition.fields:
        clauses.append(f'where UserPrincipalName =~ "{hunt.user}"')
    clauses.extend([f"project {projections}", f"sort by {definition.timestamp_field} desc"])
    return "\n| ".join(clauses)


def estimate_tokens(text: str) -> int:
    """Use a conservative character-based estimate without external tokenizers."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    return max(1, (len(text) + 3) // 4)


def plan_hunt(
    request: str,
    *,
    model: str = "gpt-5-mini",
    max_hours: int = DEFAULT_MAX_HOURS,
    max_rows: int = DEFAULT_MAX_ROWS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> HuntPlan:
    """Create a bounded hunt plan; this function performs no I/O."""
    if model not in MODEL_LIMITS:
        raise ValueError(f"Model is not allowlisted: {model}")
    if max_hours <= 0 or max_rows <= 0 or max_tokens <= 0:
        raise ValueError("Guardrail limits must be positive.")

    parsed = parse_hunt_request(request)
    warnings: list[str] = []
    hours = min(parsed.hours, max_hours)
    if parsed.hours > max_hours:
        warnings.append(f"Requested window capped from {parsed.hours} to {max_hours} hours.")
    bounded = HuntRequest(parsed.request, parsed.table, parsed.fields, hours, parsed.host, parsed.user)
    kql = build_kql(bounded)
    prompt_context = redact_secrets(f"Request: {bounded.request}\nKQL:\n{kql}")
    estimated_input = estimate_tokens(prompt_context) + max_rows * 12
    estimated_output = min(2_000, max_tokens // 10)
    context_limit, input_cost, output_cost = MODEL_LIMITS[model]
    if estimated_input + estimated_output > min(context_limit, max_tokens):
        warnings.append("Estimated prompt exceeds the selected model or configured token budget.")
    cost = (estimated_input / 1_000_000) * input_cost + (estimated_output / 1_000_000) * output_cost
    warnings.append("Live query, model call, and remediation remain disabled until separately authorized.")
    return HuntPlan(
        request=bounded,
        kql=kql,
        max_rows=max_rows,
        estimated_input_tokens=estimated_input,
        estimated_output_tokens=estimated_output,
        estimated_cost=round(cost, 6),
        model=model,
        approval_required=True,
        warnings=tuple(warnings),
    )


def propose_remediation(
    action: str, target: str, rationale: str, *, claim_id: str = ""
) -> RemediationProposal:
    """Create a human-reviewable remediation proposal without executing it.

    With ``claim_id``, the proposal is registered as a downstream
    dependent of that provenance claim, so a later correction of the
    claim propagates to the proposal for re-review.
    """
    for value, name in ((action, "action"), (target, "target"), (rationale, "rationale")):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string.")
    if claim_id:
        register_dependent(
            claim_id,
            artifact="vessell.agentic_soc.RemediationProposal",
            location=f"{action.strip()} on {target.strip()}",
        )
    return RemediationProposal(
        action=action.strip(),
        target=target.strip(),
        rationale=rationale.strip(),
        authorization_required=True,
        rollback_required=True,
        claim_id=claim_id,
    )