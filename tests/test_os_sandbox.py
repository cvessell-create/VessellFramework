import errno
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "vf_sandbox_runner", Path(__file__).resolve().parents[1] / "sandbox/run.py",
)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def isolation_fixture(monkeypatch, **changes):
    values = {
        "uid": 501, "cap": "0000000000000000", "privileges": "1",
        "interfaces": ["lo"], "root": "ro", "data": "ro",
    } | changes

    class FakePath:
        def __init__(self, name):
            self.name = str(name)

        def read_text(self):
            if self.name == "/proc/self/status":
                return f"CapEff:\t{values['cap']}\nNoNewPrivs:\t{values['privileges']}\n"
            if self.name == "/proc/mounts":
                return "\n".join([
                    f"overlay / overlay {values['root']} 0 0",
                    f"data /data bind {values['data']} 0 0",
                    "catalog /catalog.json bind ro 0 0",
                    "expansion /expansion bind ro 0 0",
                ])
            raise AssertionError(self.name)

        def iterdir(self):
            assert self.name == "/sys/class/net"
            return [FakePath(name) for name in values["interfaces"]]

        def exists(self):
            assert self.name == "/var/run/docker.sock"
            return False

        def write_text(self, _text):
            raise OSError(errno.EROFS, "Read-only filesystem")

    monkeypatch.setattr(RUNNER, "Path", FakePath)
    monkeypatch.setattr(RUNNER.os, "getuid", lambda: values["uid"])


def test_sandbox_requires_all_os_isolation_checks(monkeypatch):
    isolation_fixture(monkeypatch)
    assert RUNNER.verify_isolation()["passed"] is True


@pytest.mark.parametrize("changes", [
    {"uid": 0}, {"cap": "0000000000000001"}, {"privileges": "0"},
    {"interfaces": ["eth0", "lo"]}, {"root": "rw"}, {"data": "rw"},
])
def test_sandbox_rejects_weakened_containment(monkeypatch, changes):
    isolation_fixture(monkeypatch, **changes)
    with pytest.raises(RuntimeError, match="OS isolation failed"):
        RUNNER.verify_isolation()
