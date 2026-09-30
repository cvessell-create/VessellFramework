#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""
VesselFramework Reference Implementation — v1.1 Provenance Firewall
====================================================================

This implementation adds a shared ProvenanceRegistry and removes local
EvidenceSet authority over source independence.

Key rule:
    absence of a local upstream marker != established independence.

This file remains a reference implementation, not constitutional authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SourceStatus(Enum):
    SOURCE_ESTABLISHED = "SOURCE-ESTABLISHED"
    FRAMEWORK_SYNTHESIS = "FRAMEWORK SYNTHESIS"
    WORKING_HYPOTHESIS = "WORKING HYPOTHESIS"
    ILLUSTRATIVE = "ILLUSTRATIVE"


class ProvenanceState(Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED_PARENT = "UNRESOLVED_PARENT"
    CYCLE = "CYCLE"
    CONFLICT = "CONFLICT"
    MISSING_RECORD = "MISSING_RECORD"


@dataclass(frozen=True)
class EvidenceItem:
    description: str
    status: SourceStatus
    source_id: str
    upstream_of: Optional[str] = None


@dataclass
class ProvenanceResolution:
    source_id: str
    root_id: Optional[str]
    state: ProvenanceState
    path: list[str] = field(default_factory=list)
    note: str = ""


class ProvenanceRegistry:
    """
    Global source graph for all EvidenceSet instances.

    The registry is authoritative for lineage resolution inside this
    executable layer. EvidenceSets group evidence; they do not determine
    independence.
    """

    def __init__(self):
        self._records: dict[str, EvidenceItem] = {}
        self._conflicts: set[str] = set()

    def register(self, item: EvidenceItem) -> None:
        existing = self._records.get(item.source_id)
        if existing is not None and existing.upstream_of != item.upstream_of:
            self._conflicts.add(item.source_id)
        self._records[item.source_id] = item

    def register_many(self, items: list[EvidenceItem]) -> None:
        for item in items:
            self.register(item)

    def resolve(self, source_id: str) -> ProvenanceResolution:
        if source_id in self._conflicts:
            return ProvenanceResolution(
                source_id, None, ProvenanceState.CONFLICT, [source_id],
                "Conflicting parent claims exist for this source_id."
            )

        if source_id not in self._records:
            return ProvenanceResolution(
                source_id, None, ProvenanceState.MISSING_RECORD, [],
                "Source is not present in the shared provenance registry."
            )

        seen: set[str] = set()
        path: list[str] = []
        current_id = source_id

        while True:
            if current_id in seen:
                path.append(current_id)
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.CYCLE, path,
                    "Cycle detected in provenance chain."
                )

            seen.add(current_id)
            path.append(current_id)

            if current_id in self._conflicts:
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.CONFLICT, path,
                    f"Conflicting parent claims detected at {current_id}."
                )

            current = self._records.get(current_id)
            if current is None:
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.MISSING_RECORD, path,
                    f"Record {current_id} is missing."
                )

            if current.upstream_of is None:
                return ProvenanceResolution(
                    source_id, current.source_id, ProvenanceState.RESOLVED, path
                )

            if current.upstream_of not in self._records:
                path.append(current.upstream_of)
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.UNRESOLVED_PARENT, path,
                    f"Parent {current.upstream_of} is not present in registry."
                )

            current_id = current.upstream_of

    def compare_independence(self, source_ids: list[str]) -> dict:
        resolutions = [self.resolve(s) for s in source_ids]
        unresolved = [r for r in resolutions if r.state != ProvenanceState.RESOLVED]
        if unresolved:
            return {
                "status": "INDETERMINATE",
                "resolutions": resolutions,
                "independent": None,
                "roots": [],
            }

        roots = [r.root_id for r in resolutions]
        return {
            "status": "RESOLVED",
            "resolutions": resolutions,
            "independent": len(set(roots)) == len(roots),
            "roots": roots,
        }


class EvidenceSet:
    def __init__(
        self,
        registry: ProvenanceRegistry,
        items: Optional[list[EvidenceItem]] = None
    ):
        self.registry = registry
        self.items = items or []
        self.registry.register_many(self.items)

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)
        self.registry.register(item)

    def provenance_resolutions(self) -> list[ProvenanceResolution]:
        return [self.registry.resolve(i.source_id) for i in self.items]

    def resolved_roots(self) -> set[str]:
        roots = set()
        for r in self.provenance_resolutions():
            if r.state == ProvenanceState.RESOLVED and r.root_id is not None:
                roots.add(r.root_id)
        return roots

    def unresolved_count(self) -> int:
        return sum(
            1 for r in self.provenance_resolutions()
            if r.state != ProvenanceState.RESOLVED
        )

    def explicit_dependency_stream_count(self) -> Optional[int]:
        """
        Returns None when any lineage is unresolved.
        This prevents missing provenance from silently becoming independence.
        """
        if self.unresolved_count():
            return None
        return len(self.resolved_roots())

    def has_only_illustrative(self) -> bool:
        return bool(self.items) and all(
            i.status == SourceStatus.ILLUSTRATIVE for i in self.items
        )

    def has_source_established(self) -> bool:
        return any(i.status == SourceStatus.SOURCE_ESTABLISHED for i in self.items)


class MaskirovkaVariant(Enum):
    BUDGETARY = "Budgetary"
    STRUCTURAL = "Structural"
    OPERATIONAL = "Operational"
    BRUTE_FORCE_STEALTH = "Brute-Force Stealth"


@dataclass
class MaskirovkaAssessment:
    variant: MaskirovkaVariant
    trigger_conditions_met: bool
    trigger_evidence: EvidenceSet
    notes: str = ""

    def eligibility(self) -> tuple[bool, str]:
        if not self.trigger_conditions_met:
            return False, "Trigger conditions not met."
        if self.trigger_evidence.has_only_illustrative():
            return False, "Illustrative-only evidence cannot establish eligibility."
        if self.trigger_evidence.unresolved_count():
            return False, "Material provenance unresolved."
        if not self.trigger_evidence.has_source_established():
            return False, "No SOURCE-ESTABLISHED evidence in current reference policy."
        return True, "Eligible under current reference policy."


def assess_maskirovka_convergence(
    assessments: list[MaskirovkaAssessment],
) -> str:
    eligible = []
    for a in assessments:
        ok, reason = a.eligibility()
        if ok:
            eligible.append(a)

    if len(eligible) < 2:
        return "No multi-variant convergence claim supported."

    # Firewall: all assessments must use the same registry instance.
    registry_ids = {id(a.trigger_evidence.registry) for a in eligible}
    if len(registry_ids) != 1:
        return (
            "CONVERGENCE STATUS: INDETERMINATE — PROVENANCE GRAPH FRACTURED. "
            "Eligible variants are not using one shared ProvenanceRegistry."
        )

    # Material unresolved provenance blocks convergence.
    if any(a.trigger_evidence.unresolved_count() for a in eligible):
        return (
            "CONVERGENCE STATUS: INDETERMINATE — PROVENANCE UNRESOLVED."
        )

    root_sets = [a.trigger_evidence.resolved_roots() for a in eligible]

    # Shared ancestry across any two variants means non-independent support.
    shared = set()
    for i in range(len(root_sets)):
        for j in range(i + 1, len(root_sets)):
            shared |= root_sets[i].intersection(root_sets[j])

    if shared:
        return (
            f"CAUTION: variants share evidentiary root(s) {sorted(shared)}. "
            "Do not treat as independent convergence."
        )

    return (
        "Convergence supported on resolved, distinct evidentiary roots. "
        "This supports architectural review, not proof by itself."
    )


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------

def _run_tests() -> int:
    failures = 0

    def check(label: str, condition: bool) -> None:
        nonlocal failures
        if not condition:
            failures += 1
        print(f"[{'PASS' if condition else 'FAIL'}] {label}")

    # 1. Cross-set shared-root test
    registry = ProvenanceRegistry()
    root = EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root")
    child_a = EvidenceItem("child A", SourceStatus.SOURCE_ESTABLISHED, "child-a", upstream_of="root")
    child_b = EvidenceItem("child B", SourceStatus.SOURCE_ESTABLISHED, "child-b", upstream_of="root")
    registry.register_many([root, child_a, child_b])

    set_a = EvidenceSet(registry, [child_a])
    set_b = EvidenceSet(registry, [child_b])

    a1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, set_a)
    a2 = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, set_b)
    verdict = assess_maskirovka_convergence([a1, a2])
    check("Cross-set children of same root are detected as shared", "CAUTION" in verdict)

    # 2. Missing parent test
    registry2 = ProvenanceRegistry()
    orphan = EvidenceItem(
        "orphan child", SourceStatus.SOURCE_ESTABLISHED, "orphan",
        upstream_of="unknown-root"
    )
    orphan_set = EvidenceSet(registry2, [orphan])
    check(
        "Missing parent returns unresolved provenance",
        orphan_set.unresolved_count() == 1
    )
    ok, reason = MaskirovkaAssessment(
        MaskirovkaVariant.BUDGETARY, True, orphan_set
    ).eligibility()
    check("Unresolved provenance blocks eligibility", ok is False)

    # 3. Cycle test
    registry3 = ProvenanceRegistry()
    a = EvidenceItem("A", SourceStatus.SOURCE_ESTABLISHED, "A", upstream_of="B")
    b = EvidenceItem("B", SourceStatus.SOURCE_ESTABLISHED, "B", upstream_of="A")
    registry3.register_many([a, b])
    check(
        "Cycle is surfaced",
        registry3.resolve("A").state == ProvenanceState.CYCLE
    )

    # 4. Conflicting-parent test
    registry4 = ProvenanceRegistry()
    x1 = EvidenceItem("X", SourceStatus.SOURCE_ESTABLISHED, "X", upstream_of="P1")
    x2 = EvidenceItem("X duplicate", SourceStatus.SOURCE_ESTABLISHED, "X", upstream_of="P2")
    registry4.register(x1)
    registry4.register(x2)
    check(
        "Conflicting parents are surfaced",
        registry4.resolve("X").state == ProvenanceState.CONFLICT
    )

    # 5. Fractured graph test
    r5a = ProvenanceRegistry()
    r5b = ProvenanceRegistry()
    s1 = EvidenceSet(r5a, [EvidenceItem("one", SourceStatus.SOURCE_ESTABLISHED, "one")])
    s2 = EvidenceSet(r5b, [EvidenceItem("two", SourceStatus.SOURCE_ESTABLISHED, "two")])
    m1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, s1)
    m2 = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, s2)
    v = assess_maskirovka_convergence([m1, m2])
    check("Fractured provenance graphs block convergence", "FRACTURED" in v)

    print(f"\n{'ALL FIREWALL REGRESSION TESTS PASSED' if failures == 0 else f'{failures} TEST(S) FAILED'}")
    return failures


if __name__ == "__main__":
    raise SystemExit(_run_tests())
