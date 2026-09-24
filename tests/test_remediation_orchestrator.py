import pytest
from fastapi.testclient import TestClient

import vessell.app.remediation_orchestrator as orchestrator
from vessell.app.remediation_orchestrator import RemediationStore, validate_required_configuration


def _assets() -> list[dict]:
    return [
        {
            "asset_id": "gateway-01",
            "vendor": "Check Point",
            "product": "Security Gateway",
            "authorized": True,
            "confirmed_cves": ["CVE-2026-1"],
            "remediation_webhook": "https://automation.example.internal/checkpoint/remediate",
        }
    ]


def _catalog() -> dict:
    return {
        "catalogVersion": "test",
        "vulnerabilities": [
            {"cveID": "CVE-2026-1", "vendorProject": "Check Point", "product": "Security Gateway"}
        ],
    }


def test_synchronization_is_idempotent_and_requires_ticketed_approval(tmp_path) -> None:
    store = RemediationStore(tmp_path / "remediation.db")
    store.initialize()

    assert store.synchronize(_assets(), _catalog()) == 1
    assert store.synchronize(_assets(), _catalog()) == 0
    action = store.list_actions()[0]
    assert action["status"] == "PENDING_APPROVAL"

    store.approve(action["action_id"], "security-operator", "CHG-12345")

    assert store.list_actions()[0]["status"] == "APPROVED"
    assert store.list_actions()[0]["change_ticket"] == "CHG-12345"


def test_vendor_only_correlation_cannot_be_approved(tmp_path) -> None:
    store = RemediationStore(tmp_path / "remediation.db")
    store.initialize()
    catalog = {"vulnerabilities": [{"cveID": "CVE-2026-2", "vendorProject": "Check Point", "product": "Multiple Products"}]}

    store.synchronize(_assets(), catalog)
    action = store.list_actions()[0]

    assert action["status"] == "REVIEW_REQUIRED"


def test_configuration_fails_closed_for_missing_or_invalid_values(monkeypatch) -> None:
    for name in ("APPROVAL_TOKEN", "SCANNER_TOKEN", "WEBHOOK_SECRET", "ALLOWED_WEBHOOK_PREFIX"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="APPROVAL_TOKEN"):
        validate_required_configuration()

    monkeypatch.setenv("APPROVAL_TOKEN", "approval")
    monkeypatch.setenv("SCANNER_TOKEN", "scanner")
    monkeypatch.setenv("WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("ALLOWED_WEBHOOK_PREFIX", "http://automation.example.internal/")

    with pytest.raises(RuntimeError, match="absolute HTTPS"):
        validate_required_configuration()

    monkeypatch.setenv("ALLOWED_WEBHOOK_PREFIX", "https://automation.example.internal")

    with pytest.raises(RuntimeError, match="end with"):
        validate_required_configuration()


def test_api_rechecks_configuration_for_protected_operations(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("APPROVAL_TOKEN", "approval")
    monkeypatch.setenv("SCANNER_TOKEN", "scanner")
    monkeypatch.setenv("WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("ALLOWED_WEBHOOK_PREFIX", "https://automation.example.internal/")
    monkeypatch.setenv("DATABASE", str(tmp_path / "remediation.db"))
    monkeypatch.setenv("POLL_SECONDS", "3600")
    monkeypatch.setattr(orchestrator, "fetch_kev_catalog", lambda: {"vulnerabilities": []})

    with TestClient(orchestrator.create_app()) as client:
        dashboard = client.get("/")
        assert dashboard.status_code == 200
        assert "VessellFramework Control Room" in dashboard.text
        monkeypatch.delenv("WEBHOOK_SECRET")
        headers = {"X-Approval-Token": "approval"}

        assert client.post("/sync", headers=headers).status_code == 503
        assert client.post("/actions/example/approve", headers=headers, json={}).status_code == 503
        assert client.post("/actions/example/verify", headers={"X-Scanner-Token": "scanner"}, json={}).status_code == 503


def test_dispatch_blocks_non_allowlisted_webhook(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("APPROVAL_TOKEN", "approval")
    monkeypatch.setenv("SCANNER_TOKEN", "scanner")
    monkeypatch.setenv("WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("ALLOWED_WEBHOOK_PREFIX", "https://automation.example.internal/")

    store = RemediationStore(tmp_path / "remediation.db")
    store.initialize()
    assets = _assets()
    assets[0]["remediation_webhook"] = "https://attacker.example.org/remediate"
    store.synchronize(assets, _catalog())
    action = store.list_actions()[0]
    store.approve(action["action_id"], "security-operator", "CHG-12345")

    status = store.dispatch(action["action_id"])
    updated = store.list_actions()[0]

    assert status == "BLOCKED_CONFIGURATION"
    assert updated["status"] == "BLOCKED_CONFIGURATION"
    assert "allowlist" in str(updated["result"]).lower()


def test_dispatch_posts_signed_webhook_for_approved_action(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("APPROVAL_TOKEN", "approval")
    monkeypatch.setenv("SCANNER_TOKEN", "scanner")
    monkeypatch.setenv("WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("ALLOWED_WEBHOOK_PREFIX", "https://automation.example.internal/")

    captured: dict[str, object] = {}

    class _Response:
        text = "ok"

        def raise_for_status(self) -> None:
            return None

    def _fake_post(url: str, *, content: bytes, headers: dict[str, str], timeout: int) -> _Response:
        captured["url"] = url
        captured["content"] = content
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Response()

    import httpx

    monkeypatch.setattr(httpx, "post", _fake_post)

    store = RemediationStore(tmp_path / "remediation.db")
    store.initialize()
    store.synchronize(_assets(), _catalog())
    action = store.list_actions()[0]
    store.approve(action["action_id"], "security-operator", "CHG-12345")

    status = store.dispatch(action["action_id"])
    updated = store.list_actions()[0]

    assert status == "DISPATCHED"
    assert updated["status"] == "DISPATCHED"
    assert captured["url"] == "https://automation.example.internal/checkpoint/remediate"
    headers = captured["headers"]
    assert isinstance(headers, dict)
    assert headers["Idempotency-Key"] == action["action_id"]
    assert headers["X-Remediation-Signature"].startswith("sha256=")