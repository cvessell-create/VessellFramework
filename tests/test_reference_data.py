import gzip

import pytest

from vessell.reference_data import audit_attack, audit_epss


def test_attack_relationships_are_not_silently_assumed_complete():
    result = audit_attack({"type": "bundle", "objects": [
        {"id": "a", "type": "attack-pattern"},
        {"id": "b", "type": "attack-pattern", "revoked": True},
        {"id": "r", "type": "relationship", "source_ref": "a", "target_ref": "missing"},
    ]})
    assert result["active_techniques"] == 1
    assert result["dangling_relationship_endpoints"] == [
        {"relationship": "r", "field": "target_ref", "missing_id": "missing"},
    ]


def test_attack_duplicate_objects_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        audit_attack({"type": "bundle", "objects": [
            {"id": "a", "type": "attack-pattern"}, {"id": "a", "type": "attack-pattern"},
        ]})


def epss_fixture(path, rows, day="2025-09-01"):
    with gzip.open(path, "wt") as file:
        file.write(f"#model_version:v2025.03.14,score_date:{day}\ncve,epss,percentile\n")
        file.write(rows)


def test_historical_epss_validates_probability_and_vintage(tmp_path):
    path = tmp_path / "epss.gz"
    epss_fixture(path, "CVE-2024-1234,0.2,0.9\n")
    result = audit_epss(path, "2025-09-01")
    assert result["records"] == 1
    assert result["evidence_role"] == "HISTORICAL_PROBABILITY_SNAPSHOT"
    with pytest.raises(ValueError, match="date"):
        audit_epss(path, "2025-09-02")


@pytest.mark.parametrize("rows", [
    "", "CVE-2024-1234,nan,0.9\n", "CVE-2024-1234,1.1,0.9\n",
    "CVE-2024-1234,0.1,-1\n", "not-a-cve,0.1,0.2\n",
    "CVE-2024-1234,0.1,0.2\nCVE-2024-1234,0.1,0.2\n",
])
def test_invalid_epss_rejected(tmp_path, rows):
    path = tmp_path / "epss.gz"
    epss_fixture(path, rows)
    with pytest.raises(ValueError):
        audit_epss(path, "2025-09-01")
