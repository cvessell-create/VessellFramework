"""Tests for optional third-party tool discovery and safe local adapters."""

import subprocess
from pathlib import Path

import pytest

from vessell.tooling import (
    ToolActivity,
    decrypt_openpgp,
    discover_tools,
    get_tool,
    list_tools,
    local_files,
    run_local_inspector,
)


def test_catalog_covers_decode_crypto_osint_and_recon_tools() -> None:
    tools = {tool.tool_id: tool for tool in list_tools()}

    assert {
        "cyberchef",
        "exiftool",
        "binwalk",
        "zsteg",
        "steghide",
        "openstego",
        "gnupg",
        "openssl",
        "hashid",
        "hashcat",
        "osint-framework",
        "spiderfoot",
        "sn1per",
        "mosint",
        "user-scanner",
    } <= tools.keys()
    assert tools["sn1per"].activity is ToolActivity.ACTIVE_RECON
    assert tools["hashcat"].activity is ToolActivity.LOCAL_AUTHORIZED
    assert tools["cyberchef"].activity is ToolActivity.REFERENCE_ONLY


def test_unknown_tool_id_is_an_explicit_error() -> None:
    with pytest.raises(KeyError, match="unknown tool id"):
        get_tool("not-a-tool")


def test_discovery_checks_path_without_launching(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "vessell.tooling.catalog.shutil.which",
        lambda name: f"/tools/{name}" if name == "exiftool" else None,
    )

    results = {item.tool.tool_id: item for item in discover_tools()}

    assert results["exiftool"].available
    assert results["exiftool"].executable_path == "/tools/exiftool"
    assert not results["sn1per"].available


def test_file_inspector_uses_allowlisted_shell_free_command(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "report.txt"
    artifact.write_text("plain text", encoding="utf-8")
    observed: dict[str, object] = {}

    monkeypatch.setattr(local_files.shutil, "which", lambda _: "/tools/exiftool")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["command"] = command
        observed["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr(local_files.subprocess, "run", fake_run)
    result = run_local_inspector("exiftool", artifact)

    command = observed["command"]
    kwargs = observed["kwargs"]
    assert isinstance(command, list)
    assert command[:3] == ["/tools/exiftool", "-json", "--"]
    assert command[-1] == str(artifact.resolve())
    assert kwargs["shell"] is False
    assert result.stdout == "[]"


def test_file_inspector_rejects_unapproved_tools_before_execution(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "input.txt"
    artifact.write_text("data", encoding="utf-8")

    with pytest.raises(ValueError, match="not an allow-listed"):
        run_local_inspector("sn1per", artifact)
    with pytest.raises(ValueError, match="not an allow-listed"):
        run_local_inspector("gpg", artifact)


def test_gnupg_inspector_lists_packets_without_decrypting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "message.gpg"
    artifact.write_bytes(b"not decrypted")
    observed: dict[str, object] = {}
    monkeypatch.setattr(local_files.shutil, "which", lambda name: f"/tools/{name}")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["command"] = command
        return subprocess.CompletedProcess(command, 0, "encrypted packet", "")

    monkeypatch.setattr(local_files.subprocess, "run", fake_run)

    result = run_local_inspector("gnupg", artifact)

    command = observed["command"]
    assert isinstance(command, list)
    assert command[0] == "/tools/gpg"
    assert "--list-packets" in command
    assert "--decrypt" not in command
    assert result.stdout == "encrypted packet"


def test_openpgp_decryption_requires_authorization_and_never_overwrites(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "message.gpg"
    artifact.write_bytes(b"encrypted")
    destination = tmp_path / "message.txt"
    monkeypatch.setattr(local_files.shutil, "which", lambda _: "/tools/gpg")
    launched = False

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal launched
        launched = True
        assert "--decrypt" in command
        assert "--passphrase" not in command
        assert kwargs["shell"] is False
        assert kwargs.get("capture_output") is None
        Path(command[command.index("--output") + 1]).write_text(
            "decrypted for the owner", encoding="utf-8"
        )
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(local_files.subprocess, "run", fake_run)

    with pytest.raises(PermissionError, match="explicit authorization"):
        decrypt_openpgp(artifact, destination, authorized=False)
    assert not launched

    result = decrypt_openpgp(artifact, destination, authorized=True)
    assert result.output_path == str(destination)
    assert destination.read_text(encoding="utf-8") == "decrypted for the owner"
    assert destination.stat().st_mode & 0o777 == 0o600

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        decrypt_openpgp(artifact, destination, authorized=True)


def test_file_inspector_surfaces_nonzero_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "image.png"
    artifact.write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.setattr(local_files.shutil, "which", lambda _: "/tools/zsteg")
    monkeypatch.setattr(
        local_files.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 2, "", "bad image"),
    )

    with pytest.raises(RuntimeError, match="bad image"):
        run_local_inspector("zsteg", artifact)
