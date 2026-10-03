import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

from vessell.game_bridge import framework_play, new_session
from vessell.provenance import reset_claim_lifecycle


@pytest.fixture(autouse=True)
def lifecycle():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


def test_game_same_root_does_not_corroborate_and_actual_files_are_recalled(tmp_path):
    game = new_session(tmp_path, "framework")
    assert game.action("use")["uses_blocked"] == 1
    assert game.action("archive")["independent_roots"] == 1
    assert game.action("echo")["status"] == "UNVERIFIED"
    assert game.action("use")["uses_blocked"] == 2
    assert game.action("survey")["status"] == "CORROBORATED"
    assert game.action("use")["uses_allowed"] == 1
    result = game.action("withdraw")
    assert result["correction_files_verified"] == 4
    assert result["stale_consumers"] == 0
    assert result["correction"]["status"] == "UNVERIFIED"
    assert all(json.loads(path.read_text())["id"] == game.correction.id
               for path in game.snapshots)
    assert (game.folder / "evaluation.json").is_file()


def test_baseline_bypasses_gate_and_keeps_stale_files(tmp_path):
    game = new_session(tmp_path, "baseline")
    assert game.action("use")["uses_allowed"] == 1
    result = game.action("withdraw")
    assert result["stale_consumers"] == 4
    assert result["correction_files_verified"] == 0
    assert all(json.loads(path.read_text())["id"] == game.claim.id for path in game.snapshots)


def test_repeated_sources_and_closed_missions_fail_explicitly(tmp_path):
    game = new_session(tmp_path, "framework")
    game.action("archive")
    with pytest.raises(ValueError, match="already inspected"):
        game.action("archive")
    game.action("withdraw")
    with pytest.raises(ValueError, match="Mission ended"):
        game.action("use")


def test_corrupt_consumer_is_not_acknowledged_as_success(tmp_path):
    game = new_session(tmp_path, "framework")
    game.snapshots[0].write_text("{}")
    with pytest.raises(ValueError):
        game.action("withdraw")


def test_same_id_content_drift_fails_before_gate_or_correction(tmp_path):
    game = new_session(tmp_path, "framework")
    payload = json.loads(game.snapshots[0].read_text())
    payload["text"] = "Tampered text with unchanged identifier"
    game.snapshots[0].write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="drifted"):
        game.action("use")
    assert game.attempts == []
    assert game.correction is None


def test_missing_engine_does_not_start_or_orphan_worker(tmp_path, monkeypatch):
    def unexpected_worker(*args, **kwargs):
        pytest.fail("Worker started before validating the engine source.")

    monkeypatch.setattr(subprocess, "Popen", unexpected_worker)
    with pytest.raises(FileNotFoundError):
        framework_play(tmp_path, 42)


def test_unknown_modes_and_operations_fail(tmp_path):
    with pytest.raises(ValueError, match="Mode"):
        new_session(tmp_path, "unknown")
    game = new_session(tmp_path, "framework")
    with pytest.raises(ValueError, match="Unknown"):
        game.action("unknown")


def test_loopback_api_static_scope_and_browser_contract(tmp_path):
    (tmp_path / "lab.html").write_text("<title>Game lab</title>")
    (tmp_path / "private.json").write_text('{"private":true}')
    with socket.socket() as socket_probe:
        socket_probe.bind(("127.0.0.1", 0))
        port = socket_probe.getsockname()[1]
    process = subprocess.Popen([
        sys.executable, "-m", "vessell.game_bridge", "--game-dir", str(tmp_path),
        "--output-dir", str(tmp_path / "receipts"), "--port", str(port),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(base + "/api/status", timeout=1) as response:
                    assert json.load(response)["runtime"] == "VessellFramework"
                break
            except urllib.error.URLError:
                time.sleep(.02)
        else:
            pytest.fail("Bridge did not become responsive.")
        with urllib.request.urlopen(base + "/lab.html") as response:
            assert b"Game lab" in response.read()
        with pytest.raises(urllib.error.HTTPError) as failure:
            urllib.request.urlopen(base + "/private.json")
        assert failure.value.code == 404

        def post(path, data, origin=base):
            request = urllib.request.Request(base + path, data=json.dumps(data).encode(),
                                             headers={"Content-Type": "application/json",
                                                      "Origin": origin})
            with urllib.request.urlopen(request) as response:
                return json.load(response)

        with pytest.raises(urllib.error.HTTPError) as failure:
            post("/api/session", {"mode": "framework"}, "https://untrusted.example")
        assert failure.value.code == 403
        session = post("/api/session", {"mode": "framework"})["session"]
        for operation in ("use", "archive", "echo", "use", "survey", "use", "withdraw"):
            result = post("/api/action", {"session": session, "operation": operation})
        assert result["uses_blocked"] == 2
        assert result["uses_allowed"] == 1
        assert result["correction_files_verified"] == 4
    finally:
        process.terminate()
        process.wait(timeout=5)
