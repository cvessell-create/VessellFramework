#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""VesselFramework v1.1 Provenance Firewall — compatibility entry point.

The implementation lives in ``vessell/provenance_firewall.py`` so it ships
with the installed package. This file keeps the documented path working:

    python vesselframework_reference_v1.1_provenance_firewall.py
"""

from __future__ import annotations

from vessell.provenance_firewall import (
    EvidenceItem,
    EvidenceSet,
    MaskirovkaAssessment,
    MaskirovkaVariant,
    ProvenanceRegistry,
    ProvenanceResolution,
    ProvenanceState,
    SourceStatus,
    assess_maskirovka_convergence,
    run_regression_tests,
)

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
    "run_regression_tests",
]

if __name__ == "__main__":
    raise SystemExit(run_regression_tests())
