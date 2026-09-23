"""Generate validated Markdown reports from defensive scan findings."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

ALLOWED_STATUSES = {"Secure", "Vulnerable", "Unknown"}


class ScanFinding(TypedDict):
    host: str
    status: str
    vulns: list[str]
    remediation: str
    verification: str


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _normalise_result(result: Mapping[str, object], index: int) -> ScanFinding:
    host = _text(result.get("host"), f"scan_results[{index}].host")
    status = _text(result.get("status"), f"scan_results[{index}].status")
    if status not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        raise ValueError(f"scan_results[{index}].status must be one of: {allowed}.")

    vulnerabilities = result.get("vulns", [])
    if not isinstance(vulnerabilities, list) or not all(isinstance(item, str) for item in vulnerabilities):
        raise ValueError(f"scan_results[{index}].vulns must be a list of strings.")

    remediation = result.get("remediation", "Review and remediate according to the assignment scope.")
    verification = result.get("verification", "Repeat the approved check and record the result.")
    return {
        "host": host,
        "status": status,
        "vulns": [item.strip() for item in vulnerabilities if item.strip()],
        "remediation": _text(remediation, f"scan_results[{index}].remediation"),
        "verification": _text(verification, f"scan_results[{index}].verification"),
    }


def build_scan_report(
    scan_results: Iterable[Mapping[str, object]],
    *,
    generated_at: datetime | None = None,
    title: str = "Security Scan Report",
) -> str:
    """Build a Markdown report without performing any network activity."""
    normalised = [_normalise_result(result, index) for index, result in enumerate(scan_results)]
    if not normalised:
        raise ValueError("scan_results must contain at least one result.")

    hosts = [str(result["host"]) for result in normalised]
    if len(hosts) != len(set(hosts)):
        raise ValueError("scan_results must not contain duplicate hosts.")

    timestamp = generated_at or datetime.now(UTC)
    vulnerable = sum(result["status"] == "Vulnerable" for result in normalised)
    secure = sum(result["status"] == "Secure" for result in normalised)
    unknown = sum(result["status"] == "Unknown" for result in normalised)

    lines = [
        f"# {_markdown_cell(title)}",
        "",
        f"**Generated (UTC):** {timestamp.astimezone(UTC).isoformat(timespec='seconds')}",
        "",
        f"**Hosts assessed:** {len(normalised)}  ",
        f"**Secure:** {secure}  ",
        f"**Vulnerable:** {vulnerable}  ",
        f"**Unknown:** {unknown}",
        "",
        "| Host | Status | Vulnerabilities | Remediation | Verification |",
        "|------|--------|-----------------|-------------|--------------|",
    ]
    for result in normalised:
        vulnerabilities = ", ".join(result["vulns"]) or "None"
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(str(result[field]))
                for field in ("host", "status")
            )
            + f" | {_markdown_cell(vulnerabilities)}"
            + f" | {_markdown_cell(str(result['remediation']))}"
            + f" | {_markdown_cell(str(result['verification']))} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Notes",
            "",
            "- Record the scan tool, scope, and command or configuration used.",
            "- Preserve the original scan output before remediation.",
            "- Re-run the approved check after remediation and attach the result.",
            "- Treat `Unknown` findings as requiring review, not as secure.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_scan_report(
    scan_results: Iterable[Mapping[str, object]],
    output_path: str | Path = "scan_report.md",
    *,
    generated_at: datetime | None = None,
    title: str = "Security Scan Report",
) -> Path:
    """Write a report and return its resolved output path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    report = build_scan_report(scan_results, generated_at=generated_at, title=title)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(report, encoding="utf-8", newline="\n")
    temporary.replace(destination)
    return destination