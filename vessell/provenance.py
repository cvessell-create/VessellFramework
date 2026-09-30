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
    "ClaimRecord",
    "ClaimStatus",
    "ClaimWaiver",
    "Corroboration",
    "Dependent",
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
    "disavow",
    "gate_for_use",
    "intake_claim",
    "propagate_correction",
    "record_waiver",
    "register_dependent",
    "reset_claim_lifecycle",
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
    updated when the claim is corrected."""

    artifact: str  # e.g. "cron:daily-job-hunt", "GOAL.md"
    location: str  # where inside the artifact, e.g. "filters block"
    noted_at: str = ""  # ISO date/datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact": self.artifact,
            "location": self.location,
            "noted_at": self.noted_at,
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

    def effective_root(self) -> str:
        """The intake source's evidentiary root."""
        return self.source_root or self.source

    def independent_roots(self) -> int:
        """Distinct evidentiary roots across intake + corroborations."""
        roots = {self.effective_root()}
        roots.update(c.effective_root() for c in self.corroboration)
        return len(roots)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "subject": self.subject,
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
    """Clear the claim and dependent registries. Test/support utility."""
    _CLAIMS.clear()
    _DEPENDENTS.clear()


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
    return _store(
        ClaimRecord(
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
        )
    )


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
    return _store(updated)


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
    return _store(
        replace(
            live,
            waiver=ClaimWaiver(
                waived_by=waived_by, reason=reason, waived_at=waived_at or _utcnow()
            ),
        )
    )


def gate_for_use(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
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
    )
    correction = _store(replace(correction, supersedes=live.id))
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
    return correction


def register_dependent(
    claim_id: str,
    artifact: str,
    location: str,
    noted_at: str = "",
) -> Dependent:
    """Register a downstream artifact/location that consumed a claim, so
    corrections know where to propagate."""
    if claim_id not in _CLAIMS:
        raise ValueError(f"Unknown claim id: {claim_id}")
    if not artifact.strip() or not location.strip():
        raise ValueError("register_dependent needs an artifact and a location.")
    dependent = Dependent(
        artifact=artifact, location=location, noted_at=noted_at or _utcnow()
    )
    _DEPENDENTS.setdefault(claim_id, []).append(dependent)
    return dependent


def propagate_correction(claim_id: str) -> list[Dependent]:
    """List every downstream artifact/location that consumed the claim
    and needs updating after a disavowal. Empty list: nothing consumed
    it, nothing to fix."""
    return list(_DEPENDENTS.get(claim_id, []))
