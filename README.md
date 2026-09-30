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
python VesselFramework_SingleFile_EvilTwin_v0.2.py recognition --subject "Alex Cvessell" --evidence example_recognition_evidence.json
```

The recognition gate quarantines name-only matches, classifies recognition
stages, and counts independent provenance roots rather than search-result
quantity.

Use it as a library:

```python
from vessell import (
    EvidenceItem,
    EvidenceSet,
    ProvenanceRegistry,
    SourceStatus,
    WeightingEngine,
)

items = [
    EvidenceItem(source_id="cisa-kev", description="CISA KEV entry",
                 status=SourceStatus.SOURCE_ESTABLISHED),
    EvidenceItem(source_id="vendor-blog", description="Vendor write-up",
                 status=SourceStatus.WORKING_HYPOTHESIS),
]
registry = ProvenanceRegistry()
registry.register_many(items)

engine = WeightingEngine(registry)  # add CalibratedLlamaWeighter for live LLM scoring
weighted = engine.weight_set(EvidenceSet(registry, items))
for record in weighted.records:
    print(record.source_id, round(record.normalized_weight, 3))
```

The original flat launchers and doctrine files remain the compatibility layer for version 3.8.1. New executable functionality belongs in `vessel/`, machine-readable contracts belong in `schemas/`, and regression tests belong in `tests/`. Optional integrations are separated into `requirements/agent.txt`, `documents.txt`, and `research.txt`.

## What this demonstrates

Five-minute tour (see `VessellFramework_Portfolio_Showcase_SKILL_v1.0.md` for the guided version):

1. `python -m pytest tests/ -q` — 73-test regression suite: provenance, validation, scanner adapters, malware triage, defense planning, remediation orchestration, agentic SOC, EvilTwin gate, Llama evidence weighting.
2. `python vesselframework_case_runner.py example_case.json` — structured case intake: provenance firewall, deception (maskirovka) checks, harm gate, analyst-ready report.
3. `python run_live_kev_case.py` — live CISA Known Exploited Vulnerabilities intake through the same pipeline.
4. `python VesselFramework_SingleFile_EvilTwin_v0.2.py selftest` — identity/recognition provenance gate.
5. `python -m pytest tests/test_weights.py tests/test_weighter.py -q` — Llama-calibrated evidence weighting with per-weight provenance.

Engineering signals: typed Python, mypy + ruff gates, JSON schemas for machine-readable contracts, SHA-256 integrity manifest (`python verify_manifest.py`), CI on Python 3.13, Apache-2.0 licensed.

## License

Apache License 2.0 — see [LICENSE](LICENSE). Copyright 2026 Christopher R. Vessell.
