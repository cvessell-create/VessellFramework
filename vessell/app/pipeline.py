# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Core executable pipeline for doctrine-to-code case runs."""

from __future__ import annotations

from typing import Any

from vessell.harm_gate import evaluate_harm_gate
from vessell.provenance import (
    ClaimKind,
    ClaimRecord,
    EvidenceItem,
    EvidenceSet,
    MaskirovkaAssessment,
    MaskirovkaVariant,
    ProvenanceRegistry,
    SourceStatus,
    assess_maskirovka_convergence,
    intake_claim,
    register_dependent,
)

from .models import PipelineCounts, PipelineResult


def _parse_status(raw: str) -> SourceStatus:
    mapping = {
        "SOURCE-ESTABLISHED": SourceStatus.SOURCE_ESTABLISHED,
        "FRAMEWORK SYNTHESIS": SourceStatus.FRAMEWORK_SYNTHESIS,
        "WORKING HYPOTHESIS": SourceStatus.WORKING_HYPOTHESIS,
        "ILLUSTRATIVE": SourceStatus.ILLUSTRATIVE,
    }
    key = raw.strip().upper().replace("_", " ")
    if key not in mapping:
        raise ValueError(f"Unsupported evidence status: {raw}")
    return mapping[key]


def _parse_variant(raw: str) -> MaskirovkaVariant:
    for variant in MaskirovkaVariant:
        if variant.value.lower() == raw.strip().lower():
            return variant
    raise ValueError(f"Unsupported maskirovka variant: {raw}")


def _build_evidence_set(case: dict[str, Any], registry: ProvenanceRegistry) -> EvidenceSet:
    items: list[EvidenceItem] = []
    for row in case.get("evidence", []):
        items.append(
            EvidenceItem(
                description=row["description"],
                status=_parse_status(row["status"]),
                source_id=row["source_id"],
                upstream_of=row.get("upstream_of"),
            )
        )
    return EvidenceSet(registry=registry, items=items)


def _status_counts(evidence_set: EvidenceSet) -> dict[SourceStatus, int]:
    counts = {
        SourceStatus.SOURCE_ESTABLISHED: 0,
        SourceStatus.FRAMEWORK_SYNTHESIS: 0,
        SourceStatus.WORKING_HYPOTHESIS: 0,
        SourceStatus.ILLUSTRATIVE: 0,
    }
    for item in evidence_set.items:
        counts[item.status] += 1
    return counts


def _map_by_source_id(evidence_set: EvidenceSet) -> dict[str, EvidenceItem]:
    return {item.source_id: item for item in evidence_set.items}


def _build_maskirovka_assessments(
    case: dict[str, Any],
    registry: ProvenanceRegistry,
    evidence_map: dict[str, EvidenceItem],
) -> list[MaskirovkaAssessment]:
    assessments: list[MaskirovkaAssessment] = []
    for row in case.get("maskirovka", []):
        evidence_rows: list[EvidenceItem] = []
        for source_id in row.get("evidence_ids", []):
            item = evidence_map.get(source_id)
            if item is not None:
                evidence_rows.append(item)
        evidence_set = EvidenceSet(registry=registry, items=evidence_rows)
        assessments.append(
            MaskirovkaAssessment(
                variant=_parse_variant(row["variant"]),
                trigger_conditions_met=bool(row.get("trigger_conditions_met", False)),
                trigger_evidence=evidence_set,
                notes=str(row.get("notes", "")),
            )
        )
    return assessments


def _derive_confidence_ceiling(counts: PipelineCounts) -> str:
    # Confidence ceiling stays conservative when lineage cannot be resolved.
    if counts.unresolved_lineage > 0:
        return "LOW"
    if counts.source_established >= 2 and counts.independent_roots >= 2:
        return "MODERATE"
    if counts.source_established >= 1:
        return "LOW"
    return "VERY LOW"


def intake_case_evidence(case: dict[str, Any]) -> list[ClaimRecord]:
    """Intake every evidence row of a case document as a provenance claim.

    Evidence rows may carry an optional ``provenance`` mapping with
    ``source`` (description), ``is_official_record`` (bool), and
    ``observed_at`` keys; rows without one are intaked with a generic
    case-evidence source tag. The row's status string maps to the claim's
    source tier, so the claim lifecycle mirrors the evidence standing.
    """
    records: list[ClaimRecord] = []
    subject = str(case.get("title", "case"))
    for index, row in enumerate(case.get("evidence", [])):
        provenance = row.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        record = intake_claim(
            text=str(row["description"]),
            subject=subject,
            source=str(provenance.get("source") or f"case evidence row {index}"),
            source_tier=_parse_status(str(row.get("status", ""))),
            recorded_at=str(provenance.get("observed_at") or ""),
            is_official_record=bool(provenance.get("is_official_record", False)),
            kind=ClaimKind.REPORT,
            note=f"source_id: {row.get('source_id', 'unknown')}",
        )
        records.append(record)
    return records


def run_case_pipeline(case: dict[str, Any], *, track_provenance: bool = True) -> PipelineResult:
    """Run one end-to-end case execution.

    With ``track_provenance`` (default), every evidence row is intaked as
    a provenance claim and the resulting PipelineResult registers itself
    as a downstream dependent of those claims — doctrine's rule that
    every operational use of a claim registers itself.
    """
    registry = ProvenanceRegistry()
    harm_gate = evaluate_harm_gate(case.get("harm_gate"))
    evidence_set = _build_evidence_set(case, registry)
    status_counts = _status_counts(evidence_set)

    roots = evidence_set.explicit_dependency_stream_count()
    independent_roots = roots if roots is not None else 0

    counts = PipelineCounts(
        total_evidence=len(evidence_set.items),
        source_established=status_counts[SourceStatus.SOURCE_ESTABLISHED],
        framework_synthesis=status_counts[SourceStatus.FRAMEWORK_SYNTHESIS],
        working_hypothesis=status_counts[SourceStatus.WORKING_HYPOTHESIS],
        illustrative=status_counts[SourceStatus.ILLUSTRATIVE],
        unresolved_lineage=evidence_set.unresolved_count(),
        independent_roots=independent_roots,
    )

    evidence_map = _map_by_source_id(evidence_set)
    assessments = _build_maskirovka_assessments(case, registry, evidence_map)
    convergence_note = assess_maskirovka_convergence(assessments)

    notes: list[str] = []
    if not harm_gate.cleared:
        notes.append("Harm Gate requires review; this intake does not authorize action.")
    if counts.unresolved_lineage > 0:
        notes.append("Unresolved provenance blocks high-confidence convergence.")
    if counts.framework_synthesis > 0 or counts.working_hypothesis > 0:
        notes.append("Maintain explicit distinction between source-established and inferred material.")
    if counts.illustrative > 0:
        notes.append("Illustrative evidence cannot independently justify operational claims.")

    posture = str(case.get("analysis", {}).get("posture", "Posture not provided in input."))

    claim_ids: tuple[str, ...] = ()
    if track_provenance:
        title = str(case.get("title", "Untitled Case"))
        claim_ids = tuple(
            record.id for record in intake_case_evidence(case)
        )
        for claim_id in claim_ids:
            register_dependent(
                claim_id,
                artifact="vessell.app.pipeline.PipelineResult",
                location=title,
            )

    return PipelineResult(
        title=str(case.get("title", "Untitled Case")),
        subject=str(case.get("subject", "Unknown subject")),
        decision_question=str(case.get("decision_question", "No decision question provided.")),
        posture=posture,
        confidence_ceiling=_derive_confidence_ceiling(counts),
        counts=counts,
        notes=notes,
        convergence_note=convergence_note,
        claim_ids=claim_ids,
        harm_gate=harm_gate,
    )
