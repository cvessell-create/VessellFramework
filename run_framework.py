#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Cross-platform VesselFramework runtime launcher."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


PACKAGE_DIR = Path(__file__).resolve().parent
INSTALLER = PACKAGE_DIR / "install_vesselframework_v3_8.py"
TARGET_ROOT_FILE = PACKAGE_DIR / ".vesselframework_target_root.txt"


def resolve_python() -> str:
    """Prefer the active virtual environment, then Conda, then this interpreter."""
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        candidate = Path(virtual_env) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if candidate.is_file():
            return str(candidate)

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        candidate = Path(conda_prefix) / ("python.exe" if os.name == "nt" else "bin/python")
        if candidate.is_file():
            return str(candidate)

    return sys.executable


def resolve_target_root(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()

    environment_root = os.environ.get("VESSELFRAMEWORK_TARGET_ROOT")
    if environment_root:
        return Path(environment_root).expanduser().resolve()

    if TARGET_ROOT_FILE.is_file():
        saved_root = TARGET_ROOT_FILE.read_text(encoding="utf-8").strip()
        if saved_root:
            return Path(saved_root).expanduser().resolve()

    return PACKAGE_DIR


def run_checked(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, check=True, cwd=PACKAGE_DIR)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the VesselFramework installer consistently across environments.")
    parser.add_argument("--target-root", help="Owner-controlled target root; saved by the installer.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--apply", action="store_true", help="Write synchronized targets.")
    mode_group.add_argument("--dry-run", action="store_true", help="Validate and report without writing targets (default).")
    parser.add_argument("--create-missing", action="store_true", help="Allow creation of missing registered targets.")
    parser.add_argument("--skip-checks", action="store_true", help="Skip mypy and compile checks before synchronization.")
    args = parser.parse_args()

    if not INSTALLER.is_file():
        print(f"ERROR: installer not found: {INSTALLER}")
        return 2

    python_command = resolve_python()
    target_root = resolve_target_root(args.target_root)
    print(f"Using Python: {python_command}")
    print(f"Target root: {target_root}")

    try:
        if not args.skip_checks:
            run_checked([python_command, "-m", "mypy", str(INSTALLER), "--ignore-missing-imports"])
            run_checked([python_command, "-m", "py_compile", str(INSTALLER)])

        installer_args = [python_command, str(INSTALLER), "--target-root", str(target_root)]
        if args.create_missing:
            installer_args.append("--create-missing")
        if args.apply:
            installer_args.append("--apply")
        run_checked(installer_args)
    except subprocess.CalledProcessError as error:
        print(f"FRAMEWORK STATE: DEGRADED — command failed with exit code {error.returncode}")
        return error.returncode or 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
