"""Verify Linux containment before any offline source replay or test execution."""

import errno
import json
import os
import subprocess
import sys
from pathlib import Path


def verify_isolation() -> dict:
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            status[key] = value.strip()
    mounts = {
        row.split()[1]: set(row.split()[3].split(","))
        for row in Path("/proc/mounts").read_text().splitlines()
    }
    interfaces = sorted(path.name for path in Path("/sys/class/net").iterdir())
    checks = {
        "nonroot": os.getuid() != 0,
        "effective_capabilities_zero": int(status["CapEff"], 16) == 0,
        "no_new_privileges": status["NoNewPrivs"] == "1",
        "root_read_only": "ro" in mounts["/"],
        "data_read_only": "ro" in mounts["/data"],
        "catalog_read_only": "ro" in mounts["/catalog.json"],
        "expansion_read_only": "ro" in mounts["/expansion"],
        "network_loopback_only": interfaces == ["lo"],
        "docker_socket_not_mounted": not Path("/var/run/docker.sock").exists(),
    }
    probe = Path("/data/.vf-write-probe")
    try:
        probe.write_text("unexpected write")
    except OSError as error:
        checks["data_write_rejected"] = error.errno in (errno.EROFS, errno.EACCES)
    else:
        probe.unlink()
        checks["data_write_rejected"] = False
    result = {"checks": checks, "passed": all(checks.values()), "interfaces": interfaces}
    if not result["passed"]:
        raise RuntimeError(f"Required OS isolation failed: {result}")
    return result


def main() -> int:
    output = Path("/outputs")
    try:
        isolation = verify_isolation()
        output.mkdir(exist_ok=True)
        (output / "isolation.json").write_text(json.dumps(isolation, indent=2) + "\n")
        commands = [
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--junitxml=/outputs/tests.xml", "--basetemp=/tmp/pytest"],
            [sys.executable, "verify_manifest.py"],
            [sys.executable, "-m", "vessell.case_study",
             "--spec", "case_studies/claim_correction/spec.json",
             "--output-dir", "/outputs/case-study"],
            [sys.executable, "-m", "vessell.replay_lab",
             "--data-dir", "/data", "--catalog", "/catalog.json",
             "--output-dir", "/outputs/replay", "--workers", "4", "--repetitions", "32"],
            [sys.executable, "-m", "vessell.reference_data",
             "--data-dir", "/expansion", "--output-dir", "/outputs/reference_data"],
        ]
        failures = []
        for command in commands:
            completed = subprocess.run(command, check=False)
            if completed.returncode:
                failures.append({"command": command, "returncode": completed.returncode})
        (output / "execution.json").write_text(json.dumps({
            "passed": not failures, "failures": failures,
            "scope": "Offline Linux VM container replay; no field efficacy claim.",
        }, indent=2) + "\n")
        return 1 if failures else 0
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"SANDBOX FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
