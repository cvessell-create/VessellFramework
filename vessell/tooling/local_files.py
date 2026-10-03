"""Constrained adapters for read-only local-file inspection commands."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

_READ_ONLY_COMMANDS: dict[str, tuple[str, ...]] = {
    "exiftool": ("-json", "--"),
    "binwalk": (),
    "zsteg": (),
    "gnupg": ("--list-packets",),
}
_EXECUTABLES: dict[str, tuple[str, ...]] = {
    "gnupg": ("gpg", "gpg2"),
}


@dataclass(frozen=True)
class ToolRunResult:
    tool_id: str
    input_path: str
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class CryptoRunResult:
    tool_id: str
    input_path: str
    output_path: str
    returncode: int


def run_local_inspector(
    tool_id: str,
    input_path: Path,
    *,
    timeout_seconds: int = 60,
) -> ToolRunResult:
    """Run an allow-listed local-file inspector without a shell.

    The adapter never extracts files, decrypts content, scans a network
    target, or handles keys. Tool output is returned to the caller and is
    not logged or persisted automatically.
    """
    if tool_id not in _READ_ONLY_COMMANDS:
        raise ValueError(f"{tool_id!r} is not an allow-listed read-only inspector")
    if timeout_seconds < 1 or timeout_seconds > 600:
        raise ValueError("timeout_seconds must be between 1 and 600")
    target = input_path.expanduser().resolve(strict=True)
    if not target.is_file():
        raise ValueError("input_path must resolve to a regular file")
    executable = next(
        (path for name in _EXECUTABLES.get(tool_id, (tool_id,)) if (path := shutil.which(name))),
        None,
    )
    if executable is None:
        raise RuntimeError(f"{tool_id} is not installed or available on PATH")
    command = [executable, *_READ_ONLY_COMMANDS[tool_id], str(target)]
    completed = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
        shell=False,
    )
    result = ToolRunResult(
        tool_id=tool_id,
        input_path=str(target),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit code {completed.returncode}"
        raise RuntimeError(f"{tool_id} failed: {detail}")
    return result


def decrypt_openpgp(
    input_path: Path,
    output_path: Path,
    *,
    authorized: bool,
    timeout_seconds: int = 120,
) -> CryptoRunResult:
    """Decrypt one OpenPGP file using the local GnuPG keyring and prompt.

    The caller must explicitly acknowledge authorization. GnuPG handles its
    own key/passphrase prompt; no secret is accepted as an argument or logged.
    The destination is never overwritten and is created with owner-only
    permissions after successful decryption.
    """
    if authorized is not True:
        raise PermissionError("explicit authorization is required for decryption")
    if timeout_seconds < 1 or timeout_seconds > 600:
        raise ValueError("timeout_seconds must be between 1 and 600")
    source = input_path.expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("input_path must resolve to a regular file")
    destination = output_path.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"refusing to overwrite output: {destination}")
    parent = destination.parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("output_path parent must be a directory")
    destination = parent / destination.name
    if destination == source:
        raise ValueError("input_path and output_path must differ")
    executable = shutil.which("gpg") or shutil.which("gpg2")
    if executable is None:
        raise RuntimeError("GnuPG is not installed or available on PATH")

    with tempfile.TemporaryDirectory(prefix=".vessell-decrypt-", dir=parent) as workdir:
        decrypted = Path(workdir) / "plaintext"
        command = [executable, "--output", str(decrypted), "--decrypt", str(source)]
        completed = subprocess.run(
            command,
            check=False,
            shell=False,
            timeout=timeout_seconds,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"GnuPG decryption failed with exit code {completed.returncode}")
        if not decrypted.is_file():
            raise RuntimeError("GnuPG reported success but produced no output file")

        descriptor = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        try:
            with os.fdopen(descriptor, "wb") as output, decrypted.open("rb") as source_file:
                shutil.copyfileobj(source_file, output)
                output.flush()
                os.fsync(output.fileno())
        except OSError:
            destination.unlink(missing_ok=True)
            raise

    return CryptoRunResult(
        tool_id="gnupg",
        input_path=str(source),
        output_path=str(destination),
        returncode=completed.returncode,
    )
