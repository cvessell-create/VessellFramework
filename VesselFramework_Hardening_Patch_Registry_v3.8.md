# VesselFramework Hardening Patch Registry
## v1.0

| Patch ID | Trigger | Defect | Repair | Regression | Status |
|---|---|---|---|---|---|
| PF-001 | Shared ancestry lost across EvidenceSet boundaries | D25/D26 | Global ProvenanceRegistry; local sets no longer own lineage | Cross-set shared-root test | REGRESSION-PASS |
| PF-002 | Missing upstream source could look independent | D25 | UNRESOLVED_PARENT state; unresolved not counted as independent | Missing-parent test | REGRESSION-PASS |
| PF-003 | Cyclic provenance silently degraded | D22/D26 | Cycle detection surfaced; no silent root | Cycle test | REGRESSION-PASS |
| PF-004 | Same source assigned conflicting parents | D26 | CONFLICT state; quarantine behavior | Conflicting-parent test | REGRESSION-PASS |
| PF-005 | Separate registries could create false convergence | D26/D29 | Fractured graphs return INDETERMINATE | Fractured-graph test | REGRESSION-PASS |

## Promotion Status

These patches are implementation hardening controls. They should become permanent doctrine only after repeated validation confirms they generalize without creating unacceptable analytical friction.

| PF-006 | Live skill / private continuity paths drift from canonical artifact | D24 | Path Registry + hash-based synchronizer + managed memory blocks | Dry-run / apply log verification | OPEN FOR RUNTIME VALIDATION |
| PF-007 | Installation claims success without proof of write | D23/D24 | Post-write SHA-256 and append-only sync log | Simulated missing-path / write-path tests | OPEN FOR RUNTIME VALIDATION |
| PF-008 | Continuity update overwrites unrelated private memory | D14/D24 | Delimited managed-block replacement only | Managed-block preservation test | OPEN FOR RUNTIME VALIDATION |

## v3.8 note

PF-006 through PF-008 are packaged hardening controls. They cannot be marked runtime-validated until the installer is executed in an environment.


## PF-009 — Packaged State Misrepresented as Runtime State
- Failure: package/managed payload language can imply that live skill/private continuity paths are already synchronized.
- Patch: explicit package-state/runtime-state separation; require successful apply plus post-write verification before synchronization claims.
- Status: IMPLEMENTED IN v3.8.1; RUNTIME VALIDATION REQUIRED.

## PF-010 — Internal Method Leakage into External Deliverables
- Failure: internal/proprietary analytical taxonomy or mechanics are surfaced when only domain findings are needed.
- Patch: internal-method boundary plus domain-translation rule.
- Guardrail: never use confidentiality to evade academic-integrity or AI/source disclosure requirements.
- Status: IMPLEMENTED IN v3.8.1; OPERATOR-CONTROLLED DISCLOSURE.
