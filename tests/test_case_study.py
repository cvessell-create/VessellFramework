import copy
import json
import sqlite3
from pathlib import Path

import pytest

from vessell.case_study import (
    compare,
    repair_snapshot,
    run_arm,
    validate_spec,
    verify_receipts,
    write_snapshot,
)
from vessell.provenance import (
    SourceStatus,
    disavow,
    intake_claim,
    propagate_correction,
    register_dependent,
    reset_claim_lifecycle,
)


@pytest.fixture(autouse=True)
def isolated_lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def spec():
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / "case_studies/claim_correction/spec.json").read_text())


def test_comparison_measures_real_managed_files_and_restart_receipts(tmp_path):
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(spec()))
    result = compare(path, tmp_path / "study")
    assert result["acceptance_passed"]
    constraint, control = result["outcomes"]
    assert constraint["baseline"]["unverified_uses_allowed"] == 5
    assert constraint["framework"]["unverified_uses_allowed"] == 0
    assert constraint["framework"]["correction_files_read_back"] == 5
    assert constraint["stale_snapshot_reduction_count"] == 5
    assert control["framework"]["corroborated_uses_blocked"] == 0
    assert control["framework"]["consequential_uses_allowed"] == 2
    assert verify_receipts(tmp_path / "study/framework") == 7
    assert result["independent_external_validation"] is False


def test_receipt_verification_detects_file_drift(tmp_path):
    output = tmp_path / "arm"
    run_arm(spec(), output, "framework")
    (output / "unverified-constraint/goal.json").write_text("{}")
    with pytest.raises(ValueError, match="receipt mismatch"):
        verify_receipts(output)


def test_durable_chain_detects_event_tamper(tmp_path):
    output = tmp_path / "arm"
    run_arm(spec(), output, "framework")
    with sqlite3.connect(output / "receipts.sqlite") as connection:
        text, = connection.execute("SELECT payload FROM events LIMIT 1").fetchone()
        event = json.loads(text)
        event["detail"] = "altered"
        connection.execute("UPDATE events SET payload=? WHERE claim_id=? AND seq=?", (
            json.dumps(event), event["claim_id"], event["seq"],
        ))
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_receipts(output)


@pytest.mark.parametrize("table", ["receipts", "events", "claims"])
def test_receipt_verification_detects_incomplete_populations(tmp_path, table):
    output = tmp_path / "arm"
    run_arm(spec(), output, "framework")
    with sqlite3.connect(output / "receipts.sqlite") as connection:
        connection.execute(f"DELETE FROM {table} WHERE rowid=(SELECT MAX(rowid) FROM {table})")
    with pytest.raises(ValueError, match="population"):
        verify_receipts(output)


def test_receipt_verification_preserves_original_text_and_rejects_symlink(tmp_path):
    output = tmp_path / "arm"
    data = spec()
    run_arm(data, output, "framework")
    with sqlite3.connect(output / "receipts.sqlite") as connection:
        originals = connection.execute("SELECT payload FROM claims WHERE stage='intake'").fetchall()
    assert {json.loads(row[0])["text"] for row in originals} == {
        item["claim"] for item in data["scenarios"]
    }
    with sqlite3.connect(output / "receipts.sqlite") as connection:
        events = connection.execute(
            "SELECT payload FROM events ORDER BY claim_id, seq"
        ).fetchall()
    by_claim = {}
    for row in events:
        event = json.loads(row[0])
        by_claim.setdefault(event["claim_id"], []).append(event["timestamp"])
    for timestamps in by_claim.values():
        assert timestamps == sorted(timestamps)
    path = output / "unverified-constraint/goal.json"
    content = path.read_bytes()
    outside = tmp_path / "outside.json"
    outside.write_bytes(content)
    path.unlink()
    path.symlink_to(outside)
    with pytest.raises(ValueError, match="outside managed"):
        verify_receipts(output)


def test_failed_write_does_not_acknowledge_correction(tmp_path, monkeypatch):
    original = intake_claim("Reported claim", "subject", "report", SourceStatus.WORKING_HYPOTHESIS)
    path = tmp_path / "consumer.json"
    write_snapshot(path, original)
    register_dependent(original.id, "managed-json", str(path))
    correction = disavow(original, "operator", "withdrawn", corrected_text="Withdrawal")
    original_write = Path.write_text

    def corrupt_write(self, data, *args, **kwargs):
        return original_write(self, "{}" if self == path else data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", corrupt_write)
    with pytest.raises(ValueError, match="read-back"):
        repair_snapshot(original, correction, path)
    dependent = propagate_correction(original.id)[0]
    assert dependent.confirmed_correction is None
    assert dependent.delivered_correction == correction.id


def test_unregistered_file_is_never_rewritten(tmp_path):
    original = intake_claim("Report", "subject", "report", SourceStatus.WORKING_HYPOTHESIS)
    path = tmp_path / "unregistered.json"
    write_snapshot(path, original)
    content = path.read_bytes()
    correction = disavow(original, "operator", "withdrawn")
    with pytest.raises(ValueError, match="registered"):
        repair_snapshot(original, correction, path)
    assert path.read_bytes() == content


@pytest.mark.parametrize("field,value", [
    ("id", "../escape"), ("consumers", ["../escape"]),
    ("official_record", "true"), ("corrected_at", "2020-01-01T00:00:00Z"),
    ("observed_at", "2026-09-24"), ("corrected_at", "invalid"),
])
def test_spec_rejects_unsafe_inputs_and_noncausal_dates(field, value):
    data = copy.deepcopy(spec())
    data["scenarios"][0][field] = value
    with pytest.raises(ValueError):
        validate_spec(data)


def test_prior_run_is_never_overwritten(tmp_path):
    data = spec()
    run_arm(data, tmp_path / "study", "framework")
    with pytest.raises(ValueError, match="never overwritten"):
        run_arm(data, tmp_path / "study", "framework")
