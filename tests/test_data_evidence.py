import csv
import io
import zipfile

import pytest

from vessell.data_evidence import audit_bls, audit_noaa, audit_wwc, verify_catalog
from vessell.evaluation import sha256


def weather(day="2024-01-01", **changes):
    return {
        "STATION": "TEST", "DATE": day, "TMAX": "10", "TMIN": "0", "PRCP": "0",
        "TMAX_ATTRIBUTES": ",,W", "TMIN_ATTRIBUTES": ",,W", "PRCP_ATTRIBUTES": ",,W",
        **changes,
    }


def test_weather_gap_and_quality_are_not_hidden():
    result = audit_noaa([
        weather(TMAX_ATTRIBUTES=",X,W"),
        weather("2024-01-03", TMIN="", PRCP=""),
    ])
    assert result["station_coverage"]["TEST"]["missing_days_between_endpoints"] == 1
    assert result["quality_flagged_measurements"] == {"TMAX": 1}
    assert result["missing_measurements"] == {"TMIN": 1, "PRCP": 1}
    assert result["evidence_role"] == "OBSERVATIONS_ONLY"


@pytest.mark.parametrize("rows", [
    [], [weather(), weather()], [weather(PRCP="-1")], [weather(TMAX="nan")],
    [weather(STATION="")], [weather(TMAX_ATTRIBUTES="")],
])
def test_weather_rejects_invalid_population(rows):
    with pytest.raises(ValueError):
        audit_noaa(rows)


def test_weather_leap_day_coverage():
    result = audit_noaa([weather("2024-02-28"), weather("2024-03-01")])
    assert result["station_coverage"]["TEST"]["missing_days_between_endpoints"] == 1


def bls(rows, **changes):
    return {"status": "REQUEST_SUCCEEDED", "message": ["unavailable series"],
            "Results": {"series": [{"seriesID": "test", "data": rows}]}, **changes}


def month(period="M01", value="1"):
    return {"year": "2024", "period": period, "value": value, "footnotes": [{}]}


def test_bls_keeps_empty_series_warnings_and_annual_separate():
    empty = audit_bls(bls([]))
    assert empty["series"]["test"]["empty_series"] is True
    assert empty["source_messages"] == ["unavailable series"]
    result = audit_bls(bls([month(), month("M13")]))["series"]["test"]
    assert result["months_per_observed_year"] == {"2024": 1}
    assert result["annual_rows_not_monthly"] == 1


@pytest.mark.parametrize("payload", [
    bls([], status="REQUEST_FAILED"), bls([month(), month()]),
    bls([month("M99")]), bls([month(value="nan")]), bls([month(value="-1")]),
])
def test_bls_invalid_data_is_rejected(payload):
    with pytest.raises(ValueError):
        audit_bls(payload)


def test_wwc_counts_reviews_not_findings_and_exposes_conflicts(tmp_path):
    text = io.StringIO()
    writer = csv.writer(text)
    writer.writerow(["ReviewID", "s_StudyID", "s_Study_Design", "s_Study_Rating"])
    writer.writerows([
        ["1", "s1", "RCT", "meets"], ["1", "s1", "RCT", "meets"],
        ["2", "s2", "QED", "meets"], ["2", "s2", "RCT", "meets"],
    ])
    path = tmp_path / "reviews.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("Interventions_Studies_And_Findings.csv", text.getvalue())
    result = audit_wwc(path)
    assert result["finding_rows"] == 4
    assert result["distinct_review_ids"] == 2
    assert result["conflicting_review_metadata_ids"] == ["2"]
    assert result["consistent_review_design_counts"] == {"RCT": 1}


def test_catalog_rejects_tamper_duplicates_and_traversal(tmp_path):
    file = tmp_path / "data.json"
    file.write_text("{}")
    entry = {"file": file.name, "sha256": sha256(file)}
    assert verify_catalog(tmp_path, [entry]) == {file.name: entry["sha256"]}
    with pytest.raises(ValueError, match="duplicate"):
        verify_catalog(tmp_path, [entry, entry])
    with pytest.raises(ValueError, match="Unsafe"):
        verify_catalog(tmp_path, [{"file": "../data.json", "sha256": entry["sha256"]}])
    file.write_text("changed")
    with pytest.raises(ValueError, match="checksum"):
        verify_catalog(tmp_path, [entry])
