#!/usr/bin/env python3
"""Package access to the existing reference provenance implementation."""

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any
from uuid import uuid4


def _load_reference() -> ModuleType:
    reference_path = (
        Path(__file__).parents[1] / "vesselframework_reference_v1.1_provenance_firewall.py"
    )
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
assess_maskirovka_convergence = _reference.assess_maskirovka_convergence

if TYPE_CHECKING:

    class SourceStatus(Enum):
        SOURCE_ESTABLISHED = "SOURCE-ESTABLISHED"
        FRAMEWORK_SYNTHESIS = "FRAMEWORK SYNTHESIS"
        WORKING_HYPOTHESIS = "WORKING HYPOTHESIS"
        ILLUSTRATIVE = "ILLUSTRATIVE"
else:
    SourceStatus = _reference.SourceStatus

__all__ = [
    "EvidenceItem",
    "EvidenceSet",
    "MaskirovkaAssessment",
    "MaskirovkaVariant",
    "ProvenanceRegistry",
    "ProvenanceResolution",
    "ProvenanceState",
    "SourceStatus",
    "assess_maskirovka_convergence",
]


# Claim lifecycle -------------------------------------------------------------
# This API is intentionally kept in the provenance module so existing package
# consumers share one registry and one set of gating rules.


class ClaimStatus(Enum):
    UNVERIFIED = "UNVERIFIED"
    CORROBORATED = "CORROBORATED"
    DISAVOWED = "DISAVOWED"
    SUPERSEDED = "SUPERSEDED"


class ClaimKind(Enum):
    REPORT = "REPORT"
    ASSUMPTION = "ASSUMPTION"
    JUDGMENT = "JUDGMENT"


class DependentStatus(Enum):
    PENDING = "PENDING"
    UPDATED = "UPDATED"


class ClaimGateBlocked(ValueError):
    """Raised when a claim is not eligible for a requested use."""


class CausalOrderingError(ValueError):
    """Raised when a correction is delivered or confirmed out of causal order."""


def _timestamp(value: str | None = None) -> str:
    if value:
        return value
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _as_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed_date = date.fromisoformat(value)
        return datetime(parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


@dataclass(frozen=True)
class ClaimSource:
    description: str
    tier: SourceStatus
    recorded_at: str
    root: str | None = None
    is_official_record: bool = False
    is_ai_generated: bool = False

    def __contains__(self, value: str) -> bool:
        return value in self.description

    def __str__(self) -> str:
        return self.description

    def to_dict(self) -> dict[str, object]:
        return {
            "description": self.description,
            "tier": self.tier.value,
            "recorded_at": self.recorded_at,
            "root": self.root,
            "is_official_record": self.is_official_record,
            "is_ai_generated": self.is_ai_generated,
        }


@dataclass(frozen=True)
class Corroboration:
    source: str
    tier: SourceStatus
    root: str | None = None
    observed_at: str = ""
    is_official_record: bool = False
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "tier": self.tier.value,
            "root": self.root,
            "observed_at": self.observed_at,
            "is_official_record": self.is_official_record,
            "note": self.note,
        }


@dataclass(frozen=True)
class ClaimWaiver:
    waived_by: str
    reason: str
    waived_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "waived_by": self.waived_by,
            "reason": self.reason,
            "waived_at": self.waived_at,
        }


@dataclass(frozen=True)
class Disavowal:
    disavowed_by: str
    reason: str
    disavowed_at: str
    corrected_text: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "disavowed_by": self.disavowed_by,
            "reason": self.reason,
            "disavowed_at": self.disavowed_at,
            "corrected_text": self.corrected_text,
        }


@dataclass(init=False)
class ClaimRecord:
    id: str
    text: str
    subject: str
    source: ClaimSource
    status: ClaimStatus = ClaimStatus.UNVERIFIED
    corroboration: list[Corroboration] = field(default_factory=list)
    waiver: ClaimWaiver | None = None
    disavowal: Disavowal | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    note: str = ""
    kind: ClaimKind = ClaimKind.REPORT
    uncertainty: str = ""
    valid_until: str = ""
    causal_path: tuple[str, ...] = ()

    def __init__(
        self,
        id: str,
        text: str,
        subject: str,
        source: ClaimSource | str,
        source_tier: SourceStatus | None = None,
        recorded_at: str = "",
        status: ClaimStatus = ClaimStatus.UNVERIFIED,
        corroboration: list[Corroboration] | None = None,
        waiver: ClaimWaiver | None = None,
        disavowal: Disavowal | None = None,
        supersedes: str | None = None,
        superseded_by: str | None = None,
        note: str = "",
        kind: ClaimKind = ClaimKind.REPORT,
        uncertainty: str = "",
        valid_until: str = "",
        causal_path: tuple[str, ...] = (),
    ) -> None:
        self.id = id
        self.text = text
        self.subject = subject
        if isinstance(source, ClaimSource):
            self.source = source
        elif source_tier is not None:
            self.source = ClaimSource(source, source_tier, recorded_at)
        else:
            raise ValueError("source_tier is required when source is a string")
        self.status = status
        self.corroboration = list(corroboration or [])
        self.waiver = waiver
        self.disavowal = disavowal
        self.supersedes = supersedes
        self.superseded_by = superseded_by
        self.note = note
        self.kind = kind
        self.uncertainty = uncertainty
        self.valid_until = valid_until
        self.causal_path = tuple(causal_path)

    @property
    def source_tier(self) -> SourceStatus:
        return self.source.tier

    @property
    def source_root(self) -> str | None:
        return self.source.root

    @property
    def is_official_record(self) -> bool:
        return self.source.is_official_record

    def independent_roots(self) -> int:
        roots = {self.source.root or self.source.description}
        roots.update(item.root or item.source for item in self.corroboration)
        return len(roots)

    def is_stale(self, now: datetime | None = None) -> bool:
        if not self.valid_until:
            return False
        current = now or datetime.now(UTC)
        return current >= _as_datetime(self.valid_until)

    def causal_predecessor(self) -> str | None:
        return self.causal_path[-1] if self.causal_path else self.supersedes

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "subject": self.subject,
            "source": self.source.to_dict(),
            "status": self.status.value,
            "corroboration": [item.to_dict() for item in self.corroboration],
            "waiver": self.waiver.to_dict() if self.waiver else None,
            "disavowal": self.disavowal.to_dict() if self.disavowal else None,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "note": self.note,
            "kind": self.kind.value,
            "uncertainty": self.uncertainty,
            "valid_until": self.valid_until,
            "causal_path": list(self.causal_path),
            "causal_predecessor_id": self.causal_predecessor(),
        }


@dataclass
class Dependent:
    claim_id: str
    artifact: str
    location: str
    noted_at: str
    status: DependentStatus = DependentStatus.PENDING
    confirmed_at: str = ""
    via: str = ""
    delivered_correction: str | None = None
    confirmed_correction: str | None = None
    _delivered: list[str] = field(default_factory=list, repr=False)
    _confirmed: list[str] = field(default_factory=list, repr=False)

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
class ClaimEvent:
    claim_id: str
    event_type: str
    seq: int
    timestamp: str
    detail: str
    prev_hash: str
    event_hash: str


_CLAIMS: dict[str, ClaimRecord] = {}
_DEPENDENTS: dict[str, list[Dependent]] = {}
_EVENTS: dict[str, list[ClaimEvent]] = {}


def _append_event(
    claim_id: str, event_type: str, detail: str = "", timestamp: str | None = None
) -> ClaimEvent:
    chain = _EVENTS.setdefault(claim_id, [])
    previous = chain[-1].event_hash if chain else "GENESIS"
    seq = len(chain) + 1
    stamp = _timestamp(timestamp)
    payload = {
        "claim_id": claim_id,
        "event_type": event_type,
        "seq": seq,
        "timestamp": stamp,
        "detail": detail,
        "prev_hash": previous,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    event = ClaimEvent(claim_id, event_type, seq, stamp, detail, previous, digest)
    chain.append(event)
    return event


def intake_claim(
    text: str,
    subject: str,
    source: str,
    source_tier: SourceStatus,
    *,
    recorded_at: str | None = None,
    source_root: str | None = None,
    is_official_record: bool = False,
    is_ai_generated: bool = False,
    kind: ClaimKind = ClaimKind.REPORT,
    uncertainty: str = "",
    valid_until: str = "",
    note: str = "",
) -> ClaimRecord:
    for value, label in ((text, "text"), (subject, "subject"), (source, "source")):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be non-empty")
    if not isinstance(source_tier, SourceStatus):
        raise TypeError("source_tier must be a SourceStatus")
    if is_official_record and source_tier is not SourceStatus.SOURCE_ESTABLISHED:
        raise ValueError("official records must use SOURCE_ESTABLISHED tier")
    if is_ai_generated and is_official_record:
        raise ValueError("AI-generated material cannot be an official record")
    claim_id = f"claim-{uuid4().hex}"
    stamp = _timestamp(recorded_at)
    claim_source = ClaimSource(
        source, source_tier, stamp, source_root, is_official_record, is_ai_generated
    )
    record = ClaimRecord(
        id=claim_id,
        text=text,
        subject=subject,
        source=claim_source,
        status=(
            ClaimStatus.CORROBORATED
            if is_official_record and not is_ai_generated
            else ClaimStatus.UNVERIFIED
        ),
        note=note,
        kind=kind,
        uncertainty=uncertainty,
        valid_until=valid_until,
    )
    _CLAIMS[claim_id] = record
    _DEPENDENTS[claim_id] = []
    _append_event(claim_id, "INTAKE", f"status={record.status.value}", stamp)
    return record


def get_claim(claim_id: str) -> ClaimRecord:
    try:
        return _CLAIMS[claim_id]
    except KeyError:
        raise KeyError(f"unknown claim: {claim_id}") from None


def _has_corroboration(record: ClaimRecord) -> bool:
    official = record.is_official_record or any(
        item.is_official_record for item in record.corroboration
    )
    return official or record.independent_roots() >= 2


def add_corroboration(
    record: ClaimRecord,
    *,
    source: str,
    source_tier: SourceStatus,
    root: str | None = None,
    observed_at: str = "",
    is_official_record: bool = False,
    note: str = "",
) -> ClaimRecord:
    current = get_claim(record.id)
    if current.status in (ClaimStatus.DISAVOWED, ClaimStatus.SUPERSEDED):
        raise ValueError("cannot corroborate a disavowed or superseded claim")
    if not source.strip():
        raise ValueError("corroboration source must be non-empty")
    if is_official_record and source_tier is not SourceStatus.SOURCE_ESTABLISHED:
        raise ValueError("official records must use SOURCE_ESTABLISHED tier")
    item = Corroboration(
        source, source_tier, root, _timestamp(observed_at), is_official_record, note
    )
    current.corroboration.append(item)
    if _has_corroboration(current):
        current.status = ClaimStatus.CORROBORATED
    _append_event(current.id, "CORROBORATION", f"source={source}; root={root}")
    return current


def record_waiver(
    record: ClaimRecord,
    *,
    waived_by: str,
    reason: str,
    waived_at: str | None = None,
) -> ClaimRecord:
    current = get_claim(record.id)
    if current.status is not ClaimStatus.UNVERIFIED:
        raise ValueError("waivers are only valid for unverified claims")
    if not waived_by.strip() or not reason.strip():
        raise ValueError("waiver requires a named approver and reason")
    current.waiver = ClaimWaiver(waived_by, reason, _timestamp(waived_at))
    _append_event(current.id, "WAIVER", f"waived_by={waived_by}; reason={reason}")
    return current


def gate_for_use(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
    if stakes not in ("low", "consequential"):
        raise ValueError("stakes must be 'low' or 'consequential'")
    current = get_claim(record.id)
    if current.status in (ClaimStatus.DISAVOWED, ClaimStatus.SUPERSEDED):
        allowed, reason = False, f"{current.status.value} claims cannot be used"
    elif current.is_stale():
        allowed = stakes == "low"
        reason = (
            "STALE claim allowed for low-stakes use with status attached"
            if allowed
            else "STALE claim blocked for consequential use"
        )
    elif stakes == "low":
        allowed = True
        reason = f"low-stakes use allowed with {current.status.value} status attached"
    elif current.status is ClaimStatus.CORROBORATED:
        allowed, reason = True, "CORROBORATED claim allowed for consequential use"
    elif current.waiver is not None:
        allowed, reason = True, "consequential use allowed by explicit one-use waiver"
        current.waiver = None
    else:
        allowed, reason = False, f"{current.status.value} claim blocked for consequential use"
    _append_event(current.id, "GATE_DECISION", f"stakes={stakes}; allowed={allowed}; {reason}")
    return allowed, reason


def require_gate(record: ClaimRecord, stakes: str) -> tuple[bool, str]:
    allowed, reason = gate_for_use(record, stakes)
    if not allowed:
        raise ClaimGateBlocked(f"Claim {record.id} blocked for '{stakes}' use: {reason}")
    return allowed, reason


def disavow(
    record: ClaimRecord,
    disavowed_by: str,
    reason: str,
    *,
    corrected_text: str | None = None,
    disavowed_at: str | None = None,
) -> ClaimRecord:
    original = get_claim(record.id)
    if original.status in (ClaimStatus.DISAVOWED, ClaimStatus.SUPERSEDED):
        raise ValueError("claim has already been disavowed")
    if not disavowed_by.strip() or not reason.strip():
        raise ValueError("disavowal requires a named actor and reason")
    stamp = _timestamp(disavowed_at)
    original.status = ClaimStatus.DISAVOWED
    original.disavowal = Disavowal(disavowed_by, reason, stamp, corrected_text)
    original.waiver = None
    correction_text = corrected_text or f"Withdrawal of claim: {original.text}"
    note = f"Withdrawal: {reason}" if corrected_text is None else ""
    correction = intake_claim(
        text=correction_text,
        subject=original.subject,
        source=f"Superseding correction to {original.id}",
        source_tier=SourceStatus.WORKING_HYPOTHESIS,
        recorded_at=stamp,
        kind=original.kind,
        uncertainty=original.uncertainty,
        valid_until=original.valid_until,
        note=note,
    )
    correction.supersedes = original.id
    correction.causal_path = (*original.causal_path, original.id)
    original.superseded_by = correction.id
    _append_event(
        original.id, "DISAVOWAL", f"superseded_by={correction.id}; reason={reason}", stamp
    )
    return correction


def register_dependent(
    claim_id: str,
    artifact: str,
    location: str,
    *,
    via: str = "",
) -> Dependent:
    if claim_id not in _CLAIMS:
        raise ValueError(f"unknown claim: {claim_id}")
    if not artifact.strip() or not location.strip():
        raise ValueError("dependent artifact and location must be non-empty")
    dependent = Dependent(claim_id, artifact, location, _timestamp(), via=via)
    _DEPENDENTS.setdefault(claim_id, []).append(dependent)
    _append_event(claim_id, "DEPENDENT_REGISTERED", f"artifact={artifact}; location={location}")
    return dependent


def propagate_correction(claim_id: str, *, correction_id: str | None = None) -> list[Dependent]:
    if claim_id not in _CLAIMS:
        return []
    dependents = _DEPENDENTS.get(claim_id, [])
    if correction_id is not None:
        return deliver_correction(claim_id, correction_id)
    return list(dependents)


def _correction_for_claim(claim_id: str, correction_id: str) -> ClaimRecord:
    correction = get_claim(correction_id)
    if correction.supersedes != claim_id and claim_id not in correction.causal_path:
        raise CausalOrderingError("correction does not supersede the requested claim")
    return correction


def deliver_correction(claim_id: str, correction_id: str) -> list[Dependent]:
    dependents = _DEPENDENTS.get(claim_id)
    if dependents is None:
        raise KeyError(f"unknown claim: {claim_id}")
    correction = _correction_for_claim(claim_id, correction_id)
    causal_ancestors = correction.causal_path[1:]
    for dependent in dependents:
        if any(ancestor not in dependent._delivered for ancestor in causal_ancestors):
            raise CausalOrderingError(f"Out-of-order correction delivery: {correction_id}")
    for dependent in dependents:
        if correction_id not in dependent._delivered:
            dependent._delivered.append(correction_id)
            dependent.delivered_correction = correction_id
            dependent.status = DependentStatus.PENDING
            _append_event(claim_id, "CORRECTION_DELIVERED", f"correction_id={correction_id}")
    return list(dependents)


def confirm_dependent_update(
    claim_id: str,
    artifact: str,
    location: str,
    *,
    correction_id: str | None = None,
    confirmed_at: str | None = None,
) -> Dependent:
    dependents = _DEPENDENTS.get(claim_id)
    if dependents is None:
        raise KeyError(f"unknown claim: {claim_id}")
    dependent = next(
        (item for item in dependents if item.artifact == artifact and item.location == location),
        None,
    )
    if dependent is None:
        raise KeyError(f"unknown dependent: {artifact} ({location})")
    if correction_id is not None:
        correction = _correction_for_claim(claim_id, correction_id)
        if correction_id not in dependent._delivered:
            raise CausalOrderingError("correction was never delivered to this dependent")
        if any(ancestor not in dependent._confirmed for ancestor in correction.causal_path[1:]):
            raise CausalOrderingError("confirm causal predecessor corrections first")
        if correction_id not in dependent._confirmed:
            dependent._confirmed.append(correction_id)
        dependent.confirmed_correction = correction_id
    else:
        dependent.confirmed_correction = None
    dependent.delivered_correction = None
    dependent.confirmed_at = _timestamp(confirmed_at)
    dependent.status = DependentStatus.UPDATED
    _append_event(claim_id, "UPDATE_CONFIRMED", f"correction_id={correction_id}")
    return dependent


def pending_corrections() -> list[Dependent]:
    return [
        dependent
        for dependents in _DEPENDENTS.values()
        for dependent in dependents
        if dependent.status is DependentStatus.PENDING
    ]


def record_event(claim_id: str, event_type: str, *, detail: str = "") -> ClaimEvent:
    if claim_id not in _CLAIMS:
        raise KeyError(f"unknown claim: {claim_id}")
    if not event_type.strip():
        raise ValueError("event_type must be non-empty")
    return _append_event(claim_id, event_type, detail)


def claim_events(claim_id: str) -> list[ClaimEvent]:
    return list(_EVENTS.get(claim_id, []))


def verify_event_chain(claim_id: str) -> tuple[bool, str]:
    chain = _EVENTS.get(claim_id, [])
    previous = "GENESIS"
    if not chain:
        return True, "0 event(s)"
    for index, event in enumerate(chain, start=1):
        if event.seq != index or event.prev_hash != previous:
            return False, "events were reordered or removed"
        payload = {
            "claim_id": event.claim_id,
            "event_type": event.event_type,
            "seq": event.seq,
            "timestamp": event.timestamp,
            "detail": event.detail,
            "prev_hash": event.prev_hash,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if digest != event.event_hash:
            return False, "event altered"
        previous = event.event_hash
    return True, f"{len(chain)} event(s) verified"


def revalidate_claim(record: ClaimRecord, *, valid_until: str, note: str = "") -> ClaimRecord:
    current = get_claim(record.id)
    if current.status is not ClaimStatus.CORROBORATED:
        raise ValueError("only corroborated claims can be revalidated")
    if not valid_until:
        raise ValueError("valid_until is required")
    _as_datetime(valid_until)
    current.valid_until = valid_until
    if note:
        current.note = "; ".join(part for part in (current.note, note) if part)
    _append_event(current.id, "REVALIDATED", f"valid_until={valid_until}; note={note}")
    return current


def reset_claim_lifecycle() -> None:
    _CLAIMS.clear()
    _DEPENDENTS.clear()
    _EVENTS.clear()


__all__ += [
    "CausalOrderingError",
    "ClaimGateBlocked",
    "ClaimKind",
    "ClaimRecord",
    "ClaimStatus",
    "Dependent",
    "DependentStatus",
    "add_corroboration",
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
