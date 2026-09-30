# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Package access to the existing reference provenance implementation."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_reference() -> ModuleType:
    reference_path = Path(__file__).parents[1] / "vesselframework_reference_v1.1_provenance_firewall.py"
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
SourceStatus = _reference.SourceStatus
assess_maskirovka_convergence = _reference.assess_maskirovka_convergence

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
