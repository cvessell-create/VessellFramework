# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""A better Llama weighter for VessellFramework.

:class:`CalibratedLlamaWeighter` extends :class:`vessell.weights.LlamaWeighter`
with five upgrades, all in service of the same doctrine — every weight
carries its provenance, and the model refines while the tables govern:

1. **Factor scoring.** Instead of one opaque 0..1 number, the model scores
   four auditable sub-factors per item — reliability, corroboration,
   directness, timeliness — which are combined *deterministically* in code.
   The factor breakdown is written into the weight's rationale, so a later
   reviewer can see *why*, not just *how much*.

2. **Confidence scaling.** The model reports its confidence per item.
   Influence scales with confidence: a low-confidence assessment shrinks
   toward the static table prior instead of moving the weight on shaky
   grounds. ``s_effective = 1 - (1 - s) * confidence``.

3. **Batch scoring.** :meth:`score_batch` scores a whole evidence set in one
   model call, giving the model the full set as context (it can spot
   double-counted or shared sourcing across items). One round-trip instead
   of N.

4. **Retry with backoff.** Transient network failures retry (3 attempts,
   exponential backoff); only persistent failures fall back to the static
   tables. A single blip no longer silently downgrades to static.

5. **Prompt versioning + anchoring.** The scoring prompt is versioned
   (``PROMPT_VERSION``) and the version is stamped on every weight produced
   (``weight_model = "llama-live:<model>:prompt-v2"``). The prompt also
   tells the model the framework's static tier prior for the item, so live
   scores are anchored instead of drifting.

Drop-in compatible: it subclasses ``LlamaWeighter`` and overrides
:meth:`score`, so :class:`vessell.weights.WeightingEngine` uses it with no
changes — pass it as the ``weighter`` argument as before.
"""

from __future__ import annotations

import http.client
import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

from vessell.provenance import EvidenceItem, ProvenanceResolution
from vessell.weights import (
    SOURCE_TIER_WEIGHTS,
    LlamaScore,
    LlamaUnavailable,
    LlamaWeighter,
)

__all__ = [
    "PROMPT_VERSION",
    "FACTOR_WEIGHTS",
    "FACTOR_NAMES",
    "LlamaDetailedScore",
    "CalibratedLlamaWeighter",
    "combine_factors",
]

PROMPT_VERSION = "v2"

FACTOR_NAMES = ("reliability", "corroboration", "directness", "timeliness")

# Deterministic factor combination. Reliability of the source itself carries
# the most weight; corroboration and directness share the next tier;
# timeliness matters least for standing (stale truth is still truth).
FACTOR_WEIGHTS: dict[str, float] = {
    "reliability": 0.35,
    "corroboration": 0.25,
    "directness": 0.25,
    "timeliness": 0.15,
}

MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 1.0


def combine_factors(factors: dict[str, float]) -> float:
    """Deterministically combine sub-factor scores into one 0..1 score."""
    total = 0.0
    for name, weight in FACTOR_WEIGHTS.items():
        value = float(factors.get(name, 0.5))  # missing factor = neutral
        total += min(1.0, max(0.0, value)) * weight
    return min(1.0, max(0.0, total))


@dataclass(frozen=True)
class LlamaDetailedScore:
    """Full structured output of one calibrated Llama assessment."""

    source_id: str
    combined: float  # deterministic combination of factors, 0..1
    confidence: float  # model-reported confidence, 0..1
    effective: float  # confidence-scaled score actually applied, 0..1
    factors: dict[str, float] = field(default_factory=dict)
    rationale: str = ""
    model: str = ""
    prompt_version: str = PROMPT_VERSION


class CalibratedLlamaWeighter(LlamaWeighter):
    """Llama weighter with factor scoring, confidence, batching, and retry."""

    prompt_version: str = PROMPT_VERSION

    # -- primary API (drop-in override) ----------------------------------

    def score(self, item: EvidenceItem, resolution: ProvenanceResolution) -> LlamaScore:
        return self.score_from_detailed(self.score_detailed(item, resolution))

    def score_from_detailed(self, detailed: LlamaDetailedScore) -> LlamaScore:
        """Convert a detailed score to the LlamaScore the engine consumes."""
        return LlamaScore(
            weight=detailed.effective,
            rationale=self._format_rationale(detailed),
            # No "llama-live:" prefix here: WeightingEngine adds it.
            model=f"{self.model}:prompt-{detailed.prompt_version}",
        )

    def score_detailed(
        self, item: EvidenceItem, resolution: ProvenanceResolution
    ) -> LlamaDetailedScore:
        results = self.score_batch([(item, resolution)])
        return results[item.source_id]

    def score_batch(
        self,
        items: list[tuple[EvidenceItem, ProvenanceResolution]],
    ) -> dict[str, LlamaDetailedScore]:
        """Score a whole set in one model call; returns per-source_id scores."""
        if not items:
            return {}
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _BATCH_SYSTEM_PROMPT},
                {"role": "user", "content": _batch_user_prompt(items)},
            ],
        }
        body = self._post_with_retry(payload)
        return self._parse_batch(body, items)

    # -- HTTP with retry ----------------------------------------------------

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Single HTTP round-trip. Override in tests to stub the model."""
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={"Content-Type": "application/json", **self._auth_headers()},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post_with_retry(self, payload: dict[str, Any]) -> dict[str, Any]:
        last_exc: Optional[Exception] = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self._post(payload)
            except urllib.error.HTTPError as exc:
                last_exc = exc
                if exc.code is not None and 400 <= exc.code < 500 and exc.code != 429:
                    break  # client error: retrying won't help
            except (
                urllib.error.URLError,
                socket.timeout,
                TimeoutError,
                ConnectionError,
                http.client.HTTPException,
            ) as exc:
                last_exc = exc
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)))
        raise LlamaUnavailable(
            f"Llama endpoint {self.base_url} failed after {MAX_ATTEMPTS} "
            f"attempts: {last_exc}"
        ) from last_exc

    # -- parsing --------------------------------------------------------------

    def _parse_batch(
        self,
        body: dict[str, Any],
        items: list[tuple[EvidenceItem, ProvenanceResolution]],
    ) -> dict[str, LlamaDetailedScore]:
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlamaUnavailable(
                f"Llama endpoint {self.base_url} returned no usable content."
            ) from exc

        import re as _re

        match = _re.search(r"\{.*\}", content, _re.DOTALL)
        if not match:
            raise LlamaUnavailable(
                f"Llama endpoint {self.base_url} returned unparseable output."
            )
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LlamaUnavailable(
                f"Llama endpoint {self.base_url} returned invalid JSON."
            ) from exc

        entries = parsed.get("scores", [])
        if not isinstance(entries, list):
            raise LlamaUnavailable("Llama batch response 'scores' is not a list.")

        by_id = {item.source_id: (item, res) for item, res in items}
        results: dict[str, LlamaDetailedScore] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            source_id = str(entry.get("source_id", ""))
            if source_id not in by_id:
                continue
            results[source_id] = self._parse_entry(source_id, entry)

        missing = [sid for sid in by_id if sid not in results]
        if missing:
            raise LlamaUnavailable(
                f"Llama batch response missing scores for: {sorted(missing)}"
            )
        return results

    def _parse_entry(self, source_id: str, entry: dict[str, Any]) -> LlamaDetailedScore:
        factors: dict[str, float] = {}
        raw_factors = entry.get("factors")
        if isinstance(raw_factors, dict):
            for name in FACTOR_NAMES:
                if name in raw_factors:
                    try:
                        factors[name] = min(1.0, max(0.0, float(raw_factors[name])))
                    except (TypeError, ValueError):
                        factors[name] = 0.5

        if factors:
            combined = combine_factors(factors)
        else:
            # Tolerant legacy shape: a bare {"weight": ...} still works.
            try:
                combined = min(1.0, max(0.0, float(entry["weight"])))
            except (KeyError, TypeError, ValueError) as exc:
                raise LlamaUnavailable(
                    f"Llama score for {source_id!r} has neither factors nor weight."
                ) from exc

        try:
            confidence = min(1.0, max(0.0, float(entry.get("confidence", 0.7))))
        except (TypeError, ValueError):
            confidence = 0.7

        # Confidence scales influence: low confidence -> near the static prior.
        effective = 1.0 - (1.0 - combined) * confidence
        rationale = str(entry.get("rationale", "")).strip() or "No rationale supplied."
        return LlamaDetailedScore(
            source_id=source_id,
            combined=combined,
            confidence=confidence,
            effective=min(1.0, max(0.0, effective)),
            factors=factors,
            rationale=rationale,
            model=self.model,
            prompt_version=self.prompt_version,
        )

    # -- rationale formatting ---------------------------------------------------

    def _format_rationale(self, detailed: LlamaDetailedScore) -> str:
        if detailed.factors:
            factor_str = ", ".join(
                f"{name}={detailed.factors.get(name, 0.5):.2f}"
                for name in FACTOR_NAMES
            )
        else:
            factor_str = "factors not reported"
        return (
            f"llama factors [{factor_str}] -> combined {detailed.combined:.2f}, "
            f"confidence {detailed.confidence:.2f}, "
            f"effective {detailed.effective:.2f} "
            f"(prompt {detailed.prompt_version}); {detailed.rationale}"
        )

    # -- engine hook: stamp the prompt version on the weight model ----------------

    def model_id(self) -> str:
        return f"llama-live:{self.model}:prompt-{self.prompt_version}"


_BATCH_SYSTEM_PROMPT = """\
You score the evidentiary standing of intelligence evidence items for the \
VessellFramework, an analytic-tradecraft evaluation framework. You receive a \
SET of items together so you can calibrate them against each other and notice \
shared sourcing or double-counting. Reply with JSON only, exactly this shape:

{"scores": [{"source_id": "<id>",
  "factors": {"reliability": <0.0-1.0>, "corroboration": <0.0-1.0>,
              "directness": <0.0-1.0>, "timeliness": <0.0-1.0>},
  "confidence": <0.0-1.0>,
  "rationale": "<one or two sentences>"}]}

Factor guide:
- reliability: how trustworthy the source itself is (track record, access, \
motive to mislead).
- corroboration: independent confirmation visible in the set you were given.
- directness: first-hand observation (high) vs multi-hop inference (low).
- timeliness: currency relative to the question; stale-but-true still \
deserves a fair score.
- confidence: YOUR confidence in this assessment. Be honest: score below 0.5 \
when the item gives you little to judge by.

Each item lists the framework's standing prior for its source tier (0..1). \
Treat it as an anchor: refine within its neighborhood, discount where the \
factors warrant, and never inflate an item past what its description \
justifies. Discount for unresolved provenance, circular sourcing, or \
conflicting lineage. One entry per item, every item scored."""


def _batch_user_prompt(
    items: list[tuple[EvidenceItem, ProvenanceResolution]],
) -> str:
    lines = ["Score each of the following evidence items. JSON only."]
    for item, resolution in items:
        prior = SOURCE_TIER_WEIGHTS[item.status]
        lines.append(
            f"\n- source_id: {item.source_id}\n"
            f"  description: {item.description}\n"
            f"  source tier: {item.status.value} (framework prior: {prior:.2f})\n"
            f"  provenance: {resolution.state.value}; "
            f"root: {resolution.root_id}; note: {resolution.note or 'none'}"
        )
    return "\n".join(lines)
