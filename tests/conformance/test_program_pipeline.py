import json
from pathlib import Path

from vessell.app.pipeline import run_case_pipeline


def _load_case(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_confidence_is_capped_when_lineage_unresolved() -> None:
    case = _load_case("tests/fixtures/benchmark_cases/unresolved_lineage_case.json")

    result = run_case_pipeline(case)

    assert result.counts.unresolved_lineage == 1
    assert result.confidence_ceiling == "LOW"


def test_repeated_reporting_does_not_inflate_independence() -> None:
    case = _load_case("tests/fixtures/benchmark_cases/repeated_reporting_case.json")

    result = run_case_pipeline(case)

    assert result.counts.independent_roots == 1
    assert result.confidence_ceiling == "LOW"


def test_source_status_distinction_is_preserved() -> None:
    case = _load_case("tests/fixtures/benchmark_cases/mixed_status_case.json")

    result = run_case_pipeline(case)

    assert result.counts.source_established == 1
    assert result.counts.framework_synthesis == 1
    assert result.counts.working_hypothesis == 1
    assert result.counts.illustrative == 1
