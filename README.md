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

## Constitutional governance packet

The framework now includes a constitutional/oath governance packet at:

- `docs/governance/US_CONSTITUTION_AND_OATH_FRAMEWORK.md`

History exports can include attestation metadata with:

```powershell
vf-benchmark --prompt "..." --dry-run --history-all-branches --oath-attestor "NAME/ROLE" --human-loop-owner "@cvessell-create"
```

The export metadata records a human-in-the-loop policy where only the designated
owner may receive external escalation decisions.

## Cross-model benchmark runner

Use `vf-benchmark` to run one prompt across GPT/Claude/Grok/other providers,
capture raw responses, and score each response with weighted rubric criteria:

- intent detection (25%)
- statistical correctness (30%)
- R safety checks (20%)
- actionability (15%)
- noise control (10%)

Dry-run mode gives built-in example responses and scoring without API keys:

```powershell
vf-benchmark --prompt "I’m trying to improve my workflow..." --dry-run
```

Live mode requires provider keys:

- `OPENAI_API_KEY` (gpt)
- `ANTHROPIC_API_KEY` (claude)
- `XAI_API_KEY` (grok)
- `OTHER_API_KEY` (other openai-compatible endpoint, optional `OTHER_BASE_URL`)

Outputs are written to:

- `outputs/model_benchmarks/latest_benchmark.json`
- `outputs/model_benchmarks/latest_benchmark.md`

Each JSON artifact now includes an `upstream_meta` envelope captured before output
write, including mode, timestamp, step timeline, and pull-history inventory for
prior JSON artifacts in the same output root.
All modes also refresh a global history index under `outputs/history_index.json`
and `outputs/history_index.md` (configurable with `--history-root`), plus full
data dump artifacts under `outputs/history_dump.jsonl` and `outputs/history_dump.csv`.

Queue/swarm mode lets you process prompts continuously while adding new prompts
to the same queue:

```powershell
# Start queue worker (continuous)
vf-benchmark --queue-path q.jsonl --dry-run

# Append a prompt while worker is running
vf-benchmark --queue-path q.jsonl --enqueue "Your prompt here"
```

Queue mode defaults:

- queue field name: `q` (for JSONL rows like `{"q":"...prompt..."}`)
- offset tracking: `.state/q.offset` (stream offset of the last successfully handled queue line; successful benchmark writes and intentionally skipped malformed lines are acknowledged, and offset rebases if queue file is truncated)
- queue outputs: `outputs/model_benchmarks/hurricane/q_<offset>.{json,md}`

Process queue once and exit:

```powershell
vf-benchmark --queue-path q.jsonl --once --dry-run
```

Apply a fixed wall-clock budget in queue mode:

```powershell
vf-benchmark --queue-path q.jsonl --dry-run --time-budget-seconds 300
```

Use the full package runtime profile defaults (defensible swarm settings):

```powershell
vf-benchmark --runtime-profile full-package --queue-path q.jsonl --dry-run
```

Empirically probe session/runtime limits in full package mode:

```powershell
vf-benchmark --probe-session-limit --runtime-profile full-package --dry-run
```

Probe output artifacts are written under:

- `outputs/model_benchmarks/session_probes/<timestamp>/probe_summary.json`
- `outputs/model_benchmarks/session_probes/<timestamp>/probe_summary.md`

Probe summary JSON also includes `upstream_meta.pull_history` for all previously
written `probe_summary.json` artifacts under the probe output root.

Run an empirical secret scan across the full package and emit reports:

```powershell
vf-benchmark --empirical-secret-scan --scan-root . --scan-output-dir outputs/security_scans
```

Secret scan output artifacts are written under:

- `outputs/security_scans/<timestamp>/secret_scan_report.json`
- `outputs/security_scans/<timestamp>/secret_scan_report.md`

Secret scan report JSON includes `upstream_meta.pull_history` for all prior
`secret_scan_report.json` artifacts under the scan output root.

History export options for full metadata pull-through:

```powershell
vf-benchmark --prompt "..." --dry-run --history-root outputs --history-limit 2000 --history-export-csv
```

- `--history-root`: aggregation root for all historical JSON pull artifacts
- `--history-limit`: cap how many artifacts are ingested into the meta index
- `--history-export-csv`: also emit `history_artifacts.csv` and
  `history_benchmark_scores.csv` for R/Python analysis
- `--history-all-branches`: merge history artifacts from all local git branches
  into one aggregated index
- `--history-parallel-workers`: parallel worker count for all-branches metadata
  pull collection

Replay all historical prompts (from session artifacts) and regenerate benchmark outputs:

```powershell
vf-benchmark --redo-prompts-from-history --dry-run --history-root outputs --redo-prompt-limit 2000
```

Repository autoload defaults are now supported through:

- `.vf_benchmark_autoload.json`

This lets queue/history/oath/human-loop settings auto-load without manually
providing every flag. Use `--no-autoload` to bypass repo defaults.

Each history export run also auto-generates a runtime skill snapshot:

- `outputs/runtime_skill.json`
- `outputs/runtime_skill.md`

The empirical scan includes detector coverage metrics and supports a canary
validation phrase for detection checks.
By default, scan traversal excludes operational/cache directories (for example:
`.git/`, `.venv/`, `outputs/`, and `tests/`) and binary document/media types.

The original flat launchers and doctrine files remain the compatibility layer for version 3.8.1. New executable functionality belongs in `vessell/`, machine-readable contracts belong in `schemas/`, and regression tests belong in `tests/`. Optional integrations are separated into `requirements/agent.txt`, `documents.txt`, and `research.txt`.
