# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Importable VessellFramework core package.

Public surface: evidence intake and provenance tracking (:mod:`vessell.provenance`),
deterministic + LLM-calibrated evidence weighting (:mod:`vessell.weights`),
the calibrated live-Llama weighter (:mod:`vessell.weighter`), and claim
verification — planted-news checks, hostile-spread intel, and ghost-job
filtering (:mod:`vessell.verify`).
"""

from vessell.provenance import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    ProvenanceResolution,
    ProvenanceState,
    SourceStatus,
)
from vessell.verify import (
    BURST_MIN_SOURCES,
    BURST_WINDOW_MINUTES,
    CLONE_ARMY_MIN_SOURCES,
    NEAR_DUPLICATE_THRESHOLD,
    ClaimCheck,
    GhostJobReport,
    GhostVerdict,
    JobPosting,
    PlantedNewsReport,
    PlantedVerdict,
    SourceSighting,
    Verdict,
    VerificationResult,
    analyze_planted_news,
    detect_ghost_job,
    filter_ghost_jobs,
    group_postings_by_role,
    verify_claim,
)
from vessell.weighter import (
    CalibratedLlamaWeighter,
    LlamaDetailedScore,
    combine_factors,
)
from vessell.weights import (
    SOURCE_TIER_WEIGHTS,
    WEIGHT_TABLE_VERSION,
    AggregationResult,
    LlamaScore,
    LlamaUnavailable,
    LlamaWeighter,
    WeightedEvidenceSet,
    WeightingEngine,
    WeightRecord,
)

__version__ = "3.8.1"

__all__ = [
    "BURST_MIN_SOURCES",
    "BURST_WINDOW_MINUTES",
    "CLONE_ARMY_MIN_SOURCES",
    "NEAR_DUPLICATE_THRESHOLD",
    "SOURCE_TIER_WEIGHTS",
    "WEIGHT_TABLE_VERSION",
    "AggregationResult",
    "CalibratedLlamaWeighter",
    "ClaimCheck",
    "EvidenceItem",
    "EvidenceSet",
    "GhostJobReport",
    "GhostVerdict",
    "JobPosting",
    "LlamaDetailedScore",
    "LlamaScore",
    "LlamaUnavailable",
    "LlamaWeighter",
    "PlantedNewsReport",
    "PlantedVerdict",
    "ProvenanceRegistry",
    "ProvenanceResolution",
    "ProvenanceState",
    "SourceSighting",
    "SourceStatus",
    "Verdict",
    "VerificationResult",
    "WeightRecord",
    "WeightedEvidenceSet",
    "WeightingEngine",
    "__version__",
    "analyze_planted_news",
    "combine_factors",
    "detect_ghost_job",
    "filter_ghost_jobs",
    "group_postings_by_role",
    "verify_claim",
]
