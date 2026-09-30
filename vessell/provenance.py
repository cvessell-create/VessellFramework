# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Provenance tracking and the provenance-tagged claim lifecycle.

Package access to the existing reference provenance implementation
(:data:`EvidenceItem`, :data:`ProvenanceRegistry`, :data:`SourceStatus`,
and friends, loaded from the v1.1 reference firewall), plus the claim
lifecycle added in v3.8.1: every consequential claim enters the system
with its provenance tag, earns corroborated standing only through
independent roots, is gated before consequential use, and — when it
turns out wrong — is disavowed without deletion while corrections
propagate to every downstream artifact that consumed it.

Doctrine
--------
A claim is a liability until corroborated. The lifecycle is:

1. **Intake** (:func:`intake_claim`). A claim always enters
   :data:`~ClaimStatus.UNVERIFIED` unless its source is a tier-1
   official record. The intake record carries who said it, the source
   tier (:class:`SourceStatus`), and when — the provenance tag.
2. **Corroboration** (:func:`add_corroboration`). Corroborating
   sightings accumulate; sightings sharing an evidentiary root count
   once (the same independence discount as :func:`vessell.verify.verify_claim`).
   A claim becomes :data:`~ClaimStatus.CORROBORATED` only with two or
   more independent roots, or one official record.
3. **Gating** (:func:`gate_for_use`). Consequential use (a decision that
   changes what the system does — exclusions, filters, classifications)
   requires :data:`~ClaimStatus.CORROBORATED`, or an explicit recorded
   waiver (:func:`record_waiver`) in which someone named accepts the
   risk. Low-stakes use may proceed on
   :data:`~ClaimStatus.UNVERIFIED`, but the status travels with the
   claim: never asserted as fact.
4. **Disavowal** (:func:`disavow`). When a claim is withdrawn or
   refuted, the original record is kept, marked
   :data:`~ClaimStatus.DISAVOWED`, and never deleted; a new record
   carries the correction and links back (``supersedes``). The full
   audit trail survives.
5. **Correction propagation** (:func:`register_dependent`,
   :func:`propagate_correction`). Artifacts that consumed a claim
   register as dependents; when the claim is disavowed, the registry
   lists exactly what needs updating. No silent downstream rot.

Causal order (Section 4 of the case study)
----------------------------------
Lifecycle events are ordered by Lamport's (1978) happens-before relation,
and — following Castello, Redmond, and Kuper (2024) — every causal
relationship is witnessed by the path the information followed. Concretely:

* a correction record carries ``causal_path``: the ids of the records
  causally before it, originator first, immediate predecessor last
  (:meth:`ClaimRecord.causal_predecessor`);
* a dependent records ``via``: how the claim reached it (the witnessed path);
* corrections are *delivered* (:func:`deliver_correction`, or
  :func:`propagate_correction` with ``correction_id``) along every
  dependency path in causal order, and :func:`confirm_dependent_update`
  refuses to mark a dependent corrected for a correction it never
  received — or one that arrives out of causal order
  (:class:`CausalOrderingError`). This is the causal-broadcast guarantee
  of Redmond et al. (2022) in miniature: no dependent applies a
  correction for a claim version it never saw.
* every lifecycle transition is recorded as a hash-chained event
  (:func:`record_event`): each event's SHA-256 commits to its
  predecessor's hash, so the claim's history is a tamper-evident
  happens-before order — causal order reified as data, verifiable with
  :func:`verify_event_chain`.

Worked example: the "blacklisted" claim
----------------------------------------
On 2026-09-24 a single self-report at intake — "I am blacklisted from
federal/clearance/IC paths" — entered the job-hunt system with no
corroboration and was treated as fact. It drove employer-category
exclusions (fraud, federal, clearance, defense, IC-pedigree) across the
overnight hunt and both news editions for six days. On 2026-09-30 the
subject disavowed it: the claim came from the start of an LLM thread,
could have been someone else typing, and was not his reality. Under
this lifecycle the claim would have entered UNVERIFIED, the gate would
have blocked consequential use (or forced a recorded waiver), and the
disavowal propagated corrections to five dependents: the three cron
configs (``daily-job-hunt``, ``morning-news-edition``,
``evening-news-edition``), ``GOAL.md``, and ``MEMORY.md`` — the
original record kept, marked DISAVOWED, never deleted.
"""

import hashlib
import sys
import uuid
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import Enum
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_reference() -> ModuleType:
    reference_path = Path(__file__).parents[1] / "vesselframework_reference_v1.1_provenance_firewall.py"
    spec = spec_from_file_location("vessel_reference", reference_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load reference implementation: {reference_path}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_reference: Any = _load_reference()
EvidenceItem = _reference.EvidenceItem
EvidenceSet = _reference.EvidenceSet
MaskirovkaAssessment = _reference.MaskirovkaAssessment
MaskirovkaVariant = _reference.MaskirovkaVariant
ProvenanceRegistry = _reference.ProvenanceRegistry
ProvenanceResolution = _reference.ProvenanceResolution
ProvenanceState = _reference.ProvenanceState
SourceStatus = _reference.SourceStatus
assess_maskirovka_convergence = _reference.assess_maskirovka_convergence

__all__ = [
    "CausalOrderingError",
    "ClaimEvent",
    "ClaimGateBlocked",
    "ClaimKind",
    "ClaimRecord",
    "ClaimStatus",
    "ClaimWaiver",
    "Corroboration",
    "Dependent",
    "DependentStatus",
    "Disavowal",
    "EvidenceItem",
    "EvidenceSet",
    "MaskirovkaAssessment",
    "MaskirovkaVariant",
    "ProvenanceRegistry",
    "ProvenanceResolution",
    "ProvenanceState",
    "SourceStatus",
    "add_corroboration",
    "assess_maskirovka_convergence",
    "claim_events",
    "confirm_dependent_update",
    "deliver_correction",
    "disavow",
    "gate_for_use",
    "get_claim",
    "intake_claim",
    "pending_corrections",
    "propagate_correction",
    "record_event",
    "record_waiver",
    "register_dependent",
    "require_gate",
    "reset_claim_lifecycle",
    "revalidate_claim",
    "verify_event_chain",
]


# NOTE ON TYPING: SourceStatus is re-exported from the dynamically loaded
# v1.1 reference module (see _load_reference), so mypy sees it as a variable
# rather than a type. The targeted `type: ignore` comments below are scoped
# to that single limitation; runtime behavior is unaffected (verify.py already
# relies on the same re-export).

# ---------------------------------------------------------------------------
# Claim lifecycle: provenance-tagged claims with correction propagation
# ---------------------------------------------------------------------------


class ClaimStatus(Enum):
    """Standing of a claim in the lifecycle."""

    UNVERIFIED = "UNVERIFIED"  # intake only; never asserted as fact
    CORROBORATED = "CORROBORATED"  # 2+ independent roots, or one official record
    DISAVOWED = "DISAVOWED"  # withdrawn or refuted; kept, never deleted
    SUPERSEDED = "SUPERSEDED"  # replaced by a newer record (see superseded_by)


class ClaimKind(Enum):
    """ICD 203 information-vs-assumption-vs-judgment distinction.

    REPORT is observed or reported fact. ASSUMPTION is taken as given
    without being established. JUDGMENT is an analytic conclusion drawn
    from evidence. The kind never changes the gate: only the
    corroboration standing does.
    """

    REPORT = "REPORT"
    ASSUMPTION = "ASSUMPTION"
    JUDGMENT = "JUDGMENT"


class DependentStatus(Enum):
    """Whether a downstream dependent has confirmed it consumed a correction."""

    PENDING = "PENDING"  # correction propagated; update not yet confirmed
    UPDATED = "UPDATED"  # downstream confirmed it consumed the correction


@dataclass(frozen=True)
class Corroboration:
    """One sighting corroborating a claim."""

    source: str
    tier: SourceStatus  # type: ignore[valid-type]
    root: str | None = None  # shared evidentiary root, e.g. "intake-thread"
    observed_at: str = ""  # ISO date/datetime
    is_official_record: bool = False
    note: str = ""

    def effective_root(self) -> str:
        """Corroborations sharing a root are one evidentiary ancestor."""
        return self.root or self.source

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tier": self.tier.value,  # type: ignore[attr-defined]
            "root": self.root,
            "observed_at": self.observed_at,
            "is_official_record": self.is_official_record,
            "note": self.note,
        }


@dataclass(frozen=True)
class ClaimWaiver:
    """A named person accepted the risk of consequential use of an
    UNVERIFIED claim. The waiver is the audit trail of that decision."""

    waived_by: str
    reason: str
    waived_at: str = ""  # ISO date/datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "waived_by": self.waived_by,
            "reason": self.reason,
            "waived_at": self.waived_at,
        }


@dataclass(frozen=True)
class Disavowal:
    """A claim was withdrawn or refuted. The original record survives;
    this is the audit trail of its withdrawal."""

    disavowed_by: str
    reason: str
    disavowed_at: str = ""  # ISO date/datetime
    corrected_text: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "disavowed_by": self.disavowed_by,
            "reason": self.reason,
            "disavowed_at": self.disavowed_at,
            "corrected_text": self.corrected_text,
        }


@dataclass(frozen=True)
class Dependent:
    """A downstream artifact/location that consumed a claim and must be
    updated when the claim is corrected.

    ``via`` is the witnessed path: how the claim reached this dependent
    (e.g. "intake note -> goal constraint -> cron config"). Causal-path
    semantics (Section 4 rule 5): a dependent tracks which corrections it has
    been *delivered* (:func:`deliver_correction`) and which it has
    *confirmed* consuming (:func:`confirm_dependent_update`), so a
    correction can never be marked applied out of causal order.
    """

    artifact: str  # e.g. "cron:daily-job-hunt", "GOAL.md"
    location: str  # where inside the artifact, e.g. "filters block"
    noted_at: str = ""  # ISO date/datetime
    status: DependentStatus = DependentStatus.PENDING
    confirmed_at: str = ""  # ISO date/datetime the update was confirmed
    via: str = ""  # witnessed path: how the claim reached this dependent
    delivered_correction: str | None = None  # correction id delivered, not yet confirmed
    confirmed_correction: str | None = None  # correction id last confirmed consumed

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "location": self.location,
            "noted_at": self.noted_at,
            "status": self.status.value,
            "confirmed_at": self.confirmed_at,
            "via": self.via,
            "delivered_correction": self.delivered_correction,
            "confirmed_correction": self.confirmed_correction,
        }


@dataclass(frozen=True)
class ClaimRecord:
    """A provenance-tagged claim with its full lifecycle state.

    Records are immutable snapshots; lifecycle functions return updated
    copies and keep the module registry as the source of truth, so the
    audit trail (intake -> corroborations -> waiver -> disavowal) is
    never rewritten.
    """

    id: str
    text: str
    subject: str
    source: str  # description of where the claim came from
    source_tier: SourceStatus  # type: ignore[valid-type]
    recorded_at: str  # ISO date/datetime of intake
    status: ClaimStatus
    source_root: str | None = None  # shared evidentiary root of the intake
    is_official_record: bool = False
    corroboration: tuple[Corroboration, ...] = ()
    waiver: ClaimWaiver | None = None
    disavowal: Disavowal | None = None
    supersedes: str | None = None  # id of the record this one replaces
    superseded_by: str | None = None  # id of the record replacing this one
    note: str = ""
    kind: ClaimKind = ClaimKind.REPORT  # ICD 203: report vs assumption vs judgment
    uncertainty: str = ""  # ICD 203 uncertainty expression, in the analyst's own words
    valid_until: str = ""  # ISO date/datetime; empty means no scheduled revalidation
    causal_path: tuple[str, ...] = ()  # witnessed causal path: ids of the records
    # causally before this one — the originating claim first, the immediate
    # predecessor last. Empty for records at the head of their lineage.
    # (Lamport 1978 happens-before, reified as data; Castello/Redmond/Kuper
    # 2024: the causal relationship is witnessed by this path.)

    def effective_root(self) -> str:
        """The intake source's evidentiary root."""
        return self.source_root or self.source

    def independent_roots(self) -> int:
        """Distinct evidentiary roots across intake + corroborations."""
        roots = {self.effective_root()}
        roots.update(c.effective_root() for c in self.corroboration)
        return len(roots)

    def is_stale(self) -> bool:
        """True when a scheduled revalidation date has passed.

        Claims without a valid_until never go stale; staleness only
        applies to claims that opted into step-6 revalidation.
        """
        if not self.valid_until:
            return False
        try:
            cutoff = datetime.fromisoformat(self.valid_until)
        except ValueError:
            return False
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=UTC)
        return cutoff < datetime.now(UTC)

    def causal_predecessor(self) -> str | None:
        """Id of the record this one was caused by — the witnessed path's
        last hop.

        Falls back to ``supersedes`` for records written before
        ``causal_path`` existed, so legacy correction records still resolve
        their predecessor sensibly. ``None`` for records at the head of
        their lineage (no causal predecessor).
        """
        if self.causal_path:
            return self.causal_path[-1]
        return self.supersedes

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "subject": self.subject,
            "kind": self.kind.value,
            "uncertainty": self.uncertainty,
            "valid_until": self.valid_until,
            "causal_path": list(self.causal_path),
            "causal_predecessor_id": self.causal_predecessor(),
            "source": {
                "description": self.source,
                "tier": self.source_tier.value,  # type: ignore[attr-defined]
                "recorded_at": self.recorded_at,
                "root": self.source_root,
                "is_official_record": self.is_official_record,
            },
            "status": self.status.value,
            "corroboration": [c.to_dict() for c in self.corroboration],
            "waiver": self.waiver.to_dict() if self.waiver else None,
            "disavowal": self.disavowal.to_dict() if self.disavowal else None,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "note": self.note,
        }


# Module registries: the source of truth for live claims and their
# downstream dependents. Reset with reset_claim_lifecycle() in tests.
_CLAIMS: dict[str, ClaimRecord] = {}
_DEPENDENTS: dict[str, list[Dependent]] = {}


def reset_claim_lifecycle() -> None:
    """Clear the claim, dependent, and event registries. Test/support utility."""
    _CLAIMS.clear()
    _DEPENDENTS.clear()
    _EVENTS.clear()


# ---------------------------------------------------------------------------
# Hash-chained claim-event log: causal order as data
# ---------------------------------------------------------------------------
#
# Every lifecycle transition is recorded as an event and hashed into a
# per-claim chain: each event's hash commits to its predecessor's hash,
# so the log is a tamper-evident happens-before order (Lamport, 1978)
# made auditable. Reordering, deleting, or editing an event breaks the
# chain, and verify_event_chain() reports exactly where. The chain is the
# claim's witnessed causal history — the Section 4 rule-4/5 path from
# intake to correction, reified as data rather than narrative.

_GENESIS_HASH = "GENESIS"


@dataclass(frozen=True)
class ClaimEvent:
    """One recorded lifecycle transition, hash-chained to its predecessor.

    ``event_hash`` is the SHA-256 of the canonical payload
    ``seq|timestamp|claim_id|event_type|detail|prev_hash``; ``prev_hash``
    is the previous event's ``event_hash`` for the same claim, or
    ``GENESIS`` for the claim's first event.
    """

    seq: int
    timestamp: str
    claim_id: str
    event_type: str
    detail: str
    prev_hash: str
    event_hash: str


_EVENTS: dict[str, list[ClaimEvent]] = {}


def _hash_event(
    seq: int,
    timestamp: str,
    claim_id: str,
    event_type: str,
    detail: str,
    prev_hash: str,
) -> str:
    payload = "|".join(
        (str(seq), timestamp, claim_id, event_type, detail, prev_hash)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_event(
    claim_id: str,
    event_type: str,
    detail: str = "",
    recorded_at: str = "",
) -> ClaimEvent:
    """Record a lifecycle event for a claim and hash it into the claim's chain.

    Event types: ``INTAKE``, ``CORROBORATION``, ``WAIVER``,
    ``GATE_DECISION``, ``DISAVOWAL``, ``DEPENDENT_REGISTERED``,
    ``CORRECTION_DELIVERED``, ``UPDATE_CONFIRMED``, ``REVALIDATED``.
    The lifecycle functions record their own events automatically; call
    this directly only for transitions outside those functions.
    """
    chain = _EVENTS.setdefault(claim_id, [])
    prev_hash = chain[-1].event_hash if chain else _GENESIS_HASH
    seq = len(chain) + 1
    timestamp = recorded_at or _utcnow()
    event = ClaimEvent(
        seq=seq,
        timestamp=timestamp,
        claim_id=claim_id,
        event_type=event_type,
        detail=detail,
        prev_hash=prev_hash,
        event_hash=_hash_event(
            seq, timestamp, claim_id, event_type, detail, prev_hash
        ),
    )
    chain.append(event)
    return event


def claim_events(claim_id: str) -> list[ClaimEvent]:
    """The recorded event chain for a claim, oldest first."""
    return list(_EVENTS.get(claim_id, []))


def verify_event_chain(claim_id: str) -> tuple[bool, str]:
    """Verify a claim's event chain: every hash recomputes, every link holds.

    Returns ``(True, ...)`` when the chain is intact, ``(False, reason)``
    naming the first broken link otherwise. An empty chain verifies
    ``True`` — nothing was recorded, so nothing was altered.
    """
    chain = _EVENTS.get(claim_id, [])
    prev_hash = _GENESIS_HASH
    for event in chain:
        if event.seq < 1 or event.prev_hash != prev_hash:
            return (
                False,
                (
                    f"chain broken at event {event.seq} ({event.event_type}): "
                    "prev_hash does not match the previous event's hash — "
                    "an event was reordered or removed."
                ),
            )
        recomputed = _hash_event(
            event.seq,
            event.timestamp,
            event.claim_id,
            event.event_type,
            event.detail,
            event.prev_hash,
        )
        if recomputed != event.event_hash:
            return (
                False,
                (
                    f"chain broken at event {event.seq} ({event.event_type}): "
                    "event hash does not recompute — the event was altered."
                ),
            )
        prev_hash = event.event_hash
    return True, f"chain intact: {len(chain)} event(s) verified."


def _utcnow() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _new_claim_id() -> str:
    return f"claim-{uuid.uuid4().hex[:12]}"


def _store(record: ClaimRecord) -> ClaimRecord:
    _CLAIMS[record.id] = record
    return record


def get_claim(claim_id: str) -> ClaimRecord:
    """Fetch a claim record by id; KeyError if unknown."""
    return _CLAIMS[claim_id]


def intake_claim(
    text: str,
    subject: str,
    source: str,
    source_tier: SourceStatus,  # type: ignore[valid-type]
    recorded_at: str = "",
    source_root: str | None = None,
    is_official_record: bool = False,
    note: str = "",
    kind: ClaimKind = ClaimKind.REPORT,
    uncertainty: str = "",
    valid_until: str = "",
) -> ClaimRecord:
    """Intake a claim with its provenance tag.

    Every claim enters UNVERIFIED unless its source is a tier-1 official
    record — an official record settles the question at intake, the same
    rule as verify_claim. A single self-report, however sincerely given,
    is UNVERIFIED until corroborated.
    """
    if not text.strip():
        raise ValueError("intake_claim needs non-empty claim text.")
    if not source.strip():
        raise ValueError("intake_claim needs a source description.")
    status = (
        ClaimStatus.CORROBORATED
        if source_tier is SourceStatus.SOURCE_ESTABLISHED and is_official_record
        else ClaimStatus.UNVERIFIED
    )
    record = ClaimRecord(
        id=_new_claim_id(),
        text=text,
        subject=subject,
        source=source,
        source_tier=source_tier,
        recorded_at=recorded_at or _utcnow(),
        status=status,
        source_root=source_root,
        is_official_record=is_official_record,
        note=note,
        kind=kind,
        uncertainty=uncertainty,
        valid_until=valid_until,
    )
    _store(record)
    record_event(
        record.id,
        "INTAKE",
        detail=(
            f"source={source} status={status.value} "
            f"official_record={is_official_record}"
        ),
        recorded_at=record.recorded_at,
    )
    return record


def add_corroboration(
    record: ClaimRecord,
    source: str,
    source_tier: SourceStatus,  # type: ignore[valid-type]
    root: str | None = None,
    observed_at: str = "",
    is_official_record: bool = False,
    note: str = "",
) -> ClaimRecord:
    """Add a corroborating sighting; recompute standing.

    Independence discount: sightings sharing an evidentiary root count
    once. The claim becomes CORROBORATED with two or more independent
    roots, or a single official record. Dead claims (DISAVOWED,
    SUPERSEDED) cannot be corroborated — correct them instead.
    """
    live = _CLAIMS.get(record.id, record)
    if live.status in (ClaimStatus.DISAVOWED, ClaimStatus.SUPERSEDED):
        raise ValueError(
            f"Cannot corroborate a {live.status.value} claim; "
            "correct it with disavow() instead."
        )
    if not source.strip():
        raise ValueError("add_corroboration needs a source description.")
    sighting = Corroboration(
        source=source,
        tier=source_tier,
        root=root,
        observed_at=observed_at or _utcnow(),
        is_official_record=is_official_record,
        note=note,
    )
    updated = replace(live, corroboration=live.corroboration + (sighting,))
    has_official = updated.is_official_record or any(
        c.is_official_record for c in updated.corroboration
    )
    if has_official or updated.independent_roots() >= 2:
        updated = replace(updated, status=ClaimStatus.CORROBORATED)
    updated = _store(updated)
    record_event(
        updated.id,
        "CORROBORATION",
        detail=(
            f"source={source} independent_roots={updated.independent_roots()} "
            f"status={updated.status.value}"
        ),
        recorded_at=sighting.observed_at,
    )
    return updated


def record_waiver(
    record: ClaimRecord,
    waived_by: str,
    reason: str,
    waived_at: str = "",
) -> ClaimRecord:
    """Record a named waiver accepting the risk of consequential use of
    an UNVERIFIED claim. Waivers apply only to UNVERIFIED claims; they
    are the explicit alternative to corroboration, not a shortcut
    around it."""
    live = _CLAIMS.get(record.id, record)
    if live.status is not ClaimStatus.UNVERIFIED:
        raise ValueError(
            f"Waivers apply to UNVERIFIED claims, not {live.status.value}."
        )
    if not waived_by.strip() or not reason.strip():
        raise ValueError("record_waiver needs who waived and why.")
    waiver = ClaimWaiver(
        waived_by=waived_by, reason=reason, waived_at=waived_at or _utcnow()
    )
    updated = _store(replace(live, waiver=waiver))
    record_event(
        updated.id,
        "WAIVER",
        detail=f"waived_by={waived_by} reason={reason}",
        recorded_at=waiver.waived_at,
    )
    return updated


def _gate_for_use(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
    """Decide whether a claim may drive a decision.

    ``stakes`` is "consequential" (the decision changes what the system
    does — exclusions, filters, classifications) or "low" (informational
    use). Returns (allowed, reason); the reason is the audit line.
    """
    if stakes not in ("consequential", "low"):
        raise ValueError('stakes must be "consequential" or "low".')
    live = _CLAIMS.get(record.id, record)

    if live.status is ClaimStatus.DISAVOWED:
        by = live.disavowal.disavowed_by if live.disavowal else "unknown"
        why = live.disavowal.reason if live.disavowal else "no reason recorded"
        follow = (
            f" Follow the superseding record {live.superseded_by}."
            if live.superseded_by
            else ""
        )
        return (
            False,
            f"DISAVOWED by {by}: {why}.{follow} Do not use.",
        )
    if live.status is ClaimStatus.SUPERSEDED:
        return (
            False,
            f"SUPERSEDED by record {live.superseded_by}; use that record instead.",
        )
    if live.status is ClaimStatus.CORROBORATED:
        # Playbook step 6: a corroborated claim past its revalidation date
        # is stale. Fail closed for consequential use; low-stakes use may
        # proceed with the staleness explicitly noted. Only claims that
        # opted into revalidation (valid_until set) can go stale.
        if live.is_stale():
            if stakes == "consequential":
                return (
                    False,
                    (
                        f"CORROBORATED but STALE (valid_until {live.valid_until}); "
                        "revalidate before consequential use."
                    ),
                )
            return (
                True,
                (
                    f"CORROBORATED but STALE (valid_until {live.valid_until}); "
                    "treat with the caution of an unverified claim."
                ),
            )
        return (
            True,
            (
                f"CORROBORATED across {live.independent_roots()} independent "
                "root(s); cleared for use."
            ),
        )
    # UNVERIFIED from here.
    if stakes == "consequential":
        if live.waiver is not None:
            return (
                True,
                (
                    f"UNVERIFIED, but {live.waiver.waived_by} recorded a waiver "
                    f"accepting the risk: {live.waiver.reason}."
                ),
            )
        return (
            False,
            (
                "UNVERIFIED single-source claim blocked for consequential use: "
                "corroborate it (2+ independent roots) or record an explicit "
                "waiver accepting the risk."
            ),
        )
    return (
        True,
        (
            "UNVERIFIED — low-stakes use allowed, but carry the status: "
            "do not assert as fact."
        ),
    )


class ClaimGateBlocked(Exception):
    """Raised by require_gate when a claim fails its consequential-use gate."""


def gate_for_use(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
    """Decide whether a claim may drive a decision; the decision is recorded.

    Same contract as the underlying gate: ``stakes`` is "consequential"
    or "low", returns ``(allowed, reason)``. The decision itself is hashed
    into the claim's event chain as a ``GATE_DECISION`` event, so the
    audit trail shows not only the claim's standing but every
    consequential-use decision made about it.
    """
    allowed, reason = _gate_for_use(record, stakes)
    record_event(
        record.id,
        "GATE_DECISION",
        detail=f"stakes={stakes} allowed={allowed}: {reason}",
    )
    return allowed, reason


class CausalOrderingError(Exception):
    """A correction was applied (or delivered) to a dependent out of causal order.

    Raised instead of silently marking a dependent corrected when the
    correction was never delivered to it, belongs to a different claim, or
    arrives before the correction it causally follows. The Section 4 rule-5
    guarantee: no dependent applies a correction for a claim version it
    never received.
    """


def require_gate(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
    """Enforce the consequential-use gate, raising instead of returning False.

    Returns (True, reason) when the gate passes. Raises ClaimGateBlocked
    when gate_for_use would return False, so callers cannot silently
    ignore a blocked claim.
    """
    allowed, reason = gate_for_use(record, stakes)
    if not allowed:
        raise ClaimGateBlocked(f"Claim {record.id} blocked for {stakes!r} use: {reason}")
    return True, reason


def disavow(
    record: ClaimRecord,
    disavowed_by: str,
    reason: str,
    corrected_text: str | None = None,
    disavowed_at: str = "",
) -> ClaimRecord:
    """Disavow a claim. The original record is kept, marked DISAVOWED,
    and never deleted; a new record carries the correction (or the
    withdrawal, when corrected_text is None) and links back via
    ``supersedes``. Returns the new record."""
    live = _CLAIMS.get(record.id, record)
    if live.status is ClaimStatus.DISAVOWED:
        raise ValueError("Claim is already disavowed.")
    if live.status is ClaimStatus.SUPERSEDED:
        raise ValueError("Claim was already superseded; disavow its replacement.")
    if not disavowed_by.strip() or not reason.strip():
        raise ValueError("disavow needs who disavowed and why.")
    stamp = disavowed_at or _utcnow()
    new_text = corrected_text if corrected_text is not None else live.text
    note = (
        f"Correction of {live.id}: {reason}"
        if corrected_text is not None
        else f"Withdrawal of {live.id} with no replacement: {reason}"
    )
    correction = intake_claim(
        text=new_text,
        subject=live.subject,
        source=f"disavowal correction by {disavowed_by}",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at=stamp,
        note=note,
        kind=live.kind,
        uncertainty=live.uncertainty,
        valid_until=live.valid_until,
    )
    # Section 4 rule 4: the correction event is causally after the claim it
    # corrects, and the supersedes link is the witnessed path between them.
    # The causal path extends the predecessor's own path, so chains of
    # corrections (a correction of a correction) keep the full lineage.
    correction = _store(
        replace(
            correction,
            supersedes=live.id,
            causal_path=live.causal_path + (live.id,),
        )
    )
    _store(
        replace(
            live,
            status=ClaimStatus.DISAVOWED,
            disavowal=Disavowal(
                disavowed_by=disavowed_by,
                reason=reason,
                disavowed_at=stamp,
                corrected_text=corrected_text,
            ),
            superseded_by=correction.id,
        )
    )
    record_event(
        live.id,
        "DISAVOWAL",
        detail=(
            f"disavowed_by={disavowed_by} reason={reason} "
            f"superseded_by={correction.id}"
        ),
        recorded_at=stamp,
    )
    return correction


def register_dependent(
    claim_id: str,
    artifact: str,
    location: str,
    noted_at: str = "",
    via: str = "",
) -> Dependent:
    """Register a downstream artifact/location that consumed a claim, so
    corrections know where to propagate.

    ``via`` is the witnessed path: how the claim reached this dependent
    (e.g. "intake note -> goal constraint -> cron config"). Section 4 rule 5 —
    causal relationships are witnessed by the paths information follows —
    so the registry records the path, not just the destination.
    """
    if claim_id not in _CLAIMS:
        raise ValueError(f"Unknown claim id: {claim_id}")
    if not artifact.strip() or not location.strip():
        raise ValueError("register_dependent needs an artifact and a location.")
    dependent = Dependent(
        artifact=artifact,
        location=location,
        noted_at=noted_at or _utcnow(),
        via=via,
    )
    _DEPENDENTS.setdefault(claim_id, []).append(dependent)
    record_event(
        claim_id,
        "DEPENDENT_REGISTERED",
        detail=f"artifact={artifact} location={location} via={via}",
        recorded_at=dependent.noted_at,
    )
    return dependent


def _causal_predecessor_of(correction_id: str) -> str | None:
    """The causal predecessor of a correction record (Section 4 rule 4)."""
    correction = _CLAIMS[correction_id]
    return correction.causal_predecessor()


def _check_causal_delivery(
    claim_id: str, correction_id: str, dependent: Dependent
) -> None:
    """Reject *delivering* a correction out of causal order.

    A dependent may only be delivered a correction whose causal
    predecessor is the correction it was last delivered — or the claim
    itself when nothing has been delivered yet. Delivery order is the
    causal-broadcast guarantee: no dependent receives a later correction
    before the earlier one it causally follows.
    """
    predecessor = _causal_predecessor_of(correction_id)
    if predecessor is None:
        return  # record at the head of its lineage; nothing to order against
    last_delivered = dependent.confirmed_correction or dependent.delivered_correction
    if last_delivered == predecessor:
        return  # next hop in the witnessed path: in order
    if predecessor == claim_id and last_delivered is None:
        return  # first correction for this claim: in order
    raise CausalOrderingError(
        f"Out-of-order delivery to dependent {dependent.artifact!r} / "
        f"{dependent.location!r}: correction {correction_id} causally follows "
        f"{predecessor}, but the dependent was last delivered "
        f"{last_delivered}. Deliver and confirm the predecessor first."
    )


def _check_causal_application(
    claim_id: str, correction_id: str, dependent: Dependent
) -> None:
    """Reject *applying* (confirming) a correction out of causal order.

    Marking a dependent corrected is application, not delivery: it is
    allowed only when the correction's causal predecessor is the
    correction the dependent last confirmed — or the claim itself when
    nothing has been confirmed yet. Skipping a hop in the witnessed path
    is an ordering violation, never a silent completion.
    """
    predecessor = _causal_predecessor_of(correction_id)
    if predecessor is None:
        return
    if dependent.confirmed_correction == predecessor:
        return
    if predecessor == claim_id and dependent.confirmed_correction is None:
        return
    raise CausalOrderingError(
        f"Out-of-order application for dependent {dependent.artifact!r} / "
        f"{dependent.location!r}: correction {correction_id} causally follows "
        f"{predecessor}, but the dependent last confirmed "
        f"{dependent.confirmed_correction}. Confirm the predecessor first."
    )


def deliver_correction(claim_id: str, correction_id: str) -> list[Dependent]:
    """Deliver a correction along every dependency path of a claim, in causal order.

    Section 4 rule 5 (causal broadcast in miniature): the correction is delivered
    to each registered dependent, and delivery that would arrive out of
    causal order is rejected with :class:`CausalOrderingError` instead of
    queued. Delivery is not application: the dependent is still
    PENDING until :func:`confirm_dependent_update` verifies the update
    landed. Returns the updated dependents.

    Tradecraft: alongside the causal-broadcast guarantee, this is the
    IC's recall doctrine as code — Office of the Director of National
    Intelligence (2020), *Intelligence Community Policy Memorandum
    2020-200-01: Standards and Procedures for Revised or Recalled
    Intelligence Products*: a revision/recall notice must go to *all
    recipients of the original product*. The dependents registry is the
    recipient list; delivery to every dependent is the notice.
    """
    if correction_id not in _CLAIMS:
        raise KeyError(f"Unknown correction id: {correction_id}")
    dependents = _DEPENDENTS.get(claim_id, [])
    delivered: list[Dependent] = []
    for index, dependent in enumerate(dependents):
        _check_causal_delivery(claim_id, correction_id, dependent)
        updated = replace(dependent, delivered_correction=correction_id)
        dependents[index] = updated
        delivered.append(updated)
    record_event(
        claim_id,
        "CORRECTION_DELIVERED",
        detail=(
            f"correction={correction_id} dependents={len(delivered)}"
        ),
    )
    return delivered


def propagate_correction(
    claim_id: str, *, correction_id: str | None = None
) -> list[Dependent]:
    """List every downstream artifact/location that consumed the claim
    and needs updating after a disavowal. Empty list: nothing consumed
    it, nothing to fix.

    With ``correction_id`` given, this is the delivery step of Section 4 rule 5:
    the correction is delivered to every dependent in causal order
    (see :func:`deliver_correction`), raising :class:`CausalOrderingError`
    on any ordering violation. Without it, this is the pure enumeration
    of the TMS dependents registry.

    Tradecraft: with ``correction_id``, this is ODNI's recall doctrine
    as code — ICPM-2020-200-01 (2020) requires revision/recall notices to
    reach *all recipients of the original product*; the enumerated
    dependents are those recipients (see :func:`deliver_correction`).
    """
    if correction_id is not None:
        return deliver_correction(claim_id, correction_id)
    return list(_DEPENDENTS.get(claim_id, []))


def confirm_dependent_update(
    claim_id: str,
    artifact: str,
    location: str,
    confirmed_at: str = "",
    *,
    correction_id: str | None = None,
) -> Dependent:
    """Confirm that a downstream dependent consumed a propagated correction
    (playbook step 5: propagate, then verify the update landed).

    Marks the matching dependent UPDATED; raises KeyError when no such
    dependent is registered.

    With ``correction_id`` given, this is the causal-broadcast guard (Section 4
    rule 5): the dependent is marked corrected only for a correction it
    was actually delivered (:func:`deliver_correction`), and only when
    that correction arrives in causal order — after the correction it
    causally follows. Out-of-order application raises
    :class:`CausalOrderingError` instead of being silently marked
    complete. A dependent must never be marked corrected for a claim
    version it never received.
    """
    dependents = _DEPENDENTS.get(claim_id, [])
    for index, dependent in enumerate(dependents):
        if dependent.artifact == artifact and dependent.location == location:
            if correction_id is not None:
                if correction_id not in _CLAIMS:
                    raise KeyError(f"Unknown correction id: {correction_id}")
                if dependent.delivered_correction != correction_id:
                    raise CausalOrderingError(
                        f"Dependent {artifact!r} / {location!r} was never "
                        f"delivered correction {correction_id}; refusing to "
                        "mark it corrected. Deliver the correction first."
                    )
                _check_causal_application(claim_id, correction_id, dependent)
            updated = replace(
                dependent,
                status=DependentStatus.UPDATED,
                confirmed_at=confirmed_at or _utcnow(),
                delivered_correction=(
                    None if correction_id is not None else dependent.delivered_correction
                ),
                confirmed_correction=(
                    correction_id
                    if correction_id is not None
                    else dependent.confirmed_correction
                ),
            )
            dependents[index] = updated
            record_event(
                claim_id,
                "UPDATE_CONFIRMED",
                detail=(
                    f"artifact={artifact} location={location} "
                    f"correction={correction_id}"
                ),
                recorded_at=updated.confirmed_at,
            )
            return updated
    raise KeyError(f"No dependent {artifact!r} / {location!r} registered for claim {claim_id}.")


def pending_corrections() -> list[tuple[str, Dependent]]:
    """Every (claim_id, dependent) pair still awaiting update confirmation.

    The step-5 work queue: corrections that propagated but were never
    confirmed as consumed downstream.
    """
    pending: list[tuple[str, Dependent]] = []
    for claim_id, dependents in _DEPENDENTS.items():
        for dependent in dependents:
            if dependent.status is DependentStatus.PENDING:
                pending.append((claim_id, dependent))
    return pending


def revalidate_claim(
    record: ClaimRecord,
    valid_until: str = "",
    note: str = "",
) -> ClaimRecord:
    """Re-validate a claim on schedule (playbook step 6).

    Records a fresh revalidation date and appends the note to the audit
    trail. The record itself is never rewritten: the updated copy is
    stored in the registry and returned.
    """
    live = _CLAIMS.get(record.id, record)
    updated = replace(
        live,
        note=(live.note + "\n" + note).strip() if note else live.note,
        valid_until=valid_until,
    )
    updated = _store(updated)
    record_event(
        updated.id,
        "REVALIDATED",
        detail=f"valid_until={valid_until} note={note}",
    )
    return updated
