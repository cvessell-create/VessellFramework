"""Cross-model prompt benchmarking with weighted scoring for workflow quality."""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
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


def _format_markdown(results: list[ProviderResult], prompt: str) -> str:
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
    return "\n".join(lines).strip() + "\n"


def _parse_model_map(model_map_arg: str | None, providers: list[str]) -> dict[str, str]:
    model_map = dict(DEFAULT_MODEL_MAP)
    if model_map_arg:
        parsed = json.loads(model_map_arg)
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


def _to_jsonable(results: list[ProviderResult], prompt: str) -> dict[str, object]:
    return {
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


def main() -> int:
    parser = argparse.ArgumentParser(prog="vf-benchmark")
    parser.add_argument("--prompt", required=True, help="Prompt to benchmark across providers.")
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
    parser.add_argument("--timeout", type=int, default=45, help="API timeout per provider in seconds.")
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
    if args.timeout <= 0:
        parser.error("--timeout must be a positive integer.")
    model_map = _parse_model_map(args.model_map, providers)
    results = run_benchmark(args.prompt, providers, model_map, dry_run=args.dry_run, timeout=args.timeout)
    json_payload = _to_jsonable(results, args.prompt)
    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    md_path.write_text(_format_markdown(results, args.prompt), encoding="utf-8")
    print(f"Wrote benchmark JSON: {json_path}")
    print(f"Wrote benchmark markdown: {md_path}")
    for result in sorted(results, key=lambda item: item.weighted_score, reverse=True):
        suffix = f" ERROR: {result.error}" if result.error else ""
        print(f"{result.provider:>7} {result.weighted_score:>6.2f} ({result.model}){suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
