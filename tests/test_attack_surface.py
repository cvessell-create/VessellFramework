# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Attack-surface heat map: scanner parsers, enrichment, matrix, renderers, CLI."""
import json
from pathlib import Path

import pytest

from vessell.attack_surface import (
    KEV_SCORE,
    SEQUENTIAL_PALETTE,
    Finding,
    apply_inventory,
    apply_kev,
    build_attack_surface,
    color_for_score,
    detect_format,
    kev_cve_ids,
    load_report,
    main,
    parse_nmap_xml,
    render_csv,
    render_html,
    render_text,
)

FIX = Path(__file__).resolve().parent / "fixtures" / "attack_surface"
REPORTS = ["nmap.xml", "nuclei.jsonl", "naabu.jsonl", "httpx.jsonl", "trivy.json", "grype.json",
           "osv.json"]


@pytest.mark.parametrize(
    ("name", "fmt"),
    [("nmap.xml", "nmap"), ("nuclei.jsonl", "nuclei"), ("naabu.jsonl", "naabu"),
     ("httpx.jsonl", "httpx"), ("trivy.json", "trivy"), ("grype.json", "grype"),
     ("osv.json", "osv")],
)
def test_detect_format(name, fmt):
    assert detect_format((FIX / name).read_text(encoding="utf-8")) == fmt


def test_nmap_open_ports_vulners_and_down_hosts():
    findings = load_report(FIX / "nmap.xml")
    gw = [f for f in findings if f.asset == "gw.example.internal"]
    assert {f.port for f in gw if f.tool == "nmap"} == {22, 443}  # 8080 closed
    vulners = {f.cve: f.severity for f in gw if f.tool == "nmap-vulners"}
    assert vulners == {"CVE-2023-38408": 9.8, "CVE-2023-51385": 6.5}
    other = {f.port: f.category for f in findings if f.asset == "192.0.2.12"}
    assert other == {23: "remote-admin", 6379: "database", 445: "file-share"}
    assert not any(f.asset == "192.0.2.13" for f in findings)


def test_nmap_rejects_entity_declarations():
    evil = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><nmaprun>&a;</nmaprun>'
    with pytest.raises(ValueError, match="entity"):
        parse_nmap_xml(evil)


def test_nuclei_categories_cves_and_hosts():
    findings = load_report(FIX / "nuclei.jsonl")
    by_title = {f.title: f for f in findings}
    log4j = by_title["Apache Log4j2 Remote Code Injection"]
    assert (log4j.asset, log4j.cve, log4j.severity, log4j.category) == (
        "app.example.internal", "CVE-2021-44228", 10.0, "known-vuln")
    assert by_title["Grafana Login Panel"].category == "exposed-panel"
    assert by_title["Grafana Login Panel"].asset == "app.example.internal"


def test_trivy_vulns_misconfigs_secrets():
    findings = load_report(FIX / "trivy.json")
    cats = sorted(f.category for f in findings)
    assert cats == ["exposed-secret", "misconfiguration", "vulnerable-dependency",
                    "vulnerable-dependency"]  # PASS misconfig skipped
    assert all(f.asset == "registry.example.internal/app:1.4" for f in findings)


def test_grype_uses_related_cve_and_cvss():
    (finding,) = load_report(FIX / "grype.json")
    assert finding.cve == "CVE-2021-44228"
    assert finding.severity == 10.0


def test_osv_alias_and_group_score():
    (finding,) = load_report(FIX / "osv.json")
    assert finding.cve == "CVE-2019-10906"
    assert finding.severity == 8.6


def test_kev_raises_to_max_and_relabels():
    kev = kev_cve_ids(json.loads((FIX / "kev.json").read_text(encoding="utf-8")))
    findings = apply_kev(load_report(FIX / "grype.json"), kev)
    assert findings[0].kev and findings[0].severity == KEV_SCORE
    assert findings[0].category == "known-exploited"


def test_inventory_maps_aliases_and_flags_only_network_shadow_assets():
    inventory = json.loads((FIX / "inventory.json").read_text(encoding="utf-8"))
    findings = []
    for name in REPORTS:
        findings.extend(load_report(FIX / name))
    mapped = apply_inventory(findings, inventory)
    assets = {f.asset for f in mapped}
    assert {"edge-gateway", "customer-app", "app-image"} <= assets
    shadows = sorted(f.asset for f in mapped if f.category == "shadow-asset")
    assert shadows == ["192.0.2.12", "legacy.example.internal"]
    with pytest.raises(TypeError):
        apply_inventory(findings, {"assets": "nope"})


def test_build_matrix_orders_rows_and_cells():
    findings = [
        Finding("a", "web", 2.0, "w1", "httpx"),
        Finding("a", "web", 3.0, "w2", "httpx"),
        Finding("b", "database", 8.0, "db", "nmap", port=5432),
        Finding("b", "known-exploited", 10.0, "kev", "nuclei", cve="CVE-2021-44228", kev=True),
    ]
    surface = build_attack_surface(findings)
    assert surface["categories"] == ["known-exploited", "database", "web"]
    assert [r["asset"] for r in surface["rows"]] == ["b", "a"]
    assert surface["rows"][1]["cells"]["web"] == {"score": 3.0, "count": 2, "kev": False,
                                                  "top": "w2"}
    assert surface["summary"]["kev"] == 1
    assert surface["findings"][0]["title"] == "kev"


def test_color_scale():
    assert color_for_score(0) == SEQUENTIAL_PALETTE[0]
    assert color_for_score(10) == SEQUENTIAL_PALETTE[-1]
    assert color_for_score(99) == SEQUENTIAL_PALETTE[-1]
    assert color_for_score(None) not in SEQUENTIAL_PALETTE


def test_renderers_escape_and_neutralise():
    findings = [Finding("<img src=x onerror=alert(1)>", "web", 5.0, "<script>x</script>", "t"),
                Finding("=cmd|' /C calc'!A0", "web", 5.0, "t", "t")]
    surface = build_attack_surface(findings)
    page = render_html(surface)
    assert "<img" not in page and "<script>x" not in page
    assert "'=cmd" in render_csv(surface)
    assert "\x1b[" not in render_text(surface, color=False)
    assert "\x1b[48;2;" in render_text(surface, color=True)


def test_cli_end_to_end(tmp_path):
    args = [str(FIX / n) for n in REPORTS]
    args += ["--inventory", str(FIX / "inventory.json"), "--kev", str(FIX / "kev.json")]
    out = tmp_path / "surface.json"
    assert main([*args, "--format", "json", "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["shadow_assets"] == 2
    assert data["summary"]["kev"] == 4
    top = {r["asset"]: r["risk"] for r in data["rows"]}
    assert top["edge-gateway"] == 10.0  # OpenSSH CVE in KEV excerpt
    for fmt in ("html", "csv", "text"):
        target = tmp_path / f"surface.{fmt}"
        assert main([*args, "--format", fmt, "-o", str(target)]) == 0
        assert target.read_text(encoding="utf-8")


def test_cli_errors(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"something": 1}', encoding="utf-8")
    assert main([str(bad)]) == 1
    assert "ATTACK SURFACE FAILED" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        main([])
