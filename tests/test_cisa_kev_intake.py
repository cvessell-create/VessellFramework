"""Tests for the CISA KEV live-feed adapter and its integration with the
full VesselFramework doctrine-to-code pipeline, using a recorded real-data
snapshot (not synthetic/illustrative content) as a deterministic fixture.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from vessell.app.pipeline import run_case_pipeline
from vessell.app.sources.cisa_kev import (
    build_case_from_kev,
    select_recent_vulnerabilities,
)

FIXTURE_PATH = Path("tests/fixtures/live_sources/cisa_kev_sample.json")
FIXTURE_AS_OF = date(2026, 9, 22)


def _load_catalog() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_select_recent_vulnerabilities_filters_by_lookback_window() -> None:
    catalog = _load_catalog()

    recent = select_recent_vulnerabilities(catalog, lookback_days=14, as_of=FIXTURE_AS_OF)

    recent_ids = {entry["cveID"] for entry in recent}
    assert recent_ids == {
        "CVE-2026-93952",
        "CVE-2026-94127",
        "CVE-2026-93616",
        "CVE-2026-85102",
    }
    assert "CVE-2021-27104" not in recent_ids


def test_select_recent_vulnerabilities_respects_limit() -> None:
    catalog = _load_catalog()

    recent = select_recent_vulnerabilities(catalog, lookback_days=14, limit=2, as_of=FIXTURE_AS_OF)

    assert len(recent) == 2
    assert recent[0]["cveID"] == "CVE-2026-93952"


def test_build_case_from_kev_produces_source_established_evidence() -> None:
    catalog = _load_catalog()

    case = build_case_from_kev(catalog, lookback_days=14, as_of=FIXTURE_AS_OF)

    assert case["evidence"], "Expected at least one evidence item from the fixture."
    assert all(item["status"] == "SOURCE-ESTABLISHED" for item in case["evidence"])
    source_ids = {item["source_id"] for item in case["evidence"]}
    assert "CVE-2026-93952" in source_ids
    assert "CVE-2021-27104" not in source_ids


def test_build_case_from_kev_handles_empty_window() -> None:
    catalog = _load_catalog()

    case = build_case_from_kev(catalog, lookback_days=0, as_of=date(2026, 9, 23))

    assert case["evidence"] == []
    assert "No CISA KEV entries" in case["analysis"]["posture"]


def test_live_kev_case_runs_through_full_pipeline() -> None:
    catalog = _load_catalog()
    case = build_case_from_kev(catalog, lookback_days=14, as_of=FIXTURE_AS_OF)

    result = run_case_pipeline(case)

    assert result.counts.total_evidence == 4
    assert result.counts.source_established == 4
    assert result.counts.illustrative == 0
    assert result.confidence_ceiling in {"LOW", "MODERATE"}
