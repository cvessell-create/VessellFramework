"""Validate cyber reference populations without manufacturing exploitation negatives."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from vessell.data_evidence import verify_catalog
from vessell.evaluation import sha256, write_reports


def audit_attack(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["type"] != "bundle":
        raise ValueError("ATT&CK input must be a STIX bundle.")
    objects = payload["objects"]
    identifiers = [obj["id"] for obj in objects]
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError("ATT&CK object identifiers must be nonempty and unique.")
    known = set(identifiers)
    active = [
        obj for obj in objects
        if not obj.get("revoked", False) and not obj.get("x_mitre_deprecated", False)
    ]
    dangling = []
    for obj in objects:
        if obj["type"] == "relationship":
            for field in ("source_ref", "target_ref"):
                if obj[field] not in known:
                    dangling.append({"relationship": obj["id"], "field": field,
                                     "missing_id": obj[field]})
    return {
        "objects": len(objects), "types": dict(Counter(obj["type"] for obj in objects)),
        "active_objects": len(active),
        "active_techniques": sum(obj["type"] == "attack-pattern" for obj in active),
        "active_mitigations": sum(obj["type"] == "course-of-action" for obj in active),
        "dangling_relationship_endpoints": dangling,
        "evidence_role": "TECHNIQUE_AND_MITIGATION_KNOWLEDGE",
        "limitations": [
            "Active excludes explicitly revoked/deprecated objects, not unseen real techniques.",
            "Structural checks do not certify STIX conformance or verify cited source truth.",
            "Technique/mitigation relationships do not establish tested detection or control efficacy.",
        ],
    }


def audit_epss(path: Path, expected_date: str) -> dict[str, Any]:
    date.fromisoformat(expected_date)
    seen: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8", newline="") as file:
        comment = file.readline().strip()
        if not comment.startswith("#") or f"score_date:{expected_date}" not in comment:
            raise ValueError("EPSS score date metadata does not match the frozen acquisition.")
        for row in csv.DictReader(file):
            cve = row["cve"]
            if not re.fullmatch(r"CVE-[0-9]{4}-[0-9]{4,}", cve) or cve in seen:
                raise ValueError(f"Invalid or duplicate EPSS CVE: {cve}")
            seen.add(cve)
            for field in ("epss", "percentile"):
                value = float(row[field])
                if not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError(f"Invalid EPSS {field}: {row[field]}")
    if not seen:
        raise ValueError("EPSS population is empty.")
    return {
        "records": len(seen), "score_date": expected_date, "source_comment": comment,
        "evidence_role": "HISTORICAL_PROBABILITY_SNAPSHOT",
        "limitations": [
            "EPSS score is not CVSS severity and percentile is not exploitation probability.",
            "Current KEV absence cannot label historical non-exploitation.",
            "Independent dated exploitation outcomes are needed to score calibration.",
            "Model-version transitions must not be interpreted as vulnerability risk changes.",
        ],
    }


def audit_references(data_dir: Path) -> dict[str, Any]:
    manifest = json.loads((data_dir / "manifest.json").read_text())
    hashes = verify_catalog(data_dir, manifest["sources"])
    if set(hashes) != {"enterprise_attack.json", "epss_2025_09_01.csv.gz", "ATTACK_LICENSE.txt"}:
        raise ValueError("Unexpected reference-data population.")
    attack = audit_attack(json.loads((data_dir / "enterprise_attack.json").read_text()))
    epss = audit_epss(data_dir / "epss_2025_09_01.csv.gz", "2025-09-01")
    return {
        "evaluation": "Frozen cyber reference-data validation",
        "independent_external_validation": False,
        "source_manifest": manifest, "source_hashes": hashes,
        "implementation_sha256": sha256(Path(__file__)),
        "checks": {"attack": attack, "epss": epss},
        "limitations": [
            "Reference populations are separate from the original 23-source replay batch.",
            "No targets, malware samples or exploit payloads are executed.",
            "No control efficacy, detection accuracy or exploitation calibration is claimed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        source, output = args.data_dir.resolve(), args.output_dir.resolve()
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError("Reference outputs must be outside source data.")
        result = audit_references(source)
        machine, human = write_reports(result, output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"REFERENCE AUDIT FAILED: {error}", file=sys.stderr)
        return 2
    print(f"Reference audit synchronized: {machine}, {human}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
