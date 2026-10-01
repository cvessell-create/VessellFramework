#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Run a structured VesselFramework case intake and produce a traceable report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from vessell import provenance_firewall

SOURCE_STATUSES = {
    "SOURCE-ESTABLISHED",
    "FRAMEWORK SYNTHESIS",
    "WORKING HYPOTHESIS",
    "ILLUSTRATIVE",
}
MASKIROVKA_VARIANTS = {
    "Budgetary",
    "Structural",
    "Operational",
    "Brute-Force Stealth",
}
REQUIRED_CASE_FIELDS = {"title", "decision_question", "domain", "subject", "evidence"}
FORWARD_REGISTERS = {"POSITIVE", "NEGATIVE", "MIXED"}
ALIGNMENTS = {"NATIVE", "ADJACENT", "MISALIGNED"}
POSTURES = ["OBSERVE", "VERIFY", "CONTAIN", "RECOVER", "RESTRICT", "ESCALATE"]
PRIMARY_MASKIROVKA_CHECK = "Brute-Force Stealth"
PRIMARY_MASKIROVKA_AUTHOR = "Christopher R. Vessell"


def load_reference_module() -> ModuleType:
    """Return the packaged v1.1 provenance firewall (``vessell.provenance_firewall``)."""
    return provenance_firewall


def optional_bool(mapping: dict[str, Any], key: str, default: bool) -> bool:
    """Read a JSON boolean, rejecting truthy strings such as ``"false"``."""
    value = mapping.get(key, default)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be true or false, not {type(value).__name__}.")
    return value


def load_case(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        case = json.load(file)
    if not isinstance(case, dict):
        raise TypeError("Case file must contain a JSON object.")

    missing_fields = REQUIRED_CASE_FIELDS - set(case)
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Case is missing required fields: {missing}")
    for field_name in sorted(REQUIRED_CASE_FIELDS - {"evidence"}):
        if not isinstance(case[field_name], str) or not case[field_name].strip():
            raise ValueError(f"Case field {field_name} must be a non-empty string.")
    if not isinstance(case["evidence"], list):
        raise TypeError("Case evidence must be a list.")
    if not case["evidence"]:
        raise ValueError("Case must contain a non-empty evidence list.")
    if not isinstance(case.get("maskirovka", []), list):
        raise TypeError("The optional maskirovka field must be a list.")
    if not isinstance(case.get("analysis", {}), dict):
        raise TypeError("The optional analysis field must be an object.")
    harm_gate = case.get("harm_gate")
    if harm_gate is not None and not isinstance(harm_gate, dict):
        raise TypeError("The optional harm_gate field must be an object.")
    return case


def validate_evidence(case: dict[str, Any]) -> None:
    source_ids: set[str] = set()
    for index, evidence in enumerate(case["evidence"], start=1):
        if not isinstance(evidence, dict):
            raise TypeError(f"Evidence item {index} must be an object.")
        for field_name in ("description", "status", "source_id"):
            if not isinstance(evidence.get(field_name), str) or not evidence[field_name].strip():
                raise ValueError(f"Evidence item {index} has an invalid {field_name}.")
        if evidence["status"] not in SOURCE_STATUSES:
            raise ValueError(f"Evidence item {index} has an unknown status.")
        upstream_of = evidence.get("upstream_of")
        if upstream_of is not None and (not isinstance(upstream_of, str) or not upstream_of.strip()):
            raise ValueError(f"Evidence item {index} has an invalid upstream_of.")
        if evidence["source_id"] in source_ids:
            raise ValueError(f"Duplicate source_id: {evidence['source_id']}")
        source_ids.add(evidence["source_id"])


def build_evidence_set(reference: Any, registry: Any, evidence_items: list[dict[str, Any]]) -> Any:
    typed_items = [
        reference.EvidenceItem(
            description=item["description"],
            status=reference.SourceStatus(item["status"]),
            source_id=item["source_id"],
            upstream_of=item.get("upstream_of"),
        )
        for item in evidence_items
    ]
    return reference.EvidenceSet(registry, typed_items)


def evaluate_harm_gate(harm_gate: Any) -> dict[str, Any]:
    if not isinstance(harm_gate, dict):
        harm_gate = {}

    risk_names = [
        "accuracy_risk",
        "academic_risk",
        "professional_risk",
        "legal_risk",
        "financial_security_risk",
    ]
    risk_count = sum(optional_bool(harm_gate, name, False) for name in risk_names)
    hard_to_reverse = optional_bool(harm_gate, "hard_to_reverse", False)
    benefit_proportionate = optional_bool(harm_gate, "benefit_proportionate", True)

    if hard_to_reverse and risk_count >= 2:
        exposure = "SEVERE / IRREVERSIBLE"
    elif hard_to_reverse or risk_count >= 3:
        exposure = "HIGH"
    elif risk_count >= 1:
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

    return {
        "exposure": exposure,
        "risk_count": risk_count,
        "benefit_proportionate": benefit_proportionate,
        "cleared": benefit_proportionate,
        "safeguards": safeguards,
    }


def evaluate_forward_posture(harm_gate: Any) -> dict[str, Any]:
    """Apply the digital forward-posture safeguards when supplied."""
    if not isinstance(harm_gate, dict):
        return {"supplied": False, "posture": "NOT SUPPLIED", "review_required": False}

    forward_fields = {
        "register",
        "alignment",
        "current_posture",
        "evidence_threshold_met",
        "action_authorized",
        "rollback_available",
        "stop_condition",
        "human_review_required",
    }
    if not forward_fields.intersection(harm_gate):
        return {"supplied": False, "posture": "NOT SUPPLIED", "review_required": False}

    register = str(harm_gate.get("register", "MIXED")).upper()
    alignment = str(harm_gate.get("alignment", "ADJACENT")).upper()
    requested = str(harm_gate.get("current_posture", "VERIFY")).upper()
    if register not in FORWARD_REGISTERS:
        raise ValueError(f"Unknown forward register: {register}")
    if alignment not in ALIGNMENTS:
        raise ValueError(f"Unknown forward alignment: {alignment}")
    if requested not in POSTURES:
        raise ValueError(f"Unknown forward posture: {requested}")

    posture_index = POSTURES.index(requested)
    reasons: list[str] = []
    if register == "NEGATIVE" and posture_index > POSTURES.index("VERIFY"):
        posture_index = POSTURES.index("VERIFY")
        reasons.append("Negative register limits action to verification until risk is resolved.")
    if alignment == "MISALIGNED" and posture_index > POSTURES.index("VERIFY"):
        posture_index = POSTURES.index("VERIFY")
        reasons.append("Misaligned action is restricted to verification until the target is validated.")

    evidence_met = optional_bool(harm_gate, "evidence_threshold_met", False)
    authorized = optional_bool(harm_gate, "action_authorized", False)
    rollback = optional_bool(harm_gate, "rollback_available", False)
    stop_value = harm_gate.get("stop_condition", "")
    if stop_value is None:
        stop_value = ""
    if not isinstance(stop_value, str):
        raise TypeError("stop_condition must be a string.")
    stop_condition = bool(stop_value.strip())
    human_review = optional_bool(harm_gate, "human_review_required", False)
    final_posture = POSTURES[posture_index]

    review_required = not evidence_met
    if not evidence_met:
        reasons.append("Evidence threshold is not recorded as met.")
    if posture_index >= POSTURES.index("CONTAIN") and not authorized:
        review_required = True
        reasons.append("Containment or stronger action lacks recorded authorization.")
    if posture_index >= POSTURES.index("CONTAIN") and not rollback:
        review_required = True
        reasons.append("Containment or stronger action lacks a rollback path.")
    if posture_index >= POSTURES.index("CONTAIN") and not stop_condition:
        review_required = True
        reasons.append("Containment or stronger action lacks a stop condition.")
    if final_posture == "ESCALATE" and not human_review:
        review_required = True
        reasons.append("Escalation requires recorded human review.")

    return {
        "supplied": True,
        "register": register,
        "alignment": alignment,
        "requested_posture": requested,
        "posture": final_posture,
        "review_required": review_required,
        "reasons": reasons or ["Forward-posture conditions are recorded."],
    }


def markdown_report(case: dict[str, Any], reference: Any) -> tuple[str, bool]:
    registry = reference.ProvenanceRegistry()
    evidence_set = build_evidence_set(reference, registry, case["evidence"])
    source_ids = [item.source_id for item in evidence_set.items]
    independence = registry.compare_independence(source_ids)
    resolutions = evidence_set.provenance_resolutions()
    unresolved = [resolution for resolution in resolutions if resolution.state.value != "RESOLVED"]

    maskirovka_results: list[tuple[str, str]] = []
    assessments = []
    for entry in case.get("maskirovka", []):
        if not isinstance(entry, dict):
            raise TypeError("Each Maskirovka entry must be an object.")
        variant = entry.get("variant")
        if variant not in MASKIROVKA_VARIANTS:
            raise ValueError(f"Unknown Maskirovka variant: {variant}")
        evidence_ids = entry.get("evidence_ids", [])
        if not isinstance(evidence_ids, list) or not all(isinstance(item, str) for item in evidence_ids):
            raise TypeError(f"Maskirovka {variant} evidence_ids must be a list of source_id strings.")
        known_ids = {item["source_id"] for item in case["evidence"]}
        unknown_ids = sorted(set(evidence_ids) - known_ids)
        if unknown_ids:
            raise ValueError(f"Maskirovka {variant} references unknown evidence_ids: {', '.join(unknown_ids)}")
        notes = entry.get("notes", "")
        if not isinstance(notes, str):
            raise TypeError(f"Maskirovka {variant} notes must be a string.")
        selected = [item for item in case["evidence"] if item["source_id"] in evidence_ids]
        selected_set = build_evidence_set(reference, registry, selected)
        assessment = reference.MaskirovkaAssessment(
            variant=reference.MaskirovkaVariant(variant),
            trigger_conditions_met=optional_bool(entry, "trigger_conditions_met", False),
            trigger_evidence=selected_set,
            notes=notes,
        )
        eligible, reason = assessment.eligibility()
        maskirovka_results.append((variant, f"{'ELIGIBLE' if eligible else 'BLOCKED'}: {reason}"))
        assessments.append(assessment)

    convergence = reference.assess_maskirovka_convergence(assessments) if assessments else "No Maskirovka assessment supplied."
    harm = evaluate_harm_gate(case.get("harm_gate"))
    forward = evaluate_forward_posture(case.get("harm_gate"))
    analysis = case.get("analysis", {})
    if not isinstance(analysis, dict):
        raise TypeError("The optional analysis field must be an object.")

    lines = [
        f"# VesselFramework Case Report: {case['title']}",
        "",
        "**Runner status:** STRUCTURED INTAKE COMPLETE",
        "**Important boundary:** This report structures supplied evidence; it does not generate or independently verify analytical conclusions.",
        "",
        "## Case Intake",
        f"- **Subject:** {case['subject']}",
        f"- **Decision question:** {case['decision_question']}",
        f"- **Domain:** {case['domain']}",
        f"- **Time horizon:** {case.get('time_horizon', 'Not specified')}",
        "",
        "## Evidence and Provenance",
        f"- Evidence items: {len(evidence_set.items)}",
        f"- Provenance status: {independence['status']}",
        f"- Resolved roots: {', '.join(independence['roots']) if independence['roots'] else 'None'}",
        f"- Independent across all supplied items: {independence['independent']}",
    ]

    for item, resolution in zip(evidence_set.items, resolutions):
        lines.append(
            f"- `{item.source_id}` [{item.status.value}] -> {resolution.state.value}"
            + (f" root=`{resolution.root_id}`" if resolution.root_id else "")
        )

    lines.extend([
        "",
        "## Maskirovka Check Gate",
        f"- Primary check: **{PRIMARY_MASKIROVKA_CHECK}** (developed by {PRIMARY_MASKIROVKA_AUTHOR})",
        "- Reference checks: Budgetary / Structural / Operational",
    ])
    for variant, result in maskirovka_results:
        lines.append(f"- **{variant}:** {result}")
    lines.append(f"- **Convergence:** {convergence}")

    lines.extend([
        "",
        "## Harm Gate",
        f"- Exposure: **{harm['exposure']}**",
        f"- Risk flags: {harm['risk_count']}",
        f"- Benefit proportionate: {harm['benefit_proportionate']}",
        f"- Cleared by intake gate: {harm['cleared']}",
        "- Safeguards:",
    ])
    lines.extend(f"  - {safeguard}" for safeguard in harm["safeguards"])

    lines.extend([
        "",
        "### Forward Posture",
        f"- Supplied: {forward['supplied']}",
        f"- Posture: **{forward['posture']}**",
    ])
    if forward["supplied"]:
        lines.extend([
            f"- Register: {forward['register']}",
            f"- Alignment: {forward['alignment']}",
            f"- Requested posture: {forward['requested_posture']}",
            f"- Review required: {forward['review_required']}",
        ])
        lines.extend(f"  - {reason}" for reason in forward["reasons"])

    lines.extend(["", "## Analyst-Supplied Findings"])
    for field_name in ("paradox", "bottleneck", "dual_layer", "xfactor", "alternatives", "confidence", "posture"):
        if field_name in analysis:
            lines.append(f"- **{field_name.replace('_', ' ').title()}:** {analysis[field_name]}")
    if not analysis:
        lines.append("No analyst-supplied findings were included.")

    blocked = (
        bool(unresolved)
        or not harm["cleared"]
        or forward["review_required"]
        or "INDETERMINATE" in convergence
    )
    lines.extend([
        "",
        "## Runtime Posture",
        f"- Overall intake status: **{'REVIEW REQUIRED' if blocked else 'READY FOR ANALYST REVIEW'}**",
        "- A structured intake result is not a source-established conclusion.",
    ])
    return "\n".join(lines) + "\n", blocked


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a structured VesselFramework case intake.")
    parser.add_argument("case", type=Path, help="JSON case-intake file.")
    parser.add_argument("--output", type=Path, help="Write the Markdown report to this path.")
    args = parser.parse_args()

    try:
        case = load_case(args.case)
        validate_evidence(case)
        report, blocked = markdown_report(case, load_reference_module())
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"ERROR: {error}")
        return 2

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written: {args.output.resolve()}")
    else:
        print(report, end="")

    if blocked:
        print("RUNNER STATUS: REVIEW REQUIRED")
        return 1
    print("RUNNER STATUS: READY FOR ANALYST REVIEW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
