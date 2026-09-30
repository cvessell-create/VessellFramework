# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Fetch and normalize the CISA Known Exploited Vulnerabilities (KEV) catalog
into a VesselFramework-compliant case intake document.

Data source: CISA's official, publicly documented KEV feed
(https://www.cisa.gov/known-exploited-vulnerabilities-catalog). This is the
real, currently-updated, US-government-published list of vulnerabilities with
confirmed active exploitation, used here as SOURCE-ESTABLISHED evidence for
the doctrine-to-code pipeline.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date, datetime, timedelta
from typing import Any

KEV_FEED_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DEFAULT_LOOKBACK_DAYS = 14
DEFAULT_LIMIT = 10


def fetch_kev_catalog(url: str = KEV_FEED_URL, timeout: float = 10.0) -> dict[str, Any]:
    """Fetch the raw CISA KEV catalog JSON from the official feed."""
    request = urllib.request.Request(url, headers={"User-Agent": "VesselFramework-CaseIntake/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _added_date(entry: dict[str, Any]) -> date:
    raw = entry.get("dateAdded", "1970-01-01")
    return datetime.strptime(raw, "%Y-%m-%d").date()


def select_recent_vulnerabilities(
    catalog: dict[str, Any],
    *,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    limit: int = DEFAULT_LIMIT,
    as_of: date | None = None,
) -> list[dict[str, Any]]:
    """Select the most recently added actively-exploited vulnerabilities."""
    as_of = as_of or datetime.now().date()
    cutoff = as_of - timedelta(days=lookback_days)

    vulnerabilities = catalog.get("vulnerabilities", [])
    recent = [entry for entry in vulnerabilities if _added_date(entry) >= cutoff]
    recent.sort(key=_added_date, reverse=True)
    return recent[:limit]


def build_case_from_kev(
    catalog: dict[str, Any],
    *,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    limit: int = DEFAULT_LIMIT,
    as_of: date | None = None,
) -> dict[str, Any]:
    """Build a VesselFramework case intake document from real CISA KEV entries.

    Every evidence item is SOURCE-ESTABLISHED: each is a direct citation of an
    authoritative primary source, with no framework synthesis or hypothesis
    involved in its status classification.
    """
    selected = select_recent_vulnerabilities(
        catalog, lookback_days=lookback_days, limit=limit, as_of=as_of
    )

    evidence = [
        {
            "description": (
                f"{entry.get('cveID', 'UNKNOWN-CVE')} \u2014 "
                f"{entry.get('vendorProject', 'Unknown vendor')} {entry.get('product', '')}: "
                f"{entry.get('vulnerabilityName', 'Unnamed vulnerability')} "
                f"(added {entry.get('dateAdded', 'unknown date')})"
            ),
            "status": "SOURCE-ESTABLISHED",
            "source_id": entry.get("cveID") or f"kev-{index}",
        }
        for index, entry in enumerate(selected, start=1)
    ]

    catalog_version = catalog.get("catalogVersion", "unknown")
    date_released = catalog.get("dateReleased", "unknown")

    if not evidence:
        posture = (
            "No CISA KEV entries were added within the lookback window; hold current "
            "posture and re-check on the next feed update."
        )
    else:
        posture = (
            "Cross-reference each listed CVE against deployed assets; prioritize "
            "remediation for any matching product before treating the exposure as closed."
        )

    return {
        "title": "Active exploited-vulnerability review (CISA KEV live feed)",
        "subject": "Recently added entries in the CISA Known Exploited Vulnerabilities catalog",
        "decision_question": (
            "Does current CISA KEV activity support treating any of the listed "
            "vulnerabilities as an active, unremediated exposure for US-based systems?"
        ),
        "domain": "Cybersecurity / Vulnerability Intelligence",
        "time_horizon": f"Catalog version {catalog_version}, released {date_released}",
        "evidence": evidence,
        "maskirovka": [],
        "harm_gate": {
            "accuracy_risk": True,
            "professional_risk": True,
            "hard_to_reverse": False,
            "benefit_proportionate": True,
        },
        "analysis": {
            "posture": posture,
        },
    }
