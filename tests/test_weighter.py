"""Regression tests for vessell.weighter — the calibrated Llama weighter."""

import json
import urllib.error

import pytest

from vessell.provenance import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    SourceStatus,
)
from vessell.weights import LlamaUnavailable, WeightingEngine
from vessell.weighter import (
    FACTOR_WEIGHTS,
    PROMPT_VERSION,
    CalibratedLlamaWeighter,
    combine_factors,
)


def _item(source_id: str, status=SourceStatus.SOURCE_ESTABLISHED) -> EvidenceItem:
    return EvidenceItem(f"evidence {source_id}", status, source_id)


def _response(scores: list[dict]) -> dict:
    return {
        "choices": [
            {"message": {"content": json.dumps({"scores": scores})}}
        ]
    }


def _full_marks(source_id: str) -> dict:
    return {
        "source_id": source_id,
        "factors": {"reliability": 1.0, "corroboration": 1.0,
                    "directness": 1.0, "timeliness": 1.0},
        "confidence": 1.0,
        "rationale": "textbook established reporting",
    }


class _StubWeighter(CalibratedLlamaWeighter):
    """Canned model responses; override per-test via `responses` queue."""

    def __init__(self, bodies: list) -> None:
        super().__init__(base_url="http://stub.invalid", model="llama-stub")
        self._bodies = list(bodies)
        self.calls = 0

    def _post(self, payload):  # type: ignore[override]
        self.calls += 1
        body = self._bodies.pop(0)
        if isinstance(body, Exception):
            raise body
        return body


def _registry(*items: EvidenceItem) -> ProvenanceRegistry:
    registry = ProvenanceRegistry()
    registry.register_many(list(items))
    return registry


# ---------------------------------------------------------------------------
# Factor combination
# ---------------------------------------------------------------------------


def test_factor_weights_sum_to_one() -> None:
    assert sum(FACTOR_WEIGHTS.values()) == pytest.approx(1.0)
    assert set(FACTOR_WEIGHTS) == {"reliability", "corroboration",
                                   "directness", "timeliness"}


def test_combine_factors_is_deterministic_weighted_sum() -> None:
    factors = {"reliability": 1.0, "corroboration": 0.5,
               "directness": 0.0, "timeliness": 0.5}
    expected = 1.0 * 0.35 + 0.5 * 0.25 + 0.0 * 0.25 + 0.5 * 0.15
    assert combine_factors(factors) == pytest.approx(expected)


def test_rationale_carries_factor_breakdown() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    weighter = _StubWeighter([_response([_full_marks("e")])])
    scored = weighter.score(item, registry.resolve("e"))
    assert scored.weight == pytest.approx(1.0)
    for name in ("reliability", "corroboration", "directness", "timeliness"):
        assert name in scored.rationale
    assert f"prompt {PROMPT_VERSION}" in scored.rationale


# ---------------------------------------------------------------------------
# Confidence scaling
# ---------------------------------------------------------------------------


def test_zero_confidence_shrinks_to_static_prior() -> None:
    registry = _registry(_item("e", SourceStatus.WORKING_HYPOTHESIS))
    item = _item("e", SourceStatus.WORKING_HYPOTHESIS)
    entry = {
        "source_id": "e",
        "factors": {"reliability": 0.0, "corroboration": 0.0,
                    "directness": 0.0, "timeliness": 0.0},
        "confidence": 0.0,  # model admits it cannot judge
        "rationale": "no basis to judge",
    }
    engine = WeightingEngine(registry, weighter=_StubWeighter([_response([entry])]))
    record = engine.weight_item(item)
    # effective = 1 - (1 - 0) * 0 = 1 -> blend keeps the full static weight
    assert record.weight == pytest.approx(0.35)
    assert record.llama_score == pytest.approx(1.0)


def test_full_confidence_zero_marks_discounts_to_floor() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    entry = {
        "source_id": "e",
        "factors": {"reliability": 0.0, "corroboration": 0.0,
                    "directness": 0.0, "timeliness": 0.0},
        "confidence": 1.0,
        "rationale": "clearly worthless",
    }
    engine = WeightingEngine(registry, weighter=_StubWeighter([_response([entry])]))
    record = engine.weight_item(item)
    # effective = 0 -> engine blend floor 0.5 * static 1.0
    assert record.weight == pytest.approx(0.5)


def test_partial_confidence_partial_influence() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    entry = {
        "source_id": "e",
        "factors": {"reliability": 0.0, "corroboration": 0.0,
                    "directness": 0.0, "timeliness": 0.0},
        "confidence": 0.5,
        "rationale": "middling",
    }
    engine = WeightingEngine(registry, weighter=_StubWeighter([_response([entry])]))
    record = engine.weight_item(item)
    # effective = 1 - 1*0.5 = 0.5 -> blend 0.5 + 0.5*0.5 = 0.75
    assert record.weight == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# Batch scoring
# ---------------------------------------------------------------------------


def test_batch_scores_whole_set_in_one_call() -> None:
    items = [_item("a"), _item("b"), _item("c")]
    registry = _registry(*items)
    weighter = _StubWeighter([_response([_full_marks("a"),
                                         _full_marks("b"),
                                         _full_marks("c")])])
    results = weighter.score_batch([(i, registry.resolve(i.source_id)) for i in items])
    assert weighter.calls == 1  # one round-trip for the whole set
    assert set(results) == {"a", "b", "c"}
    assert all(r.effective == pytest.approx(1.0) for r in results.values())


def test_batch_missing_item_raises() -> None:
    items = [_item("a"), _item("b")]
    registry = _registry(*items)
    weighter = _StubWeighter([_response([_full_marks("a")])])  # 'b' missing
    with pytest.raises(LlamaUnavailable):
        weighter.score_batch([(i, registry.resolve(i.source_id)) for i in items])


# ---------------------------------------------------------------------------
# Retry behavior
# ---------------------------------------------------------------------------


def test_transient_failure_retries_then_succeeds() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    flaky = _StubWeighter([
        urllib.error.URLError("blip 1"),
        urllib.error.URLError("blip 2"),
        _response([_full_marks("e")]),
    ])
    import vessell.weighter as weighter_module
    original_sleep = weighter_module.time.sleep
    weighter_module.time.sleep = lambda s: None
    try:
        scored = flaky.score(item, registry.resolve("e"))
    finally:
        weighter_module.time.sleep = original_sleep
    assert flaky.calls == 3
    assert scored.weight == pytest.approx(1.0)


def test_persistent_failure_raises_unavailable() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    dead = _StubWeighter([urllib.error.URLError("down")] * 3)
    import vessell.weighter as weighter_module
    original_sleep = weighter_module.time.sleep
    weighter_module.time.sleep = lambda s: None
    try:
        with pytest.raises(LlamaUnavailable):
            dead.score(item, registry.resolve("e"))
    finally:
        weighter_module.time.sleep = original_sleep
    assert dead.calls == 3


def test_client_error_does_not_retry() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    bad = _StubWeighter([
        urllib.error.HTTPError("http://stub.invalid", 400, "bad request", {}, None)
    ])
    with pytest.raises(LlamaUnavailable):
        bad.score(item, registry.resolve("e"))
    assert bad.calls == 1  # 4xx: retrying won't help


# ---------------------------------------------------------------------------
# Prompt versioning + engine integration
# ---------------------------------------------------------------------------


def test_prompt_version_stamped_on_weight_model() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    engine = WeightingEngine(
        registry, weighter=_StubWeighter([_response([_full_marks("e")])]))
    record = engine.weight_item(item)
    assert record.weight_model == f"llama-live:llama-stub:prompt-{PROMPT_VERSION}"


def test_legacy_bare_weight_shape_still_accepted() -> None:
    registry = _registry(_item("e"))
    item = _item("e")
    legacy = {"source_id": "e", "weight": 0.7, "confidence": 1.0,
              "rationale": "old shape"}
    engine = WeightingEngine(registry, weighter=_StubWeighter([_response([legacy])]))
    record = engine.weight_item(item)
    # effective 0.7 -> blend 0.5 + 0.5*0.7 = 0.85 of static 1.0
    assert record.weight == pytest.approx(0.85)


def test_better_weighter_end_to_end_with_set() -> None:
    items = [_item("a"), _item("b", SourceStatus.WORKING_HYPOTHESIS)]
    registry = _registry(*items)
    evidence_set = EvidenceSet(registry, items)
    weighter = _StubWeighter([_response([_full_marks("a"), _full_marks("b")])])
    weighted = WeightingEngine(registry, weighter=weighter).weight_set(evidence_set)
    assert weighter.calls == 1  # whole set scored in one batched model call
    assert weighted.total_weight == pytest.approx(1.35)
    assert all(r.weight_model.endswith(f"prompt-{PROMPT_VERSION}")
               for r in weighted.records)
    assert all("llama-batch-scored" in r.flags for r in weighted.records)
