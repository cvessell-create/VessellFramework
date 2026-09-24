# VessellFramework

VessellFramework is an auditable Python runtime and a set of doctrine and skill artifacts for evidence, provenance, case analysis, forecasting, and approved remediation control.

Author: Christopher R. Vessell

Current package state: v3.8.1 rough working candidate prepared for graduate-level review and feedback.

For the complete skill, agent, executable-code, scanner, and authorized remediation map, start with [VesselFramework_Agent.md](VesselFramework_Agent.md). Historical artifacts retain their original `VesselFramework` names; the active Python namespace is `vessell`.

## Reviewer quick orientation

If you are reviewing this as an academic rough-working submission, read in this order:

1. `PROFESSOR_README.md` (purpose, contribution, current limits, and requested feedback)
2. `VesselFramework_MetaMatrix_Framework_v3.8_v3.9_Combined.md` (integrated doctrine and methods)
3. `SKILL.md` (operational analyst execution layer)
4. `VesselFramework_Forecasting_SKILL_v1.0.md` (forecasting controls and calibration form)
5. `vesselframework_reference_v1.1_provenance_firewall.py` + `tests/` (executable reference and regression checks)

For package boundaries and canonical scope, see `CANONICAL_REFERENCE.md`.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements\dev.txt -r requirements\core.txt
```

Run the assurance gate:

```powershell
ruff check vessel tests
mypy vessel
pytest
```

Validate a case record:

```powershell
python -m vessel.cli example_case.json --schema case.schema.json
```

Run the Identity & Recognition Provenance Gate:

```powershell
python VesselFramework_SingleFile_EvilTwin_v0.2.py selftest
python VesselFramework_SingleFile_EvilTwin_v0.2.py recognition --subject "Christopher Ray Vessell" --evidence example_recognition_evidence.json
```

The recognition gate quarantines name-only matches, classifies recognition
stages, and counts independent provenance roots rather than search-result
quantity.

The original flat launchers and doctrine files remain the compatibility layer for version 3.8.1. New executable functionality belongs in `vessel/`, machine-readable contracts belong in `schemas/`, and regression tests belong in `tests/`. Optional integrations are separated into `requirements/agent.txt`, `documents.txt`, and `research.txt`.

## Full operational remediator quick path

If you need the full approval-gated remediator (sync, approve, dispatch, verify):

1. Install orchestrator dependencies:

```powershell
python -m pip install -r requirements\orchestrator.txt
```

2. Create `.env` from `.env.example`, then replace every placeholder.

3. Preflight readiness:

```powershell
python run_preflight.py --inventory example_asset_inventory.json --strict
```

4. Start the remediator API:

```powershell
python -m vessell.app.remediation_orchestrator --host 127.0.0.1 --port 8000
```

5. Follow the operator runbook for sync/approve/verify request flow:
`docs/operations/remediator_runbook.md`.
