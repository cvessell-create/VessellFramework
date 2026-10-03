"""Optional full-document decoding and redaction-aware workforce data checks."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import date
from importlib.metadata import version
from pathlib import Path
from typing import Any


def audit_pdf(path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as error:
        raise RuntimeError("PDF decoding requires the optional [evaluation] dependencies.") from error

    try:
        reader = PdfReader(path, strict=True)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted source PDF is not supported: {path.name}")
        if not reader.pages:
            raise ValueError(f"Source PDF has no pages: {path.name}")
        pages = []
        for index, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            pages.append({
                "page": index, "characters": len(text),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "text_empty": not text.strip(),
            })
    except PdfReadError as error:
        raise ValueError(f"PDF decoding failed for {path.name}: {error}") from error
    return {
        "validation": "ALL_PAGES_DECODED",
        "reader": {"name": "pypdf", "version": version("pypdf")},
        "pages": pages, "page_count": len(pages),
        "empty_text_pages": [page["page"] for page in pages if page["text_empty"]],
        "text_characters": sum(page["characters"] for page in pages),
        "limitations": [
            "Decoding is not a substantive human audit, OCR or validation of images/diagrams.",
            "Empty text pages remain explicit; scanned/image-only content requires review.",
            "Advice and incident observations do not establish causal control efficacy.",
        ],
    }


def audit_opm_rows(
    rows: list[dict[str, Any]], expected_period: str,
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9]{6}", expected_period):
        raise ValueError("OPM expected period must be YYYYMM.")
    date(int(expected_period[:4]), int(expected_period[4:]), 1)
    required = {"count", "personnel_action_effective_date_yyyymm", "agency_code"}
    if not rows:
        raise ValueError("OPM accessions population is empty.")
    missing: Counter[str] = Counter()
    redacted: Counter[str] = Counter()
    periods: Counter[str] = Counter()
    known_count_total = unknown_counts = unknown_periods = reference_count_total = 0
    agency_known_counts: Counter[str] = Counter()
    agency_unknown_count_rows: Counter[str] = Counter()
    for row in rows:
        if not required <= row.keys():
            raise ValueError(f"OPM row lacks required columns: {sorted(required - row.keys())}")
        for field, value in row.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                missing[field] += 1
            elif value == "REDACTED":
                redacted[field] += 1
        period = row["personnel_action_effective_date_yyyymm"]
        if period is None or period in ("", "REDACTED"):
            unknown_periods += 1
        else:
            if not isinstance(period, str) or not re.fullmatch(r"[0-9]{6}", period):
                raise ValueError(f"Invalid OPM action period: {period}")
            date(int(period[:4]), int(period[4:]), 1)
            periods[period] += 1
        raw_count = row["count"]
        agency = row["agency_code"]
        agency_key = agency if isinstance(agency, str) and agency.strip() else "UNKNOWN"
        if raw_count is None or raw_count in ("", "REDACTED"):
            unknown_counts += 1
            agency_unknown_count_rows[agency_key] += 1
        else:
            if not isinstance(raw_count, str) or not re.fullmatch(r"[0-9]+", raw_count):
                raise ValueError(f"Invalid OPM count: {raw_count}")
            count = int(raw_count)
            known_count_total += count
            agency_known_counts[agency_key] += count
            if period == expected_period:
                reference_count_total += count
    return {
        "records": len(rows), "expected_period": expected_period,
        "period_counts": dict(periods), "unknown_period_rows": unknown_periods,
        "outside_reference_period_rows": sum(
            count for period, count in periods.items() if period != expected_period
        ),
        "known_count_subtotal": known_count_total, "unknown_count_rows": unknown_counts,
        "reference_period_known_count_subtotal": reference_count_total,
        "agency_known_count_subtotals": dict(sorted(agency_known_counts.items())),
        "agency_unknown_count_rows": dict(sorted(agency_unknown_count_rows.items())),
        "missing_cells_by_column": dict(sorted(missing.items())),
        "redacted_cells_by_column": dict(sorted(redacted.items())),
        "evidence_role": "REDACTION_AWARE_ADMINISTRATIVE_CONTEXT",
        "limitations": [
            "Known count subtotal is not a population total when counts are withheld.",
            "REDACTED is withheld information, never a zero or a negative finding.",
            "Rows/aggregated counts are not necessarily unique people; no identity inference.",
            "No deduplication of redaction-collapsed rows or inferred missing attributes.",
            ("File reference period and action-effective period may differ; off-period rows "
             "are exposed, not silently corrected or merged into reference-period totals."),
            "No posting-level fraud labels, comparator or causal efficacy conclusion.",
        ],
    }


def audit_opm(path: Path, expected_period: str) -> dict[str, Any]:
    try:
        import duckdb
    except ImportError as error:
        raise RuntimeError(
            "Parquet decoding requires the optional [evaluation] dependencies."
        ) from error
    local = path.resolve(strict=True)
    if not local.is_file():
        raise ValueError("OPM Parquet input must be a local regular file.")
    try:
        with duckdb.connect(":memory:", config={
            "autoinstall_known_extensions": "false", "autoload_known_extensions": "false",
        }) as connection:
            cursor = connection.execute("SELECT * FROM read_parquet(?)", [str(local)])
            names = [column[0] for column in cursor.description]
            rows = [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]
    except duckdb.Error as error:
        raise ValueError(f"Parquet decoding failed for {local.name}: {error}") from error
    result = audit_opm_rows(rows, expected_period)
    result["columns"] = names
    result["validation"] = "ALL_ROWS_DECODED_AND_REQUIRED_FIELDS_CHECKED"
    result["reader"] = {"name": "duckdb", "version": version("duckdb")}
    return result
