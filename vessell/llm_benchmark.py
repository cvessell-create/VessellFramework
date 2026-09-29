"""Cross-model prompt benchmarking with weighted scoring for workflow quality."""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

RUBRIC_WEIGHTS: Final[dict[str, float]] = {
    "intent_detection": 0.25,
    "statistical_correctness": 0.30,
    "r_safety_checks": 0.20,
    "actionability": 0.15,
    "noise_control": 0.10,
}

DEFAULT_MODEL_MAP: Final[dict[str, str]] = {
    "gpt": "gpt-4.1-mini",
    "claude": "claude-3-5-sonnet-latest",
    "grok": "grok-4-latest",
    "other": "openrouter/auto",
}
SUPPORTED_PROVIDERS: Final[set[str]] = {"gpt", "claude", "grok", "other"}

DEFAULT_BASE_URLS: Final[dict[str, str]] = {
    "gpt": "https://api.openai.com/v1/chat/completions",
    "grok": "https://api.x.ai/v1/chat/completions",
    "other": "https://openrouter.ai/api/v1/chat/completions",
}

DEFAULT_ANTHROPIC_URL: Final[str] = "https://api.anthropic.com/v1/messages"
SYSTEM_PROMPT: Final[str] = (
    "You are being evaluated for practical workflow quality. "
    "Answer clearly and with actionable steps."
)
DEFAULT_TIMEOUT_SECONDS: Final[int] = 45
DEFAULT_POLL_SECONDS: Final[float] = 1.0
DEFAULT_PROBE_BUDGETS: Final[tuple[int, ...]] = (60, 120, 300, 600, 900)
RUNTIME_PROFILES: Final[dict[str, dict[str, float | int | None]]] = {
    "default": {
        "timeout": DEFAULT_TIMEOUT_SECONDS,
        "poll_seconds": DEFAULT_POLL_SECONDS,
        "time_budget_seconds": None,
    },
    "full-package": {
        "timeout": 30,
        "poll_seconds": 0.5,
        "time_budget_seconds": 240.0,
    },
}
SECRET_SCAN_EXCLUDE_GLOBS: Final[tuple[str, ...]] = (
    ".git/*",
    ".venv/*",
    ".pytest_cache/*",
    ".mypy_cache/*",
    ".ruff_cache/*",
    "__pycache__/*",
    "outputs/*",
    "tests/*",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.pdf",
    "*.docx",
    "*.pptx",
    "*.xlsx",
    "*.ttf",
    "*.zip",
    "*.pyc",
)
SECRET_SCAN_EXCLUDED_DIRS: Final[set[str]] = {
    ".git",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "tests",
    "outputs",
}
SECRET_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "github_pat": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "aws_access_key_id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    "jwt_like_token": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "stripe_live_key": re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"),
    "secret_scan_checkphrase": re.compile(r"(?i)\bmother secret scan check\b"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(api[_-]?key|token|password|secret)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
}

EXAMPLE_RESPONSES: Final[dict[str, str]] = {
    "gpt": (
        "Use a checklist: first classify design (paired vs independent), then pick the test "
        "(paired t/Wilcoxon for paired, independent t/Mann-Whitney for independent), then run "
        "R safety checks (`names()`, `str()`, object existence, numeric types)."
    ),
    "claude": (
        "I would run this in three gates: design gate, test-selection gate, and data-integrity gate. "
        "Design gate asks whether repeated measures are on the same participants. Test gate maps "
        "normal paired data to dependent t-tests and non-normal to Wilcoxon; independent data maps "
        "to independent t-test or Mann-Whitney. Data-integrity gate confirms column names and types."
    ),
    "grok": (
        "Fast workflow: 1) identify unit and pairing, 2) inspect distribution and outliers, "
        "3) choose test, 4) run `names(df)` and `str(df)` before coding, 5) execute and report "
        "p-value + effect size."
    ),
    "other": (
        "Treat this as process optimization. Build a reusable preflight block in R that checks "
        "column names, missing values, object existence, and numeric coercion before any inferential test."
    ),
}


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    model: str
    response: str
    rubric: dict[str, int]
    weighted_score: float
    error: str | None = None


@dataclass(frozen=True)
class QueueRunSummary:
    processed_prompts: int
    start_utc: str
    end_utc: str
    start_offset: int
    end_offset: int
    exit_condition: str
    time_budget_seconds: float | None


@dataclass(frozen=True)
class SecretFinding:
    file: str
    line: int
    detector: str
    excerpt: str


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_upstream_meta(mode: str, parameters: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "mode": mode,
        "generated_at_utc": _utc_now_iso(),
        "parameters": parameters or {},
        "steps": [],
    }


def _record_upstream_step(meta: dict[str, object], step: str, **details: object) -> None:
    steps = meta.setdefault("steps", [])
    if not isinstance(steps, list):
        meta["steps"] = []
        steps = meta["steps"]
    payload = {"time_utc": _utc_now_iso(), "step": step}
    if details:
        payload["details"] = details
    steps.append(payload)


def _collect_pull_history(history_root: Path, pattern: str = "*.json") -> dict[str, object]:
    root = history_root.resolve()
    if not root.exists():
        return {"history_root": str(root), "artifact_count": 0, "artifacts": []}
    artifacts = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob(pattern)
        if path.is_file()
    )
    return {
        "history_root": str(root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def _json_files_by_mtime(root: Path, pattern: str = "*.json") -> list[Path]:
    files = [path for path in root.rglob(pattern) if path.is_file()]
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return files


def _git_current_branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    branch = result.stdout.strip()
    return branch if branch else "unknown"


def _git_local_branches(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "for-each-ref", "--format=%(refname:short)", "refs/heads"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_branch_json_metadata(repo_root: Path, branch: str, root_rel: str) -> list[dict[str, object]]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-tree", "-r", "-l", branch, "--", root_rel],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    artifacts: list[dict[str, object]] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or "\t" not in line:
            continue
        left, path = line.split("\t", 1)
        if not path.endswith(".json") or path.endswith("history_index.json"):
            continue
        parts = left.split()
        blob_sha = parts[2] if len(parts) >= 3 else None
        size_token = parts[3] if len(parts) >= 4 else None
        size_bytes = int(size_token) if size_token and size_token.isdigit() else None
        artifacts.append({"path": path, "blob_sha": blob_sha, "size_bytes": size_bytes})
    return artifacts


def _classify_history_artifact(path: Path) -> str:
    name = path.name
    if name == "probe_summary.json":
        return "probe_summary"
    if name == "secret_scan_report.json":
        return "secret_scan_report"
    if name == "latest_benchmark.json":
        return "benchmark"
    if name.startswith("q_") and name.endswith(".json"):
        return "queue_benchmark"
    return "other"


def _build_history_index(
    history_root: Path,
    history_limit: int,
    *,
    include_all_branches: bool = False,
    repo_root: Path | None = None,
    parallel_workers: int = 4,
) -> dict[str, object]:
    root = history_root.resolve()
    if history_limit <= 0:
        raise ValueError("history_limit must be a positive integer.")
    if parallel_workers <= 0:
        raise ValueError("parallel_workers must be a positive integer.")
    if not root.exists():
        return {
            "generated_at_utc": _utc_now_iso(),
            "history_root": str(root),
            "history_limit": history_limit,
            "include_all_branches": include_all_branches,
            "parallel_collection": {
                "enabled": include_all_branches,
                "workers": parallel_workers,
                "branches_scanned": 0,
                "branch_jobs_completed": 0,
            },
            "artifacts_total": 0,
            "artifacts": [],
            "analytics": {
                "artifacts_by_type": {},
                "benchmark_weighted_score_summary": {"count": 0, "avg": None, "min": None, "max": None},
                "secret_matches_total": 0,
                "probe_runs_total": 0,
            },
        }
    artifacts: list[dict[str, object]] = []
    by_type: dict[str, int] = {}
    branches_seen: dict[str, int] = {}
    branches_scanned = 0
    branch_jobs_completed = 0

    def _consume_path(
        rel_path: str,
        branch: str,
        *,
        source: str,
        size_bytes: int | None = None,
        blob_sha: str | None = None,
    ) -> None:
        artifact_type = _classify_history_artifact(Path(rel_path))
        by_type[artifact_type] = by_type.get(artifact_type, 0) + 1
        branches_seen[branch] = branches_seen.get(branch, 0) + 1
        artifacts.append(
            {
                "path": rel_path,
                "type": artifact_type,
                "generated_at_utc": None,
                "branch": branch,
                "source": source,
                "size_bytes": size_bytes,
                "blob_sha": blob_sha,
            }
        )

    if include_all_branches and repo_root is not None:
        resolved_repo = repo_root.resolve()
        current_branch = _git_current_branch(resolved_repo)
        branches = _git_local_branches(resolved_repo)
        if current_branch and current_branch in branches:
            branches = [current_branch] + [item for item in branches if item != current_branch]
        try:
            root_rel = root.relative_to(resolved_repo).as_posix()
        except ValueError:
            root_rel = root.as_posix()
        branches_scanned = len(branches)
        workers = min(parallel_workers, max(1, len(branches)))
        branch_artifacts: dict[str, list[dict[str, object]]] = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(_git_branch_json_metadata, resolved_repo, branch, root_rel): branch
                for branch in branches
            }
            for future, branch in ((item, future_map[item]) for item in future_map):
                entries = future.result()
                branch_artifacts[branch] = entries
                branch_jobs_completed += 1
        for branch in branches:
            for entry in branch_artifacts.get(branch, []):
                path_str = str(entry.get("path", ""))
                size_bytes = entry.get("size_bytes")
                blob_sha = entry.get("blob_sha")
                rel_path = path_str[len(root_rel) + 1 :] if path_str.startswith(f"{root_rel}/") else path_str
                _consume_path(
                    rel_path,
                    branch,
                    source="git_branch",
                    size_bytes=size_bytes if isinstance(size_bytes, int) else None,
                    blob_sha=blob_sha if isinstance(blob_sha, str) else None,
                )
                if len(artifacts) >= history_limit:
                    break
            if len(artifacts) >= history_limit:
                break
    else:
        branch_root = repo_root.resolve() if repo_root is not None else Path.cwd()
        current_branch = _git_current_branch(branch_root)
        branches_scanned = 1
        branch_jobs_completed = 1
        for path in _json_files_by_mtime(root):
            if path.name == "history_index.json":
                continue
            stat = path.stat()
            _consume_path(
                path.relative_to(root).as_posix(),
                current_branch,
                source="working_tree",
                size_bytes=int(stat.st_size),
                blob_sha=None,
            )
            if len(artifacts) >= history_limit:
                break
    analytics = {
        "artifacts_by_type": by_type,
        "branch_artifact_counts": branches_seen,
        "benchmark_weighted_score_summary": {"count": None, "avg": None, "min": None, "max": None},
        "secret_matches_total": None,
        "probe_runs_total": None,
    }
    return {
        "generated_at_utc": _utc_now_iso(),
        "history_root": str(root),
        "history_limit": history_limit,
        "include_all_branches": include_all_branches,
        "parallel_collection": {
            "enabled": include_all_branches,
            "workers": parallel_workers,
            "branches_scanned": branches_scanned,
            "branch_jobs_completed": branch_jobs_completed,
        },
        "artifacts_total": len(artifacts),
        "artifacts": artifacts,
        "analytics": analytics,
    }


def _write_history_exports(
    history_root: Path,
    *,
    history_limit: int,
    export_csv: bool,
    include_all_branches: bool = False,
    repo_root: Path | None = None,
    parallel_workers: int = 4,
) -> dict[str, str | int]:
    payload = _build_history_index(
        history_root,
        history_limit,
        include_all_branches=include_all_branches,
        repo_root=repo_root,
        parallel_workers=parallel_workers,
    )
    root = history_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    index_json = root / "history_index.json"
    index_md = root / "history_index.md"
    index_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    index_md.write_text(
        "# History Index\n\nSee history_index.json and history dump files for full metadata.\n",
        encoding="utf-8",
    )

    dump_jsonl_path = root / "history_dump.jsonl"
    with dump_jsonl_path.open("w", encoding="utf-8") as handle:
        for item in payload["artifacts"]:
            if isinstance(item, dict):
                handle.write(json.dumps(item, separators=(",", ":")) + "\n")

    dump_csv_path = root / "history_dump.csv"
    with dump_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["branch", "path", "type", "source", "size_bytes", "blob_sha", "generated_at_utc"],
        )
        writer.writeheader()
        for item in payload["artifacts"]:
            if isinstance(item, dict):
                writer.writerow(
                    {
                        "branch": item.get("branch"),
                        "path": item.get("path"),
                        "type": item.get("type"),
                        "source": item.get("source"),
                        "size_bytes": item.get("size_bytes"),
                        "blob_sha": item.get("blob_sha"),
                        "generated_at_utc": item.get("generated_at_utc"),
                    }
                )

    benchmark_csv = ""
    artifacts_csv = str(dump_csv_path)
    if export_csv:
        artifacts_csv_path = root / "history_artifacts.csv"
        with artifacts_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "branch",
                    "path",
                    "type",
                    "source",
                    "size_bytes",
                    "blob_sha",
                    "generated_at_utc",
                ],
            )
            writer.writeheader()
            for item in payload["artifacts"]:
                if isinstance(item, dict):
                    writer.writerow(
                        {
                            "branch": item.get("branch"),
                            "path": item.get("path"),
                            "type": item.get("type"),
                            "source": item.get("source"),
                            "size_bytes": item.get("size_bytes"),
                            "blob_sha": item.get("blob_sha"),
                            "generated_at_utc": item.get("generated_at_utc"),
                        }
                    )
        artifacts_csv = str(artifacts_csv_path)

        benchmark_csv_path = root / "history_benchmark_scores.csv"
        with benchmark_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["branch", "artifact_path", "artifact_type", "provider", "model", "weighted_score"],
            )
            writer.writeheader()
            for item in payload["artifacts"]:
                if not isinstance(item, dict):
                    continue
                if item.get("type") not in {"benchmark", "queue_benchmark"}:
                    continue
                writer.writerow(
                    {
                        "branch": item.get("branch"),
                        "artifact_path": item.get("path"),
                        "artifact_type": item.get("type"),
                        "provider": "",
                        "model": "",
                        "weighted_score": "",
                    }
                )
        benchmark_csv = str(benchmark_csv_path)

    return {
        "history_index_json": str(index_json),
        "history_index_md": str(index_md),
        "history_dump_jsonl": str(dump_jsonl_path),
        "history_dump_csv": str(dump_csv_path),
        "history_artifacts_csv": artifacts_csv,
        "history_benchmark_scores_csv": benchmark_csv,
        "artifacts_total": int(payload["artifacts_total"]),
    }


def _format_http_error(error: urllib.error.HTTPError) -> str:
    try:
        body = error.read().decode("utf-8", errors="replace").strip()
    except OSError:
        body = ""
    detail = body if body else str(error)
    return f"HTTP {error.code}: {detail}"


def _clip(value: int) -> int:
    return max(0, min(5, value))


def _score_intent_detection(response: str) -> int:
    lowered = response.lower()
    score = 0
    if any(term in lowered for term in ("workflow", "checklist", "process", "step")):
        score += 3
    if "not" in lowered and ("single error" in lowered or "debug" in lowered):
        score += 1
    if any(term in lowered for term in ("paired", "independent")):
        score += 1
    return _clip(score)


def _score_statistical_correctness(response: str) -> int:
    lowered = response.lower()
    score = 0
    if "paired" in lowered and "independent" in lowered:
        score += 2
    if any(term in lowered for term in ("paired t", "dependent t", "independent t")):
        score += 1
    if any(term in lowered for term in ("wilcoxon", "mann-whitney", "mann whitney")):
        score += 1
    if any(term in lowered for term in ("normal", "normality", "shapiro")):
        score += 1
    return _clip(score)


def _score_r_safety(response: str) -> int:
    lowered = response.lower()
    score = 0
    if "names(" in response or "names()" in lowered:
        score += 2
    if "str(" in response or "str()" in lowered:
        score += 1
    if any(term in lowered for term in ("case-sensitive", "case sensitive", "column name", "object")):
        score += 1
    if any(term in lowered for term in ("numeric", "missing", "na")):
        score += 1
    return _clip(score)


def _score_actionability(response: str) -> int:
    lowered = response.lower()
    numbered_steps = len(re.findall(r"(?:^|\s)(?:\d\)|\d\.|first|then|next|finally)\b", lowered))
    score = 2 if numbered_steps >= 2 else 1 if numbered_steps == 1 else 0
    if any(token in response for token in ("`names(", "`str(", "->", "<-")):
        score += 1
    if any(term in lowered for term in ("check", "run", "use", "confirm")):
        score += 1
    if len(response.split()) >= 40:
        score += 1
    return _clip(score)


def _score_noise_control(response: str) -> int:
    lowered = response.lower()
    score = 5
    if len(response.split()) > 220:
        score -= 2
    if len(response.split()) > 320:
        score -= 1
    if any(term in lowered for term in ("as an ai", "cannot provide", "maybe maybe", "lorem")):
        score -= 1
    return _clip(score)


def score_response(response: str) -> tuple[dict[str, int], float]:
    """Score one response against the workflow rubric."""
    if not isinstance(response, str) or not response.strip():
        raise ValueError("response must be a non-empty string.")
    rubric = {
        "intent_detection": _score_intent_detection(response),
        "statistical_correctness": _score_statistical_correctness(response),
        "r_safety_checks": _score_r_safety(response),
        "actionability": _score_actionability(response),
        "noise_control": _score_noise_control(response),
    }
    weighted = 0.0
    for key, weight in RUBRIC_WEIGHTS.items():
        weighted += (rubric[key] / 5.0) * weight * 100.0
    return rubric, round(weighted, 2)


def _http_json_post(url: str, headers: dict[str, str], body: dict[str, object], timeout: int) -> dict[str, object]:
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url=url, data=payload, method="POST")
    for key, value in headers.items():
        request.add_header(key, value)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_data = response.read().decode("utf-8")
    parsed = json.loads(response_data)
    if not isinstance(parsed, dict):
        raise ValueError("API response must decode to a JSON object.")
    return parsed


def _extract_openai_compatible_text(response_json: dict[str, object]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Missing choices in provider response.")
    first = choices[0]
    if not isinstance(first, dict):
        raise ValueError("Invalid choice object.")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ValueError("Missing message object.")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Missing textual message content.")
    return content.strip()


def _extract_anthropic_text(response_json: dict[str, object]) -> str:
    content = response_json.get("content")
    if not isinstance(content, list) or not content:
        raise ValueError("Missing content blocks in Anthropic response.")
    text_parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            text_value = block.get("text")
            if isinstance(text_value, str) and text_value.strip():
                text_parts.append(text_value.strip())
    if not text_parts:
        raise ValueError("No text blocks found in Anthropic response.")
    return "\n".join(text_parts)


def _provider_key_env(provider: str) -> str:
    if provider == "gpt":
        return "OPENAI_API_KEY"
    if provider == "claude":
        return "ANTHROPIC_API_KEY"
    if provider == "grok":
        return "XAI_API_KEY"
    return "OTHER_API_KEY"


def _call_provider(provider: str, model: str, prompt: str, timeout: int) -> str:
    import os

    env_name = _provider_key_env(provider)
    api_key = os.environ.get(env_name)
    if not api_key:
        raise RuntimeError(
            f"Missing API key environment variable '{env_name}' for provider '{provider}'."
        )
    if provider == "claude":
        response_json = _http_json_post(
            url=DEFAULT_ANTHROPIC_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            body={
                "model": model,
                "max_tokens": 700,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        return _extract_anthropic_text(response_json)
    base_url = DEFAULT_BASE_URLS[provider]
    if provider == "other":
        base_url = os.environ.get("OTHER_BASE_URL", base_url)
    response_json = _http_json_post(
        url=base_url,
        headers={"authorization": "Bearer " + api_key, "content-type": "application/json"},
        body={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=timeout,
    )
    return _extract_openai_compatible_text(response_json)


def run_benchmark(
    prompt: str,
    providers: list[str],
    model_map: dict[str, str],
    *,
    dry_run: bool = False,
    timeout: int = 45,
) -> list[ProviderResult]:
    """Run the prompt against selected providers and score each response."""
    if not prompt.strip():
        raise ValueError("prompt must be non-empty.")
    if timeout <= 0:
        raise ValueError("timeout must be a positive integer.")
    unknown = [provider for provider in providers if provider not in SUPPORTED_PROVIDERS]
    if unknown:
        raise ValueError(f"Unsupported providers: {unknown}. Allowed: {sorted(SUPPORTED_PROVIDERS)}")
    results: list[ProviderResult] = []
    for provider in providers:
        if provider not in model_map:
            raise ValueError(f"Missing model mapping for provider: {provider}")
        model = model_map[provider]
        if dry_run:
            response_text = EXAMPLE_RESPONSES.get(
                provider,
                "Use a checklist workflow and run data-name preflight checks before analysis.",
            )
            rubric, weighted_score = score_response(response_text)
            results.append(
                ProviderResult(
                    provider=provider,
                    model=model,
                    response=response_text,
                    rubric=rubric,
                    weighted_score=weighted_score,
                )
            )
            continue
        try:
            response_text = _call_provider(provider, model, prompt, timeout)
            rubric, weighted_score = score_response(response_text)
            results.append(
                ProviderResult(
                    provider=provider,
                    model=model,
                    response=response_text,
                    rubric=rubric,
                    weighted_score=weighted_score,
                )
            )
        except urllib.error.HTTPError as error:
            results.append(
                ProviderResult(
                    provider=provider,
                    model=model,
                    response="",
                    rubric={key: 0 for key in RUBRIC_WEIGHTS},
                    weighted_score=0.0,
                    error=_format_http_error(error),
                )
            )
        except (RuntimeError, OSError, ValueError, urllib.error.URLError) as error:
            results.append(
                ProviderResult(
                    provider=provider,
                    model=model,
                    response="",
                    rubric={key: 0 for key in RUBRIC_WEIGHTS},
                    weighted_score=0.0,
                    error=str(error),
                )
            )
    return results


def _format_markdown(
    results: list[ProviderResult], prompt: str, upstream_meta: dict[str, object] | None = None
) -> str:
    def _cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", "<br>")

    def _safe_inline(value: str) -> str:
        cleaned = value.replace("\n", " ").replace("\r", " ")
        for token in ("\\", "`", "*", "_", "[", "]", "(", ")", "#", "|"):
            cleaned = cleaned.replace(token, f"\\{token}")
        return cleaned

    def _fenced_lines(value: str) -> list[str]:
        runs = [len(match.group(0)) for match in re.finditer(r"`+", value)]
        fence = "`" * (max(runs, default=2) + 1)
        if len(fence) < 3:
            fence = "```"
        return [fence + "text", value, fence]

    lines = [
        "# LLM Prompt Benchmark",
        "",
        "## Prompt",
        "",
        *_fenced_lines(prompt),
        "",
        "## Weighted results",
        "",
        "| Provider | Model | Weighted Score | Error |",
        "|---|---|---:|---|",
    ]
    for result in sorted(results, key=lambda item: item.weighted_score, reverse=True):
        error_value = result.error if result.error else ""
        lines.append(
            f"| {_cell(result.provider)} | {_cell(result.model)} | {result.weighted_score:.2f} | {_cell(error_value)} |"
        )
    lines.append("")
    lines.append("## Response examples")
    lines.append("")
    for result in results:
        lines.append("### Response sample")
        lines.append("")
        lines.append(f"- Provider: {_safe_inline(result.provider)}")
        lines.append(f"- Model: {_safe_inline(result.model)}")
        if result.error:
            lines.append(f"- Error: {_safe_inline(result.error)}")
        else:
            lines.extend(_fenced_lines(result.response))
        lines.append("")
        lines.append(
            f"- Rubric: intent={result.rubric['intent_detection']}, "
            f"stats={result.rubric['statistical_correctness']}, "
            f"r_safety={result.rubric['r_safety_checks']}, "
            f"actionability={result.rubric['actionability']}, "
            f"noise={result.rubric['noise_control']}"
        )
        lines.append("")
    if upstream_meta:
        pull_history = upstream_meta.get("pull_history")
        pull_count = (
            pull_history.get("artifact_count")
            if isinstance(pull_history, dict)
            else "n/a"
        )
        lines.extend(
            [
                "## Upstream process meta",
                "",
                f"- Mode: {upstream_meta.get('mode')}",
                f"- Generated at: {upstream_meta.get('generated_at_utc')}",
                f"- Steps recorded: {len(upstream_meta.get('steps', []))}",
                f"- Pull history artifacts: {pull_count}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _parse_model_map(model_map_arg: str | None, providers: list[str]) -> dict[str, str]:
    model_map = dict(DEFAULT_MODEL_MAP)
    if model_map_arg:
        try:
            parsed = json.loads(model_map_arg)
        except json.JSONDecodeError as error:
            raise ValueError("--model-map must be valid JSON.") from error
        if not isinstance(parsed, dict):
            raise ValueError("--model-map must decode to a JSON object.")
        for provider, model in parsed.items():
            if not isinstance(provider, str) or not isinstance(model, str):
                raise ValueError("--model-map entries must be string:string.")
            if provider.strip() not in SUPPORTED_PROVIDERS:
                raise ValueError(
                    f"--model-map only supports providers {sorted(SUPPORTED_PROVIDERS)}."
                )
            model_map[provider.strip()] = model.strip()
    missing = [provider for provider in providers if provider not in model_map]
    if missing:
        raise ValueError(f"Model map missing providers: {missing}")
    return model_map


def _to_jsonable(
    results: list[ProviderResult], prompt: str, upstream_meta: dict[str, object] | None = None
) -> dict[str, object]:
    payload = {
        "prompt": prompt,
        "weights": RUBRIC_WEIGHTS,
        "results": [
            {
                "provider": result.provider,
                "model": result.model,
                "weighted_score": result.weighted_score,
                "rubric": result.rubric,
                "error": result.error,
                "response": result.response,
            }
            for result in results
        ],
    }
    if upstream_meta is not None:
        payload["upstream_meta"] = upstream_meta
    return payload


def _write_benchmark_outputs(
    prompt: str,
    results: list[ProviderResult],
    json_path: Path,
    md_path: Path,
    upstream_meta: dict[str, object] | None = None,
) -> None:
    json_payload = _to_jsonable(results, prompt, upstream_meta=upstream_meta)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    md_path.write_text(_format_markdown(results, prompt, upstream_meta=upstream_meta), encoding="utf-8")


def _parse_queue_prompt(line: str, field: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        value = parsed.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None
    return stripped


def _load_offset(offset_path: Path) -> int:
    if not offset_path.exists():
        return 0
    raw = offset_path.read_text(encoding="utf-8").strip()
    if not raw:
        return 0
    try:
        value = int(raw)
    except ValueError:
        return 0
    return max(0, value)


def _save_offset(offset_path: Path, offset: int) -> None:
    offset_path.parent.mkdir(parents=True, exist_ok=True)
    offset_path.write_text(str(max(0, offset)), encoding="utf-8")


def enqueue_prompt(queue_path: Path, prompt: str, *, field: str = "q") -> None:
    if not prompt.strip():
        raise ValueError("prompt must be non-empty.")
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    record = {field: prompt.strip()}
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")


def _make_queue_summary(
    *,
    processed_prompts: int,
    started_at: datetime,
    start_offset: int,
    end_offset: int,
    exit_condition: str,
    time_budget_seconds: float | None,
) -> QueueRunSummary:
    ended_at = datetime.now(timezone.utc)
    return QueueRunSummary(
        processed_prompts=processed_prompts,
        start_utc=started_at.isoformat(),
        end_utc=ended_at.isoformat(),
        start_offset=start_offset,
        end_offset=end_offset,
        exit_condition=exit_condition,
        time_budget_seconds=time_budget_seconds,
    )


def run_queue(
    queue_path: Path,
    offset_path: Path,
    output_dir: Path,
    providers: list[str],
    model_map: dict[str, str],
    *,
    queue_field: str = "q",
    dry_run: bool = False,
    timeout: int = 45,
    once: bool = False,
    poll_seconds: float = 1.0,
    time_budget_seconds: float | None = None,
    return_summary: bool = False,
    history_root: Path | None = None,
) -> int | QueueRunSummary:
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be a positive number.")
    if time_budget_seconds is not None and time_budget_seconds <= 0:
        raise ValueError("time_budget_seconds must be a positive number.")
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.touch(exist_ok=True)
    queue_meta = _new_upstream_meta(
        "queue",
        {
            "queue_path": str(queue_path),
            "offset_path": str(offset_path),
            "output_dir": str(output_dir),
            "queue_field": queue_field,
            "dry_run": dry_run,
            "timeout": timeout,
            "once": once,
            "poll_seconds": poll_seconds,
            "time_budget_seconds": time_budget_seconds,
        },
    )
    queue_meta["pull_history"] = _collect_pull_history(output_dir, "*.json")
    if history_root is not None:
        queue_meta["global_pull_history"] = _collect_pull_history(history_root, "*.json")
    _record_upstream_step(queue_meta, "queue_initialized")
    offset_token = _load_offset(offset_path)
    start_offset = offset_token
    started_at = datetime.now(timezone.utc)
    processed_prompts = 0
    deadline = (
        time.monotonic() + time_budget_seconds
        if time_budget_seconds is not None
        else None
    )

    def budget_reached() -> bool:
        return deadline is not None and time.monotonic() >= deadline

    while True:
        if budget_reached():
            summary = _make_queue_summary(
                processed_prompts=processed_prompts,
                started_at=started_at,
                start_offset=start_offset,
                end_offset=offset_token,
                exit_condition="time_budget_reached",
                time_budget_seconds=time_budget_seconds,
            )
            return summary if return_summary else processed_prompts
        with queue_path.open("r", encoding="utf-8") as handle:
            handle.seek(0, 2)
            end_of_file = handle.tell()
            if offset_token > end_of_file:
                offset_token = 0
                _save_offset(offset_path, offset_token)
            handle.seek(offset_token)
            while True:
                if budget_reached():
                    summary = _make_queue_summary(
                        processed_prompts=processed_prompts,
                        started_at=started_at,
                        start_offset=start_offset,
                        end_offset=offset_token,
                        exit_condition="time_budget_reached",
                        time_budget_seconds=time_budget_seconds,
                    )
                    return summary if return_summary else processed_prompts
                line = handle.readline()
                if not line:
                    break
                next_offset = handle.tell()
                prompt = _parse_queue_prompt(line, queue_field)
                if prompt is None:
                    _record_upstream_step(
                        queue_meta,
                        "queue_line_skipped",
                        next_offset=next_offset,
                        reason="unparseable_prompt",
                    )
                    offset_token = next_offset
                    _save_offset(offset_path, offset_token)
                    continue
                item_meta = _new_upstream_meta(
                    "queue_item",
                    {
                        "queue_path": str(queue_path),
                        "offset_start": offset_token,
                        "offset_end": next_offset,
                        "queue_field": queue_field,
                    },
                )
                item_meta["pull_history"] = _collect_pull_history(output_dir, "*.json")
                if history_root is not None:
                    item_meta["global_pull_history"] = _collect_pull_history(history_root, "*.json")
                _record_upstream_step(item_meta, "prompt_parsed", prompt_length=len(prompt))
                results = run_benchmark(
                    prompt,
                    providers,
                    model_map,
                    dry_run=dry_run,
                    timeout=timeout,
                )
                _record_upstream_step(item_meta, "benchmark_completed", providers=len(results))
                json_path = output_dir / f"q_{next_offset:010d}.json"
                md_path = output_dir / f"q_{next_offset:010d}.md"
                _record_upstream_step(
                    item_meta,
                    "pre_output_write",
                    json_path=str(json_path),
                    md_path=str(md_path),
                )
                _write_benchmark_outputs(
                    prompt,
                    results,
                    json_path,
                    md_path,
                    upstream_meta=item_meta,
                )
                has_success = any(result.error is None for result in results)
                if has_success:
                    offset_token = next_offset
                    _save_offset(offset_path, offset_token)
                    processed_prompts += 1
                    _record_upstream_step(
                        queue_meta, "queue_item_committed", offset_token=offset_token
                    )
                    print(
                        f"Processed queue offset {offset_token}: wrote {json_path} and {md_path}"
                    )
                else:
                    _record_upstream_step(
                        queue_meta,
                        "queue_item_retry_retained",
                        failed_offset=next_offset,
                    )
                    print(
                        "Queue offset "
                        f"{next_offset} had only provider errors; leaving offset unchanged for retry."
                    )
        if once:
            summary = _make_queue_summary(
                processed_prompts=processed_prompts,
                started_at=started_at,
                start_offset=start_offset,
                end_offset=offset_token,
                exit_condition="once_completed",
                time_budget_seconds=time_budget_seconds,
            )
            return summary if return_summary else processed_prompts
        if budget_reached():
            summary = _make_queue_summary(
                processed_prompts=processed_prompts,
                started_at=started_at,
                start_offset=start_offset,
                end_offset=offset_token,
                exit_condition="time_budget_reached",
                time_budget_seconds=time_budget_seconds,
            )
            return summary if return_summary else processed_prompts
        time.sleep(poll_seconds)


def _resolve_runtime_controls(
    runtime_profile: str,
    timeout_value: int | None,
    poll_seconds_value: float | None,
    time_budget_value: float | None,
) -> tuple[int, float, float | None]:
    profile = RUNTIME_PROFILES[runtime_profile]
    timeout = int(profile["timeout"]) if timeout_value is None else timeout_value
    poll_seconds = (
        float(profile["poll_seconds"]) if poll_seconds_value is None else poll_seconds_value
    )
    time_budget = profile["time_budget_seconds"] if time_budget_value is None else time_budget_value
    if timeout <= 0:
        raise ValueError("timeout must be a positive integer.")
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be a positive number.")
    if time_budget is not None and float(time_budget) <= 0:
        raise ValueError("time_budget_seconds must be a positive number.")
    return timeout, poll_seconds, (None if time_budget is None else float(time_budget))


def _parse_probe_budgets(raw: str) -> list[float]:
    values = [part.strip() for part in raw.split(",") if part.strip()]
    if not values:
        raise ValueError("probe budgets must include at least one value.")
    budgets: list[float] = []
    for value in values:
        try:
            budget = float(value)
        except ValueError as error:
            raise ValueError(f"Invalid probe budget: {value}") from error
        if budget <= 0:
            raise ValueError("Probe budgets must be positive numbers.")
        budgets.append(budget)
    return budgets


def _estimate_operating_budgets(probes: list[dict[str, object]]) -> dict[str, object]:
    externally_terminated = [
        float(item["budget_seconds"])
        for item in probes
        if item.get("exit_condition") == "external_termination"
    ]
    clean_budgets = [
        float(item["budget_seconds"])
        for item in probes
        if item.get("exit_condition") == "time_budget_reached"
    ]
    hard_ceiling = min(externally_terminated) if externally_terminated else None
    recommended = round(max(clean_budgets) * 0.8, 2) if clean_budgets else None
    return {
        "hard_ceiling_seconds": hard_ceiling,
        "recommended_safe_budget_seconds": recommended,
        "method": "80_percent_of_max_clean_budget",
    }


def _should_exclude_from_secret_scan(path: Path, root: Path) -> bool:
    relative = path.relative_to(root).as_posix()
    if any(part in SECRET_SCAN_EXCLUDED_DIRS for part in path.relative_to(root).parts):
        return True
    return any(fnmatch.fnmatch(relative, pattern) for pattern in SECRET_SCAN_EXCLUDE_GLOBS)


def _safe_excerpt(line: str, max_length: int = 160) -> str:
    stripped = line.strip()
    if len(stripped) <= max_length:
        return stripped
    return stripped[: max_length - 3] + "..."


def _redact_match(line: str, pattern: re.Pattern[str]) -> str:
    redacted = pattern.sub("[REDACTED]", line)
    for other_pattern in SECRET_PATTERNS.values():
        redacted = other_pattern.sub("[REDACTED]", redacted)
    return redacted


def run_empirical_secret_scan(
    *,
    scan_root: Path,
    output_root: Path,
    max_findings: int = 200,
    history_root: Path | None = None,
) -> dict[str, object]:
    if max_findings <= 0:
        raise ValueError("max_findings must be a positive integer.")
    root = scan_root.resolve()
    if not root.exists():
        raise ValueError(f"scan_root does not exist: {scan_root}")
    upstream_meta = _new_upstream_meta(
        "empirical_secret_scan",
        {
            "scan_root": str(root),
            "output_root": str(output_root),
            "max_findings": max_findings,
        },
    )
    upstream_meta["pull_history"] = _collect_pull_history(output_root, "secret_scan_report.json")
    if history_root is not None:
        upstream_meta["global_pull_history"] = _collect_pull_history(history_root, "*.json")
    _record_upstream_step(upstream_meta, "scan_initialized")
    scan_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = output_root / scan_stamp
    run_root.mkdir(parents=True, exist_ok=True)
    findings: list[SecretFinding] = []
    files_scanned = 0
    matched_detectors: set[str] = set()
    detector_counts: dict[str, int] = {}
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SECRET_SCAN_EXCLUDED_DIRS]
        for filename in sorted(filenames):
            path = Path(current_root) / filename
            if _should_exclude_from_secret_scan(path, root):
                continue
            files_scanned += 1
            try:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    relative = path.relative_to(root).as_posix()
                    for line_number, line in enumerate(handle, start=1):
                        for detector, pattern in SECRET_PATTERNS.items():
                            if pattern.search(line):
                                matched_detectors.add(detector)
                                detector_counts[detector] = detector_counts.get(detector, 0) + 1
                                if len(findings) < max_findings:
                                    findings.append(
                                        SecretFinding(
                                            file=relative,
                                            line=line_number,
                                            detector=detector,
                                            excerpt=_safe_excerpt(_redact_match(line, pattern)),
                                        )
                                    )
            except (OSError, UnicodeDecodeError):
                continue
    detector_hit_rate = round(len(matched_detectors) / len(SECRET_PATTERNS), 4) if SECRET_PATTERNS else 0.0
    _record_upstream_step(
        upstream_meta,
        "scan_completed",
        files_scanned=files_scanned,
        matches_total=sum(detector_counts.values()),
        findings_count=len(findings),
    )
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scan_root": str(root),
        "files_scanned": files_scanned,
        "matches_total": sum(detector_counts.values()),
        "findings_count": len(findings),
        "max_findings": max_findings,
        "detectors_configured": len(SECRET_PATTERNS),
        "detector_hit_rate": detector_hit_rate,
        "detector_counts": detector_counts,
        "findings": [
            {
                "file": finding.file,
                "line": finding.line,
                "detector": finding.detector,
                "excerpt": finding.excerpt,
            }
            for finding in findings
        ],
        "upstream_meta": upstream_meta,
    }
    json_path = run_root / "secret_scan_report.json"
    md_path = run_root / "secret_scan_report.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_lines = [
        "# Empirical Secret Scan Report",
        "",
        f"- Generated at: {payload['generated_at_utc']}",
        f"- Scan root: `{payload['scan_root']}`",
        f"- Files scanned: {files_scanned}",
        f"- Total matches: {sum(detector_counts.values())}",
        f"- Findings: {len(findings)}",
        f"- Detectors configured: {len(SECRET_PATTERNS)}",
        f"- Detector hit rate: {detector_hit_rate}",
        f"- Upstream steps recorded: {len(upstream_meta.get('steps', []))}",
        f"- Pull history artifacts: {upstream_meta['pull_history']['artifact_count']}",
        "",
        "## Detector counts",
        "",
    ]
    if detector_counts:
        for detector, count in sorted(detector_counts.items()):
            md_lines.append(f"- {detector}: {count}")
    else:
        md_lines.append("- none")
    md_lines.extend(
        [
            "",
            "## Upstream process meta",
            "",
            f"- Mode: {upstream_meta['mode']}",
            f"- Generated at: {upstream_meta['generated_at_utc']}",
            "",
            "## Findings",
            "",
            "| File | Line | Detector | Excerpt |",
            "|---|---:|---|---|",
        ]
    )
    if findings:
        for finding in findings:
            safe_excerpt = finding.excerpt.replace("|", "\\|")
            md_lines.append(
                f"| {finding.file} | {finding.line} | {finding.detector} | {safe_excerpt} |"
            )
    else:
        md_lines.append("| none | 0 | none | no matching patterns found |")
    md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    payload["summary_json"] = str(json_path)
    payload["summary_md"] = str(md_path)
    return payload


def run_probe_matrix(
    *,
    providers: list[str],
    model_map: dict[str, str],
    budgets: list[float],
    output_root: Path,
    timeout: int,
    poll_seconds: float,
    queue_field: str,
    dry_run: bool,
    seed_prompts: int,
    enqueue_interval_seconds: float,
    history_root: Path | None = None,
) -> dict[str, object]:
    if seed_prompts <= 0:
        raise ValueError("seed_prompts must be a positive integer.")
    if enqueue_interval_seconds <= 0:
        raise ValueError("enqueue_interval_seconds must be a positive number.")
    upstream_meta = _new_upstream_meta(
        "probe_session_limit",
        {
            "providers": providers,
            "budgets": budgets,
            "timeout": timeout,
            "poll_seconds": poll_seconds,
            "queue_field": queue_field,
            "dry_run": dry_run,
            "seed_prompts": seed_prompts,
            "enqueue_interval_seconds": enqueue_interval_seconds,
        },
    )
    upstream_meta["pull_history"] = _collect_pull_history(output_root, "probe_summary.json")
    if history_root is not None:
        upstream_meta["global_pull_history"] = _collect_pull_history(history_root, "*.json")
    _record_upstream_step(upstream_meta, "probe_initialized")
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = output_root / run_stamp
    run_root.mkdir(parents=True, exist_ok=True)
    probe_runs: list[dict[str, object]] = []
    for budget in budgets:
        _record_upstream_step(upstream_meta, "probe_budget_started", budget_seconds=budget)
        budget_tag = str(int(budget)) if float(budget).is_integer() else str(budget).replace(".", "p")
        budget_root = run_root / f"budget_{budget_tag}s"
        queue_path = budget_root / "q.jsonl"
        offset_path = budget_root / ".state" / "q.offset"
        output_dir = budget_root / "artifacts"
        budget_root.mkdir(parents=True, exist_ok=True)
        enqueue_counter = {"count": 0}
        counter_lock = threading.Lock()
        stop_event = threading.Event()

        def _feeder() -> None:
            while not stop_event.is_set():
                with counter_lock:
                    enqueue_counter["count"] += 1
                    serial = enqueue_counter["count"]
                enqueue_prompt(
                    queue_path,
                    f"session-limit-probe prompt {serial} budget={budget}",
                    field=queue_field,
                )
                stop_event.wait(enqueue_interval_seconds)

        for index in range(seed_prompts):
            enqueue_prompt(
                queue_path,
                f"session-limit-probe seed {index + 1} budget={budget}",
                field=queue_field,
            )
            with counter_lock:
                enqueue_counter["count"] += 1

        feeder = threading.Thread(target=_feeder, daemon=True)
        feeder.start()
        exit_condition = "external_termination"
        summary: QueueRunSummary | None = None
        try:
            summary = run_queue(
                queue_path,
                offset_path,
                output_dir,
                providers,
                model_map,
                queue_field=queue_field,
                dry_run=dry_run,
                timeout=timeout,
                once=False,
                poll_seconds=poll_seconds,
                time_budget_seconds=budget,
                return_summary=True,
                history_root=history_root,
            )
            if isinstance(summary, QueueRunSummary):
                exit_condition = summary.exit_condition
        finally:
            stop_event.set()
            feeder.join(timeout=3.0)

        if not isinstance(summary, QueueRunSummary):
            continue
        with counter_lock:
            enqueued = enqueue_counter["count"]
        run_record = {
            "budget_seconds": budget,
            "start_utc": summary.start_utc,
            "end_utc": summary.end_utc,
            "processed_prompts": summary.processed_prompts,
            "enqueued_prompts": enqueued,
            "offset_start": summary.start_offset,
            "offset_end": summary.end_offset,
            "offset_growth": summary.end_offset - summary.start_offset,
            "exit_condition": exit_condition,
            "output_dir": str(output_dir),
        }
        probe_runs.append(run_record)
        _record_upstream_step(
            upstream_meta,
            "probe_budget_completed",
            budget_seconds=budget,
            processed_prompts=run_record["processed_prompts"],
            exit_condition=run_record["exit_condition"],
        )

    estimates = _estimate_operating_budgets(probe_runs)
    _record_upstream_step(upstream_meta, "probe_estimates_computed", estimates=estimates)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "probe_type": "global_session_limit_exploration",
        "budgets_tested_seconds": budgets,
        "runtime_controls": {
            "timeout": timeout,
            "poll_seconds": poll_seconds,
            "queue_field": queue_field,
            "dry_run": dry_run,
            "seed_prompts": seed_prompts,
            "enqueue_interval_seconds": enqueue_interval_seconds,
        },
        "runs": probe_runs,
        "estimates": estimates,
        "upstream_meta": upstream_meta,
    }
    json_path = run_root / "probe_summary.json"
    md_path = run_root / "probe_summary.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_lines = [
        "# Session Limit Probe Summary",
        "",
        f"- Generated at: {payload['generated_at_utc']}",
        f"- Budgets tested (s): {', '.join(str(x) for x in budgets)}",
        f"- Upstream steps recorded: {len(upstream_meta.get('steps', []))}",
        f"- Pull history artifacts: {upstream_meta['pull_history']['artifact_count']}",
        "",
        "| Budget (s) | Start UTC | End UTC | Processed | Enqueued | Offset Growth | Exit |",
        "|---:|---|---|---:|---:|---:|---|",
    ]
    for item in probe_runs:
        md_lines.append(
            "| {budget_seconds} | {start_utc} | {end_utc} | {processed_prompts} | "
            "{enqueued_prompts} | {offset_growth} | {exit_condition} |".format(**item)
        )
    md_lines.extend(
        [
            "",
            "## Upstream process meta",
            "",
            f"- Mode: {upstream_meta['mode']}",
            f"- Generated at: {upstream_meta['generated_at_utc']}",
            "",
            "## Estimates",
            "",
            f"- Hard ceiling seconds: {estimates['hard_ceiling_seconds']}",
            f"- Recommended safe budget seconds: {estimates['recommended_safe_budget_seconds']}",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    payload["summary_json"] = str(json_path)
    payload["summary_md"] = str(md_path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(prog="vf-benchmark")
    parser.add_argument("--prompt", help="Prompt to benchmark across providers.")
    parser.add_argument(
        "--runtime-profile",
        choices=sorted(RUNTIME_PROFILES.keys()),
        default="default",
        help="Runtime profile for timeout/poll/time-budget defaults.",
    )
    parser.add_argument(
        "--providers",
        default="gpt,claude,grok,other",
        help="Comma-separated providers (gpt, claude, grok, other).",
    )
    parser.add_argument(
        "--model-map",
        default=None,
        help='Optional JSON map, e.g. {"gpt":"gpt-4.1-mini","claude":"claude-3-5-sonnet-latest"}',
    )
    parser.add_argument("--dry-run", action="store_true", help="Use built-in response examples.")
    parser.add_argument("--timeout", type=int, default=None, help="API timeout per provider in seconds.")
    parser.add_argument(
        "--queue-path",
        default=None,
        help="Queue file path (JSONL or plain text); when set, run queue-processing mode.",
    )
    parser.add_argument(
        "--offset-path",
        default=".state/q.offset",
        help="Offset file used by queue mode.",
    )
    parser.add_argument(
        "--queue-output-dir",
        default="outputs/model_benchmarks/hurricane",
        help="Output directory for queue mode artifacts.",
    )
    parser.add_argument(
        "--queue-field",
        default="q",
        help="Field name used when queue lines are JSON objects.",
    )
    parser.add_argument(
        "--enqueue",
        default=None,
        help="Append a prompt to queue and exit.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="In queue mode, process current queue once and exit.",
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=None,
        help="Queue polling interval in seconds for continuous queue mode.",
    )
    parser.add_argument(
        "--time-budget-seconds",
        type=float,
        default=None,
        help="Optional wall-clock budget for queue mode; worker exits when reached.",
    )
    parser.add_argument(
        "--probe-session-limit",
        action="store_true",
        help="Run empirical session-limit probe matrix in full package mode.",
    )
    parser.add_argument(
        "--probe-budgets",
        default=",".join(str(value) for value in DEFAULT_PROBE_BUDGETS),
        help="Comma-separated probe budgets in seconds.",
    )
    parser.add_argument(
        "--probe-output-dir",
        default="outputs/model_benchmarks/session_probes",
        help="Directory for probe evidence artifacts.",
    )
    parser.add_argument(
        "--probe-seed-prompts",
        type=int,
        default=25,
        help="Initial queue prompts per probe run.",
    )
    parser.add_argument(
        "--probe-enqueue-interval-seconds",
        type=float,
        default=0.25,
        help="Feeder enqueue interval during probe runs.",
    )
    parser.add_argument(
        "--empirical-secret-scan",
        action="store_true",
        help="Run empirical secret scan and write report artifacts.",
    )
    parser.add_argument(
        "--scan-root",
        default=".",
        help="Root path for empirical secret scanning.",
    )
    parser.add_argument(
        "--scan-output-dir",
        default="outputs/security_scans",
        help="Directory for empirical secret scan reports.",
    )
    parser.add_argument(
        "--scan-max-findings",
        type=int,
        default=200,
        help="Maximum number of findings to record in one empirical scan run.",
    )
    parser.add_argument(
        "--history-root",
        default="outputs",
        help="Root directory used to build aggregated history index artifacts.",
    )
    parser.add_argument(
        "--history-limit",
        type=int,
        default=2000,
        help="Maximum number of historical JSON artifacts to include in history aggregation.",
    )
    parser.add_argument(
        "--history-export-csv",
        action="store_true",
        help="Also emit CSV history exports for R/Python workflows.",
    )
    parser.add_argument(
        "--history-all-branches",
        action="store_true",
        help="Aggregate history artifacts from all local git branches into one index.",
    )
    parser.add_argument(
        "--history-parallel-workers",
        type=int,
        default=4,
        help="Parallel worker count used for all-branches metadata pull collection.",
    )
    parser.add_argument(
        "--json-out",
        default="outputs/model_benchmarks/latest_benchmark.json",
        help="Path for JSON output.",
    )
    parser.add_argument(
        "--md-out",
        default="outputs/model_benchmarks/latest_benchmark.md",
        help="Path for markdown output.",
    )
    args = parser.parse_args()
    providers = [part.strip() for part in args.providers.split(",") if part.strip()]
    unknown = [provider for provider in providers if provider not in SUPPORTED_PROVIDERS]
    if unknown:
        parser.error(f"Unsupported providers: {unknown}. Allowed: {sorted(SUPPORTED_PROVIDERS)}")
    if args.history_limit <= 0:
        parser.error("--history-limit must be a positive integer.")
    if args.history_parallel_workers <= 0:
        parser.error("--history-parallel-workers must be a positive integer.")
    try:
        timeout, poll_seconds, time_budget_seconds = _resolve_runtime_controls(
            args.runtime_profile,
            args.timeout,
            args.poll_seconds,
            args.time_budget_seconds,
        )
    except ValueError as error:
        parser.error(str(error))
    try:
        model_map = _parse_model_map(args.model_map, providers)
    except ValueError as error:
        parser.error(str(error))
    if args.probe_session_limit and (args.queue_path is not None or args.enqueue is not None or args.prompt):
        parser.error(
            "--probe-session-limit cannot be combined with --queue-path, --enqueue, or --prompt."
        )
    if args.empirical_secret_scan and (
        args.probe_session_limit or args.queue_path is not None or args.enqueue is not None or args.prompt
    ):
        parser.error(
            "--empirical-secret-scan cannot be combined with prompt/queue/probe execution modes."
        )
    if args.empirical_secret_scan:
        try:
            payload = run_empirical_secret_scan(
                scan_root=Path(args.scan_root),
                output_root=Path(args.scan_output_dir),
                max_findings=args.scan_max_findings,
                history_root=Path(args.history_root),
            )
        except ValueError as error:
            parser.error(str(error))
        history_export = _write_history_exports(
            Path(args.history_root),
            history_limit=args.history_limit,
            export_csv=args.history_export_csv,
            include_all_branches=args.history_all_branches,
            repo_root=Path.cwd(),
            parallel_workers=args.history_parallel_workers,
        )
        print("Empirical secret scan complete.")
        print("Report artifacts written under the configured scan output directory.")
        print(f"History index JSON: {history_export['history_index_json']}")
        print(f"History index markdown: {history_export['history_index_md']}")
        print(f"History dump JSONL: {history_export['history_dump_jsonl']}")
        print(f"History dump CSV: {history_export['history_dump_csv']}")
        return 0
    if args.probe_session_limit:
        try:
            budgets = _parse_probe_budgets(args.probe_budgets)
            payload = run_probe_matrix(
                providers=providers,
                model_map=model_map,
                budgets=budgets,
                output_root=Path(args.probe_output_dir),
                timeout=timeout,
                poll_seconds=poll_seconds,
                queue_field=args.queue_field,
                dry_run=args.dry_run,
                seed_prompts=args.probe_seed_prompts,
                enqueue_interval_seconds=args.probe_enqueue_interval_seconds,
                history_root=Path(args.history_root),
            )
        except ValueError as error:
            parser.error(str(error))
        history_export = _write_history_exports(
            Path(args.history_root),
            history_limit=args.history_limit,
            export_csv=args.history_export_csv,
            include_all_branches=args.history_all_branches,
            repo_root=Path.cwd(),
            parallel_workers=args.history_parallel_workers,
        )
        print(f"Probe summary JSON: {payload['summary_json']}")
        print(f"Probe summary markdown: {payload['summary_md']}")
        print(f"History index JSON: {history_export['history_index_json']}")
        print(f"History index markdown: {history_export['history_index_md']}")
        print(f"History dump JSONL: {history_export['history_dump_jsonl']}")
        print(f"History dump CSV: {history_export['history_dump_csv']}")
        estimates = payload["estimates"]
        print(
            "Estimated hard ceiling (seconds): "
            f"{estimates['hard_ceiling_seconds']}"
        )
        print(
            "Recommended safe budget (seconds): "
            f"{estimates['recommended_safe_budget_seconds']}"
        )
        return 0
    queue_path = Path(args.queue_path) if args.queue_path else None
    if args.enqueue is not None:
        target_queue = queue_path if queue_path is not None else Path("q.jsonl")
        enqueue_prompt(target_queue, args.enqueue, field=args.queue_field)
        print(f"Queued prompt in {target_queue}")
        return 0
    if queue_path is not None:
        processed = run_queue(
            queue_path,
            Path(args.offset_path),
            Path(args.queue_output_dir),
            providers,
            model_map,
            queue_field=args.queue_field,
            dry_run=args.dry_run,
            timeout=timeout,
            once=args.once,
            poll_seconds=poll_seconds,
            time_budget_seconds=time_budget_seconds,
            history_root=Path(args.history_root),
        )
        history_export = _write_history_exports(
            Path(args.history_root),
            history_limit=args.history_limit,
            export_csv=args.history_export_csv,
            include_all_branches=args.history_all_branches,
            repo_root=Path.cwd(),
            parallel_workers=args.history_parallel_workers,
        )
        print(f"Queue mode complete. Processed {processed} prompt(s).")
        print(f"History index JSON: {history_export['history_index_json']}")
        print(f"History index markdown: {history_export['history_index_md']}")
        print(f"History dump JSONL: {history_export['history_dump_jsonl']}")
        print(f"History dump CSV: {history_export['history_dump_csv']}")
        return 0
    if not args.prompt:
        parser.error("--prompt is required unless --queue-path or --enqueue is used.")
    results = run_benchmark(args.prompt, providers, model_map, dry_run=args.dry_run, timeout=timeout)
    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    upstream_meta = _new_upstream_meta(
        "single_prompt_benchmark",
        {
            "providers": providers,
            "dry_run": args.dry_run,
            "timeout": timeout,
            "json_out": str(json_path),
            "md_out": str(md_path),
        },
    )
    upstream_meta["pull_history"] = _collect_pull_history(json_path.parent, "*.json")
    upstream_meta["global_pull_history"] = _collect_pull_history(Path(args.history_root), "*.json")
    _record_upstream_step(upstream_meta, "benchmark_completed", providers=len(results))
    _record_upstream_step(
        upstream_meta,
        "pre_output_write",
        json_path=str(json_path),
        md_path=str(md_path),
    )
    _write_benchmark_outputs(
        args.prompt,
        results,
        json_path,
        md_path,
        upstream_meta=upstream_meta,
    )
    history_export = _write_history_exports(
        Path(args.history_root),
        history_limit=args.history_limit,
        export_csv=args.history_export_csv,
        include_all_branches=args.history_all_branches,
        repo_root=Path.cwd(),
        parallel_workers=args.history_parallel_workers,
    )
    print(f"Wrote benchmark JSON: {json_path}")
    print(f"Wrote benchmark markdown: {md_path}")
    print(f"History index JSON: {history_export['history_index_json']}")
    print(f"History index markdown: {history_export['history_index_md']}")
    print(f"History dump JSONL: {history_export['history_dump_jsonl']}")
    print(f"History dump CSV: {history_export['history_dump_csv']}")
    for result in sorted(results, key=lambda item: item.weighted_score, reverse=True):
        suffix = f" ERROR: {result.error}" if result.error else ""
        print(f"{result.provider:>7} {result.weighted_score:>6.2f} ({result.model}){suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
