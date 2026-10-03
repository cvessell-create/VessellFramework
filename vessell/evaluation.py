"""Reproducible retrospective scoring of externally produced CDC forecasts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date
from pathlib import Path
from statistics import fmean
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_inputs(data_dir: Path) -> dict[str, str]:
    manifest = json.loads((data_dir / "download_manifest.json").read_text(encoding="utf-8"))
    required = {
        "cdc_ensemble_state_part1.csv", "cdc_ensemble_state_part2.csv",
        "cdc_observed_state.csv", "cdc_forecast_archive_metadata.json",
    }
    hashes: dict[str, str] = {}
    for entry in manifest["downloads"]:
        if entry["file"] not in required:
            continue
        path = data_dir / entry["file"]
        actual = sha256(path)
        if actual != entry["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path}")
        hashes[entry["file"]] = actual
    if set(hashes) != required:
        raise ValueError("Manifest lacks required CDC files.")
    return hashes


def _number(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid nonnegative number in {field}: {row[field]}")
    return value


def interval_score(lower: float, upper: float, actual: float, alpha: float = 0.05) -> float:
    if not all(math.isfinite(x) for x in (lower, upper, actual, alpha)):
        raise ValueError("Interval score inputs must be finite.")
    if lower > upper or not 0 < alpha < 1:
        raise ValueError("Invalid interval bounds or alpha.")
    return upper - lower + 2 / alpha * max(lower - actual, 0, actual - upper)


def score_cdc(data_dir: Path) -> dict[str, Any]:
    hashes = verified_inputs(data_dir)
    metadata = json.loads((data_dir / "cdc_forecast_archive_metadata.json").read_text())
    if metadata["id"] != "ci7c-73kg":
        raise ValueError("Unexpected CDC dataset identifier.")
    observed: dict[tuple[str, date], float] = {}
    with (data_dir / "cdc_observed_state.csv").open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["target"] != "observed_inc_death":
                continue
            if not row["location_name"].strip():
                raise ValueError("Observed row lacks a location name.")
            key = row["location_name"], date.fromisoformat(row["point_date"])
            value = _number(row, "point")
            if key in observed:
                raise ValueError(f"Duplicate observed key: {key}")
            observed[key] = value
    history: dict[str, list[tuple[date, float]]] = {}
    for (location, day), value in sorted(observed.items()):
        history.setdefault(location, []).append((day, value))

    errors: list[float] = []
    baseline_errors: list[float] = []
    scores: list[float] = []
    covered: list[float] = []
    by_horizon: dict[str, list[tuple[float, float]]] = {}
    missing_observed = missing_baseline = missing_interval = selected = duplicates = 0
    nonfuture = 0
    seen: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for name in ("cdc_ensemble_state_part1.csv", "cdc_ensemble_state_part2.csv"):
        with (data_dir / name).open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if not row["target"].endswith(" wk ahead inc death"):
                    continue
                selected += 1
                if not row["location_name"].strip():
                    raise ValueError("Forecast row lacks a location name.")
                if row["signal_type"] != "Ensemble model" or row["location_type"] != "state":
                    raise ValueError("Unexpected forecast population.")
                issued = date.fromisoformat(row["date_forecast_submitted"])
                target_date = date.fromisoformat(row["point_date"])
                horizon = row["num_weeks_ahead_forecast"]
                if horizon not in {"1", "2", "3", "4"}:
                    raise ValueError("Invalid forecast horizon.")
                forecast_key = (
                    row["location_name"], row["date_forecast_submitted"],
                    row["point_date"], row["target"]
                )
                if forecast_key in seen:
                    if seen[forecast_key] != row:
                        raise ValueError(f"Conflicting duplicate forecast key: {forecast_key}")
                    duplicates += 1
                    continue
                seen[forecast_key] = row
                if target_date <= issued:
                    nonfuture += 1
                    continue
                actual = observed.get((row["location_name"], target_date))
                if actual is None:
                    missing_observed += 1
                    continue
                prior = [
                    value for day, value in history.get(row["location_name"], []) if day < issued
                ]
                if not prior:
                    missing_baseline += 1
                    continue
                error = abs(_number(row, "point") - actual)
                baseline_error = abs(prior[-1] - actual)
                errors.append(error)
                baseline_errors.append(baseline_error)
                by_horizon.setdefault(horizon, []).append((error, baseline_error))
                if not row["quantile_0025"] or not row["quantile_0975"]:
                    missing_interval += 1
                    continue
                lower = _number(row, "quantile_0025")
                upper = _number(row, "quantile_0975")
                scores.append(interval_score(lower, upper, actual))
                covered.append(float(lower <= actual <= upper))
    if not errors:
        raise ValueError("No forecasts could be matched and scored.")
    return {
        "evaluation": "CDC state ensemble incident-death forecasts",
        "evidence_status": "RETROSPECTIVE_EXTERNAL_DATA_EVALUATION",
        "independent_external_validation": False,
        "source_dataset": metadata["id"],
        "source_license": metadata["licenseId"],
        "source_hashes": hashes,
        "implementation_sha256": sha256(Path(__file__)),
        "counts": {
            "selected": selected, "scored": len(errors),
            "exact_duplicate_forecasts_excluded": duplicates,
            "nonfuture_targets_excluded": nonfuture,
            "unmatched_observation": missing_observed,
            "missing_baseline": missing_baseline, "missing_interval": missing_interval,
            "interval_scored": len(scores),
        },
        "metrics": {
            "ensemble_mae": fmean(errors),
            "persistence_baseline_mae": fmean(baseline_errors),
            "mean_paired_absolute_error_improvement": fmean(baseline_errors) - fmean(errors),
            "mean_95_interval_score": fmean(scores) if scores else None,
            "empirical_95_interval_coverage": fmean(covered) if covered else None,
        },
        "by_horizon": {
            horizon: {
                "n": len(pairs),
                "ensemble_mae": fmean(pair[0] for pair in pairs),
                "persistence_baseline_mae": fmean(pair[1] for pair in pairs),
            }
            for horizon, pairs in sorted(by_horizon.items())
        },
        "limitations": [
            "Joins on exact source location names; FIPS is absent for some territories.",
            "Exact repeated forecast rows are counted and excluded; conflicting duplicates fail.",
            "Targets on or before submission date are excluded rather than scored as predictions.",
            "Scores externally produced CDC ensemble forecasts, not forecasts made by VessellFramework.",
            "Retrospective exploratory analysis, not preregistered or independent external validation.",
            "Observed values are archive revisions, not guaranteed as-of-issue vintages.",
            ("Persistence uses the latest observation dated before issue; publication availability "
             "at issue time is not proven."),
            "Repeated states, weeks and horizons are correlated; no causal efficacy claim.",
            "Does not establish cybersecurity control efficacy or analyst decision improvement.",
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    report_id = hashlib.sha256(payload).hexdigest()
    return (
        f"# {result['evaluation']}\n\n"
        f"Report payload SHA-256: `{report_id}`\n\n"
        "This is an external-data scoring run, not independent validation of framework efficacy.\n\n"
        "The exact machine-readable result follows; Markdown and JSON must agree.\n\n"
        f"```json\n{json.dumps(result, indent=2, sort_keys=True)}\n```\n"
    )


def write_reports(result: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    machine = output_dir / "evaluation.json"
    human = output_dir / "evaluation.md"
    machine.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    human.write_text(render_report(result), encoding="utf-8")
    verify_reports(machine, human)
    return machine, human


def verify_reports(machine: Path, human: Path) -> None:
    result = json.loads(machine.read_text(encoding="utf-8"))
    if human.read_text(encoding="utf-8") != render_report(result):
        raise ValueError("Markdown/JSON evaluation reports are not synchronized.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = score_cdc(args.data_dir)
        machine, human = write_reports(result, args.output_dir)
    except (OSError, ValueError, KeyError) as error:
        print(f"EVALUATION FAILED: {error}")
        return 2
    print(f"Evaluation saved and synchronized: {machine}, {human}")
    print(json.dumps(result["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
