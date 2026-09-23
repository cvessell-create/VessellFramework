from types import SimpleNamespace

import pytest

from vessell.agentic_soc import plan_hunt
from vessell.agentic_soc_adapter import AzureAdapterConfigurationError, AzureLogAnalyticsAdapter


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object]] = []

    def query_workspace(self, workspace_id: str, query: str, *, timespan: object) -> object:
        self.calls.append((workspace_id, query, timespan))
        table = SimpleNamespace(
            columns=[SimpleNamespace(name="Timestamp"), SimpleNamespace(name="AccountName")],
            rows=[["2026-09-14T00:00:00Z", "analyst"], ["2026-09-14T00:01:00Z", "token=secret"]],
        )
        return SimpleNamespace(tables=[table])


def test_adapter_runs_bounded_query_and_redacts_rows() -> None:
    client = FakeClient()
    adapter = AzureLogAnalyticsAdapter(client, "workspace-1", max_rows=1)
    batch = adapter.query(plan_hunt("Investigate Windows Target One logins", max_rows=1))

    assert batch.table == "DeviceLogonEvents"
    assert len(batch.rows) == 1
    assert batch.truncated is True
    assert client.calls[0][0] == "workspace-1"


def test_adapter_fails_closed_without_workspace_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VESSELFRAMEWORK_LOG_ANALYTICS_WORKSPACE_ID", raising=False)

    with pytest.raises(AzureAdapterConfigurationError, match="WORKSPACE_ID"):
        AzureLogAnalyticsAdapter.from_environment()