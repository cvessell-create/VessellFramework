# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Writers for human-readable and machine-readable case-run outputs."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

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
    lines.append("")
    return "\n".join(lines)


def write_outputs(result: PipelineResult, output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"

    markdown_path.write_text(render_markdown_report(result), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    return markdown_path, json_path
