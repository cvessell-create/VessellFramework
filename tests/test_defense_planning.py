from datetime import UTC, datetime

from vessell.app.defense_planning import approve_plan, build_defense_plan


def test_vendor_only_match_requires_scanner_confirmation() -> None:
    assets = [
        {
            "asset_id": "gateway-01",
            "vendor": "Check Point",
            "product": "Quantum Security Gateway",
            "internet_exposed": True,
            "criticality": "critical",
            "authorized": True,
        }
    ]
    catalog = {
        "catalogVersion": "2026.09.22",
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-85102",
                "vendorProject": "Check Point",
                "product": "Multiple Products",
                "vulnerabilityName": "Certificate validation vulnerability",
                "dueDate": "2026-09-25",
            }
        ],
    }

    plan = build_defense_plan(assets, catalog, generated_at=datetime(2026, 9, 22, tzinfo=UTC))

    assert plan["matched_action_count"] == 1
    assert plan["execution_status"] == "PENDING_APPROVAL"
    assert plan["actions"][0]["match_type"] == "vendor_only"
    assert plan["actions"][0]["priority"] == "REVIEW"
    assert plan["actions"][0]["status"] == "REVIEW_REQUIRED"
    assert not plan["actions"][0]["dispatch_eligible"]


def test_scanner_confirmed_match_is_eligible_for_approval() -> None:
    assets = [
        {
            "asset_id": "web-01",
            "vendor": "Example",
            "product": "Web Server",
            "authorized": True,
            "confirmed_cves": ["CVE-2026-1"],
        }
    ]
    catalog = {"vulnerabilities": [{"cveID": "CVE-2026-1", "vendorProject": "F5", "product": "BIG-IP"}]}

    plan = build_defense_plan(assets, catalog)

    assert plan["matched_action_count"] == 1
    assert plan["actions"][0]["match_type"] == "scanner_confirmed_cve"
    assert plan["actions"][0]["dispatch_eligible"]


def test_approval_marks_plan_without_executing_actions() -> None:
    approved = approve_plan({"execution_status": "PENDING_APPROVAL", "actions": []}, "security-operator")

    assert approved["execution_status"] == "APPROVED_FOR_AUTHORIZED_DEPLOYMENT"
    assert approved["approved_by"] == "security-operator"