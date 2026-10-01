# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Attack-surface heat map: ingest open-source scanner output, score, and render.

VesselFramework does not ship or embed third-party scanners. It reads the
documented machine-readable output of widely used open-source tools, run by
the operator against assets they are authorized to test:

==============  ===========================  ==========================================
Tool            Output consumed              Upstream project / license
==============  ===========================  ==========================================
Nmap            XML (``-oX``), incl. the     nmap.org — Nmap Public Source License
                ``vulners`` NSE script
Nuclei          JSONL (``-jsonl``)           github.com/projectdiscovery/nuclei — MIT
naabu           JSONL (``-json``)            github.com/projectdiscovery/naabu — MIT
httpx           JSONL (``-json``)            github.com/projectdiscovery/httpx — MIT
Trivy           JSON (``--format json``)     github.com/aquasecurity/trivy — Apache-2.0
Grype           JSON (``-o json``)           github.com/anchore/grype — Apache-2.0
OSV-Scanner     JSON (``--format json``)     github.com/google/osv-scanner — Apache-2.0
==============  ===========================  ==========================================

Every report is normalised into :class:`Finding` records (asset, exposure
category, 0-10 severity). Findings for CVEs in the CISA Known Exploited
Vulnerabilities catalog are raised to 10.0, and — when an asset inventory
is supplied — hosts the scanners found that the inventory does not know
about are flagged as ``shadow-asset``. :func:`build_attack_surface` turns
the findings into an asset x category grid, and :func:`render_html` /
:func:`render_text` / :func:`render_csv` draw it as a heat map on the
ColorBrewer ``YlOrRd`` sequential scale (Cynthia Brewer, Apache-2.0).

CLI: ``vf-attack-surface nmap.xml nuclei.jsonl trivy.json --inventory
example_asset_inventory.json --kev kev.json --format html -o surface.html``.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from vessell.heatmap import _ansi_bg, _ansi_fg, _csv_safe, _fit, _text_color

__all__ = [
    "CATEGORIES",
    "NETWORK_TOOLS",
    "SEQUENTIAL_PALETTE",
    "Finding",
    "apply_inventory",
    "apply_kev",
    "build_attack_surface",
    "color_for_score",
    "detect_format",
    "kev_cve_ids",
    "load_report",
    "main",
    "parse_grype_json",
    "parse_httpx_jsonl",
    "parse_naabu_jsonl",
    "parse_nmap_xml",
    "parse_nuclei_jsonl",
    "parse_osv_json",
    "parse_trivy_json",
    "render_csv",
    "render_html",
    "render_text",
]

# Canonical column order for the heat map (most structural first).
CATEGORIES: tuple[str, ...] = (
    "shadow-asset",
    "known-exploited",
    "known-vuln",
    "remote-admin",
    "database",
    "file-share",
    "exposed-panel",
    "misconfiguration",
    "exposed-secret",
    "vulnerable-dependency",
    "web",
    "mail",
    "other-service",
)

# ColorBrewer YlOrRd, 9 classes, low -> high risk.
SEQUENTIAL_PALETTE: tuple[str, ...] = (
    "#ffffcc",
    "#ffeda0",
    "#fed976",
    "#feb24c",
    "#fd8d3c",
    "#fc4e2a",
    "#e31a1c",
    "#bd0026",
    "#800026",
)
EMPTY_COLOR = "#f0f0f0"

SEVERITY_SCORES: dict[str, float] = {
    "critical": 9.5,
    "high": 8.0,
    "medium": 5.5,
    "moderate": 5.5,
    "low": 3.0,
    "info": 0.5,
    "informational": 0.5,
    "negligible": 0.5,
    "unknown": 1.0,
}

NETWORK_TOOLS = frozenset({"nmap", "nmap-vulners", "nuclei", "naabu", "httpx"})

KEV_SCORE = 10.0
SHADOW_ASSET_SCORE = 6.0

# Exposed-service categories and base scores, keyed by port and by service name.
_SERVICE_RULES: dict[str, tuple[str, float]] = {
    "telnet": ("remote-admin", 9.0),
    "vnc": ("remote-admin", 8.0),
    "ms-wbt-server": ("remote-admin", 7.5),
    "rdp": ("remote-admin", 7.5),
    "winrm": ("remote-admin", 7.0),
    "wsman": ("remote-admin", 7.0),
    "ssh": ("remote-admin", 5.0),
    "redis": ("database", 8.5),
    "mongodb": ("database", 8.5),
    "elasticsearch": ("database", 8.5),
    "memcached": ("database", 8.0),
    "mysql": ("database", 8.0),
    "postgresql": ("database", 8.0),
    "ms-sql-s": ("database", 8.0),
    "oracle-tns": ("database", 8.0),
    "couchdb": ("database", 8.0),
    "microsoft-ds": ("file-share", 7.0),
    "netbios-ssn": ("file-share", 7.0),
    "smb": ("file-share", 7.0),
    "nfs": ("file-share", 6.5),
    "rsync": ("file-share", 6.0),
    "ftp": ("file-share", 6.0),
    "http": ("web", 2.5),
    "https": ("web", 2.0),
    "http-proxy": ("web", 3.5),
    "smtp": ("mail", 2.5),
    "submission": ("mail", 2.5),
    "imap": ("mail", 2.5),
    "imaps": ("mail", 2.0),
    "pop3": ("mail", 2.5),
    "pop3s": ("mail", 2.0),
}
_PORT_SERVICES: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    80: "http",
    110: "pop3",
    139: "netbios-ssn",
    143: "imap",
    443: "https",
    445: "microsoft-ds",
    587: "submission",
    873: "rsync",
    993: "imaps",
    995: "pop3s",
    1433: "ms-sql-s",
    1521: "oracle-tns",
    2049: "nfs",
    3306: "mysql",
    3389: "ms-wbt-server",
    5432: "postgresql",
    5900: "vnc",
    5984: "couchdb",
    5985: "winrm",
    5986: "winrm",
    6379: "redis",
    8000: "http",
    8080: "http-proxy",
    8443: "https",
    9200: "elasticsearch",
    11211: "memcached",
    27017: "mongodb",
}
OTHER_SERVICE_SCORE = 2.0

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,}", re.IGNORECASE)
_VULNERS_LINE = re.compile(r"(CVE-\d{4}-\d{4,})\s+(\d+(?:\.\d+)?)", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    """One normalised attack-surface observation."""

    asset: str
    category: str
    severity: float  # 0..10
    title: str
    tool: str
    cve: str | None = None
    port: int | None = None
    kev: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset": self.asset,
            "category": self.category,
            "severity": round(self.severity, 2),
            "title": self.title,
            "tool": self.tool,
            "cve": self.cve,
            "port": self.port,
            "kev": self.kev,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def severity_score(label: object, cvss: object = None) -> float:
    """Return a 0-10 score, preferring a numeric CVSS score over a label."""
    if cvss is not None:
        try:
            value = float(str(cvss))
        except ValueError:
            value = -1.0
        if 0.0 <= value <= 10.0:
            return value
    return SEVERITY_SCORES.get(str(label or "unknown").strip().lower(), SEVERITY_SCORES["unknown"])


def _service_finding(asset: str, port: int | None, service: str, tool: str) -> Finding:
    name = (service or "").lower() or _PORT_SERVICES.get(port or -1, "")
    category, score = _SERVICE_RULES.get(name, ("other-service", OTHER_SERVICE_SCORE))
    label = f"{name or 'unknown'}/{port}" if port is not None else name or "unknown"
    return Finding(
        asset=asset,
        category=category,
        severity=score,
        title=f"Open service {label}",
        tool=tool,
        port=port,
    )


def _host_of(value: str) -> str:
    value = value.strip()
    if "://" in value:
        return urlsplit(value).hostname or value
    if value.count(":") == 1:  # host:port
        return value.split(":", 1)[0]
    return value


def _to_port(value: object) -> int | None:
    if isinstance(value, dict):
        value = value.get("Port", value.get("port"))
    try:
        return int(str(value))
    except ValueError:
        return None


def _iter_jsonl(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"line {number} is not valid JSON: {error.msg}") from error
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _as_list(value: object) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_nmap_xml(text: str) -> list[Finding]:
    """Parse Nmap ``-oX`` output: open ports plus ``vulners`` NSE CVEs."""
    # Nmap emits a bare <!DOCTYPE nmaprun>; entity declarations are never
    # legitimate here and are refused to rule out entity-expansion abuse.
    if "<!ENTITY" in text.upper():
        raise ValueError("refusing XML with entity declarations")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise ValueError(f"invalid Nmap XML: {error}") from error
    findings: list[Finding] = []
    for host in root.iter("host"):
        status = host.find("status")
        if status is not None and status.get("state") not in (None, "up"):
            continue
        names = [h.get("name", "") for h in host.iter("hostname") if h.get("name")]
        addrs = [
            a.get("addr", "")
            for a in host.iter("address")
            if a.get("addrtype") in ("ipv4", "ipv6") and a.get("addr")
        ]
        asset = (names or addrs or ["unknown-host"])[0]
        for port_el in host.iter("port"):
            state = port_el.find("state")
            if state is None or state.get("state") != "open":
                continue
            port = _to_port(port_el.get("portid"))
            service_el = port_el.find("service")
            service = service_el.get("name", "") if service_el is not None else ""
            findings.append(_service_finding(asset, port, service, "nmap"))
            for script in port_el.iter("script"):
                if script.get("id") != "vulners":
                    continue
                seen: set[str] = set()
                for cve, score in _VULNERS_LINE.findall(script.get("output", "")):
                    cve = cve.upper()
                    if cve in seen:
                        continue
                    seen.add(cve)
                    findings.append(
                        Finding(
                            asset=asset,
                            category="known-vuln",
                            severity=severity_score(None, score),
                            title=f"{cve} on {service or 'port'}/{port}",
                            tool="nmap-vulners",
                            cve=cve,
                            port=port,
                        )
                    )
    return findings


def _nuclei_category(tags: list[str], cves: list[str], severity: str) -> str:
    tagset = {t.lower() for t in tags}
    if cves:
        return "known-vuln"
    if tagset & {"misconfig", "misconfiguration", "default-login", "unauth"}:
        return "misconfiguration"
    if tagset & {"exposure", "token", "secret", "keys"}:
        return "exposed-secret" if tagset & {"token", "secret", "keys"} else "exposed-panel"
    if tagset & {"panel", "login"}:
        return "exposed-panel"
    if severity in ("critical", "high", "medium"):
        return "known-vuln"
    return "web"


def parse_nuclei_jsonl(text: str) -> list[Finding]:
    """Parse ProjectDiscovery Nuclei ``-jsonl`` results."""
    findings: list[Finding] = []
    for row in _iter_jsonl(text):
        info = row.get("info") or {}
        classification = info.get("classification") or row.get("classification") or {}
        cves = [str(c).upper() for c in _as_list(classification.get("cve-id")) if c]
        severity = str(info.get("severity", "unknown")).lower()
        tags = info.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        target = str(row.get("host") or row.get("matched-at") or row.get("ip") or "unknown-host")
        findings.append(
            Finding(
                asset=_host_of(target),
                category=_nuclei_category([str(t) for t in tags], cves, severity),
                severity=severity_score(severity, classification.get("cvss-score")),
                title=str(info.get("name") or row.get("template-id") or "nuclei finding"),
                tool="nuclei",
                cve=cves[0] if cves else None,
                port=_to_port(row.get("port")),
            )
        )
    return findings


def parse_naabu_jsonl(text: str) -> list[Finding]:
    """Parse ProjectDiscovery naabu ``-json`` open-port results."""
    findings: list[Finding] = []
    for row in _iter_jsonl(text):
        asset = str(row.get("host") or row.get("ip") or "unknown-host")
        findings.append(_service_finding(asset, _to_port(row.get("port")), "", "naabu"))
    return findings


def parse_httpx_jsonl(text: str) -> list[Finding]:
    """Parse ProjectDiscovery httpx ``-json`` web-probe results."""
    findings: list[Finding] = []
    for row in _iter_jsonl(text):
        url = str(row.get("url") or row.get("input") or "")
        asset = str(row.get("host") or _host_of(url) or "unknown-host")
        if asset and re.fullmatch(r"[\d.]+|[0-9a-fA-F:]+", asset) and url:
            asset = _host_of(url)  # prefer the hostname over the resolved IP
        title = str(row.get("title") or "").strip()
        tech = ", ".join(str(t) for t in _as_list(row.get("tech") or row.get("technologies")))
        label = f"HTTP {row.get('status_code', row.get('status-code', '?'))} {url}"
        if title:
            label += f" — {title}"
        if tech:
            label += f" [{tech}]"
        findings.append(
            Finding(
                asset=asset,
                category="web",
                severity=2.5,
                title=label,
                tool="httpx",
                port=_to_port(row.get("port")),
            )
        )
    return findings


def _trivy_cvss(vuln: dict[str, Any]) -> float | None:
    best: float | None = None
    for vendor in (vuln.get("CVSS") or {}).values():
        if isinstance(vendor, dict):
            for key in ("V3Score", "V40Score", "V2Score"):
                if isinstance(vendor.get(key), (int, float)):
                    best = max(best or 0.0, float(vendor[key]))
                    break
    return best


def parse_trivy_json(data: dict[str, Any]) -> list[Finding]:
    """Parse Aqua Trivy ``--format json`` (vulns, misconfigs, secrets)."""
    asset = str(data.get("ArtifactName") or "unknown-artifact")
    findings: list[Finding] = []
    for result in data.get("Results") or []:
        target = str(result.get("Target", ""))
        for vuln in result.get("Vulnerabilities") or []:
            vid = str(vuln.get("VulnerabilityID", ""))
            cve = vid.upper() if CVE_PATTERN.fullmatch(vid) else None
            findings.append(
                Finding(
                    asset=asset,
                    category="vulnerable-dependency",
                    severity=severity_score(vuln.get("Severity"), _trivy_cvss(vuln)),
                    title=f"{vid} in {vuln.get('PkgName', '?')} {vuln.get('InstalledVersion', '')}"
                    .strip(),
                    tool="trivy",
                    cve=cve,
                )
            )
        for mis in result.get("Misconfigurations") or []:
            if str(mis.get("Status", "FAIL")).upper() == "PASS":
                continue
            findings.append(
                Finding(
                    asset=asset,
                    category="misconfiguration",
                    severity=severity_score(mis.get("Severity")),
                    title=f"{mis.get('ID', '?')}: {mis.get('Title', '')} ({target})",
                    tool="trivy",
                )
            )
        for secret in result.get("Secrets") or []:
            findings.append(
                Finding(
                    asset=asset,
                    category="exposed-secret",
                    severity=severity_score(secret.get("Severity")),
                    title=f"{secret.get('Title') or secret.get('RuleID', 'secret')} ({target})",
                    tool="trivy",
                )
            )
    return findings


def parse_grype_json(data: dict[str, Any]) -> list[Finding]:
    """Parse Anchore Grype ``-o json`` matches."""
    source = data.get("source") or {}
    target = source.get("target")
    if isinstance(target, dict):
        target = target.get("userInput") or target.get("name")
    asset = str(target or "unknown-artifact")
    findings: list[Finding] = []
    for match in data.get("matches") or []:
        vuln = match.get("vulnerability") or {}
        artifact = match.get("artifact") or {}
        vid = str(vuln.get("id", ""))
        cve = vid.upper() if CVE_PATTERN.fullmatch(vid) else None
        if cve is None:
            for related in match.get("relatedVulnerabilities") or []:
                rid = str(related.get("id", ""))
                if CVE_PATTERN.fullmatch(rid):
                    cve = rid.upper()
                    break
        scores = [
            float(c["metrics"]["baseScore"])
            for c in vuln.get("cvss") or []
            if isinstance(c.get("metrics"), dict)
            and isinstance(c["metrics"].get("baseScore"), (int, float))
        ]
        findings.append(
            Finding(
                asset=asset,
                category="vulnerable-dependency",
                severity=severity_score(vuln.get("severity"), max(scores) if scores else None),
                title=f"{vid} in {artifact.get('name', '?')} {artifact.get('version', '')}".strip(),
                tool="grype",
                cve=cve,
            )
        )
    return findings


def parse_osv_json(data: dict[str, Any], asset: str | None = None) -> list[Finding]:
    """Parse Google OSV-Scanner ``--format json`` results."""
    findings: list[Finding] = []
    for result in data.get("results") or []:
        source = result.get("source") or {}
        result_asset = asset or str(source.get("path") or "unknown-source")
        for package in result.get("packages") or []:
            pkg = package.get("package") or {}
            group_scores: dict[str, float] = {}
            for group in package.get("groups") or []:
                try:
                    score = float(group.get("max_severity", ""))
                except ValueError:
                    continue
                for gid in group.get("ids") or []:
                    group_scores[str(gid)] = score
            for vuln in package.get("vulnerabilities") or []:
                vid = str(vuln.get("id", ""))
                ids = [vid, *[str(a) for a in vuln.get("aliases") or []]]
                cve = next((i.upper() for i in ids if CVE_PATTERN.fullmatch(i)), None)
                label = (vuln.get("database_specific") or {}).get("severity")
                findings.append(
                    Finding(
                        asset=result_asset,
                        category="vulnerable-dependency",
                        severity=severity_score(label, group_scores.get(vid)),
                        title=f"{vid} in {pkg.get('name', '?')} {pkg.get('version', '')}".strip(),
                        tool="osv-scanner",
                        cve=cve,
                    )
                )
    return findings


# ---------------------------------------------------------------------------
# Format detection + loading
# ---------------------------------------------------------------------------

FORMATS = ("nmap", "nuclei", "naabu", "httpx", "trivy", "grype", "osv")


def detect_format(text: str) -> str:
    """Identify which supported tool produced ``text``."""
    stripped = text.lstrip()
    if stripped.startswith("<"):
        if "<nmaprun" in stripped[:4096]:
            return "nmap"
        raise ValueError("unrecognised XML report (only Nmap -oX is supported)")
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        if "Results" in data or "ArtifactName" in data:
            return "trivy"
        if "matches" in data and "source" in data:
            return "grype"
        if "results" in data and any(
            isinstance(r, dict) and "packages" in r for r in data.get("results") or []
        ):
            return "osv"
        rows = [data]
    else:
        rows = _iter_jsonl(stripped)
    if rows:
        first = rows[0]
        if "template-id" in first or "template" in first:
            return "nuclei"
        if "url" in first and ("status_code" in first or "status-code" in first):
            return "httpx"
        if "port" in first and ("host" in first or "ip" in first):
            return "naabu"
    raise ValueError("unrecognised report format")


def load_report(path: Path, fmt: str | None = None) -> list[Finding]:
    """Read one scanner report from disk and return its findings."""
    text = path.read_text(encoding="utf-8")
    fmt = fmt or detect_format(text)
    if fmt == "nmap":
        return parse_nmap_xml(text)
    if fmt == "nuclei":
        return parse_nuclei_jsonl(text)
    if fmt == "naabu":
        return parse_naabu_jsonl(text)
    if fmt == "httpx":
        return parse_httpx_jsonl(text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise TypeError(f"{fmt} report must be a JSON object")
    if fmt == "trivy":
        return parse_trivy_json(data)
    if fmt == "grype":
        return parse_grype_json(data)
    if fmt == "osv":
        return parse_osv_json(data)
    raise ValueError(f"unsupported format {fmt!r}; expected one of: {', '.join(FORMATS)}")


# ---------------------------------------------------------------------------
# Enrichment
# ---------------------------------------------------------------------------


def kev_cve_ids(catalog: dict[str, Any]) -> set[str]:
    """Return the CVE IDs in a CISA KEV catalog document."""
    return {
        str(v.get("cveID", "")).upper()
        for v in catalog.get("vulnerabilities") or []
        if isinstance(v, dict) and v.get("cveID")
    }


def apply_kev(findings: list[Finding], kev_ids: set[str]) -> list[Finding]:
    """Mark CVE findings that are known-exploited and raise them to 10.0."""
    out: list[Finding] = []
    for finding in findings:
        if finding.cve and finding.cve.upper() in kev_ids:
            out.append(
                replace(
                    finding,
                    kev=True,
                    severity=KEV_SCORE,
                    category="known-exploited",
                    title=f"[CISA KEV] {finding.title}",
                )
            )
        else:
            out.append(finding)
    return out


def apply_inventory(findings: list[Finding], inventory: dict[str, Any]) -> list[Finding]:
    """Map scanned hosts onto inventory asset IDs and flag shadow assets.

    An inventory asset matches a scanned host by ``asset_id`` or any entry
    in its optional ``hostnames`` / ``addresses`` lists (case-insensitive).
    Network hosts (seen by Nmap, Nuclei, naabu, or httpx) that no inventory
    entry claims get one ``shadow-asset`` finding: something is answering
    that nobody has accounted for. Unmatched artifacts from code/image
    scanners keep their findings but are not called shadow assets.
    """
    assets = inventory.get("assets")
    if not isinstance(assets, list):
        raise TypeError("Inventory must contain an assets list.")
    alias: dict[str, str] = {}
    for row in assets:
        if not isinstance(row, dict) or not row.get("asset_id"):
            continue
        asset_id = str(row["asset_id"])
        for key in (asset_id, *_as_list(row.get("hostnames")), *_as_list(row.get("addresses"))):
            alias[str(key).lower()] = asset_id
    out: list[Finding] = []
    shadow: list[str] = []
    for finding in findings:
        mapped = alias.get(finding.asset.lower())
        if mapped is None:
            if finding.tool in NETWORK_TOOLS and finding.asset not in shadow:
                shadow.append(finding.asset)
            out.append(finding)
        else:
            out.append(replace(finding, asset=mapped))
    for host in shadow:
        out.append(
            Finding(
                asset=host,
                category="shadow-asset",
                severity=SHADOW_ASSET_SCORE,
                title="Discovered by scan but absent from the asset inventory",
                tool="vessell-inventory",
            )
        )
    return out


# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------


def build_attack_surface(findings: list[Finding]) -> dict[str, Any]:
    """Aggregate findings into an asset x category heat-map matrix.

    Each cell holds the worst ``score`` in that category for that asset,
    the finding ``count``, whether any finding is ``kev``, and the ``top``
    (worst) finding title. Rows carry ``risk`` (worst score on the asset)
    and are sorted by risk, then KEV count, then finding count.
    """
    present = {f.category for f in findings}
    categories = [c for c in CATEGORIES if c in present]
    categories += sorted(present - set(CATEGORIES))

    by_asset: dict[str, list[Finding]] = {}
    for finding in findings:
        by_asset.setdefault(finding.asset, []).append(finding)

    rows: list[dict[str, Any]] = []
    for asset, items in by_asset.items():
        cells: dict[str, dict[str, Any]] = {}
        for category in categories:
            group = [f for f in items if f.category == category]
            if not group:
                continue
            worst = max(group, key=lambda f: f.severity)
            cells[category] = {
                "score": round(worst.severity, 2),
                "count": len(group),
                "kev": any(f.kev for f in group),
                "top": worst.title,
            }
        rows.append(
            {
                "asset": asset,
                "risk": round(max(f.severity for f in items), 2),
                "findings": len(items),
                "kev": sum(1 for f in items if f.kev),
                "cells": cells,
            }
        )
    rows.sort(key=lambda r: (-r["risk"], -r["kev"], -r["findings"], r["asset"]))
    ordered = sorted(findings, key=lambda f: (-f.severity, f.asset, f.category, f.title))
    return {
        "categories": categories,
        "rows": rows,
        "summary": {
            "assets": len(rows),
            "findings": len(findings),
            "kev": sum(1 for f in findings if f.kev),
            "shadow_assets": sum(1 for f in findings if f.category == "shadow-asset"),
            "tools": sorted({f.tool for f in findings}),
        },
        "findings": [f.to_dict() for f in ordered],
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def color_for_score(score: float | None) -> str:
    """Map a 0-10 risk score onto the sequential palette (``None`` = empty)."""
    if score is None:
        return EMPTY_COLOR
    s = max(0.0, min(10.0, float(score)))
    index = min(len(SEQUENTIAL_PALETTE) - 1, int(s / 10.0 * len(SEQUENTIAL_PALETTE)))
    return SEQUENTIAL_PALETTE[index]


def _cell_text(cell: dict[str, Any] | None) -> str:
    if cell is None:
        return "·"
    text = f"{float(cell['score']):.1f}"
    if int(cell.get("count", 1)) > 1:
        text += f" ×{cell['count']}"
    if cell.get("kev"):
        text += " KEV"
    return text


def render_html(
    surface: dict[str, Any], title: str = "Attack surface heat map", max_findings: int = 500
) -> str:
    """Render the attack-surface matrix as a standalone HTML page."""
    esc = html.escape
    categories: list[str] = list(surface.get("categories", []))
    rows: list[dict[str, Any]] = list(surface.get("rows", []))
    summary: dict[str, Any] = surface.get("summary", {})
    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>{esc(title)}</title>",
        "<style>",
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#111}",
        "table{border-collapse:collapse;font-size:13px;margin-bottom:24px}",
        "th,td{border:1px solid #fff;padding:6px 8px;text-align:center}",
        "th{background:#333;color:#fff;font-weight:600}",
        "td.asset{text-align:left;background:#fafafa;font-family:ui-monospace,monospace}",
        "td.cell{min-width:64px;font-variant-numeric:tabular-nums}",
        "td.kev{outline:3px solid #000;outline-offset:-3px;font-weight:700}",
        ".legend{display:flex;align-items:center;margin:12px 0}",
        ".legend span{display:inline-block;width:28px;height:14px}",
        ".legend em{font-style:normal;font-size:12px;margin:0 8px}",
        ".detail td{text-align:left}",
        "</style></head><body>",
        f"<h1>{esc(title)}</h1>",
        (
            "<p>"
            f"{int(summary.get('assets', 0))} assets · {int(summary.get('findings', 0))} findings"
            f" · {int(summary.get('kev', 0))} CISA KEV"
            f" · {int(summary.get('shadow_assets', 0))} shadow assets · tools: "
            f"{esc(', '.join(str(t) for t in summary.get('tools', [])))}</p>"
        ),
        '<div class="legend"><em>0</em>',
    ]
    out.extend(f'<span style="background:{c}"></span>' for c in SEQUENTIAL_PALETTE)
    out.append(
        f'<em>10 risk</em><span style="background:{EMPTY_COLOR}"></span><em>none</em>'
        '<span style="background:#fff;outline:3px solid #000;outline-offset:-3px"></span>'
        "<em>known exploited</em></div>"
    )
    out.append("<table><thead><tr><th>Asset</th><th>Risk</th><th>Findings</th>")
    out.extend(f"<th>{esc(c)}</th>" for c in categories)
    out.append("</tr></thead><tbody>")
    for row in rows:
        risk_bg = color_for_score(float(row["risk"]))
        out.append(
            f'<tr><td class="asset">{esc(str(row["asset"]))}</td>'
            f'<td style="background:{risk_bg};color:{_text_color(risk_bg)}">'
            f"{float(row['risk']):.1f}</td><td>{int(row['findings'])}</td>"
        )
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        for category in categories:
            cell = cells.get(category)
            bg = color_for_score(None if cell is None else float(cell["score"]))
            klass = "cell kev" if cell and cell.get("kev") else "cell"
            tip = f"{category}: none" if cell is None else f"{category}: {cell['top']}"
            out.append(
                f'<td class="{klass}" style="background:{bg};color:{_text_color(bg)}" '
                f'title="{esc(tip)}">{esc(_cell_text(cell))}</td>'
            )
        out.append("</tr>")
    out.append("</tbody></table>")

    findings: list[dict[str, Any]] = list(surface.get("findings", []))
    if findings:
        out.append(f"<h2>Findings (top {min(len(findings), max_findings)} by severity)</h2>")
        out.append(
            '<table class="detail"><thead><tr><th>Severity</th><th>Asset</th><th>Category</th>'
            "<th>Finding</th><th>CVE</th><th>Port</th><th>Tool</th></tr></thead><tbody>"
        )
        for f in findings[:max_findings]:
            bg = color_for_score(float(f["severity"]))
            out.append(
                f'<tr><td style="background:{bg};color:{_text_color(bg)}">'
                f"{float(f['severity']):.1f}</td>"
                f"<td>{esc(str(f['asset']))}</td><td>{esc(str(f['category']))}</td>"
                f"<td>{esc(str(f['title']))}</td><td>{esc(str(f.get('cve') or ''))}</td>"
                f"<td>{esc(str(f.get('port') or ''))}</td><td>{esc(str(f['tool']))}</td></tr>"
            )
        out.append("</tbody></table>")
    out.append(
        "<p><small>Generated by VesselFramework from operator-supplied scanner output. "
        "Scan only assets you are authorized to test.</small></p></body></html>"
    )
    return "\n".join(out) + "\n"


def render_text(surface: dict[str, Any], *, color: bool = True, cell_width: int = 12) -> str:
    """Render the attack-surface matrix as a terminal heat map."""
    categories: list[str] = list(surface.get("categories", []))
    rows: list[dict[str, Any]] = list(surface.get("rows", []))
    reset = "\x1b[0m" if color else ""
    asset_width = max([len("Asset"), *(len(str(r["asset"])) for r in rows)])
    asset_width = min(asset_width, 32)
    header = _fit("Asset", asset_width) + " " + _fit("Risk", 5)
    header += "".join(" " + _fit(c, cell_width) for c in categories)
    lines = [header, "-" * len(header)]
    for row in rows:
        line = _fit(str(row["asset"]), asset_width) + " " + _fit(f"{float(row['risk']):.1f}", 5)
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        for category in categories:
            cell = cells.get(category)
            text = _fit(_cell_text(cell), cell_width)
            if color:
                bg = color_for_score(None if cell is None else float(cell["score"]))
                line += " " + _ansi_bg(bg) + _ansi_fg(_text_color(bg)) + text + reset
            else:
                line += " " + text
        lines.append(line)
    summary = surface.get("summary", {})
    lines.append("")
    lines.append(
        f"{summary.get('assets', 0)} assets, {summary.get('findings', 0)} findings, "
        f"{summary.get('kev', 0)} KEV, {summary.get('shadow_assets', 0)} shadow assets"
    )
    return "\n".join(lines) + "\n"


def render_csv(surface: dict[str, Any]) -> str:
    """Render the attack-surface matrix as CSV (blank = no finding)."""
    categories: list[str] = list(surface.get("categories", []))
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["asset", "risk", "findings", "kev", *categories])
    for row in surface.get("rows", []):
        cells: dict[str, dict[str, Any]] = row.get("cells", {})
        writer.writerow(
            [
                _csv_safe(row["asset"]),
                row["risk"],
                row["findings"],
                row["kev"],
                *("" if c not in cells else cells[c]["score"] for c in categories),
            ]
        )
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read_json_object(path: Path, what: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{what} must be a JSON object")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vf-attack-surface",
        description=(
            "Build an attack-surface heat map from open-source scanner output "
            "(Nmap XML, Nuclei/naabu/httpx JSONL, Trivy/Grype/OSV-Scanner JSON). "
            "Only scan assets you are authorized to test."
        ),
    )
    parser.add_argument("reports", nargs="*", type=Path, help="Scanner report files.")
    parser.add_argument(
        "--input-format", choices=FORMATS, help="Force the report format (default: auto-detect)."
    )
    parser.add_argument("--inventory", type=Path, help="Asset inventory JSON (flags shadow assets).")
    parser.add_argument("--kev", type=Path, help="Local CISA KEV catalog JSON.")
    parser.add_argument(
        "--fetch-kev", action="store_true", help="Download the current CISA KEV catalog."
    )
    parser.add_argument(
        "--scan-local",
        nargs=2,
        metavar=("TOOL", "PATH"),
        help="Run an installed local scanner (trivy or osv-scanner) on PATH and include it.",
    )
    parser.add_argument(
        "--format", choices=("html", "text", "csv", "json"), default="text", help="Output format."
    )
    parser.add_argument("-o", "--output", type=Path, help="Write to this file instead of stdout.")
    parser.add_argument("--title", default="Attack surface heat map", help="HTML page title.")
    parser.add_argument("--no-color", action="store_true", help="Plain text without ANSI colours.")
    args = parser.parse_args(argv)

    if not args.reports and not args.scan_local:
        parser.error("provide at least one report file or --scan-local")

    try:
        findings: list[Finding] = []
        for path in args.reports:
            findings.extend(load_report(path, args.input_format))
        if args.scan_local:
            from vessell.app.scanner_adapters import run_local_scan

            tool, target = args.scan_local
            report = run_local_scan(tool, Path(target))
            findings.extend(
                parse_trivy_json(report) if tool == "trivy" else parse_osv_json(report)
            )
        kev_ids: set[str] = set()
        if args.kev:
            kev_ids |= kev_cve_ids(_read_json_object(args.kev, "KEV catalog"))
        if args.fetch_kev:
            from vessell.app.sources.cisa_kev import fetch_kev_catalog

            kev_ids |= kev_cve_ids(fetch_kev_catalog())
        if kev_ids:
            findings = apply_kev(findings, kev_ids)
        if args.inventory:
            findings = apply_inventory(findings, _read_json_object(args.inventory, "inventory"))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"ATTACK SURFACE FAILED: {error}", file=sys.stderr)
        return 1

    surface = build_attack_surface(findings)
    if args.format == "html":
        rendered = render_html(surface, title=args.title)
    elif args.format == "csv":
        rendered = render_csv(surface)
    elif args.format == "json":
        rendered = json.dumps(surface, indent=2, ensure_ascii=False) + "\n"
    else:
        use_color = not args.no_color and args.output is None and sys.stdout.isatty()
        rendered = render_text(surface, color=use_color)

    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"ATTACK SURFACE WRITTEN: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
