# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Importable VessellFramework core package.

Public surface: evidence intake and provenance tracking (:mod:`vessell.provenance`),
deterministic + LLM-calibrated evidence weighting (:mod:`vessell.weights`), and
the calibrated live-Llama weighter (:mod:`vessell.weigher`).
"""

from vessell.provenance import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    ProvenanceResolution,
    ProvenanceState,
    SourceStatus,
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
    "SOURCE_TIER_WEIGHTS",
    "WEIGHT_TABLE_VERSION",
    "AggregationResult",
    "CalibratedLlamaWeighter",
    "EvidenceItem",
    "EvidenceSet",
    "LlamaDetailedScore",
    "LlamaScore",
    "LlamaUnavailable",
    "LlamaWeighter",
    "ProvenanceRegistry",
    "ProvenanceResolution",
    "ProvenanceState",
    "SourceStatus",
    "WeightRecord",
    "WeightedEvidenceSet",
    "WeightingEngine",
    "__version__",
    "combine_factors",
]
