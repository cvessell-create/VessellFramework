"""Inventory original and paused game sources without executing game code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, TypedDict

from vessell.evaluation import write_reports

ORIGINAL_COMMIT = "0a147bf95e231eff68ea3be7f10003752ce3b573"
ORIGINAL_SHA256 = "0703c346480d6f5aa01b4793e1d760738ba3bc1d9030e225034f076f10638d60"
SOURCE_FILES = (
    "index.html", "README.md", "LICENSE", ".gitignore",
    "lab.html", "recall.html", "simulation/policy.js", "simulation/run.cjs",
    "simulation/worker.cjs", "simulation/test.cjs", "simulation/lab.js",
    "simulation/lab.css", "simulation/recall.js", "simulation/FINDINGS.md",
    ".github/workflows/ci.yml",
)


class FunctionLocation(TypedDict):
    name: str
    line: int


def inspect_game(game_dir: Path, component_map: Path) -> dict[str, Any]:
    mapping = json.loads(component_map.read_text())
    original = subprocess.run(
        ["git", "-C", str(game_dir), "show", f"{ORIGINAL_COMMIT}:index.html"],
        capture_output=True, check=False,
    )
    if original.returncode:
        raise ValueError("Pinned original game commit is not available in the checkout.")
    if hashlib.sha256(original.stdout).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Pinned original source checksum mismatch.")
    text = original.stdout.decode("utf-8")
    functions: list[FunctionLocation] = [
        {"name": match.group(1), "line": text.count("\n", 0, match.start()) + 1}
        for match in re.finditer(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", text)
    ]
    known = {function for row in mapping["components"] for function in row["functions"]}
    observed = {row["name"] for row in functions}
    if (known != observed or mapping["original_commit"] != ORIGINAL_COMMIT
            or mapping["original_index_sha256"] != ORIGINAL_SHA256):
        raise ValueError("Architecture map does not cover the pinned original function inventory.")
    files = []
    source_snapshots = []
    for name in SOURCE_FILES:
        path = game_dir / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Expected original or paused source is missing or symbolic: {name}")
        data = path.read_bytes()
        files.append({
            "file": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "standing": "original-and-paused-working-tree-snapshot",
        })
        source_snapshots.append({"file": name, "source": data.decode("utf-8")})
    narrative_symbols = {
        "setMessage", "title", "briefing", "use", "finishLevel", "victory",
        "die", "killEnemy", "damage", "cycleWeapon", "update", "drawHUD", "pause",
    }
    narrative_sources = [
        {"symbol": row["name"], "line": row["line"],
         "source_line": text.splitlines()[row["line"] - 1]}
        for row in functions if row["name"] in narrative_symbols
    ]
    return {
        "evaluation": "Pinned game architecture and paused-source inventory",
        "evidence_scope": "Read-only source observations; no original authoring history inferred.",
        "original_commit": ORIGINAL_COMMIT, "original_sha256": ORIGINAL_SHA256,
        "functions": functions, "function_coverage": {"mapped": len(known), "observed": len(functions)},
        "working_tree_sources": files, "component_map": mapping,
        "original_source": text, "working_tree_source_snapshots": source_snapshots,
        "narrative_source_lines": narrative_sources,
        "limitations": [
            "Named-function lexical inventory is not a JavaScript AST or formal call graph.",
            "Anonymous callbacks, constants and CSS are covered by component descriptions, not this regex.",
            "Source ordering does not prove historical implementation order, prompts or model authorship.",
            "Narrative source lines retain original code context; fictional dialogue is not analyst evidence.",
            "Paused working-tree files are identified by hashes, not represented as completed releases.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--component-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output_dir.exists():
            raise ValueError("Use a new inventory directory.")
        result = inspect_game(args.game_dir, args.component_map)
        write_reports(result, args.output_dir)
        print(f"GAME ARCHITECTURE VERIFIED: {result['function_coverage']}; "
              f"{len(result['working_tree_sources'])} source files pinned.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"GAME ARCHITECTURE FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
