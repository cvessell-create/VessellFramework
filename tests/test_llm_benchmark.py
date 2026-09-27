import sys

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
    assert int(offset_path.read_text(encoding="utf-8").strip()) > 0
    assert len(list(output_dir.glob("*.json"))) == 2
    assert len(list(output_dir.glob("*.md"))) == 2


def test_run_queue_skips_malformed_json_and_advances_offset(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n{"q":"broken"\n[1,\nsecond\n', encoding="utf-8")
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
    assert int(offset_path.read_text(encoding="utf-8").strip()) > 0
    assert len(list(output_dir.glob("*.json"))) == 2
    assert len(list(output_dir.glob("*.md"))) == 2


def test_run_queue_resume_from_saved_offset(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n{"q":"second"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    first_processed = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    assert first_processed == 2
    original_offset = int(offset_path.read_text(encoding="utf-8").strip())
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write('{"q":"third"}\n')
    second_processed = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    assert second_processed == 1
    assert int(offset_path.read_text(encoding="utf-8").strip()) > original_offset
    assert len(list(output_dir.glob("*.json"))) == 3


def test_run_queue_rejects_non_positive_time_budget(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    with pytest.raises(ValueError, match="time_budget_seconds must be a positive number"):
        llm_benchmark.run_queue(
            queue_path,
            offset_path,
            output_dir,
            ["gpt"],
            DEFAULT_MODEL_MAP,
            dry_run=True,
            once=True,
            time_budget_seconds=0.0,
        )


def test_run_queue_stops_at_time_budget(tmp_path, monkeypatch) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n{"q":"second"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    ticks = iter([0.0, 0.0, 0.0, 2.0, 2.0, 2.0])

    def _fake_monotonic() -> float:
        return next(ticks, 2.0)

    monkeypatch.setattr(llm_benchmark.time, "monotonic", _fake_monotonic)
    processed = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
        time_budget_seconds=1.0,
    )
    assert processed == 1
    assert len(list(output_dir.glob("*.json"))) == 1


def test_run_queue_return_summary(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    summary = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
        return_summary=True,
    )
    assert isinstance(summary, llm_benchmark.QueueRunSummary)
    assert summary.processed_prompts == 1
    assert summary.exit_condition == "once_completed"
    assert summary.end_offset >= summary.start_offset


def test_runtime_controls_and_probe_budgets_parsing() -> None:
    timeout, poll, budget = llm_benchmark._resolve_runtime_controls(
        "full-package", None, None, None
    )
    assert timeout == 30
    assert poll == 0.5
    assert budget == 240.0
    assert llm_benchmark._parse_probe_budgets("1,2.5") == [1.0, 2.5]


def test_probe_matrix_outputs_artifacts(tmp_path) -> None:
    payload = llm_benchmark.run_probe_matrix(
        providers=["gpt"],
        model_map=DEFAULT_MODEL_MAP,
        budgets=[0.05],
        output_root=tmp_path / "probes",
        timeout=5,
        poll_seconds=0.01,
        queue_field="q",
        dry_run=True,
        seed_prompts=2,
        enqueue_interval_seconds=0.01,
    )
    assert payload["runs"]
    assert payload["summary_json"]
    assert payload["summary_md"]
    assert (tmp_path / "probes").exists()


def test_run_queue_rebases_after_truncation(tmp_path) -> None:
    queue_path = tmp_path / "q.jsonl"
    queue_path.write_text('{"q":"first"}\n', encoding="utf-8")
    offset_path = tmp_path / ".state" / "q.offset"
    output_dir = tmp_path / "out"
    llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    queue_path.write_text("", encoding="utf-8")
    processed = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    assert processed == 0
    assert int(offset_path.read_text(encoding="utf-8").strip()) == 0
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write('{"q":"second"}\n')
    processed_after_append = llm_benchmark.run_queue(
        queue_path,
        offset_path,
        output_dir,
        ["gpt"],
        DEFAULT_MODEL_MAP,
        dry_run=True,
        once=True,
    )
    assert processed_after_append == 1
    assert int(offset_path.read_text(encoding="utf-8").strip()) > 0


def test_main_rejects_probe_mode_conflicting_arguments(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["vf-benchmark", "--probe-session-limit", "--prompt", "conflict", "--dry-run"],
    )
    with pytest.raises(SystemExit):
        llm_benchmark.main()


def test_main_rejects_malformed_model_map(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["vf-benchmark", "--prompt", "ok", "--model-map", "{not-json", "--dry-run"],
    )
    with pytest.raises(SystemExit):
        llm_benchmark.main()


def test_empirical_secret_scan_detects_pattern_and_writes_reports(tmp_path) -> None:
    scan_root = tmp_path / "repo"
    scan_root.mkdir(parents=True, exist_ok=True)
    target = scan_root / "src" / "file.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('token = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"\n', encoding="utf-8")
    payload = llm_benchmark.run_empirical_secret_scan(
        scan_root=scan_root,
        output_root=tmp_path / "reports",
        max_findings=10,
    )
    assert payload["files_scanned"] >= 1
    assert payload["findings_count"] >= 1
    assert payload["findings"][0]["excerpt"].find("[REDACTED]") >= 0
    assert payload["summary_json"]
    assert payload["summary_md"]
    assert (tmp_path / "reports").exists()


def test_empirical_secret_scan_redacts_multiple_tokens_on_same_line(tmp_path) -> None:
    scan_root = tmp_path / "repo"
    scan_root.mkdir(parents=True, exist_ok=True)
    target = scan_root / "src" / "combo.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        'token = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456" github_pat_abcdefghijklmnoqrstuvwxyz12345\n',
        encoding="utf-8",
    )
    payload = llm_benchmark.run_empirical_secret_scan(
        scan_root=scan_root,
        output_root=tmp_path / "reports",
        max_findings=10,
    )
    assert payload["findings_count"] >= 1
    excerpts = [item["excerpt"] for item in payload["findings"]]
    assert all("sk-" not in excerpt for excerpt in excerpts)
    assert all("github_pat_" not in excerpt for excerpt in excerpts)
    assert any("[REDACTED]" in excerpt for excerpt in excerpts)


def test_empirical_secret_scan_rejects_invalid_max_findings(tmp_path) -> None:
    with pytest.raises(ValueError, match="max_findings must be a positive integer"):
        llm_benchmark.run_empirical_secret_scan(
            scan_root=tmp_path,
            output_root=tmp_path / "reports",
            max_findings=0,
        )


def test_empirical_secret_scan_skips_nested_excluded_paths(tmp_path) -> None:
    scan_root = tmp_path / "repo"
    nested = scan_root / "tests" / "unit" / "sample.py"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_text('token = "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"\n', encoding="utf-8")
    payload = llm_benchmark.run_empirical_secret_scan(
        scan_root=scan_root,
        output_root=tmp_path / "reports",
        max_findings=10,
    )
    assert payload["findings_count"] == 0
