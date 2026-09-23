---
name: vessel-framework-agentic-soc-analyst
description: >
  Evidence-first architecture for a bounded agentic SOC analyst that converts
  natural-language hunt requests into allowlisted query plans, budgets model use,
  produces structured findings, and proposes human-approved remediation.
---

# VesselFramework Agentic SOC Analyst Skill
## Version 0.1 - Architecture and Guardrail Candidate

## 1. Purpose

This skill turns the course material into a reusable VesselFramework operating layer:

`INTAKE -> STRUCTURE -> VALIDATE -> QUERY -> MINIMIZE -> HUNT -> REPORT -> REVIEW -> PROPOSE`

The package implementation currently supports planning, validation, budgeting, redaction,
and proposal generation. It does not make live cloud queries, call an LLM, or execute
remediation actions.

## 2. Operating Contract

The agent must:
- preserve the operator's request and evidence boundary;
- select only allowlisted tables and fields;
- cap time windows, rows, and model tokens before external calls;
- redact credential-shaped values before model submission;
- emit structured findings with evidence, confidence, alternatives, and limitations;
- require human approval before isolation, account disablement, firewall changes, or other containment;
- retain rollback and stop-condition information for every proposed action.

## 3. Course-to-Package Mapping

| Course concept | VesselFramework implementation |
|---|---|
| Python data structures | `HuntRequest`, `HuntPlan`, `RemediationProposal` |
| JSON/tool schema | `TableDefinition` and allowlisted table registry |
| KQL construction | `build_kql()` with field validation |
| Token/cost awareness | `estimate_tokens()` and model limits |
| Prompt safety | secret redaction and bounded context |
| Guardrails | table, field, time, row, model, and approval controls |
| Threat-hunt output | existing scan/reporting and case-report paths |
| Agentic remediation | proposal only; execution remains separately authorized |

## 4. Intake and Query Planning

Natural-language requests are converted into a `HuntRequest` with:
- an allowlisted table;
- allowlisted fields;
- a bounded time window;
- optional host and user selectors;
- the original request with secrets redacted.

Unknown or unsupported tables must be rejected. A model may recommend a table, but the
local allowlist remains authoritative.

## 5. Threat-Hunt Evidence Contract

Every future live hunt adapter should preserve:
- request ID and evidence cutoff;
- query text and selected table/fields;
- row count and token estimate;
- model, budget, and actual usage;
- raw result location or hash;
- finding title, description, confidence, indicators, relevant log lines, and MITRE mapping;
- contradicting evidence, alternative explanations, and unresolved gaps.

An LLM output is analysis or a working hypothesis until supported by source-established
telemetry and reviewed by an operator.

## 6. Guardrails

Minimum controls:
- allowlisted tables and fields;
- maximum time window;
- maximum row count;
- maximum prompt/output token budget;
- model allowlist and estimated cost;
- secret/PII handling before model submission;
- no unapproved external action;
- explicit approval, rollback, and stop conditions for containment.

## 7. Remediation Boundary

The agent may produce a proposal such as:

```text
Action: isolate host
Target: Windows Target One
Rationale: high-confidence evidence from reviewed telemetry
Authorization: required
Rollback: required
Execution: not performed by the planning layer
```

Isolation, account disablement, firewall changes, or VM shutdown require a separate,
audited executor with least privilege, explicit authorization, and a tested rollback path.

## 8. Validation and Promotion

Promote a live adapter only after:
1. fixture-based tests pass without network access;
2. query allowlists reject unknown tables and fields;
3. time, row, token, and cost caps are enforced;
4. secrets are redacted;
5. malformed model output is rejected or quarantined;
6. reports preserve provenance and evidence lineage;
7. remediation remains review-gated;
8. dry-run and rollback tests pass in the authorized range.