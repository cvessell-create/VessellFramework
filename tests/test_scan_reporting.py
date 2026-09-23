from datetime import UTC, datetime

import pytest

from vessell.scan_reporting import build_scan_report, write_scan_report


def test_build_scan_report_includes_summary_and_evidence_notes() -> None:
    report = build_scan_report(
        [
            {"host": "192.168.1.10", "status": "Vulnerable", "vulns": ["CVE-2024-5678"]},
            {"host": "192.168.1.15", "status": "Secure", "vulns": []},
        ],
        generated_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
    )

    assert "**Hosts assessed:** 2" in report
    assert "**Vulnerable:** 1" in report
    assert "CVE-2024-5678" in report
    assert "## Evidence Notes" in report


def test_report_escapes_markdown_cells_and_writes_file(tmp_path) -> None:
    output = write_scan_report(
        [{"host": "host|one", "status": "Unknown", "vulns": []}],
        tmp_path / "reports" / "scan_report.md",
    )

    assert output.read_text(encoding="utf-8").count("host\\|one") == 1


def test_report_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="status must be one of"):
        build_scan_report([{"host": "host-1", "status": "Compromised", "vulns": []}])