from vessell.provenance import EvidenceItem, ProvenanceRegistry, ProvenanceState, SourceStatus


def test_provenance_resolves_to_root() -> None:
    registry = ProvenanceRegistry()
    registry.register(EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root"))
    registry.register(EvidenceItem("child", SourceStatus.SOURCE_ESTABLISHED, "child", "root"))

    result = registry.resolve("child")

    assert result.state == ProvenanceState.RESOLVED
    assert result.root_id == "root"


def test_missing_parent_is_not_independence() -> None:
    registry = ProvenanceRegistry()
    registry.register(EvidenceItem("orphan", SourceStatus.SOURCE_ESTABLISHED, "orphan", "missing"))

    result = registry.resolve("orphan")

    assert result.state == ProvenanceState.UNRESOLVED_PARENT
    assert registry.compare_independence(["orphan"])["independent"] is None


# ---------------------------------------------------------------------------
# Claim lifecycle: provenance-tagged claims with correction propagation
# ---------------------------------------------------------------------------

import json
from pathlib import Path

import pytest

from vessell.provenance import (
    ClaimStatus,
    add_corroboration,
    disavow,
    gate_for_use,
    get_claim,
    intake_claim,
    propagate_correction,
    record_waiver,
    register_dependent,
    reset_claim_lifecycle,
)


@pytest.fixture(autouse=True)
def _clean_lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def _intake_blacklisted(source_root: "str | None" = None) -> "object":
    from vessell.provenance import ClaimRecord, SourceStatus

    record = intake_claim(
        text="Subject is blacklisted from federal hiring, security clearances, "
        "and Intelligence Community paths.",
        subject="Christopher R. Vessell",
        source="Sept 24 2026 intake thread (self-report)",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at="2026-09-24T10:00:00",
        source_root=source_root,
    )
    assert isinstance(record, ClaimRecord)
    return record


def test_intake_self_report_starts_unverified() -> None:
    record = _intake_blacklisted()
    assert record.status is ClaimStatus.UNVERIFIED
    assert record.disavowal is None
    assert record.supersedes is None


def test_intake_official_record_settles() -> None:
    from vessell.provenance import SourceStatus

    record = intake_claim(
        text="USGS event page confirms M4.2 quake near Wauna, WA.",
        subject="Wauna quake",
        source="USGS event page",
        source_tier=SourceStatus.SOURCE_ESTABLISHED,
        is_official_record=True,
    )
    assert record.status is ClaimStatus.CORROBORATED


def test_gate_blocks_consequential_use_of_unverified() -> None:
    record = _intake_blacklisted()
    allowed, reason = gate_for_use(record, "consequential")
    assert allowed is False
    assert "UNVERIFIED" in reason


def test_gate_allows_low_stakes_with_status_attached() -> None:
    record = _intake_blacklisted()
    allowed, reason = gate_for_use(record, "low")
    assert allowed is True
    assert "UNVERIFIED" in reason


def test_gate_rejects_bad_stakes() -> None:
    record = _intake_blacklisted()
    with pytest.raises(ValueError):
        gate_for_use(record, "medium")


def test_waiver_path_permits_consequential_use() -> None:
    record = _intake_blacklisted()
    record = record_waiver(
        record,
        waived_by="analyst",
        reason="Accepting risk pending corroboration; revisit in 7 days.",
    )
    assert record.waiver is not None
    allowed, reason = gate_for_use(record, "consequential")
    assert allowed is True
    assert "waiver" in reason


def test_waiver_rejected_on_corroborated_claim() -> None:
    from vessell.provenance import SourceStatus

    record = intake_claim(
        text="Official record claim.",
        subject="s",
        source="USGS",
        source_tier=SourceStatus.SOURCE_ESTABLISHED,
        is_official_record=True,
    )
    with pytest.raises(ValueError):
        record_waiver(record, waived_by="x", reason="y")


def test_shared_root_counts_once() -> None:
    from vessell.provenance import SourceStatus

    # The intake and both echoes all trace to one thread: one root.
    record = _intake_blacklisted(source_root="intake-thread")
    record = add_corroboration(
        record,
        source="aggregator A",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="intake-thread",
    )
    record = add_corroboration(
        record,
        source="aggregator B",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        root="intake-thread",
    )
    assert record.status is ClaimStatus.UNVERIFIED
    assert record.independent_roots() == 1


def test_two_independent_roots_corroborate() -> None:
    from vessell.provenance import SourceStatus

    record = _intake_blacklisted()
    record = add_corroboration(
        record,
        source="independent outlet",
        source_tier=SourceStatus.SOURCE_ESTABLISHED,
        root="outlet-investigation",
    )
    assert record.status is ClaimStatus.CORROBORATED
    assert record.independent_roots() == 2


def test_official_record_corroboration_settles() -> None:
    from vessell.provenance import SourceStatus

    record = _intake_blacklisted()
    record = add_corroboration(
        record,
        source="agency release",
        source_tier=SourceStatus.SOURCE_ESTABLISHED,
        is_official_record=True,
    )
    assert record.status is ClaimStatus.CORROBORATED


def test_disavow_keeps_original_and_links() -> None:
    record = _intake_blacklisted()
    original_id = record.id
    correction = disavow(
        record,
        disavowed_by="Christopher R. Vessell",
        reason="Claim came from the start of an LLM thread; could have been "
        "someone else typing; not the subject's reality.",
        corrected_text="Subject does not hold a security clearance.",
        disavowed_at="2026-09-30T06:05:00",
    )
    original = get_claim(original_id)
    # Original kept, marked, never deleted.
    assert original.status is ClaimStatus.DISAVOWED
    assert original.disavowal is not None
    assert original.disavowal.disavowed_by == "Christopher R. Vessell"
    assert original.superseded_by == correction.id
    # New record links back and starts unverified (a fresh assertion).
    assert correction.supersedes == original_id
    assert correction.status is ClaimStatus.UNVERIFIED
    assert "blacklist" not in correction.text


def test_disavow_without_corrected_text_withdraws() -> None:
    record = _intake_blacklisted()
    correction = disavow(
        record, disavowed_by="subject", reason="Withdrawn in full."
    )
    assert correction.disavowal is None  # correction is a fresh record
    assert "Withdrawal" in correction.note
    assert get_claim(record.id).status is ClaimStatus.DISAVOWED


def test_disavowed_claim_is_gated_out() -> None:
    record = _intake_blacklisted()
    disavow(record, disavowed_by="subject", reason="Not true.")
    allowed, reason = gate_for_use(record, "consequential")
    assert allowed is False
    assert "DISAVOWED" in reason
    allowed_low, _ = gate_for_use(record, "low")
    assert allowed_low is False


def test_cannot_corroborate_dead_claim() -> None:
    from vessell.provenance import SourceStatus

    record = _intake_blacklisted()
    disavow(record, disavowed_by="subject", reason="Not true.")
    with pytest.raises(ValueError):
        add_corroboration(
            record, source="late outlet", source_tier=SourceStatus.SOURCE_ESTABLISHED
        )


def test_double_disavow_rejected() -> None:
    record = _intake_blacklisted()
    disavow(record, disavowed_by="subject", reason="Not true.")
    with pytest.raises(ValueError):
        disavow(record, disavowed_by="subject", reason="Again.")


def test_dependents_and_propagation() -> None:
    record = _intake_blacklisted()
    register_dependent(record.id, "cron:daily-job-hunt", "filters block")
    register_dependent(record.id, "cron:morning-news-edition", "job section rules")
    register_dependent(record.id, "cron:evening-news-edition", "job section rules")
    register_dependent(record.id, "GOAL.md", "Constraints + plan shape")
    register_dependent(record.id, "MEMORY.md", "Preferences section")
    targets = propagate_correction(record.id)
    assert len(targets) == 5
    artifacts = [t.artifact for t in targets]
    assert "cron:daily-job-hunt" in artifacts
    assert "MEMORY.md" in artifacts


def test_propagate_unknown_claim_is_empty() -> None:
    assert propagate_correction("claim-does-not-exist") == []


def test_register_dependent_rejects_unknown_claim() -> None:
    with pytest.raises(ValueError):
        register_dependent("claim-does-not-exist", "artifact", "location")


def test_worked_example_full_lifecycle() -> None:
    """The Sept 2026 'blacklisted' incident, end to end: intake ->
    gate blocks consequential use -> disavowal -> propagation list."""
    record = _intake_blacklisted()

    # The failure mode: the claim drove employer-category exclusions
    # (consequential use) without ever passing the gate.
    allowed, _ = gate_for_use(record, "consequential")
    assert allowed is False  # the gate would have stopped it

    for artifact, location in [
        ("cron:daily-job-hunt", "filters block"),
        ("cron:morning-news-edition", "job section rules"),
        ("cron:evening-news-edition", "job section rules"),
        ("GOAL.md", "Constraints + plan shape"),
        ("MEMORY.md", "Preferences section"),
    ]:
        register_dependent(record.id, artifact, location)

    correction = disavow(
        record,
        disavowed_by="Christopher R. Vessell",
        reason="From the start of an LLM thread; could have been someone "
        "else typing; not reality.",
        corrected_text="Subject does not hold a security clearance.",
        disavowed_at="2026-09-30T06:05:00",
    )
    targets = propagate_correction(record.id)
    assert len(targets) == 5
    assert correction.supersedes == record.id
    assert get_claim(record.id).superseded_by == correction.id


def test_claim_record_validates_against_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema_path = (
        Path(__file__).parents[1] / "vessell" / "schemas" / "claim.record.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    record = _intake_blacklisted()
    record = disavow(
        record,
        disavowed_by="subject",
        reason="Not true.",
        corrected_text="Corrected.",
    )
    jsonschema.Draft202012Validator(schema).validate(
        {"record_type": "claim", "claim": record.to_dict()}
    )
