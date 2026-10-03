"""Shared intake assessment: unknown exposure never becomes clearance."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

RISK_FIELDS = (
    "accuracy_risk",
    "academic_risk",
    "professional_risk",
    "legal_risk",
    "financial_security_risk",
)
REQUIRED_FIELDS = (*RISK_FIELDS, "hard_to_reverse", "benefit_proportionate")


@dataclass(frozen=True)
class HarmGateResult:
    exposure: str
    risk_count: int
    benefit_proportionate: bool | None
    cleared: bool
    safeguards: list[str]
    missing_fields: list[str] = field(default_factory=list)


def evaluate_harm_gate(harm_gate: Any) -> HarmGateResult:
    if harm_gate is None:
        harm_gate = {}
    if not isinstance(harm_gate, dict):
        raise TypeError("Harm Gate must be an object.")
    for name in REQUIRED_FIELDS:
        if name in harm_gate and not isinstance(harm_gate[name], bool):
            raise ValueError(f"Harm Gate {name} must be a boolean.")

    missing = [name for name in REQUIRED_FIELDS if name not in harm_gate]
    risk_count = sum(harm_gate.get(name) is True for name in RISK_FIELDS)
    proportionate = harm_gate.get("benefit_proportionate")
    if missing:
        return HarmGateResult(
            exposure="UNKNOWN",
            risk_count=risk_count,
            benefit_proportionate=proportionate,
            cleared=False,
            safeguards=["Complete missing Harm Gate fields before clearance: " + ", ".join(missing)],
            missing_fields=missing,
        )

    hard_to_reverse = harm_gate["hard_to_reverse"]
    if hard_to_reverse and risk_count >= 2:
        exposure = "SEVERE / IRREVERSIBLE"
    elif hard_to_reverse or risk_count >= 3:
        exposure = "HIGH"
    elif risk_count:
        exposure = "MODERATE"
    else:
        exposure = "LOW"
    safeguards = {
        "LOW": ["Ordinary evidence threshold and normal review."],
        "MODERATE": ["Document the Harm Gate and at least one mitigation or alternative."],
        "HIGH": [
            "Strengthen provenance and alternatives testing.",
            "Calibrate claims to the evidence.",
            "Perform pre-action verification.",
        ],
        "SEVERE / IRREVERSIBLE": [
            "Obtain independent human review where feasible.",
            "Record what would have to be wrong for the action to fail.",
            "Prepare an explicit fallback or undo plan.",
        ],
    }[exposure]
    return HarmGateResult(exposure, risk_count, proportionate, proportionate is True, safeguards)
