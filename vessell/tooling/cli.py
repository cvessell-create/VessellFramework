"""Command-line entry point for discovering and using optional local tools."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vessell.tooling.catalog import discover_tools, list_tools
from vessell.tooling.local_files import decrypt_openpgp, run_local_inspector


def main() -> int:
    parser = argparse.ArgumentParser(prog="vessell-tools")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list supported tools and their use modes")
    commands.add_parser("doctor", help="check which command-line tools are on PATH")
    inspect = commands.add_parser("inspect", help="inspect a local file with a read-only tool")
    inspect.add_argument("tool", choices=("exiftool", "binwalk", "zsteg", "gnupg"))
    inspect.add_argument("file", type=Path)
    inspect.add_argument("--timeout", type=int, default=60)
    decrypt = commands.add_parser(
        "decrypt-openpgp",
        help="decrypt a local OpenPGP file using your local GnuPG keyring",
    )
    decrypt.add_argument("file", type=Path)
    decrypt.add_argument("output", type=Path)
    decrypt.add_argument(
        "--authorized",
        action="store_true",
        required=True,
        help="confirm you are authorized to decrypt this file",
    )
    decrypt.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    if args.command == "list":
        for tool in list_tools():
            print(f"{tool.tool_id}\t{tool.activity.value}\t{tool.name}: {tool.purpose}")
        return 0
    if args.command == "doctor":
        for status in discover_tools():
            path = status.executable_path or (
                "manual integration" if not status.tool.executables else "not found"
            )
            print(f"{status.tool.tool_id}\t{path}")
        return 0
    if args.command == "inspect":
        result = run_local_inspector(args.tool, args.file, timeout_seconds=args.timeout)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    if args.command == "decrypt-openpgp":
        decrypt_result = decrypt_openpgp(
            args.file,
            args.output,
            authorized=args.authorized,
            timeout_seconds=args.timeout,
        )
        print(f"Decrypted output written to {decrypt_result.output_path}")
        return 0
    parser.error("unsupported command")
    return 2
