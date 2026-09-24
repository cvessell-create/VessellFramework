# Doctrine-to-Code Traceability Matrix (Initial)

Purpose: provide committee-visible evidence that doctrine claims are mapped to executable behavior and test coverage.

| Doctrine requirement | Code implementation | Conformance test | Status |
|---|---|---|---|
| Distinguish SOURCE-ESTABLISHED, FRAMEWORK SYNTHESIS, WORKING HYPOTHESIS, ILLUSTRATIVE evidence classes | vessel/app/pipeline.py status parser and counts | tests/conformance/test_program_pipeline.py::test_source_status_distinction_is_preserved | Initial mapped |
| Repeated reporting from one root must not inflate independent stream count | vessel/provenance.py + vessel/app/pipeline.py independent root handling | tests/conformance/test_program_pipeline.py::test_repeated_reporting_does_not_inflate_independence | Initial mapped |
| Missing lineage must not be treated as independence | vessel/provenance.py unresolved parent state + vessel/app/pipeline.py confidence ceiling logic | tests/conformance/test_program_pipeline.py::test_confidence_is_capped_when_lineage_unresolved | Initial mapped |
| Emit deterministic machine/human outputs for case review | vessel/app/reporting.py + vessel/app/main.py output writers | tests/conformance/test_program_reporting.py::test_render_markdown_report_is_deterministic | Initial mapped |
| Trace maskirovka convergence through shared provenance graph | vessel/provenance.py assess_maskirovka_convergence + vessel/app/pipeline.py | (existing) tests/test_provenance.py + (to add) cross-domain benchmark tests | Partial |

## Next Matrix Expansion

1. Add one row per Decision Provenance chain step where code support exists.
2. Add one benchmark-linked row per failure class: governance, authority, efficacy, operator-risk.
3. Add external-validation row references once benchmark outcomes are reviewed.
