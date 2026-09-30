"""Causal-path correction semantics: Section 4 causal-order rules as executable tests.

Grounded in Lamport (1978) happens-before and Castello/Redmond/Kuper
(2024) causal separation diagrams — causal relationships are witnessed by
the paths information follows:

* a correction/supersession record carries ``causal_path``: the ids of the
  records causally before it, originator first, immediate predecessor last;
* a dependent records ``via``: how the claim reached it (the witnessed path);
* propagation delivers corrections in causal order, and out-of-order
  application raises :class:`CausalOrderingError` instead of being
  silently marked complete — the causal-broadcast guarantee of Redmond et
  al. (2022) in miniature.
"""

import pytest

from vessell.provenance import (
    CausalOrderingError,
    ClaimRecord,
    ClaimStatus,
    DependentStatus,
    SourceStatus,
    confirm_dependent_update,
    deliver_correction,
    disavow,
    get_claim,
    intake_claim,
    propagate_correction,
    register_dependent,
    reset_claim_lifecycle,
)


@pytest.fixture(autouse=True)
def _clean_lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def _intake_blacklisted() -> ClaimRecord:
    return intake_claim(
        text="Subject is blacklisted from federal hiring, security clearances, "
        "and Intelligence Community paths.",
        subject="Christopher R. Vessell",
        source="Sept 24 2026 intake thread (self-report)",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at="2026-09-24T10:00:00",
    )


def _disavow_chain() -> tuple[ClaimRecord, ClaimRecord, ClaimRecord]:
    """A -> C1 -> C2: a correction of a correction, with full causal paths."""
    original = _intake_blacklisted()
    c1 = disavow(
        original,
        disavowed_by="Christopher R. Vessell",
        reason="From an LLM thread; not reality.",
        corrected_text="Subject does not hold a security clearance.",
        disavowed_at="2026-09-30T06:05:00",
    )
    c2 = disavow(
        c1,
        disavowed_by="Christopher R. Vessell",
        reason="Correction refined: clearance status vs. eligibility.",
        corrected_text="Subject does not hold an active security clearance.",
        disavowed_at="2026-09-30T07:00:00",
    )
    return original, c1, c2


# ---------------------------------------------------------------------------
# Rule 4: corrections carry their causal predecessor (the witnessed path)
# ---------------------------------------------------------------------------


def test_disavow_correction_carries_causal_path() -> None:
    original = _intake_blacklisted()
    correction = disavow(
        original, disavowed_by="subject", reason="Not true.", corrected_text="Fixed."
    )
    assert correction.causal_path == (original.id,)
    assert correction.causal_predecessor() == original.id
    assert correction.supersedes == original.id


def test_causal_path_chains_across_correction_of_correction() -> None:
    original, c1, c2 = _disavow_chain()
    assert c1.causal_path == (original.id,)
    assert c2.causal_path == (original.id, c1.id)
    assert c2.causal_predecessor() == c1.id
    # The original keeps its head-of-lineage position.
    assert original.causal_path == ()
    assert original.causal_predecessor() is None


def test_causal_predecessor_falls_back_to_supersedes_for_legacy_records() -> None:
    """Records written before causal_path existed still resolve sensibly."""
    legacy = ClaimRecord(
        id="claim-legacy",
        text="x",
        subject="s",
        source="src",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at="2026-01-01",
        status=ClaimStatus.SUPERSEDED,
        supersedes="claim-original",
    )
    assert legacy.causal_path == ()
    assert legacy.causal_predecessor() == "claim-original"


def test_causal_path_in_to_dict() -> None:
    original, c1, _ = _disavow_chain()
    as_dict = c1.to_dict()
    assert as_dict["causal_path"] == [original.id]
    assert as_dict["causal_predecessor_id"] == original.id


# ---------------------------------------------------------------------------
# Rule 5: dependents record HOW the claim reached them (via)
# ---------------------------------------------------------------------------


def test_register_dependent_records_via_witnessed_path() -> None:
    record = _intake_blacklisted()
    dependent = register_dependent(
        record.id,
        "cron:daily-job-hunt",
        "filters block",
        via="intake note -> goal constraint -> cron filters block",
    )
    assert dependent.via == "intake note -> goal constraint -> cron filters block"
    assert dependent.to_dict()["via"] == dependent.via


def test_via_defaults_to_empty_for_existing_callers() -> None:
    record = _intake_blacklisted()
    dependent = register_dependent(record.id, "GOAL.md", "Constraints")
    assert dependent.via == ""


# ---------------------------------------------------------------------------
# Rule 5: causal-order delivery; no silent out-of-order completion
# ---------------------------------------------------------------------------


def test_deliver_correction_stamps_all_dependents() -> None:
    original = _intake_blacklisted()
    register_dependent(original.id, "cron:daily-job-hunt", "filters block")
    register_dependent(original.id, "GOAL.md", "Constraints")
    correction = disavow(original, disavowed_by="subject", reason="Not true.")
    delivered = deliver_correction(original.id, correction.id)
    assert len(delivered) == 2
    assert all(d.delivered_correction == correction.id for d in delivered)
    assert all(d.status is DependentStatus.PENDING for d in delivered)


def test_deliver_unknown_correction_raises_keyerror() -> None:
    record = _intake_blacklisted()
    register_dependent(record.id, "GOAL.md", "Constraints")
    with pytest.raises(KeyError):
        deliver_correction(record.id, "correction-does-not-exist")


def test_deliver_correction_for_wrong_claim_is_ordering_violation() -> None:
    first = _intake_blacklisted()
    register_dependent(first.id, "GOAL.md", "Constraints")
    second = intake_claim(
        text="Unrelated claim.", subject="s", source="src",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
    )
    other_correction = disavow(second, disavowed_by="x", reason="y")
    with pytest.raises(CausalOrderingError):
        deliver_correction(first.id, other_correction.id)


def test_out_of_order_delivery_is_rejected_not_queued() -> None:
    """C2 causally follows C1: delivering C2 before C1 is an ordering violation."""
    original, _c1, c2 = _disavow_chain()
    register_dependent(original.id, "GOAL.md", "Constraints")
    with pytest.raises(CausalOrderingError) as exc_info:
        deliver_correction(original.id, c2.id)
    assert "Out-of-order" in str(exc_info.value)
    # Nothing was stamped: the violation aborted delivery.
    dependents = propagate_correction(original.id)
    assert dependents[0].delivered_correction is None
    assert get_claim(original.id).status is ClaimStatus.DISAVOWED  # claim itself untouched


def test_confirm_requires_delivery_first() -> None:
    """A dependent must not be marked corrected for a correction it never received."""
    original = _intake_blacklisted()
    register_dependent(original.id, "GOAL.md", "Constraints")
    correction = disavow(original, disavowed_by="subject", reason="Not true.")
    with pytest.raises(CausalOrderingError) as exc_info:
        confirm_dependent_update(
            original.id, "GOAL.md", "Constraints", correction_id=correction.id
        )
    assert "never delivered" in str(exc_info.value)
    assert propagate_correction(original.id)[0].status is DependentStatus.PENDING


def test_confirm_wrong_correction_id_is_rejected() -> None:
    original, c1, c2 = _disavow_chain()
    register_dependent(original.id, "GOAL.md", "Constraints")
    deliver_correction(original.id, c1.id)
    with pytest.raises(CausalOrderingError):
        confirm_dependent_update(
            original.id, "GOAL.md", "Constraints", correction_id=c2.id
        )


def test_confirm_unknown_correction_id_raises_keyerror() -> None:
    record = _intake_blacklisted()
    register_dependent(record.id, "GOAL.md", "Constraints")
    with pytest.raises(KeyError):
        confirm_dependent_update(
            record.id, "GOAL.md", "Constraints",
            correction_id="correction-does-not-exist",
        )


def test_causal_order_happy_path_deliver_confirm_in_sequence() -> None:
    """C1 then C2, delivered and confirmed in causal order: the full Section 4 rule-5 walk."""
    original, c1, c2 = _disavow_chain()
    register_dependent(original.id, "GOAL.md", "Constraints")

    deliver_correction(original.id, c1.id)
    updated = confirm_dependent_update(
        original.id, "GOAL.md", "Constraints", correction_id=c1.id
    )
    assert updated.status is DependentStatus.UPDATED
    assert updated.confirmed_correction == c1.id
    assert updated.delivered_correction is None  # consumed, no longer outstanding

    deliver_correction(original.id, c2.id)
    updated = confirm_dependent_update(
        original.id, "GOAL.md", "Constraints", correction_id=c2.id
    )
    assert updated.status is DependentStatus.UPDATED
    assert updated.confirmed_correction == c2.id


def test_confirm_after_skipped_hop_is_rejected() -> None:
    """Delivering both in order but confirming C2 while C1 is unconfirmed: violation."""
    original, c1, c2 = _disavow_chain()
    register_dependent(original.id, "GOAL.md", "Constraints")
    deliver_correction(original.id, c1.id)
    deliver_correction(original.id, c2.id)
    with pytest.raises(CausalOrderingError):
        confirm_dependent_update(
            original.id, "GOAL.md", "Constraints", correction_id=c2.id
        )


def test_propagate_with_correction_id_delivers_in_causal_order() -> None:
    original = _intake_blacklisted()
    register_dependent(original.id, "GOAL.md", "Constraints")
    correction = disavow(original, disavowed_by="subject", reason="Not true.")
    delivered = propagate_correction(original.id, correction_id=correction.id)
    assert len(delivered) == 1
    assert delivered[0].delivered_correction == correction.id


def test_propagate_without_correction_id_stays_pure_enumeration() -> None:
    record = _intake_blacklisted()
    register_dependent(record.id, "GOAL.md", "Constraints")
    targets = propagate_correction(record.id)
    assert len(targets) == 1
    assert targets[0].delivered_correction is None
