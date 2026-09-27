from vessell.llm_benchmark import DEFAULT_MODEL_MAP, run_benchmark, score_response


def test_score_response_rewards_workflow_and_r_checks() -> None:
    response = (
        "Use a workflow checklist: determine paired vs independent, choose paired t-test or "
        "Mann-Whitney/Wilcoxon as needed, then run names(df) and str(df) to verify column names."
    )
    rubric, weighted = score_response(response)
    assert rubric["intent_detection"] >= 4
    assert rubric["statistical_correctness"] >= 4
    assert rubric["r_safety_checks"] >= 3
    assert weighted > 70.0


def test_run_benchmark_dry_run_produces_rankable_examples() -> None:
    results = run_benchmark(
        "Prompt text for benchmark",
        ["gpt", "claude", "grok", "other"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
    )
    assert len(results) == 4
    assert all(result.error is None for result in results)
    assert all(result.response for result in results)
    assert all(result.weighted_score > 0 for result in results)
