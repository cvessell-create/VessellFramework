# Doctrine-to-Code Traceability Matrix (Initial)

Purpose: provide committee-visible evidence that doctrine claims are mapped to executable behavior and test coverage.

| Doctrine requirement | Code implementation | Conformance test | Status |
|---|---|---|---|
| Distinguish SOURCE-ESTABLISHED, FRAMEWORK SYNTHESIS, WORKING HYPOTHESIS, ILLUSTRATIVE evidence classes | vessell/app/pipeline.py status parser and counts | tests/conformance/test_program_pipeline.py::test_source_status_distinction_is_preserved | Initial mapped |
| Repeated reporting from one root must not inflate independent stream count | vessell/provenance.py + vessell/app/pipeline.py independent root handling | tests/conformance/test_program_pipeline.py::test_repeated_reporting_does_not_inflate_independence | Initial mapped |
| Missing lineage must not be treated as independence | vessell/provenance.py unresolved parent state + vessell/app/pipeline.py confidence ceiling logic | tests/conformance/test_program_pipeline.py::test_confidence_is_capped_when_lineage_unresolved | Initial mapped |
| Emit deterministic machine/human outputs for case review | vessell/app/reporting.py + vessell/app/main.py output writers | (to add) end-to-end output snapshot test | Partial |
| Trace maskirovka convergence through shared provenance graph | vessell/provenance.py assess_maskirovka_convergence + vessell/app/pipeline.py | (existing) tests/test_provenance.py + (to add) cross-domain benchmark tests | Partial |

## Next Matrix Expansion

1. Add one row per Decision Provenance chain step where code support exists.
2. Add one benchmark-linked row per failure class: governance, authority, efficacy, operator-risk.
3. Add external-validation row references once benchmark outcomes are reviewed.

## Causal-path correction semantics (Section 4, redone 2026-09-30)

Grounded in Lamport (1978) happens-before and Castello/Redmond/Kuper (2024) causal separation diagrams: causal relationships are witnessed by the paths information follows.

| Section 4 rule | Code implementation | Conformance test | Status |
|---|---|---|---|
| 4. Correction carries its causal predecessor (the witnessed path) | `vessell.provenance.ClaimRecord.causal_path` / `causal_predecessor()`; stamped by `disavow()` (chains across correction-of-correction; falls back to `supersedes` for legacy records) | `tests/test_causal_paths.py::test_disavow_correction_carries_causal_path`, `test_causal_path_chains_across_correction_of_correction`, `test_causal_predecessor_falls_back_to_supersedes_for_legacy_records` | Mapped |
| 5. Dependents record HOW the claim reached them | `vessell.provenance.register_dependent(..., via=)` — the witnessed path (artifact + location + via) | `tests/test_causal_paths.py::test_register_dependent_records_via_witnessed_path`, `test_via_defaults_to_empty_for_existing_callers` | Mapped |
| 5. Causal-order delivery; no silent out-of-order completion (causal broadcast, Redmond et al. 2022) | `vessell.provenance.deliver_correction()` / `propagate_correction(..., correction_id=)` (delivery-order guard); `confirm_dependent_update(..., correction_id=)` (never-delivered + application-order guard); `CausalOrderingError` | `tests/test_causal_paths.py` (11 tests: delivery stamping, never-delivered rejection, out-of-order delivery/application rejection, wrong-claim rejection, causal-order happy path) | Mapped |

## Meta-note mechanism (Section 1: the analyst's miss, 2026-09-30)

| Section 1 rule | Code implementation | Conformance test | Status |
|---|---|---|---|
| A negative existential ("no X exists") enters UNVERIFIED and may not be reported/operationalized until ≥2 independent search paths corroborate the absence; every attempted path is recorded provenance | `vessell.verify.SearchPath`, `record_search_path()`, `search_paths()`, `gate_negative_finding()` / `require_negative_finding()` (independence = distinct strategy+source; any hit contradicts the absence; `MIN_ABSENCE_PATHS = 2`) | `tests/test_verify.py` (10 tests incl. the Castello worked example end-to-end) | Mapped |

## Tradecraft standards (ICD 203; ICPM-2020-200-01)

| Tradecraft standard | Code implementation | Conformance test | Status |
|---|---|---|---|
| ICD 203: properly describe the quality and credibility of underlying sources; properly express and explain uncertainties | `vessell.verify.verify_claim` — tier-weighted independent-root counting, independence discounting, official-record rule; verdicts express uncertainty. `gate_negative_finding()` / `require_negative_finding()` — recorded search paths are the source-quality description for negative findings; the gated-or-cleared outcome is the expressed uncertainty | `tests/test_verify.py` (corroboration scoring, official-record rule, independence discount; 10 Section 1 gate tests incl. the Castello worked example) | Mapped |
| ICPM-2020-200-01: revision/recall notices go to *all recipients of the original product* | `vessell.provenance.deliver_correction()` / `propagate_correction(..., correction_id=)` — correction delivered to every registered dependent in causal order; `confirm_dependent_update` verifies receipt (`CausalOrderingError` on never-delivered or out-of-order) | `tests/test_causal_paths.py` (delivery stamping, never-delivered rejection, out-of-order delivery/application rejection, causal-order happy path) | Mapped |

## Claim-Correction Playbook (governing doctrine: docs/claim-correction-case-study.md)

| Playbook step | Code implementation | Conformance test | Status |
|---|---|---|---|
| 1. Tag at intake | `vessell.provenance.intake_claim` (source/tier/kind/uncertainty/observed_at); `vessell.validation.require_provenance_fields` rejects untagged records | `tests/test_doctrine_reconciliation.py::test_require_provenance_fields_rejects_untagged_records`, `test_intake_records_kind_and_uncertainty` | Mapped |
| 2. Corroborate before operationalizing | `vessell.provenance.gate_for_use` / `require_gate`; `vessell.verify.verify_and_record`, `analyze_planted_news_and_record`, `detect_ghost_job_and_record`; `filter_ghost_jobs` gates LIKELY_GHOST exclusion | `test_verify_and_record_mirrors_verdict_in_claim_standing`, `test_verify_and_record_unverified_stays_gated`, `test_filter_ghost_jobs_gates_the_exclusion` | Mapped |
| 3. Explicit waivers | `vessell.provenance.record_waiver` (named/dated/reasoned); orchestrator `approve()` requires approver + change ticket | `tests/test_provenance.py` (waiver tests) | Mapped |
| 4. Disavow by supersession, never erasure | `vessell.provenance.disavow` (original kept, correction linked; kind/uncertainty/valid_until inherited) | `test_disavow_correction_inherits_kind_uncertainty_valid_until` | Mapped |
| 5. Propagate, then verify the update landed | `register_dependent` on every operational use (pipeline results, reports, weight records, scan imports, defense plans, proposals); `confirm_dependent_update` / `pending_corrections` | `test_dependent_confirmation_workflow`, `test_pipeline_intakes_evidence_and_links_result`, `test_scanner_import_claim_content`, `test_defense_plan_carries_corroborated_claim`, `test_propose_remediation_with_claim_registers_dependent` | Mapped |
| 6. Re-validate on schedule | `ClaimRecord.valid_until` / `is_stale` / `revalidate_claim`; stale CORROBORATED claims fail closed for consequential use | `test_stale_corroborated_claim_blocked_for_consequential_use`, `test_revalidate_claim_clears_staleness_and_keeps_audit_trail`, `test_claim_without_valid_until_never_goes_stale` | Mapped |
| Causal order as data (Section 4) | `vessell.provenance.record_event` / `claim_events` / `verify_event_chain` — every lifecycle transition hashed into a per-claim SHA-256 chain (each event commits to its predecessor's hash); tampering, reordering, or deletion breaks verification | `tests/test_provenance_events.py` (genesis event, full lifecycle chain, tamper/reorder/removal detection, reset clears log) | Mapped |
