# VessellFramework Operational Remediator Runbook

This runbook is for the full approval-gated remediation workflow in
`vessell.app.remediation_orchestrator`.

## 1) Environment and dependencies

Use Python 3.13 and install:

```bash
python -m pip install -r requirements/dev.txt -r requirements/core.txt -r requirements/orchestrator.txt
```

## 2) Configure required secrets and inventory

1. Copy `.env.example` to `.env`.
2. Replace every placeholder value:
   - `APPROVAL_TOKEN`
   - `SCANNER_TOKEN`
   - `WEBHOOK_SECRET`
   - `ALLOWED_WEBHOOK_PREFIX` (absolute HTTPS URL ending with `/`)
3. Update `example_asset_inventory.json` (or your own inventory file):
   - Set at least one `authorized: true` asset
   - Provide real `asset_id`
   - Provide remediation routing (`remediation_webhook` and/or Intune fields)

## 3) Preflight gate

Run readiness checks before start:

```bash
python run_preflight.py --inventory example_asset_inventory.json --strict
```

Expected: every check is `READY`.

## 4) Start the API

```bash
python -m vessell.app.remediation_orchestrator --host 127.0.0.1 --port 8000
```

Sanity checks:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/
```

## 5) Operational request flow

### 5.1 Sync KEV → actions

```bash
curl -X POST http://127.0.0.1:8000/sync \
  -H "X-Approval-Token: $APPROVAL_TOKEN"
```

### 5.2 List actions

```bash
curl "http://127.0.0.1:8000/actions"
curl "http://127.0.0.1:8000/actions?status=PENDING_APPROVAL"
```

### 5.3 Approve one action (dispatch starts asynchronously)

```bash
curl -X POST "http://127.0.0.1:8000/actions/<action_id>/approve" \
  -H "Content-Type: application/json" \
  -H "X-Approval-Token: $APPROVAL_TOKEN" \
  -d '{"approved_by":"security-operator","change_ticket":"CHG-12345"}'
```

### 5.4 Verify remediation outcome

```bash
curl -X POST "http://127.0.0.1:8000/actions/<action_id>/verify" \
  -H "Content-Type: application/json" \
  -H "X-Scanner-Token: $SCANNER_TOKEN" \
  -d '{"fixed":true,"evidence":"scanner run 2026-09-24T00:00:00Z"}'
```

## 6) Release-ready criteria

Treat remediator as release-ready only when all are true:

1. CI tests pass on supported Python version.
2. Preflight passes with real configuration.
3. Sync → approve → dispatch → verify flow succeeds with audit records.
4. Output artifacts are deterministic for fixed inputs (validated by tests).
5. Operator can reproduce the workflow from a clean clone using this runbook.
