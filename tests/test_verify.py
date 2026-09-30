"""Regression tests for vessell.verify — planted-news checks and ghost-job filtering."""

from typing import Any

import pytest

from vessell.provenance import SourceStatus
from vessell.verify import (
    ClaimCheck,
    GhostVerdict,
    JobPosting,
    PlantedVerdict,
    SourceSighting,
    Verdict,
    analyze_planted_news,
    detect_ghost_job,
    filter_ghost_jobs,
    group_postings_by_role,
    verify_claim,
)

EST = SourceStatus.SOURCE_ESTABLISHED
SYN = SourceStatus.FRAMEWORK_SYNTHESIS
HYP = SourceStatus.WORKING_HYPOTHESIS
ILL = SourceStatus.ILLUSTRATIVE


def _sighting(source: str, tier: SourceStatus, **kwargs: Any) -> SourceSighting:
    return SourceSighting(source_name=source, tier=tier, **kwargs)


# ---------------------------------------------------------------------------
# Planted-news check
# ---------------------------------------------------------------------------


def _quake_check() -> ClaimCheck:
    """The Sept 29 2026 Wauna M4.2: official record plus press corroboration."""
    return ClaimCheck(
        claim="M4.2 earthquake near Wauna, WA at 2:05 PM PT Sept 29 2026",
        sightings=(
            _sighting("USGS", EST, is_official_record=True,
                       note="M4.2 event page, reviewed by seismologist, 7,155 felt reports"),
            _sighting("PNSN", EST, note="ShakeAlert detection, weak shaking in Olympia"),
            _sighting("KOMO News", EST, note="intensity map, Sound Transit reroute"),
            _sighting("Kitsap Sun", SYN, note="local reporting"),
        ),
    )


def test_official_record_verifies_claim() -> None:
    result = verify_claim(_quake_check())
    assert result.verdict is Verdict.VERIFIED
    assert result.official_record is True
    assert result.corroboration_score == 1.0
    assert "USGS" in result.rationale


def test_two_established_roots_verify_without_official_record() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            _sighting("Outlet A", EST),
            _sighting("Outlet B", EST),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.VERIFIED
    assert result.official_record is False


def test_aggregator_only_is_uncorroborated() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            _sighting("Random Aggregator", ILL),
            _sighting("Content Farm", ILL),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.UNCORROBORATED
    assert result.corroboration_score < 0.6


def test_single_sighting_is_single_source() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(_sighting("One Blog", HYP),),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.SINGLE_SOURCE
    assert result.independent_roots == 1


def test_no_sightings_is_uncorroborated() -> None:
    result = verify_claim(ClaimCheck(claim="Something happened"))
    assert result.verdict is Verdict.UNCORROBORATED
    assert result.corroboration_score == 0.0
    assert result.independent_roots == 0


def test_established_denial_contradicts() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            _sighting("Blog A", ILL),
            _sighting("Blog B", ILL),
            _sighting("Wire Service", EST, denies=True, note="no such event"),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.CONTRADICTED


def test_shared_wire_root_counts_once() -> None:
    """Ten sites running the same wire copy are one root, not ten."""
    check = ClaimCheck(
        claim="Something happened",
        sightings=tuple(
            _sighting(f"Site {i}", SYN, root="ap-wire") for i in range(10)
        ),
    )
    result = verify_claim(check)
    assert result.independent_roots == 1
    # One synthesis root: 0.6 / 2 = 0.3 -> uncorroborated despite ten sightings.
    assert result.verdict is Verdict.UNCORROBORATED


def test_result_to_dict_is_auditable() -> None:
    result = verify_claim(_quake_check())
    record = result.to_dict()
    assert record["verdict"] == "VERIFIED"
    assert record["official_record"] is True
    signals = record["signals"]
    assert isinstance(signals, list) and len(signals) == 4


# ---------------------------------------------------------------------------
# Ghost-job detection
# ---------------------------------------------------------------------------

ULINE_TEXT = """Operations Manager. Pay from $96,000 to $160,000 per year.
Washington Branch, Lacey WA. Oversee operations including the Warehouse,
Customer Service, Sales, HR, IT and Facilities departments. Bachelor's
degree. 5+ years experience in operations or general management."""


def _uline_posting(source: str, listing_id: str, claimed: str, seen: str) -> JobPosting:
    return JobPosting(
        title="Operations Manager",
        employer="Uline",
        location="Lacey, WA",
        description_text=ULINE_TEXT,
        salary_text="$96,000-$160,000",
        source=source,
        listing_id=listing_id,
        claimed_posted=claimed,
        first_seen=seen,
    )


def _uline_sightings() -> list[JobPosting]:
    """The observed ghost pattern: same text, 4 sources, 4 IDs, ~280 days."""
    return [
        _uline_posting("Monster", "m-741f855b", "2026-09-25", "2025-12-24"),
        _uline_posting("CareerBuilder", "cb-e6547854", "2026-09-23", "2026-01-15"),
        _uline_posting("CareerBuilder", "cb-0090a8c5", "2026-09-01", "2026-03-02"),
        _uline_posting("Ladders", "la-88670188", "2026-09-07", "2026-02-10"),
    ]


def test_likely_ghost_on_classic_pattern() -> None:
    report = detect_ghost_job(_uline_sightings())
    assert report.verdict is GhostVerdict.LIKELY_GHOST
    assert report.distinct_sources == 3  # Monster, CareerBuilder x2, Ladders
    assert report.distinct_listing_ids == 4
    assert report.circulation_days is not None and report.circulation_days >= 60
    assert report.freshness_gap_days is not None and report.freshness_gap_days >= 30
    assert len(report.signals) >= 3


def test_single_posting_has_no_signal() -> None:
    report = detect_ghost_job([_uline_posting("Uline Jobs", "u-1", "2026-09-29", "2026-09-29")])
    assert report.verdict is GhostVerdict.NO_SIGNAL
    assert "Single sighting" in report.rationale


def test_fresh_unique_posting_has_no_signal() -> None:
    postings = [
        JobPosting(
            title="Data Analyst I",
            employer="F5",
            location="Seattle, WA",
            description_text="Analyze product telemetry and build dashboards.",
            source="F5 Jobs",
            listing_id="RP1038819",
            claimed_posted="2026-09-20",
            first_seen="2026-09-20",
        ),
        JobPosting(
            title="Data Analyst I",
            employer="F5",
            location="Seattle, WA",
            description_text="Analyze product telemetry and build dashboards.",
            source="LinkedIn",
            listing_id="li-99821",
            claimed_posted="2026-09-21",
            first_seen="2026-09-21",
        ),
    ]
    report = detect_ghost_job(postings)
    assert report.verdict is GhostVerdict.NO_SIGNAL


def test_two_sources_alone_is_no_signal() -> None:
    postings = [
        _uline_posting("Monster", "m-1", "2026-09-25", "2026-09-25"),
        _uline_posting("Ladders", "la-1", "2026-09-26", "2026-09-26"),
    ]
    report = detect_ghost_job(postings)
    # Same text on 2 sources only: no signal thresholds met.
    assert report.verdict is GhostVerdict.NO_SIGNAL


def test_repost_ids_alone_raise_suspect() -> None:
    base = _uline_sightings()
    trimmed = [
        JobPosting(
            title=p.title, employer=p.employer, location=p.location,
            description_text=p.description_text, source="One Board",
            listing_id=f"id-{i}", claimed_posted="2026-09-2{i}",
            first_seen="2026-09-2{i}",
        )
        for i, p in enumerate(base[:4])
    ]
    report = detect_ghost_job(trimmed)
    assert report.verdict is GhostVerdict.SUSPECT
    assert any("listing IDs" in s for s in report.signals)


def test_near_duplicate_text_groups_together() -> None:
    tweaked = ULINE_TEXT.replace("Bachelor's", "Bachelors").replace("  ", " ")
    postings = [
        _uline_posting("Monster", "m-1", "2026-09-25", "2026-09-25"),
        JobPosting(
            title="Operations Manager", employer="Uline", location="Lacey, WA",
            description_text=tweaked, source="Ladders", listing_id="la-1",
            claimed_posted="2026-09-26", first_seen="2026-09-26",
        ),
    ]
    report = detect_ghost_job(postings)
    assert report.text_groups == 1
    assert report.largest_group_size == 2


def test_detect_ghost_job_rejects_empty() -> None:
    with pytest.raises(ValueError):
        detect_ghost_job([])


def test_filter_ghost_jobs_drops_ghost_role_keeps_legit() -> None:
    legit = JobPosting(
        title="Data Analyst I", employer="F5", location="Seattle, WA",
        description_text="Analyze product telemetry and build dashboards.",
        source="F5 Jobs", listing_id="RP1038819",
        claimed_posted="2026-09-20", first_seen="2026-09-20",
    )
    kept, reports = filter_ghost_jobs(_uline_sightings() + [legit])
    assert kept == [legit]
    by_employer = {r.employer: r for r in reports}
    assert by_employer["Uline"].verdict is GhostVerdict.LIKELY_GHOST
    assert by_employer["F5"].verdict is GhostVerdict.NO_SIGNAL


def test_group_postings_by_role() -> None:
    grouped = group_postings_by_role(
        _uline_sightings()
        + [JobPosting(title="OPERATIONS MANAGER", employer="ULINE",
                       location="Lacey, WA", description_text="x")]
    )
    # Case/punctuation-insensitive role keying: all five are one role.
    assert len(grouped) == 1
    assert len(next(iter(grouped.values()))) == 5


def test_ghost_report_to_dict_is_auditable() -> None:
    report = detect_ghost_job(_uline_sightings())
    record = report.to_dict()
    assert record["verdict"] == "LIKELY_GHOST"
    assert record["employer"] == "Uline"
    signals = record["signals"]
    assert isinstance(signals, list) and len(signals) >= 3


# ---------------------------------------------------------------------------
# Planted-news intelligence
# ---------------------------------------------------------------------------

PLANTED_TEXT = (
    "BREAKING: Officials confirm the downtown bridge will close indefinitely "
    "due to a structural failure discovered during a routine inspection."
)


def _burst_sighting(name: str, published: str) -> SourceSighting:
    return SourceSighting(
        source_name=name,
        tier=ILL,
        published_at=published,
        text=PLANTED_TEXT,
    )


def _manufactured_claim() -> ClaimCheck:
    """Five low-tier outlets, identical text, inside 25 minutes, no primary."""
    return ClaimCheck(
        claim="Downtown bridge closed indefinitely over structural failure",
        sightings=tuple(
            _burst_sighting(f"Outlet {i}", f"2026-09-29T14:{10 + i * 5:02d}:00")
            for i in range(5)
        ),
    )


def test_official_record_is_authentic() -> None:
    report = analyze_planted_news(_quake_check())
    assert report.verdict is PlantedVerdict.AUTHENTIC
    assert "official-record" in report.indicators
    assert report.corroboration.verdict is Verdict.VERIFIED


def test_coordinated_burst_is_likely_planted() -> None:
    report = analyze_planted_news(_manufactured_claim())
    assert report.verdict is PlantedVerdict.LIKELY_PLANTED
    assert report.burst_detected is True
    assert report.orphaned is True
    assert "synchronized-burst" in report.indicators
    assert "no-primary-source" in report.indicators
    assert "text-clone-army" in report.indicators
    assert report.clone_army_size == 5


def test_established_denial_is_likely_planted() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            _burst_sighting("Outlet A", "2026-09-29T14:10:00"),
            _burst_sighting("Outlet B", "2026-09-29T14:12:00"),
            SourceSighting(
                source_name="Wire Service",
                tier=EST,
                denies=True,
                note="no such event on record",
            ),
        ),
    )
    report = analyze_planted_news(check)
    assert report.verdict is PlantedVerdict.LIKELY_PLANTED
    assert "established-denial" in report.indicators


def test_single_origin_laundering_chain() -> None:
    """Three sites, one shared rumor root, no primary: laundering, not news."""
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            SourceSighting("Site A", HYP, root="rumor-mill", text="word is " + "x" * 40),
            SourceSighting("Site B", HYP, root="rumor-mill", text="word is " + "y" * 40),
            SourceSighting("Site C", ILL, root="rumor-mill", text="word is " + "z" * 40),
        ),
    )
    report = analyze_planted_news(check)
    assert report.single_origin is True
    assert "single-origin-laundering" in report.indicators
    assert "no-primary-source" in report.indicators
    # Two hostile indicators -> likely planted.
    assert report.verdict is PlantedVerdict.LIKELY_PLANTED


def test_one_indicator_is_suspect() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            SourceSighting("Blog A", ILL, text="claim text " + "a" * 60),
            SourceSighting("Blog B", ILL, text="claim text " + "b" * 60),
        ),
    )
    report = analyze_planted_news(check)
    # Only no-primary-source fires: burst needs 4, clone army needs 5.
    assert report.verdict is PlantedVerdict.SUSPECT
    assert report.indicators == ("no-primary-source",)


def test_clean_corroboration_is_authentic() -> None:
    check = ClaimCheck(
        claim="Something happened",
        sightings=(
            SourceSighting("Outlet A", EST),
            SourceSighting("Outlet B", EST),
        ),
    )
    report = analyze_planted_news(check)
    assert report.verdict is PlantedVerdict.AUTHENTIC
    assert report.burst_detected is False
    assert report.orphaned is False


def test_no_sightings_is_unverifiable() -> None:
    report = analyze_planted_news(ClaimCheck(claim="Something happened"))
    assert report.verdict is PlantedVerdict.UNVERIFIABLE


def test_planted_report_to_dict_is_auditable() -> None:
    report = analyze_planted_news(_manufactured_claim())
    record = report.to_dict()
    assert record["verdict"] == "LIKELY_PLANTED"
    indicators = record["indicators"]
    assert isinstance(indicators, list) and "synchronized-burst" in indicators
    corroboration = record["corroboration"]
    assert isinstance(corroboration, dict)
    assert corroboration["verdict"] == "UNCORROBORATED"


# ---------------------------------------------------------------------------
# Search-path provenance for negative findings (§6: the analyst's miss)
# ---------------------------------------------------------------------------

from vessell.provenance import (
    ClaimGateBlocked,
    intake_claim,
    reset_claim_lifecycle,
)
from vessell.verify import (
    MIN_ABSENCE_PATHS,
    SearchPath,
    gate_negative_finding,
    record_search_path,
    require_negative_finding,
    reset_search_paths,
    search_paths,
)


@pytest.fixture()
def _clean_search_paths():
    reset_claim_lifecycle()
    reset_search_paths()
    yield
    reset_claim_lifecycle()
    reset_search_paths()


def _absence_claim() -> str:
    """The negative existential: 'no such paper exists.' Enters UNVERIFIED."""
    record = intake_claim(
        text="No arXiv paper matches 'Jonathan Castillo, Patrick Redmond, "
        "Lindsey Kipper'.",
        subject="arXiv:2307.10484 identification",
        source="analyst search",
        source_tier=HYP,
    )
    assert record.status.value == "UNVERIFIED"
    return record.id


def test_record_search_path_logs_against_claim(_clean_search_paths: None) -> None:
    claim_id = _absence_claim()
    path = record_search_path(
        claim_id,
        query="Jonathan Castillo",
        strategy="literal-author-name",
        source="arxiv.org",
        date="2026-09-30",
        result_summary="zero hits",
    )
    assert isinstance(path, SearchPath)
    assert path.date == "2026-09-30"
    assert search_paths(claim_id) == [path]
    assert path.to_dict()["result_summary"] == "zero hits"


def test_record_search_path_rejects_unknown_claim(_clean_search_paths: None) -> None:
    with pytest.raises(KeyError):
        record_search_path(
            "claim-does-not-exist", query="x", strategy="y", source="z"
        )


def test_zero_paths_stays_gated(_clean_search_paths: None) -> None:
    allowed, reason = gate_negative_finding(_absence_claim())
    assert allowed is False
    assert "gated" in reason


def test_single_search_path_stays_gated(_clean_search_paths: None) -> None:
    """The §6 failure mode, exactly: one literal search, reported as a finding."""
    claim_id = _absence_claim()
    record_search_path(
        claim_id,
        query="Jonathan Castillo",
        strategy="literal-author-name",
        source="arxiv.org",
        result_summary="zero hits",
    )
    allowed, reason = gate_negative_finding(claim_id)
    assert allowed is False
    assert str(MIN_ABSENCE_PATHS) in reason
    with pytest.raises(ClaimGateBlocked):
        require_negative_finding(claim_id)


def test_two_independent_paths_clear_the_gate(_clean_search_paths: None) -> None:
    claim_id = _absence_claim()
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits",
    )
    record_search_path(
        claim_id, query="Castillo Redmond Kipper", strategy="spelling-variant",
        source="arxiv.org", result_summary="zero hits",
    )
    allowed, reason = gate_negative_finding(claim_id)
    assert allowed is True
    assert "2 independent search paths" in reason
    assert require_negative_finding(claim_id) == (True, reason)


def test_same_strategy_same_source_counts_once(_clean_search_paths: None) -> None:
    """Re-running the same query on the same source is one path, not two."""
    claim_id = _absence_claim()
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits",
    )
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits again",
    )
    allowed, _ = gate_negative_finding(claim_id)
    assert allowed is False


def test_same_strategy_different_source_is_independent(_clean_search_paths: None) -> None:
    claim_id = _absence_claim()
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits",
    )
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="Semantic Scholar", result_summary="zero hits",
    )
    allowed, _ = gate_negative_finding(claim_id)
    assert allowed is True


def test_found_path_contradicts_the_absence(_clean_search_paths: None) -> None:
    """The Castello correction: a co-author cross-check finds the paper."""
    claim_id = _absence_claim()
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits",
    )
    record_search_path(
        claim_id, query="Redmond Kuper", strategy="coauthor-cross-check",
        source="arxiv.org", result_summary="found arXiv:2307.10484",
        found=True,
    )
    allowed, reason = gate_negative_finding(claim_id)
    assert allowed is False
    assert "contradicted" in reason
    with pytest.raises(ClaimGateBlocked):
        require_negative_finding(claim_id)


def test_castello_worked_example_end_to_end(_clean_search_paths: None) -> None:
    """§6 as the machine would have run it: the single-path miss stays gated."""
    claim_id = _absence_claim()
    # The analyst's actual (deficient) search history.
    record_search_path(
        claim_id, query="Jonathan Castillo", strategy="literal-author-name",
        source="arxiv.org", result_summary="zero hits", date="2026-09-30",
    )
    allowed, _ = gate_negative_finding(claim_id)
    assert allowed is False  # may not be reported as a finding

    # The unwalked paths, walked after the user's correction.
    record_search_path(
        claim_id, query="Jonathan Castello", strategy="spelling-variant",
        source="arxiv.org", result_summary="found arXiv:2307.10484",
        found=True, date="2026-09-30",
    )
    record_search_path(
        claim_id, query="Redmond Kuper", strategy="coauthor-cross-check",
        source="arxiv.org", result_summary="found arXiv:2307.10484",
        found=True, date="2026-09-30",
    )
    record_search_path(
        claim_id, query="inductive diagrams causal reasoning",
        strategy="title-keyword", source="arxiv.org",
        result_summary="found arXiv:2307.10484", found=True, date="2026-09-30",
    )
    assert len(search_paths(claim_id)) == 4
    allowed, reason = gate_negative_finding(claim_id)
    assert allowed is False
    assert "contradicted" in reason  # the absence is refuted, not corroborated


def test_every_attempted_path_is_provenance(_clean_search_paths: None) -> None:
    """Hits and misses alike are recorded: the search history is the witnessed path."""
    claim_id = _absence_claim()
    record_search_path(
        claim_id, query="a", strategy="s1", source="src1", result_summary="miss",
    )
    record_search_path(
        claim_id, query="b", strategy="s2", source="src2", result_summary="hit",
        found=True,
    )
    paths = search_paths(claim_id)
    assert [p.found for p in paths] == [False, True]
    assert all(p.date for p in paths)  # dates default to now
