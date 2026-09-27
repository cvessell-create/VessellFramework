import pytest

import vessell.llm_benchmark as llm_benchmark
from vessell.llm_benchmark import DEFAULT_MODEL_MAP, ProviderResult, run_benchmark, score_response


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


def test_run_benchmark_live_path_captures_provider_errors(monkeypatch) -> None:
    def _raise_error(provider: str, model: str, prompt: str, timeout: int) -> str:
        raise RuntimeError(f"provider failure: {provider}/{model}/{timeout}")

    monkeypatch.setattr(llm_benchmark, "_call_provider", _raise_error)
    results = run_benchmark("Prompt text for benchmark", ["gpt"], DEFAULT_MODEL_MAP, dry_run=False)
    assert len(results) == 1
    result = results[0]
    assert result.provider == "gpt"
    assert result.model == DEFAULT_MODEL_MAP["gpt"]
    assert result.error is not None and "provider failure" in result.error
    assert result.weighted_score == 0.0
    assert result.response == ""
    assert result.rubric == {
        "intent_detection": 0,
        "statistical_correctness": 0,
        "r_safety_checks": 0,
        "actionability": 0,
        "noise_control": 0,
    }


def test_run_benchmark_rejects_invalid_provider_and_timeout() -> None:
    with pytest.raises(ValueError, match="Unsupported providers"):
        run_benchmark("Prompt text", ["invalid-provider"], DEFAULT_MODEL_MAP, dry_run=True)
    with pytest.raises(ValueError, match="timeout must be a positive integer"):
        run_benchmark("Prompt text", ["gpt"], DEFAULT_MODEL_MAP, dry_run=True, timeout=0)


def test_markdown_and_json_output_escape_and_serialize() -> None:
    error_result = ProviderResult(
        provider="gpt|pipe#md",
        model="model\nline*md",
        response="# Heading\ncontent\n```code```",
        rubric={
            "intent_detection": 5,
            "statistical_correctness": 4,
            "r_safety_checks": 3,
            "actionability": 2,
            "noise_control": 1,
        },
        weighted_score=77.7,
        error="bad|error\nwith#md",
    )
    success_result = ProviderResult(
        provider="claude",
        model="claude-model",
        response="response with ```triple``` backticks",
        rubric={
            "intent_detection": 3,
            "statistical_correctness": 3,
            "r_safety_checks": 3,
            "actionability": 3,
            "noise_control": 3,
        },
        weighted_score=60.0,
        error=None,
    )
    markdown = llm_benchmark._format_markdown(
        [error_result, success_result], "Prompt with | and\nnew line ```x```"
    )
    assert "gpt\\|pipe#md" in markdown
    assert "model<br>line" in markdown
    assert "gpt\\|pipe\\#md" in markdown
    assert "\\#md" in markdown
    assert "````text" in markdown
    assert "response with ```triple``` backticks" in markdown
    payload = llm_benchmark._to_jsonable([error_result], "Prompt with | and\nnew line")
    assert payload["prompt"] == "Prompt with | and\nnew line"
    serialized = payload["results"][0]
    assert serialized["provider"] == "gpt|pipe#md"
    assert serialized["weighted_score"] == 77.7
    assert serialized["error"] == "bad|error\nwith#md"


def test_enqueue_and_parse_queue_prompt(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    llm_benchmark.enqueue_prompt(queue_path, "first prompt")
    lines = queue_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert llm_benchmark._parse_queue_prompt(lines[0], "q") == "first prompt"
    assert llm_benchmark._parse_queue_prompt("plain text prompt", "q") == "plain text prompt"
    assert llm_benchmark._parse_queue_prompt('{"x":"nope"}', "q") is None


def test_run_queue_once_processes_new_prompts(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\nsecond\n{"x":"skip"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    processed = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    assert processed == 2
    assert offset_path.read_text(encoding="utf-8").strip() == "3"
    assert (output_dir / "q_000001.json").exists()
    assert (output_dir / "q_000001.md").exists()
    assert (output_dir / "q_000002.json").exists()
    assert (output_dir / "q_000002.md").exists()
    assert not (output_dir / "q_000003.json").exists()
