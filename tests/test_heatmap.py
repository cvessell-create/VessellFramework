# Copyright 2026 Christopher R. Vessell. Licensed under the Apache License, Version 2.0. See LICENSE.
"""Heat map: event_matrix aggregation, colour scale, renderers, and CLI."""
import json
from pathlib import Path

import pytest

from vessell.heatmap import (
    DIVERGING_PALETTE,
    SILENT_COLOR,
    color_for_weight,
    load_checks,
    main,
    render_csv,
    render_html,
    render_text,
)
from vessell.provenance import SourceStatus
from vessell.report import event_matrix
from vessell.verify import ClaimCheck, SourceSighting, clock_sort_key, detect_clock_drift

EST = SourceStatus.SOURCE_ESTABLISHED
HYP = SourceStatus.WORKING_HYPOTHESIS
EXAMPLE = Path(__file__).resolve().parents[1] / "example_event_checks.json"


def _s(name, tier=EST, clock=None, denies=False):
    return SourceSighting(source_name=name, tier=tier, event_clock=clock, denies=denies)


def test_repeat_sightings_from_one_source_are_not_overwritten():
    check = ClaimCheck(
        claim="STL leads",
        sightings=(_s("Elbotola", clock="10'"), _s("Elbotola", HYP, clock="41'")),
    )
    cell = event_matrix([check])["rows"][0]["cells"]["Elbotola"]
    # Strongest affirming tier is kept (previously the later, weaker
    # sighting silently replaced it) and both clocks are reported.
    assert cell == {"weight": 1.0, "clock": "10' / 41'", "denies": False}


def test_self_contradicting_source_nets_to_zero_and_flags_denial():
    check = ClaimCheck(claim="X", sightings=(_s("A", clock="5'"), _s("A", clock="9'", denies=True)))
    cell = event_matrix([check])["rows"][0]["cells"]["A"]
    assert cell["weight"] == 0.0
    assert cell["denies"] is True


def test_lone_denial_is_negative():
    check = ClaimCheck(claim="X", sightings=(_s("A", denies=True),))
    assert event_matrix([check])["rows"][0]["cells"]["A"]["weight"] == -1.0


def test_clock_drift_orders_clocks_naturally():
    check = ClaimCheck(claim="X", sightings=(_s("A", clock="10'"), _s("B", clock="5'")))
    signal = detect_clock_drift(check)
    assert signal is not None
    assert "(5' vs 10')" in signal


def test_clock_sort_key_handles_stoppage_and_labels():
    clocks = ["90'", "HT", "45+2'", "5'", "45'", "10'"]
    assert sorted(clocks, key=clock_sort_key) == ["5'", "10'", "45'", "45+2'", "90'", "HT"]


def test_color_scale_endpoints_and_silent():
    assert color_for_weight(-1.0) == DIVERGING_PALETTE[0]
    assert color_for_weight(0.0) == DIVERGING_PALETTE[5]
    assert color_for_weight(1.0) == DIVERGING_PALETTE[-1]
    assert color_for_weight(5.0) == DIVERGING_PALETTE[-1]
    assert color_for_weight(None) == SILENT_COLOR


def test_html_escapes_untrusted_text():
    check = ClaimCheck(
        claim="<script>alert(1)</script>",
        sightings=(_s('"><img src=x onerror=alert(1)>'),),
    )
    page = render_html(event_matrix([check]), title="<b>t</b>")
    assert "<script>alert" not in page
    assert "<img" not in page
    assert "&lt;script&gt;" in page
    assert "<title>&lt;b&gt;t&lt;/b&gt;</title>" in page


def test_html_colours_cells_by_weight():
    check = ClaimCheck(claim="X", sightings=(_s("A"), _s("B", denies=True)))
    page = render_html(event_matrix([check]))
    assert f"background:{DIVERGING_PALETTE[-1]}" in page
    assert f"background:{DIVERGING_PALETTE[0]}" in page


def test_text_renderer_plain_and_colour():
    matrix = event_matrix([ClaimCheck(claim="X", sightings=(_s("A", clock="3'"),))])
    plain = render_text(matrix, color=False)
    assert "\x1b[" not in plain
    assert "+1.00 @3'" in plain
    assert "\x1b[48;2;" in render_text(matrix, color=True)


def test_csv_neutralises_formula_injection():
    check = ClaimCheck(claim="=HYPERLINK(\"http://x\")", sightings=(_s("@evil"),))
    out = render_csv(event_matrix([check]))
    assert "'=HYPERLINK" in out
    assert "'@evil" in out


def test_load_checks_accepts_names_and_values_and_rejects_bad_input():
    checks = load_checks(
        {"checks": [{"claim": "X", "sightings": [
            {"source_name": "A", "tier": "SOURCE_ESTABLISHED"},
            {"source_name": "B", "tier": "WORKING HYPOTHESIS"},
        ]}]}
    )
    assert checks[0].sightings[1].tier is HYP
    with pytest.raises(ValueError, match="unknown source tier"):
        load_checks([{"claim": "X", "sightings": [{"source_name": "A", "tier": "NOPE"}]}])
    with pytest.raises(ValueError, match="unknown sighting field"):
        load_checks([{"claim": "X", "sightings": [{"source_name": "A", "tier": "ILLUSTRATIVE",
                                                   "bogus": 1}]}])
    with pytest.raises(TypeError):
        load_checks({"nope": []})


def test_cli_renders_example_in_every_format(tmp_path, capsys):
    for fmt in ("html", "text", "csv", "json"):
        out = tmp_path / f"heat.{fmt}"
        assert main([str(EXAMPLE), "--format", fmt, "-o", str(out)]) == 0
        assert out.read_text(encoding="utf-8")
    data = json.loads((tmp_path / "heat.json").read_text(encoding="utf-8"))
    verdicts = [row["verdict"] for row in data["rows"]]
    assert verdicts == ["VERIFIED", "VERIFIED", "SINGLE_SOURCE", "CONTRADICTED"]


def test_cli_reports_bad_input(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert main([str(bad)]) == 1
    assert "HEATMAP FAILED" in capsys.readouterr().err
