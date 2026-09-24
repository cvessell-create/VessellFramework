import json
from pathlib import Path

from vessell.app.models import PipelineCounts, PipelineResult
from vessell.app.reporting import render_markdown_report, write_outputs


def _result() -> PipelineResult:
    return PipelineResult(
        title="Deterministic Output Case",
        subject="Output fixture",
        decision_question="Does output remain stable?",
        posture="Maintain review posture.",
        confidence_ceiling="LOW",
        counts=PipelineCounts(
            total_evidence=3,
            source_established=2,
            framework_synthesis=1,
            working_hypothesis=0,
            illustrative=0,
            unresolved_lineage=1,
            independent_roots=1,
        ),
        notes=["Unresolved lineage blocks high-confidence convergence."],
        convergence_note="No convergence due to unresolved lineage.",
    )


def test_render_markdown_report_is_deterministic() -> None:
    expected = """# Deterministic Output Case

Subject: Output fixture
Decision question: Does output remain stable?

## Doctrine-to-Code Result

Confidence ceiling: LOW
Maskirovka convergence note: No convergence due to unresolved lineage.

## Evidence and Provenance Counts

- total_evidence: 3
- source_established: 2
- framework_synthesis: 1
- working_hypothesis: 0
- illustrative: 0
- unresolved_lineage: 1
- independent_roots: 1

## Analyst Posture

Maintain review posture.

## Program Notes

- Unresolved lineage blocks high-confidence convergence.
"""
    assert render_markdown_report(_result()) == expected


def test_write_outputs_writes_expected_json_and_markdown(tmp_path: Path) -> None:
    markdown_path, json_path = write_outputs(_result(), tmp_path, "deterministic-case")

    assert markdown_path.read_text(encoding="utf-8").startswith("# Deterministic Output Case")

    machine = json.loads(json_path.read_text(encoding="utf-8"))
    assert machine["title"] == "Deterministic Output Case"
    assert machine["counts"]["unresolved_lineage"] == 1
    assert machine["confidence_ceiling"] == "LOW"
