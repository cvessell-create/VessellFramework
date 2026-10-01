# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Verification heat map: render the claim x source matrix.

:func:`vessell.report.event_matrix` produces the data — one row per claim,
one column per source, each cell a signed tier weight (positive = the
source affirms, negative = it denies, absent = silent). This module turns
that grid into something an analyst can read at a glance:

- :func:`render_html` — a standalone, dependency-free HTML page (inline
  CSS, no JavaScript, every string escaped) suitable for attaching to a
  case file or opening in any browser.
- :func:`render_text` — a terminal heat map using 24-bit ANSI background
  colours, with a plain fallback for logs and non-colour terminals.
- :func:`render_csv` — the same grid as CSV for spreadsheets / pandas.

Colour scale follows the open-source conventions used by matplotlib,
seaborn, and ggplot2 for signed data: a *diverging* palette centred on
zero. The stops are ColorBrewer ``RdBu`` (11-class, colour-blind safe;
Cynthia Brewer, Penn State, Apache-2.0): red for denial, white for
neutral, blue for affirmation, with silent cells in neutral grey so
"no evidence" is never confused with "evidence of zero weight".

The CLI (``vf-heatmap``) reads a JSON batch of claim checks, runs them
through :func:`~vessell.verify.verify_claim` via ``event_matrix``, and
writes the heat map in the requested format.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import sys
from pathlib import Path
from typing import Any

from vessell.provenance import SourceStatus
from vessell.report import event_matrix
from vessell.verify import ClaimCheck, SourceSighting

__all__ = [
    "DIVERGING_PALETTE",
    "SILENT_COLOR",
    "color_for_weight",
    "load_checks",
    "main",
    "render_csv",
    "render_html",
    "render_text",
]

# ColorBrewer RdBu, 11 classes, ordered from -1 (deny) to +1 (affirm).
DIVERGING_PALETTE: tuple[str, ...] = (
    "#67001f",
    "#b2182b",
    "#d6604d",
    "#f4a582",
    "#fddbc7",
    "#f7f7f7",
    "#d1e5f0",
    "#92c5de",
    "#4393c3",
    "#2166ac",
    "#053061",
)
SILENT_COLOR = "#e0e0e0"

_VERDICT_COLORS: dict[str, str] = {
    "VERIFIED": "#2166ac",
    "CORROBORATED": "#4393c3",
    "SINGLE_SOURCE": "#b8860b",
    "UNCORROBORATED": "#6b6b6b",
    "CONTRADICTED": "#b2182b",
}

_SIGHTING_FIELDS = {
    "source_name",
    "tier",
    "url",
    "seen_at",
    "published_at",
    "text",
    "root",
    "denies",
    "is_official_record",
    "note",
    "event_clock",
}


# ---------------------------------------------------------------------------
# Colour scale
# ---------------------------------------------------------------------------


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def color_for_weight(weight: float | None) -> str:
    """Map a signed weight in ``[-1, 1]`` onto the diverging palette.

    Values are clamped to the range and linearly interpolated between the
    two nearest palette stops. ``None`` (source silent) returns
    :data:`SILENT_COLOR`.
    """
    if weight is None:
        return SILENT_COLOR
    w = max(-1.0, min(1.0, float(weight)))
    position = (w + 1.0) / 2.0 * (len(DIVERGING_PALETTE) - 1)
    lower = int(position)
    if lower >= len(DIVERGING_PALETTE) - 1:
        return DIVERGING_PALETTE[-1]
    frac = position - lower
    lo = _hex_to_rgb(DIVERGING_PALETTE[lower])
    hi = _hex_to_rgb(DIVERGING_PALETTE[lower + 1])
    mixed = tuple(round(a + (b - a) * frac) for a, b in zip(lo, hi, strict=True))
    return _rgb_to_hex((mixed[0], mixed[1], mixed[2]))


def _text_color(background: str) -> str:
    r, g, b = _hex_to_rgb(background)
    # WCAG relative-luminance approximation; dark text on light cells.
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#111111" if luminance > 140 else "#ffffff"


def _cell_label(cell: dict[str, Any] | None) -> str:
    if cell is None:
        return "·"
    label = f"{float(cell['weight']):+.2f}"
    if cell.get("clock"):
        label += f" @{cell['clock']}"
    return label


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_html(matrix: dict[str, Any], title: str = "Verification heat map") -> str:
    """Render ``event_matrix`` output as a standalone HTML document."""
    esc = html.escape
    sources: list[str] = list(matrix.get("sources", []))
    rows: list[dict[str, Any]] = list(matrix.get("rows", []))

    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>{esc(title)}</title>",
        "<style>",
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#111}",
        "table{border-collapse:collapse;font-size:13px}",
        "th,td{border:1px solid #fff;padding:6px 8px;text-align:center}",
        "th{background:#333;color:#fff;font-weight:600}",
        "td.claim{text-align:left;background:#fafafa;max-width:360px}",
        "td.cell{min-width:72px;font-variant-numeric:tabular-nums}",
        ".verdict{color:#fff;border-radius:3px;padding:2px 6px;font-size:11px}",
        ".legend{display:flex;align-items:center;gap:0;margin:16px 0}",
        ".legend span{display:inline-block;width:28px;height:14px}",
        ".legend em{font-style:normal;font-size:12px;margin:0 8px}",
        "</style></head><body>",
        f"<h1>{esc(title)}</h1>",
        '<div class="legend"><em>deny −1</em>',
    ]
    out.extend(f'<span style="background:{c}"></span>' for c in DIVERGING_PALETTE)
    out.append(
        f'<em>+1 affirm</em><span style="background:{SILENT_COLOR}"></span>'
        "<em>silent</em></div>"
    )
    out.append("<table><thead><tr><th>Claim</th><th>Verdict</th><th>Score</th>")
    out.extend(f"<th>{esc(source)}</th>" for source in sources)
    out.append("</tr></thead><tbody>")

    for row in rows:
        verdict = str(row.get("verdict", ""))
        badge = _VERDICT_COLORS.get(verdict, "#6b6b6b")
        rationale = str(row.get("rationale", ""))
        signals = "\n".join(str(s) for s in row.get("signals", []))
        out.append(
            f'<tr><td class="claim" title="{esc(rationale)}">{esc(str(row.get("claim", "")))}'
            "</td>"
            f'<td><span class="verdict" style="background:{badge}" '
            f'title="{esc(signals)}">{esc(verdict)}</span></td>'
            f"<td>{float(row.get('score', 0.0)):.2f}</td>"
        )
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        for source in sources:
            cell = cells.get(source)
            bg = color_for_weight(None if cell is None else float(cell["weight"]))
            fg = _text_color(bg)
            if cell is None:
                tip = f"{source}: silent"
            else:
                stance = "denies" if cell.get("denies") else "affirms"
                tip = f"{source} {stance} (weight {float(cell['weight']):+.2f})"
                if cell.get("clock"):
                    tip += f" at event clock {cell['clock']}"
            out.append(
                f'<td class="cell" style="background:{bg};color:{fg}" '
                f'title="{esc(tip)}">{esc(_cell_label(cell))}</td>'
            )
        out.append("</tr>")

    out.append("</tbody></table>")
    out.append(
        "<p><small>Cell value = source tier weight (affirming minus denying). "
        "Row score = independence-discounted corroboration from "
        "<code>verify_claim</code>.</small></p>"
    )
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def _ansi_bg(hex_color: str) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"\x1b[48;2;{r};{g};{b}m"


def _ansi_fg(hex_color: str) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"\x1b[38;2;{r};{g};{b}m"


def _fit(value: str, width: int) -> str:
    if len(value) > width:
        return value[: max(0, width - 1)] + "…"
    return value.ljust(width)


def render_text(
    matrix: dict[str, Any],
    *,
    color: bool = True,
    claim_width: int = 40,
    cell_width: int = 14,
) -> str:
    """Render ``event_matrix`` output as a terminal heat map.

    With ``color=True`` each cell gets a 24-bit ANSI background from the
    diverging palette; with ``color=False`` the same grid is emitted as
    plain text (signed weights, ``·`` for silent sources).
    """
    sources: list[str] = list(matrix.get("sources", []))
    rows: list[dict[str, Any]] = list(matrix.get("rows", []))
    reset = "\x1b[0m" if color else ""

    header = _fit("Claim", claim_width) + " " + _fit("Verdict", 15) + " " + _fit("Score", 6)
    header += "".join(" " + _fit(source, cell_width) for source in sources)
    lines = [header, "-" * len(header)]
    for row in rows:
        line = (
            _fit(str(row.get("claim", "")), claim_width)
            + " "
            + _fit(str(row.get("verdict", "")), 15)
            + " "
            + _fit(f"{float(row.get('score', 0.0)):.2f}", 6)
        )
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        for source in sources:
            cell = cells.get(source)
            text = _fit(_cell_label(cell), cell_width)
            if color:
                bg = color_for_weight(None if cell is None else float(cell["weight"]))
                line += " " + _ansi_bg(bg) + _ansi_fg(_text_color(bg)) + text + reset
            else:
                line += " " + text
        lines.append(line)
    return "\n".join(lines) + "\n"


def _csv_safe(value: Any) -> Any:
    """Neutralise spreadsheet formula injection in free-text CSV fields."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def render_csv(matrix: dict[str, Any]) -> str:
    """Render ``event_matrix`` output as CSV (blank cell = silent source).

    Claim and source text is untrusted input, so any value that a
    spreadsheet would evaluate as a formula is prefixed with ``'``.
    """
    sources: list[str] = list(matrix.get("sources", []))
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        ["claim", "verdict", "score", "independent_roots", *(_csv_safe(s) for s in sources)]
    )
    for row in matrix.get("rows", []):
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        writer.writerow(
            [
                _csv_safe(row.get("claim", "")),
                row.get("verdict", ""),
                row.get("score", ""),
                row.get("independent_roots", ""),
                *(
                    "" if cells.get(source) is None else cells[source]["weight"]
                    for source in sources
                ),
            ]
        )
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Input loading + CLI
# ---------------------------------------------------------------------------


def _parse_tier(value: Any) -> SourceStatus:
    if isinstance(value, SourceStatus):
        return value
    text = str(value).strip()
    for status in SourceStatus:
        if text in (status.name, status.value):
            return status
    allowed = ", ".join(s.name for s in SourceStatus)
    raise ValueError(f"unknown source tier {value!r}; expected one of: {allowed}")


def _parse_sighting(raw: Any) -> SourceSighting:
    if not isinstance(raw, dict):
        raise TypeError("each sighting must be a JSON object")
    unknown = set(raw) - _SIGHTING_FIELDS
    if unknown:
        raise ValueError(f"unknown sighting field(s): {', '.join(sorted(unknown))}")
    if "source_name" not in raw or "tier" not in raw:
        raise ValueError("each sighting requires 'source_name' and 'tier'")
    fields = dict(raw)
    fields["tier"] = _parse_tier(fields["tier"])
    for flag in ("denies", "is_official_record"):
        if flag in fields and not isinstance(fields[flag], bool):
            raise TypeError(f"sighting field {flag!r} must be true/false")
    return SourceSighting(**fields)


def load_checks(data: Any) -> list[ClaimCheck]:
    """Build :class:`ClaimCheck` objects from decoded JSON.

    Accepts either a list of checks or ``{"checks": [...]}``. Each check is
    ``{"claim": str, "sightings": [ {source_name, tier, ...}, ... ]}``,
    where ``tier`` is a :class:`~vessell.provenance.SourceStatus` name
    (``SOURCE_ESTABLISHED``) or value (``SOURCE-ESTABLISHED``).
    """
    if isinstance(data, dict):
        data = data.get("checks")
    if not isinstance(data, list):
        raise TypeError("input must be a list of checks or an object with a 'checks' list")
    checks: list[ClaimCheck] = []
    for raw in data:
        if not isinstance(raw, dict) or not isinstance(raw.get("claim"), str):
            raise TypeError("each check must be an object with a string 'claim'")
        sightings = raw.get("sightings", [])
        if not isinstance(sightings, list):
            raise TypeError("'sightings' must be a list")
        checks.append(
            ClaimCheck(
                claim=raw["claim"],
                sightings=tuple(_parse_sighting(s) for s in sightings),
            )
        )
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vf-heatmap",
        description="Render a claim x source verification heat map from a JSON batch of checks.",
    )
    parser.add_argument("input", type=Path, help="JSON file of claim checks.")
    parser.add_argument(
        "--format",
        choices=("html", "text", "csv", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument("-o", "--output", type=Path, help="Write to this file instead of stdout.")
    parser.add_argument("--title", default="Verification heat map", help="HTML page title.")
    parser.add_argument(
        "--no-color", action="store_true", help="Plain text output without ANSI colours."
    )
    args = parser.parse_args(argv)

    try:
        with args.input.open("r", encoding="utf-8") as file:
            checks = load_checks(json.load(file))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"HEATMAP FAILED: {error}", file=sys.stderr)
        return 1

    matrix = event_matrix(checks)
    if args.format == "html":
        rendered = render_html(matrix, title=args.title)
    elif args.format == "csv":
        rendered = render_csv(matrix)
    elif args.format == "json":
        rendered = json.dumps(matrix, indent=2, ensure_ascii=False) + "\n"
    else:
        use_color = not args.no_color and args.output is None and sys.stdout.isatty()
        rendered = render_text(matrix, color=use_color)

    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"HEATMAP WRITTEN: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
