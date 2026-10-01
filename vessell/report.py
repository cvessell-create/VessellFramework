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

from vessell.verify import ClaimCheck, SourceSighting, clock_sort_key, verify_claim
from vessell.weights import SOURCE_TIER_WEIGHTS

__all__ = ["event_matrix"]


def _cell(sightings: list[SourceSighting]) -> dict[str, Any]:
    """Collapse every sighting one source made of one claim into a cell.

    A source can sight the same claim more than once on a live event
    (e.g. at 10' and again at 41'), or affirm and later deny it. The cell
    keeps all of that: ``weight`` is the strongest affirming tier weight
    minus the strongest denying tier weight (so a lone denial is negative
    and a self-contradicting source nets toward zero), ``clock`` lists
    every distinct event clock in natural order, and ``denies`` is set if
    any sighting denies the claim.
    """
    affirm = max(
        (SOURCE_TIER_WEIGHTS[s.tier] for s in sightings if not s.denies), default=0.0
    )
    deny = max((SOURCE_TIER_WEIGHTS[s.tier] for s in sightings if s.denies), default=0.0)
    clocks = sorted({s.event_clock for s in sightings if s.event_clock}, key=clock_sort_key)
    return {
        "weight": round(affirm - deny, 4),
        "clock": " / ".join(clocks) if clocks else None,
        "denies": any(s.denies for s in sightings),
    }


def event_matrix(checks: list[ClaimCheck]) -> dict[str, Any]:
    """Build the claim x source verification matrix for a batch of checks.

    Returns ``{"sources": [...], "rows": [...]}`` where each row holds the
    claim text, verdict, corroboration score, independent-root count, the
    rationale, and ``cells`` mapping each source name to its
    ``{"weight", "clock", "denies"}`` triple (see :func:`_cell` for how
    repeat sightings from one source are combined). Sources silent on a
    claim simply have no cell. Render it with :mod:`vessell.heatmap`.
    """
    sources: list[str] = []
    for check in checks:
        for sighting in check.sightings:
            if sighting.source_name not in sources:
                sources.append(sighting.source_name)

    rows: list[dict[str, Any]] = []
    for check in checks:
        result = verify_claim(check)
        by_source: dict[str, list[SourceSighting]] = {}
        for sighting in check.sightings:
            by_source.setdefault(sighting.source_name, []).append(sighting)
        rows.append(
            {
                "claim": result.claim,
                "verdict": result.verdict.value,
                "score": round(result.corroboration_score, 4),
                "independent_roots": result.independent_roots,
                "rationale": result.rationale,
                "signals": list(result.signals),
                "cells": {name: _cell(group) for name, group in by_source.items()},
            }
        )
    return {"sources": sources, "rows": rows}
