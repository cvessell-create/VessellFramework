import pytest

from vessell.agentic_soc import (
    build_kql,
    parse_hunt_request,
    plan_hunt,
    propose_remediation,
    redact_secrets,
)


def test_plan_selects_allowlisted_table_and_bounds_window() -> None:
    plan = plan_hunt("I am worried Windows Target One had sign-in activity in the last 10 days.")

    assert plan.request.table == "DeviceLogonEvents"
    assert plan.request.hours == 96
    assert "capped" in " ".join(plan.warnings)
    assert "DeviceLogonEvents" in plan.kql
    assert plan.approval_required is True


def test_signin_request_extracts_user_and_uses_matching_schema() -> None:
    request = parse_hunt_request("Investigate tenant sign-ins for analyst@example.com over 12 hours")
    query = build_kql(request)

    assert request.table == "SigninLogs"
    assert request.user == "analyst@example.com"
    assert "UserPrincipalName" in query
    assert "analyst@example.com" in query


def test_secret_redaction_and_remediation_are_non_operational() -> None:
    assert "[REDACTED]" in redact_secrets("api_key=super-secret-value")
    proposal = propose_remediation("isolate host", "Windows Target One", "High-confidence evidence")

    assert proposal.executed is False
    assert proposal.authorization_required is True
    assert proposal.rollback_required is True


def test_guardrails_reject_unknown_model_and_table() -> None:
    with pytest.raises(ValueError, match="Model is not allowlisted"):
        plan_hunt("Investigate sign-ins", model="unapproved-model")

    request = parse_hunt_request("Investigate sign-ins")
    invalid = request.__class__(request.request, "AuditLogs", request.fields, request.hours, request.host, request.user)
    with pytest.raises(ValueError, match="not allowlisted"):
        build_kql(invalid)