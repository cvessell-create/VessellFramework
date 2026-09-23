import pytest

from vessell.app.microsoft_intune import _settings, sync_device


def test_intune_adapter_fails_closed_without_credentials(monkeypatch) -> None:
    for name in ("MICROSOFT_TENANT_ID", "MICROSOFT_CLIENT_ID", "MICROSOFT_CLIENT_SECRET"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="MICROSOFT_TENANT_ID"):
        _settings()


def test_intune_adapter_requires_managed_device_id() -> None:
    with pytest.raises(RuntimeError, match="intune_device_id"):
        sync_device({})