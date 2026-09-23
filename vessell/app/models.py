"""Typed models for the executable case-run pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineCounts:
    """Evidence and provenance counts used for confidence and reporting."""

    total_evidence: int
    source_established: int
    framework_synthesis: int
    working_hypothesis: int
    illustrative: int
    unresolved_lineage: int
    independent_roots: int


@dataclass(frozen=True)
class PipelineResult:
    """Structured output from one end-to-end case execution."""

    title: str
    subject: str
    decision_question: str
    posture: str
    confidence_ceiling: str
    counts: PipelineCounts
    notes: list[str]
    convergence_note: str
