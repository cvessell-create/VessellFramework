# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Live-event verification regression test.

Recorded sightings from a real live event (NY Red Bulls vs St. Louis
City SC, MLS, 2026-09-30, first half). No network calls: the sightings
are frozen as observed. Guards the planted-news corroboration path
against regressions:

- multi-root established claims verify,
- single-source claims stay gated,
- a stale low-tier page can never corroborate a live claim.
"""
from vessell.provenance import SourceStatus, verify_event_chain
from vessell.verify import ClaimCheck, SourceSighting, Verdict, verify_and_record, verify_claim

EST = SourceStatus.SOURCE_ESTABLISHED
HYP = SourceStatus.WORKING_HYPOTHESIS
SEEN = "2026-10-01T00:55:00Z"
SL = "https://www.sportinglife.com/football/live/222667/new-york-red-bulls-vs-st-louis-city-sc?scrollTo=match-tabs"
LS = "https://www.livescore.com/en/football/usa/major-league-soccer/new-york-red-bulls-vs-st-louis-city/1696654/table/"
EB = "https://www.elbotola.com/en/analytics/match/y0or5jh8o52yqwz"
FP = "https://footballpredictions.ai/football-predictions/new-york-red-bulls-vs-st.-louis-city-predictions-tips-29-jan-2025/"


def _sighting(name, tier, url, text, note="", clock=None):
    return SourceSighting(source_name=name, tier=tier, url=url, seen_at=SEEN,
                          text=text, note=note, event_clock=clock)


def test_three_independent_roots_verify():
    check = ClaimCheck(
        claim="St. Louis City SC lead the NY Red Bulls 1-0 (live, first half)",
        sightings=(
            _sighting("Sporting Life", EST, SL, "[10'] NY Red Bulls 0 - St. Louis City SC 1"),
            _sighting("LiveScore", EST, LS, "[45'] New York Red Bulls 0 - 1 St. Louis City"),
            _sighting("Elbotola", EST, EB, "[41'] New York Red Bulls 0-1 St. Louis City SC"),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.VERIFIED
    assert result.independent_roots == 3
    assert result.corroboration_score == 1.0


def test_two_roots_verify_goal_detail():
    check = ClaimCheck(
        claim="Rafael Navarro scored for St. Louis in the 5th minute",
        sightings=(
            _sighting("Sporting Life", EST, SL, "[10'] 5' Rafael Navarro"),
            _sighting("Elbotola", EST, EB, "[41'] Goal Rafael Navarro Leal 5'"),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.VERIFIED
    assert result.independent_roots == 2


def test_single_source_stays_gated():
    check = ClaimCheck(
        claim="Corners are 0 NYRB / 2 STL",
        sightings=(_sighting("Elbotola", EST, EB, "[41'] 0 Corners 2"),),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.SINGLE_SOURCE
    assert result.independent_roots == 1


def test_stale_page_cannot_corroborate_live_claim():
    check = ClaimCheck(
        claim="NY Red Bulls lead St. Louis City SC 2-1",
        sightings=(
            _sighting("footballpredictions.ai", HYP, FP, "[stale] 2 - 1",
                      note="Stale prediction page from Jan 2025, not a live feed"),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.SINGLE_SOURCE
    assert result.corroboration_score < 0.2


def test_verification_outcome_is_recorded_with_intact_chain():
    check = ClaimCheck(
        claim="St. Louis City SC lead the NY Red Bulls 1-0 (live, first half)",
        sightings=(
            _sighting("Sporting Life", EST, SL, "[10'] NY Red Bulls 0 - St. Louis City SC 1"),
            _sighting("LiveScore", EST, LS, "[45'] New York Red Bulls 0 - 1 St. Louis City"),
        ),
    )
    result, _record = verify_and_record(check)
    ok, _msg = verify_event_chain(result.claim_id)
    assert ok


def test_clock_drift_flagged_not_contradicted():
    # Same claim sighted at 10' and 41': values evolve (shots on target
    # 1 -> 3). The framework must flag drift, never contradiction.
    check = ClaimCheck(
        claim="STL leads shots on target",
        sightings=(
            _sighting("Sporting Life", EST, SL, "On Target 0 NYRB / 1 STL", clock="10'"),
            _sighting("Elbotola", EST, EB, "2 Shots on target 3 (NYRB/STL)", clock="41'"),
        ),
    )
    result = verify_claim(check)
    assert result.verdict is Verdict.VERIFIED
    assert any("event-clock drift" in s for s in result.signals)


def test_no_drift_signal_without_clocks():
    check = ClaimCheck(
        claim="St. Louis City SC lead the NY Red Bulls 1-0 (live, first half)",
        sightings=(
            _sighting("Sporting Life", EST, SL, "NY Red Bulls 0 - St. Louis City SC 1"),
            _sighting("LiveScore", EST, LS, "New York Red Bulls 0 - 1 St. Louis City"),
        ),
    )
    result = verify_claim(check)
    assert not any("event-clock drift" in s for s in result.signals)


def test_event_matrix_builds_claim_by_source_grid():
    from vessell.report import event_matrix

    checks = [
        ClaimCheck(
            claim="STL leads 1-0",
            sightings=(
                _sighting("Sporting Life", EST, SL, "0-1", clock="10'"),
                _sighting("Elbotola", EST, EB, "0-1", clock="41'"),
            ),
        ),
        ClaimCheck(
            claim="Corners 0/2 STL",
            sightings=(_sighting("Elbotola", EST, EB, "0 Corners 2", clock="41'"),),
        ),
    ]
    matrix = event_matrix(checks)
    assert matrix["sources"] == ["Sporting Life", "Elbotola"]
    assert len(matrix["rows"]) == 2
    assert matrix["rows"][0]["verdict"] == "VERIFIED"
    assert matrix["rows"][0]["cells"]["Sporting Life"] == {
        "weight": 1.0, "clock": "10'", "denies": False,
    }
    assert matrix["rows"][1]["verdict"] == "SINGLE_SOURCE"
    assert "Sporting Life" not in matrix["rows"][1]["cells"]
