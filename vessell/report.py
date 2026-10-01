# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Verification reporting: claim x source matrices.

:func:`event_matrix` runs a batch of :class:`~vessell.verify.ClaimCheck`
through :func:`~vessell.verify.verify_claim` and returns the full
claim-by-source grid: per-cell tier weights, event clocks, and denial
flags, plus per-row verdicts and scores. It is the data behind the
verification heat map — built for live/developing events where the same
claim is sighted at different points on the event clock.
"""
from __future__ import annotations

from typing import Any

from vessell.verify import ClaimCheck, verify_claim
from vessell.weights import SOURCE_TIER_WEIGHTS

__all__ = ["event_matrix"]


def event_matrix(checks: list[ClaimCheck]) -> dict[str, Any]:
    """Build the claim x source verification matrix for a batch of checks.

    Returns ``{"sources": [...], "rows": [...]}`` where each row holds the
    claim text, verdict, corroboration score, independent-root count, the
    rationale, and ``cells`` mapping each source name to its
    ``{"weight", "clock", "denies"}`` triple. Sources silent on a claim
    simply have no cell.
    """
    sources: list[str] = []
    for check in checks:
        for sighting in check.sightings:
            if sighting.source_name not in sources:
                sources.append(sighting.source_name)

    rows: list[dict[str, Any]] = []
    for check in checks:
        result = verify_claim(check)
        cells: dict[str, dict[str, Any]] = {}
        for sighting in check.sightings:
            weight = SOURCE_TIER_WEIGHTS[sighting.tier]
            if sighting.denies:
                weight = -weight
            cells[sighting.source_name] = {
                "weight": round(weight, 4),
                "clock": sighting.event_clock,
                "denies": sighting.denies,
            }
        rows.append(
            {
                "claim": result.claim,
                "verdict": result.verdict.value,
                "score": round(result.corroboration_score, 4),
                "independent_roots": result.independent_roots,
                "rationale": result.rationale,
                "signals": list(result.signals),
                "cells": cells,
            }
        )
    return {"sources": sources, "rows": rows}
