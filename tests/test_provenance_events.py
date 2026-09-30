# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Tests for the hash-chained claim-event log (case-study Section 4).

Every lifecycle transition is recorded as an event hashed into a
per-claim chain; verify_event_chain() recomputes every hash and checks
every link, so reordering, deletion, or alteration of an event is
detectable. Worked example: the September 30 "blacklisted" disavowal.
"""

import itertools
from dataclasses import replace

import pytest

from vessell import provenance
from vessell.provenance import (
    SourceStatus,
    add_corroboration,
    claim_events,
    confirm_dependent_update,
    disavow,
    gate_for_use,
    intake_claim,
    propagate_correction,
    record_event,
    record_waiver,
    register_dependent,
    reset_claim_lifecycle,
    verify_event_chain,
)


@pytest.fixture(autouse=True)
def _clean_lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def _intake_blacklisted():
    return intake_claim(
        text="Subject is blacklisted from federal hiring, security clearances, "
        "and Intelligence Community paths.",
        subject="Christopher R. Vessell",
        source="Sept 24 2026 intake thread (self-report)",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at="2026-09-24T10:00:00",
    )


def test_intake_records_genesis_event() -> None:
    record = _intake_blacklisted()
    events = claim_events(record.id)
    assert len(events) == 1
    event = events[0]
    assert event.event_type == "INTAKE"
    assert event.seq == 1
    assert event.prev_hash == "GENESIS"
    assert len(event.event_hash) == 64  # SHA-256 hex
    ok, reason = verify_event_chain(record.id)
    assert ok, reason


def test_full_lifecycle_chain_links_and_verifies() -> None:
    record = _intake_blacklisted()
    add_corroboration(
        record,
        source="second sighting",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="independent-root",
        observed_at="2026-09-25T10:00:00",
    )
    record = add_corroboration(
        record,
        source="third sighting",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="another-root",
        observed_at="2026-09-26T10:00:00",
    )
    gate_for_use(record, "consequential")
    register_dependent(
        record.id,
        artifact="GOAL.md",
        location="constraints",
        via="intake note -> goal constraint",
    )
    correction = disavow(
        record,
        disavowed_by="Christopher R. Vessell",
        reason="originated at the start of an LLM thread; not my reality",
        corrected_text="No clearance held; clearance-required roles excluded.",
        disavowed_at="2026-09-30T10:00:00",
    )
    propagate_correction(record.id, correction_id=correction.id)
    confirm_dependent_update(
        record.id,
        artifact="GOAL.md",
        location="constraints",
        correction_id=correction.id,
    )

    events = claim_events(record.id)
    types = [e.event_type for e in events]
    assert types == [
        "INTAKE",
        "CORROBORATION",
        "CORROBORATION",
        "GATE_DECISION",
        "DEPENDENT_REGISTERED",
        "DISAVOWAL",
        "CORRECTION_DELIVERED",
        "UPDATE_CONFIRMED",
    ]
    # Linkage: each event's prev_hash is the previous event's hash.
    for previous, current in itertools.pairwise(events):
        assert current.prev_hash == previous.event_hash
        assert current.seq == previous.seq + 1
    ok, reason = verify_event_chain(record.id)
    assert ok, reason


def test_waiver_and_gate_decision_recorded() -> None:
    record = _intake_blacklisted()
    record_waiver(record, waived_by="analyst", reason="time-critical")
    allowed, _ = gate_for_use(record, "consequential")
    assert allowed
    types = [e.event_type for e in claim_events(record.id)]
    assert types == ["INTAKE", "WAIVER", "GATE_DECISION"]


def test_blocked_gate_decision_is_recorded() -> None:
    record = _intake_blacklisted()
    allowed, _ = gate_for_use(record, "consequential")
    assert not allowed
    events = claim_events(record.id)
    assert events[-1].event_type == "GATE_DECISION"
    assert "allowed=False" in events[-1].detail


def test_tampered_event_breaks_chain() -> None:
    record = _intake_blacklisted()
    add_corroboration(
        record,
        source="second sighting",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="independent-root",
    )
    chain = provenance._EVENTS[record.id]
    tampered = replace(chain[1], detail="forged corroboration")
    chain[1] = tampered
    ok, reason = verify_event_chain(record.id)
    assert not ok
    assert "altered" in reason


def test_reordered_events_break_chain() -> None:
    record = _intake_blacklisted()
    add_corroboration(
        record,
        source="second sighting",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="independent-root",
    )
    chain = provenance._EVENTS[record.id]
    chain[0], chain[1] = chain[1], chain[0]
    ok, reason = verify_event_chain(record.id)
    assert not ok
    assert "reordered or removed" in reason


def test_removed_event_breaks_chain() -> None:
    record = _intake_blacklisted()
    add_corroboration(
        record,
        source="second sighting",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="independent-root",
    )
    del provenance._EVENTS[record.id][0]
    ok, _ = verify_event_chain(record.id)
    assert not ok


def test_empty_chain_verifies() -> None:
    ok, reason = verify_event_chain("claim-that-does-not-exist")
    assert ok
    assert "0 event(s)" in reason


def test_reset_clears_event_log() -> None:
    record = _intake_blacklisted()
    assert claim_events(record.id)
    reset_claim_lifecycle()
    assert claim_events(record.id) == []


def test_manual_record_event_appends_to_chain() -> None:
    record = _intake_blacklisted()
    event = record_event(record.id, "CUSTOM", detail="analyst note")
    assert event.seq == 2
    assert event.prev_hash == claim_events(record.id)[0].event_hash
    ok, reason = verify_event_chain(record.id)
    assert ok, reason


def test_correction_record_gets_own_intake_chain() -> None:
    record = _intake_blacklisted()
    correction = disavow(
        record,
        disavowed_by="Christopher R. Vessell",
        reason="not my reality",
        corrected_text="No clearance held.",
    )
    # The correction is a new claim record: its own chain starts at GENESIS
    # with INTAKE, and the original claim's chain ends at DISAVOWAL.
    correction_events = claim_events(correction.id)
    assert [e.event_type for e in correction_events] == ["INTAKE"]
    assert correction_events[0].prev_hash == "GENESIS"
    original_events = claim_events(record.id)
    assert original_events[-1].event_type == "DISAVOWAL"
    assert f"superseded_by={correction.id}" in original_events[-1].detail
    ok, reason = verify_event_chain(record.id)
    assert ok, reason
    ok, reason = verify_event_chain(correction.id)
    assert ok, reason
