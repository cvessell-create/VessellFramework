# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Writers for human-readable and machine-readable case-run outputs."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from vessell.provenance import register_dependent

from .models import PipelineResult


def render_markdown_report(result: PipelineResult) -> str:
    counts = result.counts
    lines = [
        f"# {result.title}",
        "",
        f"Subject: {result.subject}",
        f"Decision question: {result.decision_question}",
        "",
        "## Doctrine-to-Code Result",
        "",
        f"Confidence ceiling: {result.confidence_ceiling}",
        f"Maskirovka convergence note: {result.convergence_note}",
        "",
        "## Evidence and Provenance Counts",
        "",
        f"- total_evidence: {counts.total_evidence}",
        f"- source_established: {counts.source_established}",
        f"- framework_synthesis: {counts.framework_synthesis}",
        f"- working_hypothesis: {counts.working_hypothesis}",
        f"- illustrative: {counts.illustrative}",
        f"- unresolved_lineage: {counts.unresolved_lineage}",
        f"- independent_roots: {counts.independent_roots}",
        "",
        "## Analyst Posture",
        "",
        result.posture,
        "",
        "## Program Notes",
        "",
    ]
    if result.notes:
        for note in result.notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No additional notes.")
    lines.extend(["", "## Harm Gate", ""])
    if result.harm_gate is None:
        lines.append("- UNKNOWN: no Harm Gate result; review required.")
    else:
        lines.extend([
            f"- Exposure: {result.harm_gate.exposure}",
            f"- Cleared by intake gate: {result.harm_gate.cleared}",
            f"- Missing fields: {', '.join(result.harm_gate.missing_fields) or 'None'}",
        ])
        lines.extend(f"- {item}" for item in result.harm_gate.safeguards)
    lines.extend([
        "",
        ("This report structures supplied evidence; it does not independently verify "
         "source contents or establish control efficacy."),
    ])
    lines.append("")
    return "\n".join(lines)


def write_outputs(result: PipelineResult, output_dir: Path, stem: str) -> tuple[Path, Path]:
    """Write the markdown and JSON reports; register them as dependents.

    Each written artifact registers itself against the provenance claims
    the result was derived from, so a later correction of a claim
    propagates to the exact report files that consumed it.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    markdown_path.write_text(render_markdown_report(result), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    verify_outputs(result, markdown_path, json_path)
    for claim_id in result.claim_ids:
        register_dependent(
            claim_id,
            artifact="vessell.app.reporting.case-report",
            location=str(markdown_path),
        )
        register_dependent(
            claim_id,
            artifact="vessell.app.reporting.case-report",
            location=str(json_path),
        )
    return markdown_path, json_path


def verify_outputs(result: PipelineResult, markdown_path: Path, json_path: Path) -> None:
    expected = json.loads(json.dumps(asdict(result)))
    actual = json.loads(json_path.read_text(encoding="utf-8"))
    if actual != expected or markdown_path.read_text(encoding="utf-8") != render_markdown_report(result):
        raise ValueError("Case report files do not match the evaluated pipeline result.")
