"""Link historical ordinal assessment to current evidence without inflating scores."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from vessell.evaluation import sha256, verify_reports, write_reports

IMPLEMENTATION_LINKS = {
    "vesselframework_case_runner.py": [
        "vessell/harm_gate.py", "tests/test_harm_gate.py",
    ],
    "vessell/app/pipeline.py": [
        "vessell/harm_gate.py", "tests/test_harm_gate.py",
    ],
    "install_vesselframework_v3_8.py": ["tests/test_path_sync.py"],
    "vessell/app/reporting.py": ["tests/test_harm_gate.py"],
    "schemas/verification.record.schema.json": ["tests/test_schema_contracts.py"],
    "schemas/forecast.schema.json": ["tests/test_schema_contracts.py"],
    "schemas/evidence_product.schema.json": ["tests/test_schema_contracts.py"],
    "schemas/skill_record.schema.json": ["tests/test_schema_contracts.py"],
    "schemas/case.schema.json": ["tests/test_harm_gate.py", "tests/test_schema_contracts.py"],
    "vessell/app/sources/cisa_kev.py": ["tests/test_cisa_kev_intake.py"],
}


def combine_assessment(
    historical: dict[str, Any],
    data_audit: dict[str, Any],
    forecast_evaluation: dict[str, Any],
    artifact_hashes: dict[str, str],
) -> dict[str, Any]:
    for evidence in (data_audit, forecast_evaluation):
        if evidence.get("independent_external_validation") is not False:
            raise ValueError("Expected limited local evaluation, not an external efficacy claim.")
    records = historical["file_scores"]
    paths = [row["path"] for row in records]
    if len(paths) != len(set(paths)):
        raise ValueError("Historical assessment contains duplicate artifact paths.")
    links = []
    for row in records:
        linked = [
            path for path in IMPLEMENTATION_LINKS.get(row["path"], [])
            if path in artifact_hashes
        ]
        links.append({
            "path": row["path"],
            "historical_gap": row["gap"],
            "current_evidence_paths": linked,
            "status": "CURRENT_LOCAL_EVIDENCE_LINKED" if linked else "NOT_REASSESSED",
            "score_changed": False,
        })
    return {
        "evaluation": "Historical weight assessment with current validation extension",
        "independent_external_validation": False,
        "historical_assessment": copy.deepcopy(historical),
        "validation_extension": {
            "artifact_hashes": artifact_hashes,
            "artifact_gap_links": links,
            "public_data_audit": copy.deepcopy(data_audit),
            "external_forecast_scoring": copy.deepcopy(forecast_evaluation),
            "methods": [
                "docs/evaluation-methods.md", "docs/free-method-courses.md",
                "vessell/data_evidence.py", "tests/test_data_evidence.py",
            ],
            "remaining_gaps": [
                "Independent external/prospective framework validation and control outcomes.",
                "Posting-level ghost-job and source-grouped claim-verification labels.",
                "Archived weather forecast vintages and as-published outcome vintages.",
                "Controlled analyst/learning studies with meaningful outcomes.",
                "Full PDF source-content and Parquet row-level validation.",
                "Unlinked historical artifacts have not been individually reassessed.",
                "Remote GitHub and other-machine synchronization has not been verified.",
            ],
        },
        "limitations": [
            "Historical scores and roll-ups are preserved, not converted into probabilities.",
            "Evidence links indicate inspected implementation/test surfaces, not higher weights.",
            "A source hash or a passing unit test is not proof of real-world efficacy.",
            "CDC performance concerns external ensemble forecasts, not framework predictions.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment", required=True, type=Path)
    parser.add_argument("--data-audit", required=True, type=Path)
    parser.add_argument("--forecast-evaluation", required=True, type=Path)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        for report in (args.data_audit, args.forecast_evaluation):
            verify_reports(report, report.with_suffix(".md"))
        artifacts = set(IMPLEMENTATION_LINKS)
        artifacts.update(path for paths in IMPLEMENTATION_LINKS.values() for path in paths)
        artifacts.update({
            "vessell/evaluation.py", "vessell/data_evidence.py", "vessell/evidence_assessment.py",
            "tests/test_evaluation.py", "tests/test_data_evidence.py",
            "tests/test_evidence_assessment.py",
            "docs/evaluation-methods.md", "docs/free-method-courses.md",
        })
        hashes = {path: sha256(args.project_root / path) for path in sorted(artifacts)}
        result = combine_assessment(
            json.loads(args.assessment.read_text(encoding="utf-8")),
            json.loads(args.data_audit.read_text(encoding="utf-8")),
            json.loads(args.forecast_evaluation.read_text(encoding="utf-8")), hashes,
        )
        result["historical_assessment_sha256"] = sha256(args.assessment)
        result["input_report_hashes"] = {
            str(path): sha256(path) for path in (args.data_audit, args.forecast_evaluation)
        }
        machine, human = write_reports(result, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ASSESSMENT LINK FAILED: {error}", file=sys.stderr)
        return 2
    print(f"Assessment preserved and evidence linked: {machine}, {human}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
