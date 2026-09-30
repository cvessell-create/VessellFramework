# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Claim verification: planted-news checks and ghost-job filtering.

Doctrine
--------
A claim is only as strong as its *independent* corroboration. This module
implements the verification pass first used in the evening news editions:

1. **Planted-news check** (:func:`verify_claim`). A claim (e.g. "M4.2 quake
   near Wauna, WA") is tested against sightings across sources. Each
   sighting carries a :class:`~vessell.provenance.SourceStatus` tier, and
   the corroboration score reuses the framework's calibrated tier weights
   (:data:`~vessell.weights.SOURCE_TIER_WEIGHTS`) with the independence
   discount for sightings that share an evidentiary root (the same wire
   copy on ten sites is one root, not ten). An official record — a USGS
   event page, an employer's own careers listing — settles the question;
   aggregator-only sightings never do.

2. **Ghost-job filtering** (:func:`filter_ghost_jobs`). A posting whose
   identical text circulates across aggregators under multiple listing
   IDs, whose claimed "posted N days ago" contradicts its first-seen
   date, is the ghost-job pattern: a listing kept alive without hiring
   intent. The detector surfaces the signals; the filter drops
   ``LIKELY_GHOST`` roles from a candidate set.

3. **Planted-news intelligence** (:func:`analyze_planted_news`). Full
   hostile-spread analysis: synchronized low-tier publish bursts,
   text-clone armies, single-origin laundering chains, orphaned
   circulation with no primary source, and established denial. Built
   for the question "is this story manufactured?" — answered
   deterministically, with every indicator carrying its evidence.

Both paths return auditable records: every verdict carries its rationale
and the raw signals stay visible. Verification informs; the analyst (or
the calling pipeline) decides.

4. **Search-path provenance for negative findings**
   (:func:`record_search_path`, :func:`gate_negative_finding`). A negative
   existential ("no X exists") is a claim like any other: it enters
   UNVERIFIED and may not be reported/operationalized as a finding until
   at least two independent search paths corroborate the absence — with
   every attempted path recorded as the claim's provenance. The analyst's
   own search history is the witnessed path (§4 rule 5: causal
   relationships are witnessed by the paths information follows; a
   one-path absence claim is an unwitnessed edge).

   Worked example (§6 of the case study): on 2026-09-30 the analyst
   searched arXiv for the literal string "Jonathan Castillo", found
   nothing, and reported no such author — operationalizing a negative
   finding off a single unwitnessed path. The paper was there all along:
   "Inductive Diagrams for Causal Reasoning" by Jonathan **Castello**,
   Patrick Redmond, and Lindsey **Kuper** (arXiv:2307.10484) — one letter
   off on both names. The paths never walked: spelling variants,
   co-author cross-check ("Redmond" + "Kuper"), title-keyword search.
   Under this gate the absence stays UNVERIFIED and unreportable until a
   second independent path corroborates it; a path that finds the target
   contradicts the absence outright.
"""

from __future__ import annotations

import difflib
import hashlib
import re
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any

from vessell.provenance import (
    ClaimGateBlocked,
    ClaimKind,
    ClaimRecord,
    SourceStatus,
    add_corroboration,
    get_claim,
    intake_claim,
    register_dependent,
    require_gate,
)
from vessell.weights import SOURCE_TIER_WEIGHTS

__all__ = [
    "BURST_MIN_SOURCES",
    "BURST_WINDOW_MINUTES",
    "CLONE_ARMY_MIN_SOURCES",
    "MIN_ABSENCE_PATHS",
    "NEAR_DUPLICATE_THRESHOLD",
    "ClaimCheck",
    "GhostJobReport",
    "GhostVerdict",
    "JobPosting",
    "PlantedNewsReport",
    "PlantedVerdict",
    "SearchPath",
    "SourceSighting",
    "Verdict",
    "VerificationResult",
    "analyze_planted_news",
    "analyze_planted_news_and_record",
    "detect_ghost_job",
    "detect_ghost_job_and_record",
    "filter_ghost_jobs",
    "gate_negative_finding",
    "group_postings_by_role",
    "record_search_path",
    "require_negative_finding",
    "reset_search_paths",
    "search_paths",
    "verify_and_record",
    "verify_claim",
]


# ---------------------------------------------------------------------------
# Planted-news check
# ---------------------------------------------------------------------------


class Verdict(Enum):
    """Standing of a claim after the corroboration pass."""

    VERIFIED = "VERIFIED"  # official record, or >=2 established independent roots
    CORROBORATED = "CORROBORATED"  # multiple independent roots, none official
    SINGLE_SOURCE = "SINGLE_SOURCE"  # exactly one sighting
    UNCORROBORATED = "UNCORROBORATED"  # no sightings, or only low-tier echoes
    CONTRADICTED = "CONTRADICTED"  # an established source denies the claim


@dataclass(frozen=True)
class SourceSighting:
    """One place a claim was seen (or denied)."""

    source_name: str
    tier: SourceStatus
    url: str = ""
    seen_at: str = ""  # ISO date/datetime, when the sighting was observed
    published_at: str = ""  # ISO date/datetime the source claims as publish time
    text: str = ""  # excerpt of the item's wording, for clone detection
    root: str | None = None  # shared evidentiary root, e.g. "ap-wire"
    denies: bool = False  # this sighting contradicts the claim
    is_official_record: bool = False  # authoritative record (USGS event page, ...)
    note: str = ""

    def effective_root(self) -> str:
        """Sightings sharing a root are one evidentiary ancestor."""
        return self.root or self.source_name

    def to_corroboration(self) -> dict[str, Any]:
        """Render this sighting as ``add_corroboration`` keyword arguments,
        so a verification pass can record its evidence on the claim."""
        return {
            "source": self.source_name,
            "source_tier": self.tier,
            "root": self.root,
            "observed_at": self.seen_at,
            "is_official_record": self.is_official_record,
            "note": self.note,
        }


@dataclass(frozen=True)
class ClaimCheck:
    """A claim plus every sighting gathered for it."""

    claim: str
    sightings: tuple[SourceSighting, ...] = ()


@dataclass(frozen=True)
class VerificationResult:
    """Verdict on a claim, with the audit trail attached."""

    claim: str
    verdict: Verdict
    corroboration_score: float  # 0..1, tier-weighted, independence-discounted
    independent_roots: int
    official_record: bool
    rationale: str
    signals: tuple[str, ...] = ()
    claim_id: str = ""  # provenance claim id, set by verify_and_record

    def to_dict(self) -> dict[str, object]:
        return {
            "claim": self.claim,
            "verdict": self.verdict.value,
            "corroboration_score": round(self.corroboration_score, 4),
            "independent_roots": self.independent_roots,
            "official_record": self.official_record,
            "rationale": self.rationale,
            "signals": list(self.signals),
            "claim_id": self.claim_id,
        }


def verify_claim(check: ClaimCheck) -> VerificationResult:
    """Run the planted-news check on a claim.

    Rule order: official record first, then established denial, then root
    counting. The corroboration score is the tier-weighted count of
    independent affirming roots, scaled so two established roots score 1.0.
    """
    sightings = [s for s in check.sightings if not s.denies]
    denials = [s for s in check.sightings if s.denies]

    if not check.sightings:
        return VerificationResult(
            claim=check.claim,
            verdict=Verdict.UNCORROBORATED,
            corroboration_score=0.0,
            independent_roots=0,
            official_record=False,
            rationale="No sightings gathered; nothing corroborates the claim.",
        )

    official = [s for s in sightings if s.is_official_record]
    if official:
        names = ", ".join(s.source_name for s in official)
        return VerificationResult(
            claim=check.claim,
            verdict=Verdict.VERIFIED,
            corroboration_score=1.0,
            independent_roots=len({s.effective_root() for s in sightings}),
            official_record=True,
            rationale=f"Official record affirms the claim: {names}.",
            signals=tuple(_signal_line(s) for s in check.sightings),
        )

    established_denials = [
        s for s in denials if s.tier is SourceStatus.SOURCE_ESTABLISHED
    ]
    if established_denials:
        names = ", ".join(s.source_name for s in established_denials)
        return VerificationResult(
            claim=check.claim,
            verdict=Verdict.CONTRADICTED,
            corroboration_score=0.0,
            independent_roots=len({s.effective_root() for s in sightings}),
            official_record=False,
            rationale=f"Established source(s) deny the claim: {names}.",
            signals=tuple(_signal_line(s) for s in check.sightings),
        )

    # Independence discount: one root counts once, at its strongest tier.
    best_per_root: dict[str, float] = {}
    for sighting in sightings:
        weight = SOURCE_TIER_WEIGHTS[sighting.tier]
        root = sighting.effective_root()
        best_per_root[root] = max(best_per_root.get(root, 0.0), weight)

    weighted_roots = sum(best_per_root.values())
    established_roots = len(
        {
            s.effective_root()
            for s in sightings
            if s.tier is SourceStatus.SOURCE_ESTABLISHED
        }
    )
    score = min(1.0, weighted_roots / 2.0)

    if established_roots >= 2:
        verdict = Verdict.VERIFIED
        rationale = (
            f"{established_roots} independent established roots affirm the "
            "claim; treated as verified."
        )
    elif len(check.sightings) == 1:
        verdict = Verdict.SINGLE_SOURCE
        rationale = "Exactly one sighting; single-threaded until corroborated."
    elif score >= 0.6:
        verdict = Verdict.CORROBORATED
        rationale = (
            f"Corroboration score {score:.2f} across "
            f"{len(best_per_root)} independent root(s); no official record."
        )
    else:
        verdict = Verdict.UNCORROBORATED
        rationale = (
            f"Corroboration score {score:.2f}: only low-tier or shared-root "
            "sightings; insufficient to affirm."
        )

    return VerificationResult(
        claim=check.claim,
        verdict=verdict,
        corroboration_score=score,
        independent_roots=len(best_per_root),
        official_record=False,
        rationale=rationale,
        signals=tuple(_signal_line(s) for s in check.sightings),
    )


def verify_and_record(
    check: ClaimCheck,
    subject: str = "",
    *,
    kind: ClaimKind = ClaimKind.REPORT,
) -> tuple[VerificationResult, ClaimRecord]:
    """Run :func:`verify_claim` and intake the outcome as a provenance claim.

    The recorded claim is the *verification outcome* ("claim X came back
    VERIFIED/CONTRADICTED ..."), with every sighting attached as a
    corroboration via :meth:`SourceSighting.to_corroboration`. The claim's
    evidentiary root is anchored in the sightings — the analyzer records
    the outcome but does not count as evidence for it, so a single
    sighting cannot corroborate by itself. A VERIFIED outcome backed by an
    official record (or 2+ independent roots) is CORROBORATED and passes
    the consequential-use gate for acting on the outcome; weaker outcomes
    stay UNVERIFIED and are blocked until corroborated or explicitly
    waived. The result carries the claim id.
    """
    result = verify_claim(check)
    sighting_roots = [s.effective_root() for s in check.sightings]
    record = intake_claim(
        text=(
            f"Verification of {check.claim!r}: {result.verdict.value} — "
            f"{result.rationale}"
        ),
        subject=subject or check.claim,
        source="vessell.verify.verify_claim",
        source_tier=SourceStatus.FRAMEWORK_SYNTHESIS,
        source_root=sighting_roots[0] if sighting_roots else None,
        kind=kind,
        note=f"{result.independent_roots} independent root(s); score {result.corroboration_score:.2f}",
    )
    for sighting in check.sightings:
        record = add_corroboration(record, **sighting.to_corroboration())
    register_dependent(
        record.id,
        artifact="vessell.verify.VerificationResult",
        location=subject or check.claim,
    )
    return replace(result, claim_id=record.id), record


def _signal_line(sighting: SourceSighting) -> str:
    stance = "denies" if sighting.denies else "affirms"
    official = ", official record" if sighting.is_official_record else ""
    note = f" — {sighting.note}" if sighting.note else ""
    return (
        f"{sighting.source_name} ({sighting.tier.value}{official}) "
        f"{stance}{note}"
    )


# ---------------------------------------------------------------------------
# Planted-news intelligence
# ---------------------------------------------------------------------------

LOW_TIERS = frozenset({SourceStatus.WORKING_HYPOTHESIS, SourceStatus.ILLUSTRATIVE})
BURST_WINDOW_MINUTES = 90  # synchronized-publish window
BURST_MIN_SOURCES = 4  # low-tier outlets inside one window
CLONE_ARMY_MIN_SOURCES = 5  # distinct sources, near-identical text

_HOSTILE_INDICATORS = frozenset(
    {
        "established-denial",
        "synchronized-burst",
        "no-primary-source",
        "single-origin-laundering",
        "text-clone-army",
    }
)


class PlantedVerdict(Enum):
    """Standing of a claim after the hostile-spread analysis."""

    AUTHENTIC = "AUTHENTIC"  # official record, or clean corroboration
    LIKELY_PLANTED = "LIKELY_PLANTED"  # manufactured: denial or 2+ hostile indicators
    SUSPECT = "SUSPECT"  # one hostile indicator; verify against a primary source
    UNVERIFIABLE = "UNVERIFIABLE"  # insufficient evidence either way


@dataclass(frozen=True)
class PlantedNewsReport:
    """Hostile-spread analysis for one claim, with the audit trail attached."""

    claim: str
    verdict: PlantedVerdict
    rationale: str
    indicators: tuple[str, ...]  # machine-readable indicator codes
    signals: tuple[str, ...]  # human-readable evidence lines
    burst_detected: bool
    orphaned: bool  # circulating with no primary source behind it
    single_origin: bool  # every sighting traces to one low root
    clone_army_size: int  # largest near-identical-text group, distinct sources
    corroboration: VerificationResult  # the base planted-news check, embedded
    claim_id: str = ""  # provenance claim id, set by analyze_planted_news_and_record

    def to_dict(self) -> dict[str, object]:
        return {
            "claim": self.claim,
            "verdict": self.verdict.value,
            "rationale": self.rationale,
            "indicators": list(self.indicators),
            "signals": list(self.signals),
            "burst_detected": self.burst_detected,
            "orphaned": self.orphaned,
            "single_origin": self.single_origin,
            "clone_army_size": self.clone_army_size,
            "corroboration": self.corroboration.to_dict(),
            "claim_id": self.claim_id,
        }


def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def _detect_synchronized_burst(
    sightings: list[SourceSighting],
) -> tuple[bool, int]:
    """Coordinated-push signature: >=BURST_MIN_SOURCES low-tier outlets
    publishing near-identical text inside a BURST_WINDOW_MINUTES window."""
    timed = [
        (published, sighting)
        for sighting in sightings
        if sighting.tier in LOW_TIERS
        and (published := _parse_datetime(sighting.published_at)) is not None
        and sighting.text.strip()
    ]
    timed.sort(key=lambda pair: pair[0])
    best = 0
    window_seconds = BURST_WINDOW_MINUTES * 60
    for start in range(len(timed)):
        window = [
            sighting
            for published, sighting in timed
            if 0 <= (published - timed[start][0]).total_seconds() <= window_seconds
        ]
        if len({s.source_name for s in window}) < BURST_MIN_SOURCES:
            continue
        groups = _cluster_near_duplicate_texts([s.text for s in window])
        for group in groups:
            best = max(best, len({window[i].source_name for i in group}))
    return best >= BURST_MIN_SOURCES, best


def analyze_planted_news(check: ClaimCheck) -> PlantedNewsReport:
    """Full-blast planted-news analysis on a claim.

    Runs the base corroboration check, then hunts hostile-spread
    indicators: synchronized low-tier bursts, text-clone armies,
    single-origin laundering, orphaned circulation, and established
    denial. Verdicts are deterministic and every indicator ships with
    its evidence line.
    """
    base = verify_claim(check)
    affirming = [s for s in check.sightings if not s.denies]
    denials = [s for s in check.sightings if s.denies]

    indicators: list[str] = []
    signals: list[str] = []

    official = [s for s in affirming if s.is_official_record]
    if official:
        indicators.append("official-record")
        signals.append(
            "Official record affirms: "
            + ", ".join(s.source_name for s in official)
            + "."
        )

    established_denials = [
        s for s in denials if s.tier is SourceStatus.SOURCE_ESTABLISHED
    ]
    if established_denials:
        indicators.append("established-denial")
        signals.append(
            "Established source(s) deny the claim: "
            + ", ".join(s.source_name for s in established_denials)
            + "."
        )

    burst_detected, burst_size = _detect_synchronized_burst(affirming)
    if burst_detected:
        indicators.append("synchronized-burst")
        signals.append(
            f"{burst_size} low-tier outlets published near-identical text "
            f"inside a {BURST_WINDOW_MINUTES}-minute window: coordinated push."
        )

    has_primary = bool(official) or any(
        s.tier is SourceStatus.SOURCE_ESTABLISHED for s in affirming
    )
    orphaned = bool(affirming) and not has_primary
    if orphaned:
        indicators.append("no-primary-source")
        signals.append(
            "Claim circulates with no official record and no established "
            "outlet behind it: orphaned."
        )

    roots = {s.effective_root() for s in affirming}
    single_origin = bool(affirming) and len(roots) == 1 and not has_primary
    if single_origin:
        indicators.append("single-origin-laundering")
        signals.append(
            f"Every sighting traces to one non-established root "
            f"({next(iter(roots))}): laundering chain, not corroboration."
        )

    texted = [(s.source_name, s.text) for s in affirming if s.text.strip()]
    clone_army_size = 0
    if texted:
        groups = _cluster_near_duplicate_texts([text for _, text in texted])
        for group in groups:
            clone_army_size = max(
                clone_army_size, len({texted[i][0] for i in group})
            )
    if clone_army_size >= CLONE_ARMY_MIN_SOURCES:
        indicators.append("text-clone-army")
        signals.append(
            f"{clone_army_size} distinct sources carry near-identical wording: "
            "clone army, not independent reporting."
        )

    hostile = [i for i in indicators if i in _HOSTILE_INDICATORS]

    if official:
        verdict = PlantedVerdict.AUTHENTIC
        rationale = (
            "Official record affirms the claim; spread pattern is "
            "distribution, not manufacture."
        )
    elif established_denials:
        verdict = PlantedVerdict.LIKELY_PLANTED
        rationale = (
            "Established source(s) deny a claim no official record supports: "
            "manufactured."
        )
    elif len(hostile) >= 2:
        verdict = PlantedVerdict.LIKELY_PLANTED
        rationale = (
            f"{len(hostile)} hostile indicators ({', '.join(hostile)}): "
            "coordinated or manufactured spread."
        )
    elif len(hostile) == 1:
        verdict = PlantedVerdict.SUSPECT
        rationale = (
            f"One hostile indicator ({hostile[0]}); verify against a "
            "primary source before repeating the claim."
        )
    elif base.verdict in (Verdict.VERIFIED, Verdict.CORROBORATED):
        verdict = PlantedVerdict.AUTHENTIC
        rationale = (
            "Independently corroborated with no hostile spread indicators."
        )
    elif not check.sightings:
        verdict = PlantedVerdict.UNVERIFIABLE
        rationale = "No sightings gathered; nothing to judge."
    else:
        verdict = PlantedVerdict.UNVERIFIABLE
        rationale = "Insufficient evidence either way; do not assert."

    return PlantedNewsReport(
        claim=check.claim,
        verdict=verdict,
        rationale=rationale,
        indicators=tuple(indicators),
        signals=tuple(signals),
        burst_detected=burst_detected,
        orphaned=orphaned,
        single_origin=single_origin,
        clone_army_size=clone_army_size,
        corroboration=base,
    )


def analyze_planted_news_and_record(
    check: ClaimCheck,
    subject: str = "",
    *,
    kind: ClaimKind = ClaimKind.JUDGMENT,
) -> tuple[PlantedNewsReport, ClaimRecord]:
    """Run :func:`analyze_planted_news` and intake the outcome as a claim.

    The hostile-spread analysis is a framework judgment, so the claim is
    intaked as a JUDGMENT sourced to the analyzer; every sighting becomes
    a corroboration, with the claim's root anchored in the sightings (the
    analyzer does not count as evidence for its own outcome). A
    LIKELY_PLANTED or AUTHENTIC outcome backed by 2+ independent roots
    (or an official record) is CORROBORATED and passes the
    consequential-use gate for acting on the outcome (e.g. dropping the
    claim from an edition); anything weaker stays gated. The report
    carries the claim id.
    """
    report = analyze_planted_news(check)
    sighting_roots = [s.effective_root() for s in check.sightings]
    record = intake_claim(
        text=(
            f"Planted-news analysis of {check.claim!r}: {report.verdict.value} "
            f"— {report.rationale}"
        ),
        subject=subject or check.claim,
        source="vessell.verify.analyze_planted_news",
        source_tier=SourceStatus.FRAMEWORK_SYNTHESIS,
        source_root=sighting_roots[0] if sighting_roots else None,
        kind=kind,
        note=f"indicators: {', '.join(report.indicators) or 'none'}",
    )
    for sighting in check.sightings:
        record = add_corroboration(record, **sighting.to_corroboration())
    register_dependent(
        record.id,
        artifact="vessell.verify.PlantedNewsReport",
        location=subject or check.claim,
    )
    return replace(report, claim_id=record.id), record


# ---------------------------------------------------------------------------
# Ghost-job detection and filtering
# ---------------------------------------------------------------------------

NEAR_DUPLICATE_THRESHOLD = 0.92  # difflib ratio for aggregator-tweaked reposts
GHOST_MIN_SOURCES = 3  # identical text across this many distinct sources
GHOST_MIN_LISTING_IDS = 3  # same text under this many listing IDs
GHOST_MIN_CIRCULATION_DAYS = 60  # text circulating this long
GHOST_MIN_FRESHNESS_GAP_DAYS = 30  # claimed-posted vs first-seen gap


class GhostVerdict(Enum):
    """Standing of a job role's postings after the ghost-job pass."""

    LIKELY_GHOST = "LIKELY_GHOST"  # 3+ ghost signals
    SUSPECT = "SUSPECT"  # 1-2 ghost signals
    NO_SIGNAL = "NO_SIGNAL"  # no ghost pattern detected


@dataclass(frozen=True)
class JobPosting:
    """One sighting of a job posting."""

    title: str
    employer: str
    location: str
    description_text: str
    salary_text: str = ""
    source: str = ""  # aggregator or the employer's own site
    listing_id: str = ""
    claimed_posted: str = ""  # ISO date the source claims it was posted
    first_seen: str = ""  # ISO date this text was first observed
    url: str = ""

    def role_key(self) -> tuple[str, str, str]:
        """Normalized (employer, title, location): what counts as one role."""
        return (
            _normalize_text(self.employer),
            _normalize_text(self.title),
            _normalize_text(self.location),
        )


@dataclass(frozen=True)
class GhostJobReport:
    """Ghost-job verdict for one role, with the raw signals attached."""

    title: str
    employer: str
    location: str
    verdict: GhostVerdict
    rationale: str
    signals: tuple[str, ...] = ()
    text_groups: int = 0  # distinct posting-text groups observed
    largest_group_size: int = 0
    distinct_sources: int = 0
    distinct_listing_ids: int = 0
    circulation_days: int | None = None
    freshness_gap_days: int | None = None
    claim_id: str = ""  # provenance claim id, set by detect_ghost_job_and_record

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "employer": self.employer,
            "location": self.location,
            "verdict": self.verdict.value,
            "rationale": self.rationale,
            "signals": list(self.signals),
            "claim_id": self.claim_id,
            "text_groups": self.text_groups,
            "largest_group_size": self.largest_group_size,
            "distinct_sources": self.distinct_sources,
            "distinct_listing_ids": self.distinct_listing_ids,
            "circulation_days": self.circulation_days,
            "freshness_gap_days": self.freshness_gap_days,
        }


def _normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace: for text matching."""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _text_fingerprint(text: str) -> str:
    return hashlib.sha256(_normalize_text(text).encode("utf-8")).hexdigest()


def _cluster_near_duplicate_texts(texts: list[str]) -> list[list[int]]:
    """Cluster indexes by identical or near-identical text.

    Exact matches group by fingerprint; near matches (aggregators tweak
    boilerplate, IO shops spin wording) merge by difflib ratio at
    NEAR_DUPLICATE_THRESHOLD.
    """
    normalized = [_normalize_text(t) for t in texts]
    groups: list[list[int]] = []
    for index, text in enumerate(normalized):
        if not text:
            continue
        placed = False
        for group in groups:
            if difflib.SequenceMatcher(
                None, text, normalized[group[0]]
            ).ratio() >= NEAR_DUPLICATE_THRESHOLD:
                group.append(index)
                placed = True
                break
        if not placed:
            groups.append([index])
    return groups


def _group_near_duplicate_texts(postings: list[JobPosting]) -> list[list[int]]:
    return _cluster_near_duplicate_texts([p.description_text for p in postings])


def _parse_iso_day(value: str) -> date | None:
    try:
        return date.fromisoformat(value.strip()[:10])
    except (ValueError, AttributeError):
        return None


def group_postings_by_role(
    postings: list[JobPosting],
) -> dict[tuple[str, str, str], list[JobPosting]]:
    """Group sightings by normalized (employer, title, location)."""
    grouped: dict[tuple[str, str, str], list[JobPosting]] = {}
    for posting in postings:
        grouped.setdefault(posting.role_key(), []).append(posting)
    return grouped


def detect_ghost_job(postings: list[JobPosting]) -> GhostJobReport:
    """Judge one role's postings for the ghost-job pattern.

    ``postings`` should already be one role (see :func:`group_postings_by_role`).
    A single sighting cannot be judged — there is nothing to compare it to.
    """
    if not postings:
        raise ValueError("detect_ghost_job needs at least one posting.")
    first = postings[0]

    groups = _group_near_duplicate_texts(postings)
    largest = max(groups, key=len)
    member_postings = [postings[i] for i in largest]
    distinct_sources = {p.source for p in member_postings if p.source}
    distinct_ids = {p.listing_id for p in member_postings if p.listing_id}

    seen = [_parse_iso_day(p.first_seen) for p in member_postings]
    seen_dates = [d for d in seen if d is not None]
    circulation_days: int | None = None
    if len(seen_dates) >= 2:
        circulation_days = (max(seen_dates) - min(seen_dates)).days

    freshness_gap_days: int | None = None
    claimed = [_parse_iso_day(p.claimed_posted) for p in member_postings]
    claimed_dates = [d for d in claimed if d is not None]
    if claimed_dates and seen_dates:
        # A repost masked as fresh: claimed posted date is later than the
        # earliest real observation of the same text.
        freshness_gap_days = (max(claimed_dates) - min(seen_dates)).days

    signals: list[str] = []
    if len(distinct_sources) >= GHOST_MIN_SOURCES:
        signals.append(
            f"Identical posting text on {len(distinct_sources)} distinct "
            f"sources: {', '.join(sorted(distinct_sources))}."
        )
    if len(distinct_ids) >= GHOST_MIN_LISTING_IDS:
        signals.append(
            f"Same text reposted under {len(distinct_ids)} distinct listing IDs."
        )
    if circulation_days is not None and circulation_days >= GHOST_MIN_CIRCULATION_DAYS:
        signals.append(
            f"Identical text circulating for {circulation_days} days."
        )
    if (
        freshness_gap_days is not None
        and freshness_gap_days >= GHOST_MIN_FRESHNESS_GAP_DAYS
    ):
        signals.append(
            f"Claimed posted date is {freshness_gap_days} days later than the "
            "first observation of the same text — repost masked as fresh."
        )

    if len(postings) == 1:
        verdict = GhostVerdict.NO_SIGNAL
        rationale = "Single sighting; nothing to compare it against."
    elif len(signals) >= 3:
        verdict = GhostVerdict.LIKELY_GHOST
        rationale = (
            f"{len(signals)} ghost-job signals: listing circulates without "
            "evidence of hiring intent."
        )
    elif signals:
        verdict = GhostVerdict.SUSPECT
        rationale = (
            f"{len(signals)} ghost-job signal(s); treat with skepticism, "
            "verify against the employer's own careers page."
        )
    else:
        verdict = GhostVerdict.NO_SIGNAL
        rationale = "No ghost-job pattern detected in these sightings."

    return GhostJobReport(
        title=first.title,
        employer=first.employer,
        location=first.location,
        verdict=verdict,
        rationale=rationale,
        signals=tuple(signals),
        text_groups=len(groups),
        largest_group_size=len(largest),
        distinct_sources=len(distinct_sources),
        distinct_listing_ids=len(distinct_ids),
        circulation_days=circulation_days,
        freshness_gap_days=freshness_gap_days,
    )


def detect_ghost_job_and_record(
    postings: list[JobPosting],
    *,
    kind: ClaimKind = ClaimKind.JUDGMENT,
) -> tuple[GhostJobReport, ClaimRecord]:
    """Run :func:`detect_ghost_job` and intake the verdict as a claim.

    Each observed ghost signal becomes one corroboration on its own
    evidentiary root, so the 2+-independent-roots rule applies directly:
    a LIKELY_GHOST verdict (3+ signals by construction) is CORROBORATED
    and passes the consequential-use gate for exclusion; SUSPECT and
    NO_SIGNAL verdicts stay gated. The claim's root is anchored in the
    first signal — the detector records the outcome but does not count
    as evidence for it. The report carries the claim id.
    """
    report = detect_ghost_job(postings)
    subject = f"{report.employer} — {report.title} ({report.location})"
    record = intake_claim(
        text=f"Ghost-job analysis: {report.verdict.value} — {report.rationale}",
        subject=subject,
        source="vessell.verify.detect_ghost_job",
        source_tier=SourceStatus.FRAMEWORK_SYNTHESIS,
        source_root="ghost-signal-0" if report.signals else None,
        kind=kind,
        note=f"{len(report.signals)} ghost signal(s) observed",
    )
    for index, signal in enumerate(report.signals):
        record = add_corroboration(
            record,
            source=f"ghost-job signal {index + 1}",
            source_tier=SourceStatus.WORKING_HYPOTHESIS,
            root=f"ghost-signal-{index}",
            note=signal,
        )
    register_dependent(
        record.id,
        artifact="vessell.verify.GhostJobReport",
        location=subject,
    )
    return replace(report, claim_id=record.id), record


def filter_ghost_jobs(
    postings: list[JobPosting],
    *,
    track_provenance: bool = True,
) -> tuple[list[JobPosting], list[GhostJobReport]]:
    """Split postings into (kept, ghost_reports).

    Roles judged LIKELY_GHOST are dropped from the kept set and reported;
    SUSPECT roles are kept but flagged in their report. Every decision is
    auditable through the returned reports.

    With ``track_provenance`` (default), each role's verdict is intaked as
    a claim, and the exclusion of a LIKELY_GHOST role passes through the
    consequential-use gate — the drop only happens when the verdict's
    claim is corroborated (3+ independent ghost signals), otherwise
    :class:`ClaimGateBlocked` is raised instead of silently dropping.
    """
    kept: list[JobPosting] = []
    reports: list[GhostJobReport] = []
    for role_postings in group_postings_by_role(postings).values():
        record: ClaimRecord | None = None
        if track_provenance:
            report, record = detect_ghost_job_and_record(role_postings)
        else:
            report = detect_ghost_job(role_postings)
        reports.append(report)
        if report.verdict is GhostVerdict.LIKELY_GHOST:
            if record is not None:
                require_gate(record, "consequential")
            continue
        kept.extend(role_postings)
    # Deterministic order for auditability.
    reports.sort(key=lambda r: (r.employer, r.title, r.location))
    return kept, reports


# ---------------------------------------------------------------------------
# Search-path provenance for negative findings (§6: the analyst's miss)
# ---------------------------------------------------------------------------

MIN_ABSENCE_PATHS = 2  # independent search paths that must corroborate an absence


@dataclass(frozen=True)
class SearchPath:
    """One attempted search path logged against a claim — the witnessed path
    of a negative finding.

    Worked example (case study §6): on 2026-09-30 the analyst searched arXiv
    for the literal string "Jonathan Castillo", found nothing, and reported
    no such author — operationalizing a negative finding off a single
    unwitnessed path. The paper was there all along: "Inductive Diagrams for
    Causal Reasoning" by Jonathan Castello, Patrick Redmond, and Lindsey
    Kuper (arXiv:2307.10484), one letter off on both names. The paths never
    walked: spelling variants, co-author cross-check, title-keyword search.
    Every path attempted — hits and misses — is recorded here, because the
    analyst's search history is the witnessed path an absence claim stands on.
    """

    query: str  # what was searched for, e.g. "Jonathan Castillo"
    strategy: str  # how it was searched, e.g. "literal-author-name"
    source: str  # where it was searched, e.g. "arxiv.org"
    date: str = ""  # ISO date/datetime the search ran; defaults to now
    result_summary: str = ""  # what came back, in the analyst's own words
    found: bool = False  # True when this path surfaced the target

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.query,
            "strategy": self.strategy,
            "source": self.source,
            "date": self.date,
            "result_summary": self.result_summary,
            "found": self.found,
        }


_SEARCH_PATHS: dict[str, list[SearchPath]] = {}


def reset_search_paths() -> None:
    """Clear the search-path registry. Test/support utility."""
    _SEARCH_PATHS.clear()


def record_search_path(
    claim_id: str,
    query: str,
    strategy: str,
    source: str,
    date: str = "",
    result_summary: str = "",
    found: bool = False,
) -> SearchPath:
    """Log one attempted search path against a claim's provenance.

    Hits and misses alike: the analyst's search history is the witnessed
    path of a negative finding, and a negative existential may not be
    reported until :func:`gate_negative_finding` clears it. Raises
    KeyError for an unknown claim id.
    """
    get_claim(claim_id)  # KeyError if unknown
    if not query.strip() or not strategy.strip() or not source.strip():
        raise ValueError("record_search_path needs a query, a strategy, and a source.")
    path = SearchPath(
        query=query,
        strategy=strategy,
        source=source,
        date=date or datetime.now(UTC).isoformat(timespec="seconds"),
        result_summary=result_summary,
        found=found,
    )
    _SEARCH_PATHS.setdefault(claim_id, []).append(path)
    return path


def search_paths(claim_id: str) -> list[SearchPath]:
    """Every search path attempted against a claim, in the order walked."""
    get_claim(claim_id)  # KeyError if unknown
    return list(_SEARCH_PATHS.get(claim_id, []))


def _independent_absence_paths(paths: list[SearchPath]) -> set[tuple[str, str]]:
    """Distinct (strategy, source) pairs among paths corroborating the absence.

    Re-running the same literal query on the same source is one path, not
    two; a spelling variant, a co-author cross-check, or a different index
    is a new one.
    """
    return {(p.strategy, p.source) for p in paths if not p.found}


def gate_negative_finding(claim_id: str) -> tuple[bool, str]:
    """The §6 gate: may this negative existential be reported as a finding?

    A "no X exists" claim enters UNVERIFIED like any other claim and stays
    gated until at least ``MIN_ABSENCE_PATHS`` independent search paths
    corroborate the absence. Any path that found the target contradicts the
    absence outright — the finding is refuted, not gated. Returns
    (allowed, reason); the reason is the audit line.
    """
    paths = search_paths(claim_id)
    hits = [p for p in paths if p.found]
    if hits:
        return (
            False,
            (
                "Negative finding contradicted: "
                + "; ".join(f"{p.source} via {p.strategy} ({p.query!r})" for p in hits)
                + ". The absence claim is refuted; disavow it instead of reporting it."
            ),
        )
    independent = _independent_absence_paths(paths)
    if len(independent) < MIN_ABSENCE_PATHS:
        return (
            False,
            (
                f"Negative finding gated: {len(independent)} independent search "
                f"path(s) corroborate the absence, need {MIN_ABSENCE_PATHS}. A "
                "single-path absence is an unwitnessed edge — walk another "
                "independent path (spelling variant, co-author cross-check, "
                "different index) before reporting."
            ),
        )
    return (
        True,
        (
            f"{len(independent)} independent search paths corroborate the absence; "
            "cleared to report as a finding."
        ),
    )


def require_negative_finding(claim_id: str) -> tuple[bool, str]:
    """Enforce the §6 negative-finding gate, raising instead of returning False.

    Returns (True, reason) when the absence is cleared to report. Raises
    :class:`~vessell.provenance.ClaimGateBlocked` when
    :func:`gate_negative_finding` would return False, so callers cannot
    silently report a single-path absence.
    """
    allowed, reason = gate_negative_finding(claim_id)
    if not allowed:
        raise ClaimGateBlocked(
            f"Negative finding for claim {claim_id} blocked: {reason}"
        )
    return True, reason
