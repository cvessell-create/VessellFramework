#!/usr/bin/env python3
"""
VesselFramework v3.8.1 Shared Private Path Synchronizer

Purpose
-------
Synchronize the packaged live skill and managed continuity blocks into the
configured owner-controlled target paths for the current runtime copy.

Safety properties
-----------------
- dry-run by default;
- --apply required to write;
- atomic skill replacement;
- timestamped backups;
- managed-block updates for continuity files;
- SHA-256 before/after hashes;
- append-only JSONL sync log;
- no claim of success unless a write completes and the post-write hash is read.

This script validates target access before attempting to synchronize paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone
from typing import Any

VERSION = "3.8"
MANAGED_START = "<!-- VESSELFRAMEWORK MANAGED START -->"
MANAGED_END = "<!-- VESSELFRAMEWORK MANAGED END -->"

PACKAGE_DIR = Path(__file__).resolve().parent
SKILL_SOURCE = PACKAGE_DIR / "SKILL.md"
LOG_NAME = "VesselFramework_Path_Sync_Log.jsonl"
TARGET_ROOT_FILE = PACKAGE_DIR / ".vesselframework_target_root.txt"


def read_saved_target_root() -> Path | None:
    if not TARGET_ROOT_FILE.exists():
        return None
    try:
        value = TARGET_ROOT_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not value:
        return None
    return Path(value).expanduser().resolve()


TARGET_ROOT = (
    Path(os.environ.get("VESSELFRAMEWORK_TARGET_ROOT", "")).expanduser().resolve()
    if os.environ.get("VESSELFRAMEWORK_TARGET_ROOT")
    else read_saved_target_root()
)


def save_target_root(path: Path) -> None:
    TARGET_ROOT_FILE.write_text(str(path.expanduser().resolve()), encoding="utf-8")


def resolve_target(path: str) -> Path:
    if TARGET_ROOT is None:
        return Path(path)
    return TARGET_ROOT / path.lstrip("/")


TARGETS = {
    "/mnt/skills/user/vessel-framework-analyst/SKILL.md": {
        "role": "live_skill",
        "source": SKILL_SOURCE,
        "mode": "replace",
        "required": True,
    },
    "/areas/vessel-framework.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__vessel-framework.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/areas/maskirovka-paper.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__maskirovka-paper.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/areas/bottleneck-thesis.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__bottleneck-thesis.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/topics/writing-style.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "topics__writing-style.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
}

def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def backup_path(target: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return target.with_name(target.name + f".vesselframework_backup_{stamp}")

def atomic_write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, target)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

def update_managed_block(existing: str, managed: str) -> str:
    managed = managed.strip()
    if MANAGED_START not in managed or MANAGED_END not in managed:
        raise ValueError("Managed payload does not contain required block markers.")

    if MANAGED_START in existing and MANAGED_END in existing:
        start = existing.index(MANAGED_START)
        end = existing.index(MANAGED_END, start) + len(MANAGED_END)
        prefix = existing[:start].rstrip()
        suffix = existing[end:].lstrip()
        parts = [p for p in (prefix, managed, suffix) if p]
        return "\n\n".join(parts).rstrip() + "\n"

    existing = existing.rstrip()
    return ((existing + "\n\n") if existing else "") + managed + "\n"

def log_event(log_path: Path, event: dict[str, Any]) -> None:
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

def path_has_access(path: Path, *, read: bool = False, write: bool = False) -> bool:
    flags = 0
    if read:
        flags |= os.R_OK
    if write:
        flags |= os.W_OK
    if not flags:
        return False
    try:
        return os.access(path, flags)
    except (TypeError, ValueError):
        return False

def sync_one(target_text: str, cfg: dict[str, Any], apply: bool, create_missing: bool, log_path: Path) -> dict[str, Any]:
    target = resolve_target(target_text)
    source = Path(cfg["source"])
    event = {
        "timestamp": utc_now(),
        "framework_version": VERSION,
        "target": str(target),
        "role": cfg["role"],
        "mode": cfg["mode"],
        "source": str(source),
        "required": bool(cfg["required"]),
        "apply": apply,
        "status": "PENDING",
        "pre_hash": sha256_path(target),
        "post_hash": None,
        "backup": None,
        "error": None,
    }

    try:
        if not source.exists():
            raise FileNotFoundError(f"Package source missing: {source}")

        if target.exists() and not path_has_access(target, read=True):
            raise PermissionError(f"Cannot read target path: {target}")

        if not target.parent.exists():
            if not create_missing:
                event["status"] = "MISSING_TARGET"
                return event
            target.parent.mkdir(parents=True, exist_ok=True)

        if apply and not path_has_access(target.parent, write=True):
            raise PermissionError(f"Cannot write to target directory: {target.parent}")

        if not target.exists() and not create_missing:
            event["status"] = "MISSING_TARGET"
            return event

        if not apply:
            event["status"] = "DRY_RUN"
            return event

        if target.exists():
            bkp = backup_path(target)
            bkp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, bkp)
            event["backup"] = str(bkp)

        if cfg["mode"] == "replace":
            content = source.read_text(encoding="utf-8")
            atomic_write_text(target, content)
        elif cfg["mode"] == "managed_block":
            managed = source.read_text(encoding="utf-8")
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
            content = update_managed_block(existing, managed)
            atomic_write_text(target, content)
        else:
            raise ValueError(f"Unknown sync mode: {cfg['mode']}")

        event["post_hash"] = sha256_path(target)
        if event["post_hash"] is None:
            raise RuntimeError("Write returned without readable post-write hash.")
        event["status"] = "UPDATED"
        return event

    except Exception as exc:
        event["status"] = "ERROR"
        event["error"] = f"{type(exc).__name__}: {exc}"
        return event

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write target files. Default is dry-run.")
    parser.add_argument("--create-missing", action="store_true", help="Allow creation of missing registered targets.")
    parser.add_argument("--log", default=str(PACKAGE_DIR / LOG_NAME), help="JSONL sync log path.")
    parser.add_argument(
        "--target-root",
        type=str,
        default=None,
        help="Override the target root path used for owned mirrored/copy environments and save it for future runs.",
    )
    args = parser.parse_args()

    if args.target_root:
        target_root = Path(args.target_root).expanduser().resolve()
        save_target_root(target_root)
        globals()["TARGET_ROOT"] = target_root

    log_path = Path(args.log)
    required_failure = False

    print(f"VesselFramework Path Synchronizer v{VERSION}")
    print("MODE:", "APPLY" if args.apply else "DRY RUN")

    for target, cfg in TARGETS.items():
        event = sync_one(target, cfg, args.apply, args.create_missing, log_path)
        log_event(log_path, event)
        print(f"[{event['status']}] {target}")
        if event["error"]:
            print("  ", event["error"])
        if cfg["required"] and event["status"] not in ("UPDATED", "DRY_RUN"):
            required_failure = True

    if required_failure:
        print("FRAMEWORK STATE: DEGRADED — RUNTIME PATH NOT SYNCHRONIZED")
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
