"""Doctrine-reconciliation tests: claim-correction case study playbook.

Covers the step-5/step-6 and ICD 203 extensions to vessell.provenance
(ClaimKind, uncertainty, valid_until/revalidation, dependent confirmation,
require_gate) and the intake/gating wiring added across verify, weights,
validation, scan_reporting, malware_triage, agentic_soc, and the app
pipeline (scanner adapters, KEV intake, defense planning, reporting).
"""

import jsonschema
import pytest

from vessell import agentic_soc
from vessell.agentic_soc_adapter import QueryBatch
from vessell.app import defense_planning, pipeline, reporting, scanner_adapters
from vessell.app.models import PipelineResult
from vessell.app.sources import cisa_kev
from vessell.malware_triage import triage_source_and_record
from vessell.provenance import (
    ClaimGateBlocked,
    ClaimKind,
    ClaimStatus,
    DependentStatus,
    SourceStatus,
    add_corroboration,
    confirm_dependent_update,
    disavow,
    gate_for_use,
    get_claim,
    intake_claim,
    pending_corrections,
    propagate_correction,
    register_dependent,
    require_gate,
    reset_claim_lifecycle,
    revalidate_claim,
)
from vessell.scan_reporting import build_scan_report
from vessell.validation import load_schema, require_provenance_fields
from vessell.verify import (
    ClaimCheck,
    GhostVerdict,
    JobPosting,
    SourceSighting,
    Verdict,
    analyze_planted_news_and_record,
    detect_ghost_job_and_record,
    filter_ghost_jobs,
    verify_and_record,
)
from vessell.weights import WeightingEngine

EST = SourceStatus.SOURCE_ESTABLISHED
SYN = SourceStatus.FRAMEWORK_SYNTHESIS
HYP = SourceStatus.WORKING_HYPOTHESIS


@pytest.fixture(autouse=True)
def _clean_registry():
    reset_claim_lifecycle()
    yield
    reset_claim_lifecycle()


# ---------------------------------------------------------------------------
# provenance: ICD 203 kinds, uncertainty, revalidation
# ---------------------------------------------------------------------------


def test_intake_records_kind_and_uncertainty() -> None:
    record = intake_claim(
        "x", "s", "src", EST,
        kind=ClaimKind.JUDGMENT,
        uncertainty="Medium confidence: single analyst judgment.",
    )
    assert record.kind is ClaimKind.JUDGMENT
    assert "Medium confidence" in record.uncertainty
    assert record.to_dict()["kind"] == "JUDGMENT"


def test_claim_without_valid_until_never_goes_stale() -> None:
    record = intake_claim("x", "s", "src", EST, is_official_record=True)
    assert record.is_stale() is False
    assert gate_for_use(record, "consequential")[0] is True


def test_stale_corroborated_claim_blocked_for_consequential_use() -> None:
    record = intake_claim(
        "x", "s", "src", EST, is_official_record=True, valid_until="2000-01-01"
    )
    assert record.is_stale() is True
    allowed, reason = gate_for_use(record, "consequential")
    assert allowed is False
    assert "STALE" in reason
    # Low-stakes use may proceed with the staleness explicitly noted.
    allowed_low, reason_low = gate_for_use(record, "low")
    assert allowed_low is True
    assert "STALE" in reason_low


def test_revalidate_claim_clears_staleness_and_keeps_audit_trail() -> None:
    record = intake_claim(
        "x", "s", "src", EST, is_official_record=True, valid_until="2000-01-01",
        note="original note",
    )
    updated = revalidate_claim(record, valid_until="2099-01-01", note="rechecked Sept 30")
    assert updated.is_stale() is False
    assert gate_for_use(updated, "consequential")[0] is True
    assert "original note" in updated.note
    assert "rechecked Sept 30" in updated.note
    assert get_claim(record.id).valid_until == "2099-01-01"


def test_require_gate_raises_instead_of_returning_false() -> None:
    record = intake_claim("x", "s", "src", HYP)
    with pytest.raises(ClaimGateBlocked, match="blocked for 'consequential' use"):
        require_gate(record, "consequential")
    ok, _ = require_gate(record, "low")
    assert ok is True


def test_disavow_correction_inherits_kind_uncertainty_valid_until() -> None:
    record = intake_claim(
        "x", "s", "src", EST, is_official_record=True,
        kind=ClaimKind.ASSUMPTION, uncertainty="low", valid_until="2099-06-01",
    )
    correction = disavow(record, "analyst", "wrong", corrected_text="y")
    assert correction.kind is ClaimKind.ASSUMPTION
    assert correction.uncertainty == "low"
    assert correction.valid_until == "2099-06-01"


def test_claim_record_validates_against_extended_schema() -> None:
    schema = load_schema("claim.record.schema.json")
    record = intake_claim(
        "x", "s", "src", EST, is_official_record=True,
        kind=ClaimKind.JUDGMENT, uncertainty="u", valid_until="2099-01-01",
    )
    register_dependent(record.id, "artifact", "location")
    dependent = confirm_dependent_update(record.id, "artifact", "location")
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate({"record_type": "claim", "claim": record.to_dict()})
    validator.validate({"record_type": "dependent", "dependent": dependent.to_dict()})


# ---------------------------------------------------------------------------
# provenance: step-5 dependent confirmation
# ---------------------------------------------------------------------------


def test_dependent_confirmation_workflow() -> None:
    record = intake_claim("x", "s", "src", EST, is_official_record=True)
    register_dependent(record.id, "cron:job-hunt", "filters")
    assert len(pending_corrections()) == 1
    updated = confirm_dependent_update(record.id, "cron:job-hunt", "filters")
    assert updated.status is DependentStatus.UPDATED
    assert updated.confirmed_at != ""
    assert pending_corrections() == []
    assert propagate_correction(record.id)[0].status is DependentStatus.UPDATED


def test_confirm_unknown_dependent_raises() -> None:
    record = intake_claim("x", "s", "src", EST, is_official_record=True)
    with pytest.raises(KeyError):
        confirm_dependent_update(record.id, "nope", "nowhere")


# ---------------------------------------------------------------------------
# verify: intake bridges and gated filtering
# ---------------------------------------------------------------------------


def _quake_check() -> ClaimCheck:
    return ClaimCheck(
        claim="M4.2 earthquake near Wauna, WA",
        sightings=(
            SourceSighting("USGS", EST, is_official_record=True, seen_at="2026-09-29"),
            SourceSighting("PNSN", EST, seen_at="2026-09-29"),
        ),
    )


def test_sighting_to_corroboration_round_trip() -> None:
    sighting = SourceSighting(
        "USGS", EST, root="usgs", seen_at="2026-09-29",
        is_official_record=True, note="event page",
    )
    kwargs = sighting.to_corroboration()
    record = intake_claim("x", "s", "src", HYP)
    updated = add_corroboration(record, **kwargs)
    assert updated.corroboration[0].source == "USGS"
    assert updated.corroboration[0].observed_at == "2026-09-29"


def test_verify_and_record_mirrors_verdict_in_claim_standing() -> None:
    result, record = verify_and_record(_quake_check(), subject="wauna")
    assert result.verdict is Verdict.VERIFIED
    assert result.claim_id == record.id
    assert record.status is ClaimStatus.CORROBORATED
    assert require_gate(record, "consequential")[0] is True


def test_verify_and_record_unverified_stays_gated() -> None:
    check = ClaimCheck(
        claim="something shaky",
        sightings=(SourceSighting("blog", HYP, seen_at="2026-09-30"),),
    )
    result, record = verify_and_record(check)
    assert result.verdict is Verdict.SINGLE_SOURCE
    assert record.status is ClaimStatus.UNVERIFIED
    with pytest.raises(ClaimGateBlocked):
        require_gate(record, "consequential")


def test_analyze_planted_news_and_record_links_claim() -> None:
    report, record = analyze_planted_news_and_record(_quake_check(), subject="wauna")
    assert report.claim_id == record.id
    assert record.kind is ClaimKind.JUDGMENT
    assert "vessell.verify.analyze_planted_news" in record.source


ULINE_TEXT = "Operations Manager. Lacey WA. Same text everywhere."


def _ghost_postings() -> list[JobPosting]:
    return [
        JobPosting(
            title="Operations Manager", employer="Uline", location="Lacey, WA",
            description_text=ULINE_TEXT, salary_text="", source=source,
            listing_id=listing_id, claimed_posted="2026-09-25", first_seen="2025-12-24",
        )
        for source, listing_id in [
            ("Monster", "m-1"), ("Indeed", "i-2"), ("ZipRecruiter", "z-3"),
        ]
    ]


def test_detect_ghost_job_and_record_corraborates_likely_ghost() -> None:
    report, record = detect_ghost_job_and_record(_ghost_postings())
    assert report.verdict is GhostVerdict.LIKELY_GHOST
    assert len(report.signals) >= 3
    assert record.status is ClaimStatus.CORROBORATED
    assert require_gate(record, "consequential")[0] is True
    assert report.claim_id == record.id


def test_filter_ghost_jobs_gates_the_exclusion() -> None:
    kept, reports = filter_ghost_jobs(_ghost_postings())
    assert kept == []
    assert reports[0].verdict is GhostVerdict.LIKELY_GHOST
    assert reports[0].claim_id != ""
    record = get_claim(reports[0].claim_id)
    assert record.status is ClaimStatus.CORROBORATED


def test_filter_ghost_jobs_without_provenance_unchanged() -> None:
    kept, reports = filter_ghost_jobs(_ghost_postings(), track_provenance=False)
    assert kept == []
    assert reports[0].claim_id == ""


# ---------------------------------------------------------------------------
# weights: claim linkage
# ---------------------------------------------------------------------------


def test_weight_set_registers_dependents_against_claim() -> None:
    from vessell.provenance import EvidenceItem, EvidenceSet, ProvenanceRegistry

    claim = intake_claim("x", "s", "src", EST, is_official_record=True)
    registry = ProvenanceRegistry()
    engine = WeightingEngine(registry=registry, weighter=None)
    evidence_set = EvidenceSet(
        registry=registry,
        items=[EvidenceItem(description="d", status=EST, source_id="s1")],
    )
    weighted = engine.weight_set(evidence_set, claim_id=claim.id)
    assert weighted.records[0].claim_id == claim.id
    assert weighted.records[0].to_dict()["claim_id"] == claim.id
    dependents = propagate_correction(claim.id)
    assert any(d.artifact == "vessell.weights.WeightRecord" for d in dependents)


def test_weight_record_validates_against_extended_schema() -> None:
    from vessell.provenance import EvidenceItem, EvidenceSet, ProvenanceRegistry

    schema = load_schema("weight.record.schema.json")
    registry = ProvenanceRegistry()
    engine = WeightingEngine(registry=registry, weighter=None)
    evidence_set = EvidenceSet(
        registry=registry,
        items=[EvidenceItem(description="d", status=EST, source_id="s1")],
    )
    record = engine.weight_item(evidence_set.items[0], use_llama=False)
    jsonschema.Draft202012Validator(schema).validate(record.to_dict())


# ---------------------------------------------------------------------------
# validation / scan_reporting / malware_triage / agentic_soc
# ---------------------------------------------------------------------------


def test_require_provenance_fields_rejects_untagged_records() -> None:
    with pytest.raises(ValueError, match="missing provenance fields"):
        require_provenance_fields({"source": "x"})
    tagged = {
        "source": "trivy", "source_tier": "FRAMEWORK SYNTHESIS",
        "observed_at": "2026-09-30", "status": "UNVERIFIED",
    }
    assert require_provenance_fields(tagged) is tagged


def test_scan_report_renders_provenance_section_when_tagged() -> None:
    report = build_scan_report(
        [{
            "host": "h1", "status": "Vulnerable", "vulns": ["CVE-2024-1"],
            "source": "trivy fs scan", "source_tier": "FRAMEWORK SYNTHESIS",
            "observed_at": "2026-09-30", "claim_id": "claim-abc",
        }],
    )
    assert "## Finding Provenance" in report
    assert "trivy fs scan" in report
    assert "claim-abc" in report


def test_scan_report_omits_provenance_section_when_untagged() -> None:
    report = build_scan_report([{"host": "h1", "status": "Secure", "vulns": []}])
    assert "## Finding Provenance" not in report


def test_triage_source_and_record_intakes_judgment_claims() -> None:
    findings, records = triage_source_and_record(
        "import subprocess\nsubprocess.call('x', shell=True)\n",
        source_name="evil.py",
    )
    assert findings and records
    assert len(records) == len(findings)
    assert all(r.kind is ClaimKind.JUDGMENT for r in records)
    assert all(r.source_tier is SourceStatus.FRAMEWORK_SYNTHESIS for r in records)


def test_triage_clean_source_intakes_negative_result_claim() -> None:
    findings, records = triage_source_and_record("print('hi')", source_name="clean.py")
    assert findings == []
    assert len(records) == 1
    assert "No suspicious capability" in records[0].text


def test_propose_remediation_with_claim_registers_dependent() -> None:
    claim = intake_claim("x", "s", "src", EST, is_official_record=True)
    proposal = agentic_soc.propose_remediation(
        "isolate host", "ws-1", "lateral movement suspected", claim_id=claim.id
    )
    assert proposal.claim_id == claim.id
    assert proposal.authorization_required is True
    dependents = propagate_correction(claim.id)
    assert len(dependents) == 1
    assert dependents[0].artifact == "vessell.agentic_soc.RemediationProposal"


def test_query_batch_carries_provenance_tag() -> None:
    batch = QueryBatch("DeviceLogonEvents", ("a",), (), False, queried_at="2026-09-30")
    assert batch.source == "azure-log-analytics"
    assert batch.queried_at == "2026-09-30"


# ---------------------------------------------------------------------------
# app pipeline: intake at the boundary, dependents on the outputs
# ---------------------------------------------------------------------------


def _kev_catalog() -> dict:
    return {
        "catalogVersion": "2026.09.30",
        "dateReleased": "2026-09-30",
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-0001", "vendorProject": "Acme",
                "product": "Widget", "vulnerabilityName": "RCE",
                "dateAdded": "2026-09-29", "dueDate": "2026-10-20",
            },
        ],
    }


def test_kev_rows_carry_provenance_tags() -> None:
    case = cisa_kev.build_case_from_kev(_kev_catalog())
    row = case["evidence"][0]
    assert row["provenance"]["source"] == "CISA Known Exploited Vulnerabilities catalog"
    assert row["provenance"]["is_official_record"] is True


def test_pipeline_intakes_evidence_and_links_result(tmp_path) -> None:
    case = cisa_kev.build_case_from_kev(_kev_catalog())
    result = pipeline.run_case_pipeline(case)
    assert isinstance(result, PipelineResult)
    assert len(result.claim_ids) == 1
    claim = get_claim(result.claim_ids[0])
    assert claim.status is ClaimStatus.CORROBORATED  # official-record intake rule
    assert claim.source_tier is SourceStatus.SOURCE_ESTABLISHED
    markdown_path, json_path = reporting.write_outputs(result, tmp_path, "case")
    dependents = propagate_correction(claim.id)
    locations = {d.location for d in dependents}
    assert str(markdown_path) in locations
    assert str(json_path) in locations


def test_pipeline_without_provenance_stays_silent() -> None:
    case = cisa_kev.build_case_from_kev(_kev_catalog())
    result = pipeline.run_case_pipeline(case, track_provenance=False)
    assert result.claim_ids == ()


def test_scanner_import_intakes_per_cve_claims() -> None:
    inventory = {"assets": [{"asset_id": "a1", "authorized": True}]}
    scanner_adapters.import_confirmed_cves(
        inventory, asset_id="a1", source="trivy",
        report={"Results": [{"id": "CVE-2026-0001"}, {"id": "CVE-2026-0003"}]},
    )
    assert inventory["assets"][0]["confirmed_cves"] == ["CVE-2026-0001", "CVE-2026-0003"]
    # One claim per newly confirmed CVE.
    assert len(_all_claim_ids()) == 2


def _all_claim_ids() -> list:
    from vessell.provenance import _CLAIMS

    return list(_CLAIMS.keys())


def test_scanner_import_claim_content() -> None:
    inventory = {"assets": [{"asset_id": "a1", "authorized": True}]}
    scanner_adapters.import_confirmed_cves(
        inventory, asset_id="a1", source="trivy", report={"x": "CVE-2026-0002"},
    )
    claim_id = _all_claim_ids()[0]
    claim = get_claim(claim_id)
    assert "CVE-2026-0002" in claim.text
    assert claim.kind is ClaimKind.REPORT
    assert claim.source_tier is SourceStatus.FRAMEWORK_SYNTHESIS
    dependents = propagate_correction(claim_id)
    assert dependents[0].artifact == "asset-inventory"
    assert dependents[0].location == "a1:confirmed_cves"


def test_defense_plan_carries_corroborated_claim() -> None:
    assets = [{
        "asset_id": "a1", "vendor": "Acme", "product": "Widget",
        "internet_exposed": True, "criticality": "critical", "authorized": True,
        "confirmed_cves": ["CVE-2026-0001"], "remediation_webhook": "",
    }]
    plan = defense_planning.build_defense_plan(assets, _kev_catalog())
    assert plan["claim_id"] != ""
    claim = get_claim(plan["claim_id"])
    assert claim.kind is ClaimKind.JUDGMENT
    assert claim.status is ClaimStatus.CORROBORATED  # KEV official-record corroboration
    assert plan["approval_required"] is True
    assert plan["execution_status"] == "PENDING_APPROVAL"


def test_defense_plan_without_actions_has_no_claim() -> None:
    plan = defense_planning.build_defense_plan([], _kev_catalog())
    assert plan["claim_id"] == ""
    assert plan["matched_action_count"] == 0
