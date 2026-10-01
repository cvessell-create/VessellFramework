"""Input-validation regressions for the root-level runner scripts.

Every malformed input must exit with status 2 and a one-line ERROR message,
never a traceback, and truthy strings such as ``"false"`` must not pass a
boolean gate.
"""

import copy
import importlib.util
import json
import sys
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).parents[1]


def _load(filename: str, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = _load("vesselframework_case_runner.py", "vf_case_runner_under_test")
agent = _load("vesselframework_agent.py", "vf_agent_under_test")
manifest = _load("verify_manifest.py", "vf_verify_manifest_under_test")

BASE_CASE: dict[str, Any] = json.loads((ROOT / "example_case.json").read_text(encoding="utf-8"))


def _run_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: Any) -> int:
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps(case), encoding="utf-8")
    (tmp_path / runner.REFERENCE_NAME).write_bytes((ROOT / runner.REFERENCE_NAME).read_bytes())
    monkeypatch.setattr(sys, "argv", ["vesselframework_case_runner.py", str(case_path)])
    return int(runner.main())


def _mutated(**changes: Any) -> dict[str, Any]:
    case = copy.deepcopy(BASE_CASE)
    case.update(changes)
    return case


def _mask(**changes: Any) -> list[dict[str, Any]]:
    entry = copy.deepcopy(BASE_CASE["maskirovka"][0])
    entry.update(changes)
    return [entry]


def _gate(**changes: Any) -> dict[str, Any]:
    gate = copy.deepcopy(BASE_CASE["harm_gate"])
    gate.update(changes)
    return gate


def test_example_case_still_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_case(tmp_path, monkeypatch, BASE_CASE) == 0
    assert "RUNNER STATUS: READY FOR ANALYST REVIEW" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ([1], "must contain a JSON object"),
        (_mutated(title=5), "title must be a non-empty string"),
        (_mutated(evidence="notalist"), "evidence must be a list"),
        (_mutated(evidence=[]), "non-empty evidence list"),
        (_mutated(evidence=["x"]), "Evidence item 1 must be an object"),
        (_mutated(evidence=[dict(BASE_CASE["evidence"][0], upstream_of=5)]), "invalid upstream_of"),
        (_mutated(maskirovka="abc"), "maskirovka field must be a list"),
        (_mutated(maskirovka={"variant": "Structural"}), "maskirovka field must be a list"),
        (_mutated(maskirovka=["x"]), "Maskirovka entry must be an object"),
        (_mutated(maskirovka=_mask(evidence_ids="assessment-001,telemetry-001")), "must be a list of source_id strings"),
        (_mutated(maskirovka=_mask(evidence_ids=["nope"])), "unknown evidence_ids: nope"),
        (_mutated(maskirovka=_mask(trigger_conditions_met="false")), "trigger_conditions_met must be true or false"),
        (_mutated(maskirovka=_mask(notes=7)), "notes must be a string"),
        (_mutated(analysis=[1]), "analysis field must be an object"),
        (_mutated(harm_gate=[1]), "harm_gate field must be an object"),
        (_mutated(harm_gate=_gate(benefit_proportionate="false")), "benefit_proportionate must be true or false"),
        (_mutated(harm_gate=_gate(accuracy_risk="no")), "accuracy_risk must be true or false"),
        (
            _mutated(harm_gate=_gate(current_posture="CONTAIN", evidence_threshold_met=True, action_authorized="false")),
            "action_authorized must be true or false",
        ),
        (_mutated(harm_gate=_gate(current_posture="VERIFY", stop_condition=3)), "stop_condition must be a string"),
    ],
)
def test_case_runner_rejects_malformed_input_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case: Any,
    message: str,
) -> None:
    assert _run_case(tmp_path, monkeypatch, case) == 2
    output = capsys.readouterr().out
    assert output.startswith("ERROR: ")
    assert message in output


def test_null_stop_condition_is_not_recorded_as_present() -> None:
    result = runner.evaluate_forward_posture(
        {"current_posture": "CONTAIN", "evidence_threshold_met": True, "action_authorized": True,
         "rollback_available": True, "stop_condition": None}
    )
    assert result["review_required"] is True
    assert "Containment or stronger action lacks a stop condition." in result["reasons"]


def test_manifest_rejects_wrong_shape_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    for body in ("[]", '{"files": 3}', "{bad"):
        path = tmp_path / "manifest.json"
        path.write_text(body, encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["verify_manifest.py", str(path)])
        assert manifest.main() == 2
        assert capsys.readouterr().out.startswith("INVALID: ")


def test_agent_rejects_non_object_case_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "case.json"
    path.write_text("[1]", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["vesselframework_agent.py", "--dry-run", "--case", str(path)])
    assert agent.main() == 2
    assert "Case file must contain a JSON object" in capsys.readouterr().err


def test_agent_tool_with_non_object_arguments_returns_tool_failure() -> None:
    result = agent.execute_tool("search_web", "[1]")
    assert result["error"] == "Tool arguments must be a JSON object."
    assert "TOOL FAILURE" in result["source_status"]


@pytest.fixture
def model_server() -> Iterator[tuple[str, dict[str, bytes | None]]]:
    state: dict[str, bytes | None] = {"body": None}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            self.rfile.read(int(self.headers["Content-Length"]))
            body = state["body"]
            if body is None:
                self.close_connection = True
                return
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: Any) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", state
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (b"<html>gateway error</html>", "did not return JSON"),
        (json.dumps({"choices": []}).encode(), "did not contain choices[0].message"),
        (json.dumps({"choices": [{"message": [1]}]}).encode(), "invalid message"),
        (json.dumps({"choices": [{"message": {"tool_calls": {"a": 1}}}]}).encode(), "malformed tool_calls"),
        (json.dumps({"choices": [{"message": {"tool_calls": ["x"]}}]}).encode(), "malformed tool_calls"),
        (None, "Model connection failed"),
    ],
)
def test_agent_reports_bad_model_responses_without_traceback(
    model_server: tuple[str, dict[str, bytes | None]],
    capsys: pytest.CaptureFixture[str],
    body: bytes | None,
    message: str,
) -> None:
    url, state = model_server
    state["body"] = body
    code = agent.run_session("hi", None, "test-model", url, "test-key", False, False, 0)
    assert code == 2
    assert message in capsys.readouterr().err


def test_model_response_error_keeps_runtime_error_contract() -> None:
    assert issubclass(agent.ModelResponseError, RuntimeError)


def test_agent_interactive_reset_then_eof_exits_cleanly(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    answers = iter(["/reset"])

    def fake_input(prompt: str = "") -> str:
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", fake_input)
    assert agent.run_session("hi", None, "m", "http://unused", "", True, True, 0) == 0
    capsys.readouterr()


def test_agent_interactive_skips_blank_follow_ups(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    answers = iter(["", "  ", "next", "/quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert agent.run_session("hi", None, "m", "http://unused", "", True, True, 0) == 0
    last_dump = "{" + capsys.readouterr().out.rsplit("\n{", 1)[-1]
    user_messages = [m["content"] for m in json.loads(last_dump)["messages"] if m["role"] == "user"]
    assert user_messages == ["hi", "next"]
