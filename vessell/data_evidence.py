"""Audit downloaded public data without confusing context with efficacy evidence."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
import zipfile
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from vessell.evaluation import sha256, write_reports


def audit_noaa(rows: list[dict[str, str]]) -> dict[str, Any]:
    stations: dict[str, set[date]] = {}
    missing: Counter[str] = Counter()
    flagged: Counter[str] = Counter()
    reversed_temperature = 0
    for row in rows:
        station = row["STATION"].strip()
        if not station:
            raise ValueError("NOAA station is empty.")
        day = date.fromisoformat(row["DATE"])
        days = stations.setdefault(station, set())
        if day in days:
            raise ValueError(f"Duplicate NOAA station/date: {station}, {day}")
        days.add(day)
        values: dict[str, float] = {}
        for field in ("TMAX", "TMIN", "PRCP"):
            text = row.get(field, "").strip()
            if not text:
                missing[field] += 1
                continue
            value = float(text)
            if not math.isfinite(value) or (field == "PRCP" and value < 0):
                raise ValueError(f"Invalid NOAA {field}: {text}")
            values[field] = value
            attributes = row.get(f"{field}_ATTRIBUTES", "").split(",")
            if len(attributes) < 3:
                raise ValueError(f"Missing NOAA quality attributes: {field}")
            if attributes[1].strip():
                flagged[field] += 1
        if "TMIN" in values and "TMAX" in values and values["TMIN"] > values["TMAX"]:
            reversed_temperature += 1
    if not rows:
        raise ValueError("NOAA population is empty.")
    coverage = {}
    for station, days in sorted(stations.items()):
        start, end = min(days), max(days)
        expected = {start + timedelta(days=i) for i in range((end - start).days + 1)}
        coverage[station] = {
            "start": start.isoformat(), "end": end.isoformat(), "observed_days": len(days),
            "missing_days_between_endpoints": len(expected - days),
        }
    return {
        "records": len(rows), "station_coverage": coverage,
        "missing_measurements": dict(missing), "quality_flagged_measurements": dict(flagged),
        "temperature_order_anomalies": reversed_temperature,
        "evidence_role": "OBSERVATIONS_ONLY",
        "limitations": [
            "Coverage is measured between observed endpoints, not an assumed requested window.",
            "Flags are retained and counted; no flagged value is treated as a validated outcome.",
            "Units and upstream query must be verified before cross-source comparisons.",
            "No forecast vintages exist in this file; no forecasting efficacy is scored.",
        ],
    }


def audit_bls(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["status"] != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS request failed: {payload.get('message')}")
    series_results = {}
    for series in payload["Results"]["series"]:
        identifier = series["seriesID"]
        if identifier in series_results:
            raise ValueError(f"Duplicate BLS series: {identifier}")
        periods: set[tuple[int, str]] = set()
        annual = footnoted = 0
        years: Counter[str] = Counter()
        for row in series["data"]:
            year, period = int(row["year"]), row["period"]
            if period not in {f"M{i:02d}" for i in range(1, 14)}:
                raise ValueError(f"Invalid BLS period: {period}")
            key = year, period
            if key in periods:
                raise ValueError(f"Duplicate BLS period: {identifier}, {key}")
            periods.add(key)
            value = float(row["value"].replace(",", ""))
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid BLS value: {row['value']}")
            if period == "M13":
                annual += 1
            else:
                years[str(year)] += 1
            footnoted += bool(any(note.get("text") for note in row["footnotes"]))
        series_results[identifier] = {
            "records": len(periods), "annual_rows_not_monthly": annual,
            "months_per_observed_year": dict(sorted(years.items())),
            "footnoted_rows": footnoted,
            "empty_series": not periods,
        }
    if not series_results:
        raise ValueError("BLS response has no series.")
    return {
        "source_messages": payload["message"], "series": series_results,
        "evidence_role": "AGGREGATE_CONTEXT",
        "limitations": [
            "Success status does not establish success of every series; empty series remain explicit.",
            "Observed years are not proof that every requested year was returned.",
            "Openings are a stock and hires a flow; their difference does not count ghost jobs.",
            "No posting-level labels, causal effect or framework efficacy is inferred.",
        ],
    }


def audit_wwc(path: Path) -> dict[str, Any]:
    reviews: dict[str, set[tuple[str, str, str]]] = {}
    findings = 0
    with zipfile.ZipFile(path) as archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            raise ValueError(f"Corrupt WWC ZIP member: {corrupt}")
        with archive.open("Interventions_Studies_And_Findings.csv") as binary:
            for row in csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig")):
                review = row["ReviewID"].strip()
                if not review:
                    raise ValueError("WWC row has no ReviewID.")
                reviews.setdefault(review, set()).add((
                    row["s_StudyID"], row["s_Study_Design"], row["s_Study_Rating"]
                ))
                findings += 1
    if not reviews:
        raise ValueError("WWC review population is empty.")
    conflicts = [key for key, variants in reviews.items() if len(variants) != 1]
    consistent = [next(iter(variants)) for variants in reviews.values() if len(variants) == 1]
    return {
        "finding_rows": findings, "distinct_review_ids": len(reviews),
        "distinct_nonempty_study_ids": len({
            study for variants in reviews.values() for study, _, _ in variants if study
        }),
        "conflicting_review_metadata_ids": sorted(conflicts),
        "consistent_review_design_counts": dict(Counter(x[1] for x in consistent)),
        "consistent_review_rating_counts": dict(Counter(x[2] for x in consistent)),
        "evidence_role": "STUDY_APPRAISAL_REFERENCE",
        "limitations": [
            "Distributions count consistent reviews once, not repeated finding rows.",
            "Design strings retain source spelling/case; missing categories remain explicit.",
            "A review ID is not necessarily an independent experiment.",
            "No pooled effect size or transfer of education efficacy to this framework is claimed.",
        ],
    }


def verify_catalog(data_dir: Path, entries: list[dict[str, Any]]) -> dict[str, str]:
    hashes = {}
    root = data_dir.resolve()
    for entry in entries:
        name = entry["file"]
        path = (root / name).resolve()
        if path.parent != root or name in hashes:
            raise ValueError(f"Unsafe or duplicate catalog filename: {name}")
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise ValueError(f"Source checksum mismatch: {name}")
        hashes[name] = actual
    return hashes


def audit_data(data_dir: Path, previous_catalog: Path | None = None) -> dict[str, Any]:
    initial = json.loads((data_dir / "download_manifest.json").read_text(encoding="utf-8"))
    verified_catalog = verify_catalog(data_dir, initial["downloads"])
    if previous_catalog is not None:
        prior = json.loads(previous_catalog.read_text(encoding="utf-8"))
        verified_catalog.update(verify_catalog(data_dir, prior["sources"]))
    files = sorted(p for p in data_dir.iterdir() if p.is_file() and p.name != "download_manifest.json")
    sources = [{
        "file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path),
        "integrity_status": (
            "MATCHED_PRIOR_LOCAL_MANIFEST" if path.name in verified_catalog
            else "BASELINE_CAPTURED_THIS_RUN_NOT_REMOTE_AUTHENTICATED"
        ),
    } for path in files]
    checks: dict[str, Any] = {}
    for name in ("bls_jolts_2016_2025.json", "bls_jolts_professional_2016_2025.json"):
        checks[name] = audit_bls(json.loads((data_dir / name).read_text()))
    checks["noaa_daily_2024_sample.json"] = audit_noaa(
        json.loads((data_dir / "noaa_daily_2024_sample.json").read_text())
    )
    checks["wwc_study_reviews.zip"] = audit_wwc(data_dir / "wwc_study_reviews.zip")
    for name in ("dod_prime_awards_sample.json", "dod_professional_scientific_awards_sample.json",
                 "dod_subawards_sample.json"):
        payload = json.loads((data_dir / name).read_text())
        checks[name] = {
            "records": len(payload["results"]), "pagination": payload["page_metadata"],
            "evidence_role": "AWARD_DISCOVERY_ONLY",
            "limitation": "Bounded award sample; not study-design or efficacy evidence.",
        }
    stix = json.loads((data_dir / "cisa_aa24_038a_stix.json").read_text())
    if stix["type"] != "bundle":
        raise ValueError("Expected CISA STIX bundle.")
    checks["cisa_aa24_038a_stix.json"] = {
        "objects": len(stix["objects"]),
        "object_types": dict(Counter(obj["type"] for obj in stix["objects"])),
        "evidence_role": "INCIDENT_INTELLIGENCE",
        "limitation": "Bundle shape only, not STIX conformance or negative labels/patch outcomes.",
    }
    checks["state_travel_advisories.xml"] = {
        "items": len(ElementTree.parse(data_dir / "state_travel_advisories.xml")
                     .findall("./channel/item")),
        "evidence_role": "POLICY_CONTEXT_NOT_EVENT_PROBABILITY",
    }
    for name in ("cisa_ssvc_guide.pdf", "cisa_aa24_038a_advisory.pdf"):
        with (data_dir / name).open("rb") as file:
            if file.read(5) != b"%PDF-":
                raise ValueError(f"Invalid PDF header: {name}")
        checks[name] = {"validation": "PDF header only; full-content audit pending."}
    parquet = data_dir / "opm_accessions_202409_v3.parquet"
    with parquet.open("rb") as file:
        start = file.read(4)
        file.seek(-4, 2)
        end = file.read(4)
    if start != b"PAR1" or end != b"PAR1":
        raise ValueError("Invalid OPM Parquet framing.")
    checks[parquet.name] = {"validation": "Framing only; semantic/row validation pending."}
    return {
        "evaluation": "Public-data suitability and quality audit",
        "independent_external_validation": False,
        "implementation_sha256": sha256(Path(__file__)),
        "sources": sources, "checks": checks,
        "limitations": [
            "Local hashes establish subsequent identity, not remote authenticity or source truth.",
            ("Supplemental retrieval URLs/queries remain in the source inventory; this is a "
             "quality baseline, not a reconstructed complete acquisition log."),
            "Only named checks were executed; a catalog entry is not semantic validation.",
            "Courses guide methods; course completion and framework efficacy are not claimed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--previous-catalog", type=Path)
    args = parser.parse_args()
    try:
        if args.output_dir.resolve() == args.data_dir.resolve():
            raise ValueError("Audit outputs must be separate from source data.")
        result = audit_data(args.data_dir, args.previous_catalog)
        machine, human = write_reports(result, args.output_dir)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile,
            ElementTree.ParseError) as error:
        print(f"DATA AUDIT FAILED: {error}", file=sys.stderr)
        return 2
    print(f"Data audit saved and synchronized: {machine}, {human}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
