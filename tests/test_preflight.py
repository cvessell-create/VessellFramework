import json

from vessell.app.preflight import run_preflight


def test_preflight_flags_placeholder_inventory_and_secrets(tmp_path, monkeypatch) -> None:
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps({"assets": [{"asset_id": "replace-with-id", "authorized": True}]}),
        encoding="utf-8",
    )
    for name in ("APPROVAL_TOKEN", "SCANNER_TOKEN", "WEBHOOK_SECRET", "ALLOWED_WEBHOOK_PREFIX"):
        monkeypatch.delenv(name, raising=False)

    checks = {check["name"]: check for check in run_preflight(inventory, tmp_path / ".env")}

    assert not checks["authorized_inventory"]["ready"]
    assert not checks["control_room_secrets"]["ready"]