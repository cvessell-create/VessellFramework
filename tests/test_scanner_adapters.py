import pytest

from vessell.app.scanner_adapters import _scanner_executable, authorized_asset, extract_cves, import_confirmed_cves


@pytest.mark.parametrize("source", ["greenbone", "trivy", "osv-scanner", "wazuh"])
def test_supported_scanner_exports_yield_cve_ids(source: str) -> None:
    report = {"finding": {"identifiers": ["CVE-2026-12345", "CVE-2025-9999"]}}

    assert extract_cves(source, report) == {"CVE-2026-12345", "CVE-2025-9999"}


def test_import_requires_an_authorized_known_asset() -> None:
    inventory = {"assets": [{"asset_id": "gateway-01", "authorized": True, "confirmed_cves": ["CVE-2024-1"]}]}

    updated = import_confirmed_cves(
        inventory,
        asset_id="gateway-01",
        source="greenbone",
        report={"result": "CVE-2026-12345"},
    )

    assert updated["assets"][0]["confirmed_cves"] == ["CVE-2024-1", "CVE-2026-12345"]
    assert updated["assets"][0]["scanner_source"] == "greenbone"


def test_import_rejects_unauthorized_asset() -> None:
    with pytest.raises(ValueError, match="not authorized"):
        import_confirmed_cves(
            {"assets": [{"asset_id": "gateway-01", "authorized": False}]},
            asset_id="gateway-01",
            source="trivy",
            report={"result": "CVE-2026-12345"},
        )


def test_authorization_check_happens_before_local_scan() -> None:
    with pytest.raises(ValueError, match="not authorized"):
        authorized_asset({"assets": [{"asset_id": "gateway-01", "authorized": False}]}, "gateway-01")


def test_homebrew_scanner_path_is_used_when_path_is_unset(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("vessell.app.scanner_adapters.shutil.which", lambda _: None)
    monkeypatch.setattr("vessell.app.scanner_adapters.Path", lambda _: tmp_path)

    with pytest.raises(RuntimeError, match="not installed"):
        _scanner_executable("trivy")