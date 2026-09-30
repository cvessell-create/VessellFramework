# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Llama-weighted evidence scoring for VessellFramework.

Doctrine
--------
A weight is a claim about evidentiary standing, so every weight carries its
own provenance. This module provides two paths, both auditable:

1. **Static calibrated tables** (default). Base weights per
   :class:`~vessell.provenance.SourceStatus`, provenance multipliers per
   :class:`~vessell.provenance.ProvenanceState`, and an independence
   discount for shared evidentiary roots. The table values were calibrated
   by LLM analysis (``WEIGHT_TABLE_VERSION``) and are built into the
   framework as versioned constants — no silent numbers.

2. **Live Llama scoring** (:class:`LlamaWeighter`). A Llama model reachable
   through an OpenAI-compatible endpoint (Ollama default) scores individual
   evidence items 0..1 with a rationale. The live score can only *discount*
   within the tier ceiling set by the static tables — the model refines,
   the tables govern. If the model is unreachable, the engine falls back
   to the static path and records the fallback in the weight's provenance.

Calibration rationale (static tables)
-------------------------------------
- ``SOURCE_ESTABLISHED = 1.00``: anchors decisions; full evidentiary
  standing. The ceiling against which everything else is discounted.
- ``FRAMEWORK_SYNTHESIS = 0.60``: analyst-derived synthesis of established
  material. Informative, but one inferential step removed from the source.
- ``WORKING_HYPOTHESIS = 0.35``: provisional. Shapes inquiry; never settles
  a judgment on its own.
- ``ILLUSTRATIVE = 0.10``: exposition only. Mirrors
  ``MaskirovkaAssessment.eligibility``, which rejects illustrative-only
  evidence — illustration may color an assessment but must not drive it.

Provenance multipliers encode the provenance firewall: unresolved lineage
carries *zero* weight because absence of a resolved parent is not
independence. Cycles are inadmissible. Conflicting parent claims are
heavily discounted and flagged for human review rather than silently
dropped, so the conflict stays visible in the audit trail.

Independence discount: items resolving to the same evidentiary root share
ancestry. Each item's weight is divided by the size of its root group, so a
root's total contribution is conserved no matter how many derivative items
cite it. The framework counts independent provenance roots, not items.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from vessell.provenance import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    ProvenanceResolution,
    ProvenanceState,
    SourceStatus,
)

__all__ = [
    "CONFLICT_MULTIPLIER",
    "PROVENANCE_STATE_MULTIPLIERS",
    "SOURCE_TIER_WEIGHTS",
    "WEIGHT_TABLE_VERSION",
    "AggregationResult",
    "LlamaScore",
    "LlamaUnavailable",
    "LlamaWeighter",
    "WeightRecord",
    "WeightedEvidenceSet",
    "WeightingEngine",
]


# ---------------------------------------------------------------------------
# Built-in calibrated weight tables (LLM-calibrated, versioned)
# ---------------------------------------------------------------------------

WEIGHT_TABLE_VERSION = "llama-calibrated-v1"

SOURCE_TIER_WEIGHTS: dict[SourceStatus, float] = {
    SourceStatus.SOURCE_ESTABLISHED: 1.00,
    SourceStatus.FRAMEWORK_SYNTHESIS: 0.60,
    SourceStatus.WORKING_HYPOTHESIS: 0.35,
    SourceStatus.ILLUSTRATIVE: 0.10,
}

PROVENANCE_STATE_MULTIPLIERS: dict[ProvenanceState, float] = {
    ProvenanceState.RESOLVED: 1.0,
    ProvenanceState.UNRESOLVED_PARENT: 0.0,
    ProvenanceState.MISSING_RECORD: 0.0,
    ProvenanceState.CYCLE: 0.0,
    ProvenanceState.CONFLICT: 0.25,
}

CONFLICT_MULTIPLIER = PROVENANCE_STATE_MULTIPLIERS[ProvenanceState.CONFLICT]

# Live Llama scores blend as: final = static * (LLAMA_FLOOR + (1 - LLAMA_FLOOR) * s)
# so a live model can discount up to 50% but can never inflate past the tier ceiling.
LLAMA_FLOOR = 0.5

STATIC_MODEL_ID = f"llama-static-{WEIGHT_TABLE_VERSION}"


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WeightRecord:
    """One evidence item's weight, with full provenance of the weight itself."""

    source_id: str
    description: str
    status: str
    provenance_state: str
    root_id: str | None
    weight: float  # final raw weight
    normalized_weight: float = 0.0  # share of set total; set by weight_set()
    static_weight: float = 0.0  # static-table prior before any live scoring
    llama_score: float | None = None  # live Llama 0..1 score, if used
    independence_factor: float = 1.0
    weight_model: str = STATIC_MODEL_ID  # what produced this number
    table_version: str = WEIGHT_TABLE_VERSION
    rationale: str = ""
    flags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "description": self.description,
            "status": self.status,
            "provenance_state": self.provenance_state,
            "root_id": self.root_id,
            "weight": self.weight,
            "normalized_weight": self.normalized_weight,
            "static_weight": self.static_weight,
            "llama_score": self.llama_score,
            "independence_factor": self.independence_factor,
            "weight_model": self.weight_model,
            "table_version": self.table_version,
            "rationale": self.rationale,
            "flags": list(self.flags),
        }


@dataclass
class WeightedEvidenceSet:
    """Weight records for an evidence set plus set-level aggregates."""

    records: list[WeightRecord] = field(default_factory=list)
    total_weight: float = 0.0
    independent_root_count: int | None = None
    notes: list[str] = field(default_factory=list)

    def by_source(self, source_id: str) -> WeightRecord:
        for record in self.records:
            if record.source_id == source_id:
                return record
        raise KeyError(f"No weight record for source_id={source_id!r}")


@dataclass(frozen=True)
class AggregationResult:
    """Weighted aggregation of analyst-supplied per-item values."""

    value: float | None
    total_weight: float
    contributors: int
    weight_model: str
    table_version: str
    note: str = ""


# ---------------------------------------------------------------------------
# Live Llama scoring
# ---------------------------------------------------------------------------


class LlamaUnavailable(RuntimeError):
    """Raised when no live Llama endpoint can be reached."""


@dataclass(frozen=True)
class LlamaScore:
    weight: float  # 0..1
    rationale: str
    model: str


class LlamaWeighter:
    """Scores evidence items with a live Llama model via an OpenAI-compatible API.

    Defaults target Ollama (``http://localhost:11434/v1``). Any
    OpenAI-compatible endpoint works — point ``base_url`` at it and set
    ``model`` accordingly. Uses only the standard library, so live scoring
    adds no new dependencies.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "llama3.1",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    # -- public API ------------------------------------------------------

    def score(
        self,
        item: EvidenceItem,
        resolution: ProvenanceResolution,
    ) -> LlamaScore:
        """Ask Llama to score one evidence item 0..1 with a rationale."""
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _SCORING_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _scoring_user_prompt(item, resolution),
                },
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={"Content-Type": "application/json", **self._auth_headers()},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # unreachable endpoint, timeout, bad status...
            raise LlamaUnavailable(
                f"Llama endpoint {self.base_url} unreachable: {exc}"
            ) from exc

        try:
            content = body["choices"][0]["message"]["content"]
            parsed = _extract_json(content)
            weight = float(parsed["weight"])
            rationale = str(parsed.get("rationale", "")).strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise LlamaUnavailable(
                f"Llama endpoint {self.base_url} returned an unparseable score."
            ) from exc

        return LlamaScore(
            weight=min(1.0, max(0.0, weight)),
            rationale=rationale or "No rationale supplied by model.",
            model=self.model,
        )

    def ping(self) -> bool:
        """True when the endpoint answers a models listing."""
        request = urllib.request.Request(
            f"{self.base_url}/models",
            headers=self._auth_headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout):
                return True
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    # -- internals ---------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}


_SCORING_SYSTEM_PROMPT = """\
You score the evidentiary standing of a single intelligence evidence item for \
the VessellFramework, an analytic-tradecraft evaluation framework. Reply with \
JSON only: {"weight": <0.0-1.0>, "rationale": "<one or two sentences>"}.

Calibration guide:
- 1.0: first-hand, verified, directly probative reporting.
- 0.6-0.8: credible but second-hand, partially corroborated, or one \
inferential step from the source.
- 0.3-0.5: provisional, single-threaded, or context-dependent; shapes \
inquiry but settles nothing alone.
- 0.0-0.2: illustrative, anecdotal, or exposition-only; must not drive a \
judgment.

Discount for unresolved provenance, circular sourcing, or conflicting \
lineage. Never inflate past what the item's description justifies."""


def _scoring_user_prompt(item: EvidenceItem, resolution: ProvenanceResolution) -> str:
    return (
        f"Evidence description: {item.description}\n"
        f"Source tier: {item.status.value}\n"
        f"Provenance state: {resolution.state.value}\n"
        f"Resolved root: {resolution.root_id}\n"
        f"Provenance note: {resolution.note or 'none'}\n"
        "Score this item's evidentiary standing 0.0-1.0 with a brief rationale. "
        "JSON only."
    )


def _extract_json(content: str) -> dict[str, Any]:
    """Pull the first JSON object out of model output, tolerating prose."""
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if not match:
        raise ValueError("No JSON object in model output.")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise TypeError("Model output JSON is not an object.")
    return parsed


# ---------------------------------------------------------------------------
# Weighting engine
# ---------------------------------------------------------------------------


class WeightingEngine:
    """Assigns auditable weights to evidence items.

    ``weighter`` is optional: when supplied and reachable, its live Llama
    scores refine (only downward, never past the tier ceiling) the static
    calibrated weights. When absent or unreachable, the static tables
    govern and the fallback is recorded on the weight record.
    """

    def __init__(
        self,
        registry: ProvenanceRegistry,
        weighter: LlamaWeighter | None = None,
        table_version: str = WEIGHT_TABLE_VERSION,
    ) -> None:
        self.registry = registry
        self.weighter = weighter
        self.table_version = table_version
        # One-shot cache: weight_set() fills this via score_batch() when the
        # weighter supports it, so a set costs one model call, not N.
        self._batch_cache: dict[str, Any] | None = None

    # -- item-level ---------------------------------------------------------

    def weight_item(self, item: EvidenceItem, use_llama: bool = True) -> WeightRecord:
        resolution = self.registry.resolve(item.source_id)
        tier_weight = SOURCE_TIER_WEIGHTS[item.status]
        prov_multiplier = PROVENANCE_STATE_MULTIPLIERS[resolution.state]
        static_weight = tier_weight * prov_multiplier

        flags: list[str] = []
        if resolution.state != ProvenanceState.RESOLVED:
            flags.append(f"provenance-{resolution.state.value.lower()}")

        llama_score: float | None = None
        weight_model = f"llama-static-{self.table_version}"
        rationale = (
            f"tier={item.status.value}({tier_weight:.2f}) x "
            f"provenance={resolution.state.value}({prov_multiplier:.2f})"
        )

        if use_llama and self.weighter is not None and static_weight > 0:
            cached = (self._batch_cache or {}).get(item.source_id)
            try:
                score_from_detailed = getattr(
                    self.weighter, "score_from_detailed", None
                )
                if cached is not None and score_from_detailed is not None:
                    scored = score_from_detailed(cached)
                    flags.append("llama-batch-scored")
                else:
                    scored = self.weighter.score(item, resolution)
                llama_score = scored.weight
                blend = LLAMA_FLOOR + (1.0 - LLAMA_FLOOR) * scored.weight
                final_weight = static_weight * blend
                weight_model = f"llama-live:{scored.model}"
                rationale += (
                    f" x llama={scored.weight:.2f}(floor {LLAMA_FLOOR:.2f}); "
                    f"{scored.rationale}"
                )
            except LlamaUnavailable:
                flags.append("llama-unreachable-fallback")
                final_weight = static_weight
                rationale += "; live Llama unreachable, static tables govern"
        else:
            final_weight = static_weight
            if use_llama and self.weighter is None:
                rationale += "; no live weighter configured, static tables govern"

        return WeightRecord(
            source_id=item.source_id,
            description=item.description,
            status=item.status.value,
            provenance_state=resolution.state.value,
            root_id=resolution.root_id,
            weight=final_weight,
            static_weight=tier_weight * prov_multiplier,
            llama_score=llama_score,
            weight_model=weight_model,
            table_version=self.table_version,
            rationale=rationale,
            flags=tuple(flags),
        )

    # -- set-level ----------------------------------------------------------

    def _prefetch_batch(
        self, evidence_set: EvidenceSet
    ) -> dict[str, Any] | None:
        """One model call for the whole set when the weighter supports it.

        Returns None (per-item scoring) when there is no weighter, no batch
        support, or the batch call fails — the LlamaUnavailable fallback in
        weight_item() still applies per item.
        """
        weighter = self.weighter
        score_batch = getattr(weighter, "score_batch", None)
        if weighter is None or score_batch is None:
            return None
        try:
            pairs = [
                (item, self.registry.resolve(item.source_id))
                for item in evidence_set.items
            ]
            batch: dict[str, Any] | None = score_batch(pairs)
            return batch
        except LlamaUnavailable:
            return None

    def weight_set(self, evidence_set: EvidenceSet) -> WeightedEvidenceSet:
        """Weight every item, apply the independence discount, normalize."""
        self._batch_cache = self._prefetch_batch(evidence_set)
        try:
            records = [self.weight_item(item) for item in evidence_set.items]
        finally:
            self._batch_cache = None

        # Independence discount: conserve each resolved root's contribution.
        root_groups: dict[str, list[int]] = {}
        for index, record in enumerate(records):
            if record.root_id is not None and record.weight > 0:
                root_groups.setdefault(record.root_id, []).append(index)

        discounted: list[WeightRecord] = []
        for index, record in enumerate(records):
            factor = 1.0
            for root_id, members in root_groups.items():
                if index in members:
                    factor = 1.0 / len(members)
                    break
            if factor != 1.0:
                discounted.append(
                    WeightRecord(
                        **{**record.to_dict(), "flags": tuple(record.flags),
                           "weight": record.weight * factor,
                           "independence_factor": factor,
                           "rationale": record.rationale
                           + f"; independence discount 1/{len(members)} "
                           + f"(shared root {root_id})",
                           "normalized_weight": 0.0}
                    )
                )
            else:
                discounted.append(record)

        total = sum(r.weight for r in discounted)
        notes: list[str] = []
        if total <= 0:
            notes.append(
                "Total set weight is zero: no item carries resolved, "
                "non-conflicted provenance. Nothing here can drive a judgment."
            )
            normalized = discounted
        else:
            normalized = [
                WeightRecord(
                    **{**r.to_dict(), "flags": tuple(r.flags),
                       "normalized_weight": r.weight / total}
                )
                for r in discounted
            ]

        return WeightedEvidenceSet(
            records=normalized,
            total_weight=total,
            independent_root_count=evidence_set.explicit_dependency_stream_count(),
            notes=notes,
        )

    # -- aggregation --------------------------------------------------------

    def aggregate(
        self,
        weighted: WeightedEvidenceSet,
        values: dict[str, float],
        value_label: str = "analyst assessment",
    ) -> AggregationResult:
        """Weighted mean of analyst-supplied per-item values (e.g. 0..1)."""
        contributors = [
            r for r in weighted.records
            if r.source_id in values and r.normalized_weight > 0
        ]
        if not contributors:
            return AggregationResult(
                value=None,
                total_weight=weighted.total_weight,
                contributors=0,
                weight_model=f"llama-static-{self.table_version}",
                table_version=self.table_version,
                note=f"No {value_label} values supplied for weighted items.",
            )
        total = sum(r.normalized_weight for r in contributors)
        weighted_sum = sum(
            values[r.source_id] * r.normalized_weight for r in contributors
        )
        result: float | None = weighted_sum / total if total > 0 else None
        return AggregationResult(
            value=result,
            total_weight=weighted.total_weight,
            contributors=len(contributors),
            weight_model=contributors[0].weight_model,
            table_version=self.table_version,
            note=f"Weighted mean of {len(contributors)} {value_label}(s).",
        )
