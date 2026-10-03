import csv
import json

import pytest

from vessell.evaluation import (
    interval_score,
    score_cdc,
    sha256,
    verified_inputs,
    verify_reports,
    write_reports,
)
from vessell.validation import validate_record


def data_fixture(tmp_path):
    fields = ["location_name", "fips", "point_date", "target", "point", "signal_type", "location_type",
              "date_forecast_submitted", "num_weeks_ahead_forecast",
              "quantile_0025", "quantile_0975"]
    observed = [
        {"location_name": "Alabama", "fips": "01", "point_date": "2020-01-04",
         "target": "observed_inc_death", "point": "10"},
        {"location_name": "Alabama", "fips": "01", "point_date": "2020-01-11",
         "target": "observed_inc_death", "point": "20"},
    ]
    forecasts = [{
        "location_name": "Alabama", "fips": "01", "point_date": "2020-01-11",
        "target": "1 wk ahead inc death",
        "point": "18", "signal_type": "Ensemble model", "location_type": "state",
        "date_forecast_submitted": "2020-01-06", "num_weeks_ahead_forecast": "1",
        "quantile_0025": "15", "quantile_0975": "25",
    }]
    for name, rows in (
        ("cdc_observed_state.csv", observed),
        ("cdc_ensemble_state_part1.csv", forecasts),
        ("cdc_ensemble_state_part2.csv", []),
    ):
        with (tmp_path / name).open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    metadata = tmp_path / "cdc_forecast_archive_metadata.json"
    metadata.write_text(json.dumps({"id": "ci7c-73kg", "licenseId": "CC_40_BY"}))
    manifest = {"downloads": [{"file": p.name, "sha256": sha256(p)}
                              for p in tmp_path.iterdir()]}
    (tmp_path / "download_manifest.json").write_text(json.dumps(manifest))
    return tmp_path


def test_empirical_scoring_uses_prior_observation_not_future(tmp_path) -> None:
    result = score_cdc(data_fixture(tmp_path))
    assert result["metrics"]["ensemble_mae"] == 2
    assert result["metrics"]["persistence_baseline_mae"] == 10
    assert result["metrics"]["mean_95_interval_score"] == 10
    assert result["counts"]["scored"] == 1
    assert result["independent_external_validation"] is False
    validate_record(result, "evaluation.schema.json")


def test_source_tampering_is_rejected(tmp_path) -> None:
    data_fixture(tmp_path)
    (tmp_path / "cdc_observed_state.csv").write_text("tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verified_inputs(tmp_path)


def test_reports_read_back_match_and_detect_drift(tmp_path) -> None:
    result = score_cdc(data_fixture(tmp_path))
    machine, human = write_reports(result, tmp_path / "reports")
    verify_reports(machine, human)
    human.write_text(human.read_text() + "drift")
    with pytest.raises(ValueError, match="not synchronized"):
        verify_reports(machine, human)


def test_interval_score_penalizes_misses() -> None:
    assert interval_score(10, 20, 15) == 10
    assert interval_score(10, 20, 25) == 210
    assert interval_score(10, 20, 5) == 210
    with pytest.raises(ValueError):
        interval_score(20, 10, 15)
    with pytest.raises(ValueError):
        interval_score(10, float("nan"), 15)


@pytest.mark.parametrize("conflict", [False, True])
def test_duplicates_are_counted_or_conflicts_rejected(tmp_path, conflict: bool) -> None:
    data_fixture(tmp_path)
    path = tmp_path / "cdc_ensemble_state_part1.csv"
    lines = path.read_text().splitlines()
    duplicate = lines[1].replace(",18,", ",19,") if conflict else lines[1]
    path.write_text("\n".join([*lines, duplicate]) + "\n")
    manifest_path = tmp_path / "download_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["downloads"]:
        if entry["file"] == path.name:
            entry["sha256"] = sha256(path)
    manifest_path.write_text(json.dumps(manifest))
    if conflict:
        with pytest.raises(ValueError, match="Conflicting duplicate"):
            score_cdc(tmp_path)
    else:
        result = score_cdc(tmp_path)
        assert result["counts"]["exact_duplicate_forecasts_excluded"] == 1
        assert result["counts"]["scored"] == 1
