"""Loopback-only bridge between the framework and the user's fictional game."""

from __future__ import annotations

import argparse
import json
import select
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

from vessell.case_study import repair_snapshot, write_snapshot
from vessell.evaluation import sha256, write_reports
from vessell.provenance import (
    ClaimRecord,
    SourceStatus,
    add_corroboration,
    claim_events,
    disavow,
    gate_for_use,
    intake_claim,
    register_dependent,
    verify_event_chain,
)


@dataclass
class GameSession:
    folder: Path
    mode: str
    claim: ClaimRecord
    snapshots: list[Path]
    sources: set[str] = field(default_factory=set)
    attempts: list[bool] = field(default_factory=list)
    correction: ClaimRecord | None = None
    snapshot_hashes: dict[str, str] = field(default_factory=dict)

    def action(self, operation: str) -> dict[str, Any]:
        if self.correction is not None:
            raise ValueError("Mission ended; start a new session.")
        self.report()
        if operation in {"archive", "echo", "survey"}:
            if operation in self.sources:
                raise ValueError("Source already inspected; repeated sightings are not new evidence.")
            self.sources.add(operation)
            root = "archive-root" if operation in {"archive", "echo"} else "survey-root"
            add_corroboration(self.claim, source=f"Fictional {operation} terminal",
                              source_tier=SourceStatus.SOURCE_ESTABLISHED, root=root)
        elif operation == "use":
            allowed, _ = gate_for_use(self.claim, "consequential")
            self.attempts.append(allowed if self.mode == "framework" else True)
        elif operation == "withdraw":
            self.correction = disavow(
                self.claim, "Game operator", "Synthetic map changed after the briefing",
                corrected_text="East route clearance is withdrawn; new routes need verification.",
            )
            if self.mode == "framework":
                for path in self.snapshots:
                    self.snapshot_hashes[path.name] = repair_snapshot(
                        self.claim, self.correction, path,
                    )
        else:
            raise ValueError("Unknown mission operation.")
        return self.report()

    def report(self) -> dict[str, Any]:
        for record in [self.claim] + ([self.correction] if self.correction else []):
            valid, reason = verify_event_chain(record.id)
            if not valid:
                raise ValueError(f"Game event chain failed: {reason}")
        expected = self.correction if self.correction and self.mode == "framework" else self.claim
        receipts = []
        for path in self.snapshots:
            payload = json.loads(path.read_text())
            if (not isinstance(payload, dict) or payload.get("id") != expected.id
                    or sha256(path) != self.snapshot_hashes[path.name]):
                raise ValueError("Game consumer has drifted from its expected claim version.")
            receipts.append({"consumer": path.stem, "claim_id": payload["id"], "sha256": sha256(path)})
        result = {
            "evaluation": "Fictional provenance game mission",
            "evidence_scope": "Actual Python lifecycle and local files; synthetic evidence only.",
            "session": self.folder.name, "mode": self.mode,
            "status": self.claim.status.value, "independent_roots": self.claim.independent_roots(),
            "sources": sorted(self.sources), "uses_allowed": sum(self.attempts),
            "uses_blocked": len(self.attempts) - sum(self.attempts),
            "withdrawn": self.correction is not None,
            "correction_files_verified": len(receipts)
            if self.correction and self.mode == "framework" else 0,
            "stale_consumers": len(receipts) if self.correction and self.mode == "baseline" else 0,
            "receipts": receipts, "original_claim": self.claim.to_dict(),
            "correction": self.correction.to_dict() if self.correction else None,
            "events": {
                record.id: [asdict(event) for event in claim_events(record.id)]
                for record in [self.claim] + ([self.correction] if self.correction else [])
            },
            "limitations": [
                "Terminal source roots are prescribed synthetic game evidence, not authenticated sources.",
                "Baseline deliberately bypasses game claim gating and downstream correction.",
                "Live sessions are process-local; saved reports are audit artifacts, not restart recovery.",
                "No external account, job, weapon, scanner or remediation system is connected.",
            ],
        }
        write_reports(result, self.folder)
        return result


def new_session(output: Path, mode: str) -> GameSession:
    if mode not in {"framework", "baseline"}:
        raise ValueError("Mode must be framework or baseline.")
    folder = output / f"game-{uuid4().hex}"
    folder.mkdir(parents=True, exist_ok=False)
    claim = intake_claim(
        "The east passage is clear for the fictional evacuation.",
        "Fictional station", "Unverified radio rumor", SourceStatus.WORKING_HYPOTHESIS,
        source_root="archive-root",
        uncertainty="Synthetic single-source report; not a real-world safety assertion.",
    )
    snapshots = [folder / f"{name}.json" for name in ("goals", "search", "briefing", "memory")]
    for path in snapshots:
        write_snapshot(path, claim)
        register_dependent(claim.id, "managed-json", str(path), via="provisional game archive")
    return GameSession(folder, mode, claim, snapshots,
                       snapshot_hashes={path.name: sha256(path) for path in snapshots})


def framework_play(game_dir: Path, seed: int) -> dict[str, Any]:
    """Execute planner proposals only after the actual Python consequential-use gate."""
    engine_hash = sha256(game_dir / "index.html")
    claim = intake_claim(
        "The local fictional engine is the primary record for this simulation session.",
        "Fictional FPS session", f"Local engine SHA-256 {engine_hash}",
        SourceStatus.SOURCE_ESTABLISHED, is_official_record=True,
        uncertainty="Trusted game-state observations only; no claim of real-world source authenticity.",
    )
    process = subprocess.Popen(
        ["node", str(game_dir / "simulation/worker.cjs")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    assert process.stdin is not None and process.stdout is not None
    frames = 0

    def exchange(request: dict[str, Any]) -> dict[str, Any]:
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        if not select.select([process.stdout], [], [], 5)[0]:
            raise RuntimeError("Game worker timed out.")
        line = process.stdout.readline()
        if not line:
            raise RuntimeError("Game worker exited without a response.")
        response: dict[str, Any] = json.loads(line)
        if "error" in response:
            raise RuntimeError(f"Game worker rejected action: {response['error']}")
        return response

    try:
        response = exchange({"operation": "reset", "seed": seed})
        while response["observation"]["state"] not in {"victory", "dead"} and frames < 36000:
            observation = response["observation"]
            proposal = response["proposal"]
            if proposal["fire"] and not observation["enemies"]:
                raise ValueError("Planner proposed fire without an observed fictional enemy.")
            allowed, reason = gate_for_use(claim, "consequential")
            if not allowed:
                raise ValueError(f"Framework player blocked proposal: {reason}")
            response = exchange({"operation": "step", "action": proposal})
            frames += 1
        result: dict[str, Any] = exchange({"operation": "result"})["result"]
        valid, reason = verify_event_chain(claim.id)
        if not valid:
            raise ValueError(reason)
        result["python_gate_decisions"] = frames
        result["python_gate_blocked"] = 0
        result["gate_claim"] = claim.to_dict()
        result["gate_events"] = [asdict(event) for event in claim_events(claim.id)]
        return result
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        process.stdin.close()
        process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()


def simulate(game_dir: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError("Simulation requires a new output directory.")
    output.mkdir(parents=True)
    fps_path = output / "fps.json"
    process = subprocess.run(
        ["node", str(game_dir / "simulation/run.cjs"), str(fps_path)],
        capture_output=True, text=True, check=False, timeout=120,
    )
    if process.returncode:
        raise RuntimeError(f"Game engine failed: {process.stdout}\n{process.stderr}")
    fps = json.loads(fps_path.read_text())
    framework_player = [framework_play(game_dir, seed) for seed in (1, 7, 42, 99, 2026)]
    for row in framework_player:
        comparison = next(item for item in fps["results"]
                          if item["seed"] == row["seed"] and item["policy"] == "planned")
        if row["trace_sha256"] != comparison["trace_sha256"]:
            raise ValueError("Python-gated player trajectory differs from the same scripted proposals.")
    write_reports({
        "evaluation": "Actual Python-gated autonomous FPS player",
        "evidence_scope": "Local engine primary records and scripted proposals; not real source verification.",
        "results": framework_player,
    }, output / "framework-player")
    provenance = []
    for mode in ("baseline", "framework"):
        session = new_session(output, mode)
        session.action("use")
        session.action("archive")
        session.action("echo")
        prior_blocked = session.report()["uses_blocked"]
        same_root_blocked = session.action("use")["uses_blocked"] - prior_blocked
        session.action("survey")
        before = session.action("use")
        after = session.action("withdraw")
        provenance.append({
            "mode": mode, "uses_allowed": before["uses_allowed"],
            "uses_blocked": before["uses_blocked"],
            "same_root_attempts_blocked": same_root_blocked,
            "correction_files_verified": after["correction_files_verified"],
            "stale_consumers": after["stale_consumers"],
        })
    summary = {}
    for policy in ("reactive", "planned"):
        runs = [row for row in fps["results"] if row["policy"] == policy]
        summary[policy] = {
            "runs": len(runs), "victories": sum(row["state"] == "victory" for row in runs),
            "mean_simulated_seconds": sum(row["simulated_seconds"] for row in runs) / len(runs),
            "mean_intel": sum(row["intel"] for row in runs) / len(runs),
            "hit_fraction": sum(row["hits"] for row in runs) / sum(row["shots"] for row in runs),
        }
    result = {
        "evaluation": "Connected framework/game comparison",
        "evidence_scope": "Seeded scripted FPS controllers plus actual Python provenance-game operations.",
        "fps": fps, "fps_summary": summary, "provenance": provenance,
        "framework_player": {
            "runs": len(framework_player),
            "victories": sum(row["state"] == "victory" for row in framework_player),
            "gate_decisions": sum(row["python_gate_decisions"] for row in framework_player),
            "gate_blocked": sum(row["python_gate_blocked"] for row in framework_player),
            "trajectories_match_scripted_planner": True,
            "worker_sha256": sha256(game_dir / "simulation/worker.cjs"),
            "scope": "Python gates every planned FPS action using trusted fictional engine records.",
        },
        "bridge_sha256": sha256(Path(__file__)),
        "independent_external_validation": False,
        "sequel_design_findings": [
            "Perfect shot accuracy under exact LOS observations is not evidence of analytical skill.",
            "Mission completion alone cannot discriminate these policies on the tested seeds.",
            "Repeated same-root sources do not establish independent corroboration.",
            "A sequel needs claim gating and actual correction receipts, not only an intel score.",
        ],
    }
    write_reports(result, output)
    return result


def serve(game_dir: Path, output: Path, port: int) -> None:
    root = game_dir.resolve()
    sessions: dict[str, GameSession] = {}

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(5)

        def send_json(self, status: int, data: dict[str, Any]) -> None:
            payload = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            if self.headers.get("Host") != f"127.0.0.1:{port}":
                self.send_json(403, {"error": "Use the advertised loopback host."})
                return
            if self.path == "/api/status":
                self.send_json(200, {"runtime": "VessellFramework", "local_only": True})
                return
            name = self.path.split("?", 1)[0].lstrip("/") or "lab.html"
            path = (root / name).resolve()
            public = {"index.html", "lab.html", "recall.html",
                      "simulation/policy.js", "simulation/lab.js", "simulation/recall.js",
                      "simulation/lab.css"}
            if name not in public or not path.is_relative_to(root) or not path.is_file():
                self.send_json(404, {"error": "Unknown public game asset."})
                return
            payload = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", {
                ".html": "text/html; charset=utf-8", ".js": "text/javascript",
                ".json": "application/json", ".css": "text/css",
            }[path.suffix])
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:
            origin = self.headers.get("Origin")
            if (self.headers.get("Host") != f"127.0.0.1:{port}"
                    or origin not in (None, f"http://127.0.0.1:{port}")
                    or self.headers.get("Content-Type") != "application/json"):
                self.send_json(403, {"error": "Use same-origin localhost JSON requests."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise ValueError("Request body must contain at most 4096 bytes.")
                data = json.loads(self.rfile.read(length))
                if self.path == "/api/session" and set(data) == {"mode"}:
                    if len(sessions) >= 100:
                        raise ValueError("Session limit reached; restart server explicitly.")
                    session = new_session(output, data["mode"])
                    sessions[session.folder.name] = session
                    self.send_json(201, session.report())
                elif self.path == "/api/action" and set(data) == {"session", "operation"}:
                    session = sessions[data["session"]]
                    self.send_json(200, session.action(data["operation"]))
                else:
                    raise ValueError("Unknown API operation or request shape.")
            except (ValueError, KeyError, TypeError, OSError) as error:
                self.send_json(400, {"error": str(error)})

    server = HTTPServer(("127.0.0.1", port), Handler)
    server.timeout = 5
    print(f"Game bridge: http://127.0.0.1:{port}/lab.html", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Game bridge stopped.", flush=True)
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    try:
        if args.simulate:
            result = simulate(args.game_dir.resolve(), args.output_dir.resolve())
            print(json.dumps(result["fps_summary"], indent=2))
        else:
            if not 1024 <= args.port <= 65535:
                raise ValueError("Port must be between 1024 and 65535.")
            serve(args.game_dir, args.output_dir, args.port)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError,
            subprocess.TimeoutExpired) as error:
        print(f"GAME BRIDGE FAILED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
