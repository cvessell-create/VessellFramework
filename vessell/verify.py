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
"""

from __future__ import annotations

import difflib
import hashlib
import re
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from vessell.provenance import SourceStatus
from vessell.weights import SOURCE_TIER_WEIGHTS

__all__ = [
    "BURST_MIN_SOURCES",
    "BURST_WINDOW_MINUTES",
    "CLONE_ARMY_MIN_SOURCES",
    "NEAR_DUPLICATE_THRESHOLD",
    "ClaimCheck",
    "GhostJobReport",
    "GhostVerdict",
    "JobPosting",
    "PlantedNewsReport",
    "PlantedVerdict",
    "SourceSighting",
    "Verdict",
    "VerificationResult",
    "analyze_planted_news",
    "detect_ghost_job",
    "filter_ghost_jobs",
    "group_postings_by_role",
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

    def to_dict(self) -> dict[str, object]:
        return {
            "claim": self.claim,
            "verdict": self.verdict.value,
            "corroboration_score": round(self.corroboration_score, 4),
            "independent_roots": self.independent_roots,
            "official_record": self.official_record,
            "rationale": self.rationale,
            "signals": list(self.signals),
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

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "employer": self.employer,
            "location": self.location,
            "verdict": self.verdict.value,
            "rationale": self.rationale,
            "signals": list(self.signals),
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


def filter_ghost_jobs(
    postings: list[JobPosting],
) -> tuple[list[JobPosting], list[GhostJobReport]]:
    """Split postings into (kept, ghost_reports).

    Roles judged LIKELY_GHOST are dropped from the kept set and reported;
    SUSPECT roles are kept but flagged in their report. Every decision is
    auditable through the returned reports.
    """
    kept: list[JobPosting] = []
    reports: list[GhostJobReport] = []
    for role_postings in group_postings_by_role(postings).values():
        report = detect_ghost_job(role_postings)
        reports.append(report)
        if report.verdict is GhostVerdict.LIKELY_GHOST:
            continue
        kept.extend(role_postings)
    # Deterministic order for auditability.
    reports.sort(key=lambda r: (r.employer, r.title, r.location))
    return kept, reports
