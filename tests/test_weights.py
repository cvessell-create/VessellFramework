"""Regression tests for vessell.weights — Llama-weighted evidence scoring."""

import json
from pathlib import Path

import pytest

from vessell.provenance import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    ProvenanceState,
    SourceStatus,
)
from vessell.weights import (
    CONFLICT_MULTIPLIER,
    PROVENANCE_STATE_MULTIPLIERS,
    SOURCE_TIER_WEIGHTS,
    WEIGHT_TABLE_VERSION,
    AggregationResult,
    LlamaScore,
    LlamaUnavailable,
    LlamaWeighter,
    WeightingEngine,
)


def _registry_with(*items: EvidenceItem) -> ProvenanceRegistry:
    registry = ProvenanceRegistry()
    registry.register_many(list(items))
    return registry


# ---------------------------------------------------------------------------
# Static calibrated tables
# ---------------------------------------------------------------------------


def test_static_tier_weights_are_documented_and_ordered() -> None:
    assert SOURCE_TIER_WEIGHTS[SourceStatus.SOURCE_ESTABLISHED] == 1.00
    assert SOURCE_TIER_WEIGHTS[SourceStatus.FRAMEWORK_SYNTHESIS] == 0.60
    assert SOURCE_TIER_WEIGHTS[SourceStatus.WORKING_HYPOTHESIS] == 0.35
    assert SOURCE_TIER_WEIGHTS[SourceStatus.ILLUSTRATIVE] == 0.10
    ordered = [SOURCE_TIER_WEIGHTS[s] for s in SourceStatus]
    assert ordered == sorted(ordered, reverse=True)
    assert all(0 < w <= 1.0 for w in ordered)


def test_provenance_firewall_zeroes_unresolved_weights() -> None:
    for state, item_kwargs in [
        (ProvenanceState.UNRESOLVED_PARENT, {"upstream_of": "missing-parent"}),
        (ProvenanceState.MISSING_RECORD, {}),
        (ProvenanceState.CYCLE, {"upstream_of": "loop-b"}),
    ]:
        registry = ProvenanceRegistry()
        if state is ProvenanceState.CYCLE:
            a = EvidenceItem("a", SourceStatus.SOURCE_ESTABLISHED, "loop-a", upstream_of="loop-b")
            b = EvidenceItem("b", SourceStatus.SOURCE_ESTABLISHED, "loop-b", upstream_of="loop-a")
            registry.register_many([a, b])
            item = a
        elif state is ProvenanceState.MISSING_RECORD:
            item = EvidenceItem("ghost", SourceStatus.SOURCE_ESTABLISHED, "ghost")
            # deliberately NOT registered
        else:
            item = EvidenceItem("orphan", SourceStatus.SOURCE_ESTABLISHED, "orphan", **item_kwargs)
            registry.register(item)
        engine = WeightingEngine(registry)
        record = engine.weight_item(item)
        assert record.provenance_state == state.value
        assert record.weight == 0.0
        assert PROVENANCE_STATE_MULTIPLIERS[state] == 0.0


def test_conflict_is_discounted_and_flagged_not_dropped() -> None:
    registry = ProvenanceRegistry()
    registry.register(EvidenceItem("x v1", SourceStatus.SOURCE_ESTABLISHED, "x", upstream_of="p1"))
    registry.register(EvidenceItem("x v2", SourceStatus.SOURCE_ESTABLISHED, "x", upstream_of="p2"))
    engine = WeightingEngine(registry)
    record = engine.weight_item(EvidenceItem("x", SourceStatus.SOURCE_ESTABLISHED, "x"))
    assert record.provenance_state == ProvenanceState.CONFLICT.value
    assert record.weight == pytest.approx(1.0 * CONFLICT_MULTIPLIER)
    assert any("conflict" in flag for flag in record.flags)
    assert record.weight > 0.0  # visible in the audit trail, not silently dropped


# ---------------------------------------------------------------------------
# Independence discount
# ---------------------------------------------------------------------------


def test_shared_root_conserves_root_contribution() -> None:
    registry = _registry_with(
        EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root"),
        EvidenceItem("child a", SourceStatus.SOURCE_ESTABLISHED, "child-a", upstream_of="root"),
        EvidenceItem("child b", SourceStatus.SOURCE_ESTABLISHED, "child-b", upstream_of="root"),
        EvidenceItem("lone", SourceStatus.SOURCE_ESTABLISHED, "lone"),
    )
    evidence_set = EvidenceSet(registry, [
        EvidenceItem("child a", SourceStatus.SOURCE_ESTABLISHED, "child-a", upstream_of="root"),
        EvidenceItem("child b", SourceStatus.SOURCE_ESTABLISHED, "child-b", upstream_of="root"),
        EvidenceItem("lone", SourceStatus.SOURCE_ESTABLISHED, "lone"),
    ])
    weighted = WeightingEngine(registry).weight_set(evidence_set)

    child_a = weighted.by_source("child-a")
    child_b = weighted.by_source("child-b")
    lone = weighted.by_source("lone")

    assert child_a.independence_factor == pytest.approx(0.5)
    assert child_b.independence_factor == pytest.approx(0.5)
    assert lone.independence_factor == pytest.approx(1.0)
    # Two derivatives of one root carry no more than the root would alone.
    assert child_a.weight + child_b.weight == pytest.approx(1.0)
    assert "shared root root" in child_a.rationale


def test_independent_roots_are_not_discounted() -> None:
    registry = _registry_with(
        EvidenceItem("r1", SourceStatus.SOURCE_ESTABLISHED, "r1"),
        EvidenceItem("r2", SourceStatus.SOURCE_ESTABLISHED, "r2"),
    )
    evidence_set = EvidenceSet(registry, [
        EvidenceItem("r1", SourceStatus.SOURCE_ESTABLISHED, "r1"),
        EvidenceItem("r2", SourceStatus.SOURCE_ESTABLISHED, "r2"),
    ])
    weighted = WeightingEngine(registry).weight_set(evidence_set)
    assert weighted.total_weight == pytest.approx(2.0)
    assert weighted.independent_root_count == 2


def test_normalized_weights_sum_to_one() -> None:
    registry = _registry_with(
        EvidenceItem("est", SourceStatus.SOURCE_ESTABLISHED, "est"),
        EvidenceItem("hyp", SourceStatus.WORKING_HYPOTHESIS, "hyp"),
        EvidenceItem("ill", SourceStatus.ILLUSTRATIVE, "ill"),
    )
    evidence_set = EvidenceSet(registry, [
        EvidenceItem("est", SourceStatus.SOURCE_ESTABLISHED, "est"),
        EvidenceItem("hyp", SourceStatus.WORKING_HYPOTHESIS, "hyp"),
        EvidenceItem("ill", SourceStatus.ILLUSTRATIVE, "ill"),
    ])
    weighted = WeightingEngine(registry).weight_set(evidence_set)
    total = sum(r.normalized_weight for r in weighted.records)
    assert total == pytest.approx(1.0)
    by_id = {r.source_id: r for r in weighted.records}
    assert by_id["est"].normalized_weight > by_id["hyp"].normalized_weight > by_id["ill"].normalized_weight


def test_all_unresolved_set_produces_zero_total_with_note() -> None:
    registry = ProvenanceRegistry()
    orphan = EvidenceItem("orphan", SourceStatus.SOURCE_ESTABLISHED, "orphan", upstream_of="missing")
    registry.register(orphan)
    weighted = WeightingEngine(registry).weight_set(EvidenceSet(registry, [orphan]))
    assert weighted.total_weight == 0.0
    assert weighted.notes  # the analyst is told nothing here can drive a judgment


# ---------------------------------------------------------------------------
# Weight provenance (the weight's own audit trail)
# ---------------------------------------------------------------------------


def test_every_weight_carries_its_provenance() -> None:
    registry = _registry_with(EvidenceItem("e", SourceStatus.FRAMEWORK_SYNTHESIS, "e"))
    record = WeightingEngine(registry).weight_item(
        EvidenceItem("e", SourceStatus.FRAMEWORK_SYNTHESIS, "e")
    )
    assert record.weight_model == f"llama-static-{WEIGHT_TABLE_VERSION}"
    assert record.table_version == WEIGHT_TABLE_VERSION
    assert record.rationale  # no silent numbers
    assert record.static_weight == pytest.approx(0.60)
    assert record.weight == pytest.approx(0.60)


def test_weight_record_serializes_to_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema_path = Path(__file__).parents[1] / "schemas" / "weight.record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    registry = _registry_with(EvidenceItem("e", SourceStatus.SOURCE_ESTABLISHED, "e"))
    record = WeightingEngine(registry).weight_item(
        EvidenceItem("e", SourceStatus.SOURCE_ESTABLISHED, "e")
    )
    jsonschema.Draft202012Validator(schema).validate(record.to_dict())


# ---------------------------------------------------------------------------
# Live Llama path
# ---------------------------------------------------------------------------


class _StubWeighter(LlamaWeighter):
    def __init__(self, score_value: float) -> None:
        super().__init__(base_url="http://stub.invalid", model="llama-stub")
        self._score_value = score_value

    def score(self, item, resolution):  # type: ignore[override]
        return LlamaScore(weight=self._score_value, rationale="stub rationale", model=self.model)


class _DeadWeighter(LlamaWeighter):
    def score(self, item, resolution):  # type: ignore[override]
        raise LlamaUnavailable("no endpoint in tests")


def test_live_llama_refines_within_tier_ceiling() -> None:
    registry = _registry_with(EvidenceItem("e", SourceStatus.SOURCE_ESTABLISHED, "e"))
    item = EvidenceItem("e", SourceStatus.SOURCE_ESTABLISHED, "e")

    full_marks = WeightingEngine(registry, weighter=_StubWeighter(1.0)).weight_item(item)
    assert full_marks.weight == pytest.approx(1.0)  # ceiling holds
    assert full_marks.llama_score == 1.0
    assert full_marks.weight_model == "llama-live:llama-stub"

    zero_marks = WeightingEngine(registry, weighter=_StubWeighter(0.0)).weight_item(item)
    assert zero_marks.weight == pytest.approx(0.5)  # floor: never below 50% of static
    assert "stub rationale" in zero_marks.rationale


def test_llama_unreachable_falls_back_to_static_with_flag() -> None:
    registry = _registry_with(EvidenceItem("e", SourceStatus.WORKING_HYPOTHESIS, "e"))
    item = EvidenceItem("e", SourceStatus.WORKING_HYPOTHESIS, "e")
    record = WeightingEngine(registry, weighter=_DeadWeighter()).weight_item(item)
    assert record.weight == pytest.approx(0.35)  # static tables govern
    assert record.llama_score is None
    assert "llama-unreachable-fallback" in record.flags
    assert record.weight_model.startswith("llama-static-")


def test_weighter_ping_false_for_dead_endpoint() -> None:
    weighter = LlamaWeighter(base_url="http://127.0.0.1:1", timeout=1.0)
    assert weighter.ping() is False


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def test_aggregate_weighted_mean_and_empty_case() -> None:
    registry = _registry_with(
        EvidenceItem("est", SourceStatus.SOURCE_ESTABLISHED, "est"),
        EvidenceItem("hyp", SourceStatus.WORKING_HYPOTHESIS, "hyp"),
    )
    evidence_set = EvidenceSet(registry, [
        EvidenceItem("est", SourceStatus.SOURCE_ESTABLISHED, "est"),
        EvidenceItem("hyp", SourceStatus.WORKING_HYPOTHESIS, "hyp"),
    ])
    engine = WeightingEngine(registry)
    weighted = engine.weight_set(evidence_set)

    result = engine.aggregate(weighted, {"est": 0.8, "hyp": 0.2})
    assert isinstance(result, AggregationResult)
    # est carries 1.0/1.35 of normalized weight, hyp 0.35/1.35
    assert result.value == pytest.approx((0.8 * 1.0 + 0.2 * 0.35) / 1.35)
    assert result.contributors == 2

    empty = engine.aggregate(weighted, {})
    assert empty.value is None
    assert empty.contributors == 0
