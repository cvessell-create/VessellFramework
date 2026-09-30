#!/usr/bin/env python3
# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Verify package files against a VesselFramework SHA-256 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS_PASS = "PASS"
STATUS_CHANGED = "CHANGED"
STATUS_MISSING = "MISSING"
STATUS_INVALID = "INVALID"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise ValueError("Manifest must be an object containing a 'files' list.")
    return manifest


def verify_manifest(manifest_path: Path) -> tuple[list[tuple[str, str]], int]:
    manifest = load_manifest(manifest_path)
    package_root = manifest_path.parent.resolve()
    results: list[tuple[str, str]] = []
    failures = 0

    for entry in manifest["files"]:
        if not isinstance(entry, dict):
            results.append((STATUS_INVALID, "manifest entry is not an object"))
            failures += 1
            continue

        relative_path = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            results.append((STATUS_INVALID, "manifest entry has invalid path or sha256"))
            failures += 1
            continue

        target = (package_root / relative_path).resolve()
        try:
            target.relative_to(package_root)
        except ValueError:
            results.append((STATUS_INVALID, relative_path))
            failures += 1
            continue

        if not target.is_file():
            results.append((STATUS_MISSING, relative_path))
            failures += 1
            continue

        actual_hash = sha256_path(target)
        if actual_hash.lower() == expected_hash.lower():
            results.append((STATUS_PASS, relative_path))
        else:
            results.append((STATUS_CHANGED, relative_path))
            failures += 1

    return results, failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify files listed in a VesselFramework SHA-256 manifest."
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        default="VessellFramework_v3.8.1_SHA256_Manifest.json",
        help="Path to the JSON manifest.",
    )
    args = parser.parse_args()
    manifest_path = Path(args.manifest).expanduser().resolve()

    try:
        manifest = load_manifest(manifest_path)
        results, failures = verify_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"{STATUS_INVALID}: {manifest_path}: {error}")
        return 2

    print(f"VesselFramework package version: {manifest.get('package_version', 'unknown')}")
    print(f"Manifest: {manifest_path}")
    for status, relative_path in results:
        print(f"[{status}] {relative_path}")

    total = len(results)
    passed = sum(status == STATUS_PASS for status, _ in results)
    print(f"\n{passed}/{total} files verified")
    if failures:
        print("MANIFEST VERIFICATION: FAILED")
        return 1

    print("MANIFEST VERIFICATION: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
