# Isolated public-data replay lab

The lab is a separate Python dependency environment, not an OS sandbox, VM,
container, or controlled field study. It performs only local reads and writes,
does not scan real targets, and does not deploy patches or contact employers.
Package installation during setup requires network access.

## Setup and run

Use Python 3.13 or newer and keep the environment/output outside source data.
Replace the example absolute paths with the actual source checkout and saved
23-source audit catalog. The data remain external to GitHub.

```sh
python3.13 -m venv /absolute/path/to/replay-lab/venv
/absolute/path/to/replay-lab/venv/bin/python -m pip install -e \
  '/absolute/path/to/rebuild[evaluation,dev,core,orchestrator]'
/absolute/path/to/replay-lab/venv/bin/python -m vessell.replay_lab \
  --data-dir /absolute/path/to/public_evaluation_data \
  --catalog /absolute/path/to/data_audit/evaluation.json \
  --output-dir /absolute/path/to/replay-lab/results \
  --workers 4 --repetitions 32
/absolute/path/to/replay-lab/venv/bin/python -m pytest \
  /absolute/path/to/rebuild/tests
```

Use the repository's editable/source-checkout installation: the provenance
adapter loads a legacy reference file from the checkout root. A non-editable
wheel currently omits that file and cannot run this lab independently. The
lab still has its own dependency environment; implementation hashes record the
exact checkout used. After source changes, rerun the lab and verify new hashes;
reinstall when declared dependencies change. Record `python -m pip freeze`
from that environment for replication.

## Scenarios and exact acceptance criteria

| Scenario | Population | Passing rule |
|---|---|---|
| Harm Gate concurrency | All 128 complete Boolean inputs, seven individually missing-field inputs and empty intake, repeated 32 times (4,352 evaluations) | Four-worker results equal serial results; inputs unchanged; zero incomplete clearances; complete clearance follows the explicit proportionality rule |
| Missing-intake pipeline | Synthetic empty-evidence case | Shared gate reports UNKNOWN and uncleared |
| Report fault | Copy of actual paired case output | Modified Markdown is rejected; original reports remain synchronized |
| Source fault | Temporary copies of four CDC sources and original manifest | Corrupted observation copy is rejected by checksum before scoring |
| Real forecast replay | Retrospective CDC ensemble forecasts with matched observations | Nonempty scored population; every selected row accounted for; missing intervals explicitly counted |
| Input preservation | Frozen catalog and original download manifest | Every hash still matches after replay |

Outputs include synchronized JSON/Markdown, source and implementation hashes,
runtime identity, full PDF-page decoding checks and redaction-aware OPM row
checks. Source PDF text extraction is not OCR, image inspection or a complete
substantive audit. Reference-file month does not relabel OPM action dates;
off-period rows are reported separately. No REDACTED field is replaced with
zero or treated as evidence of absence.

Exit status is 0 for passing checks, 1 for a failed acceptance criterion, and
2 for invalid inputs/decoding/runtime errors. `--skip-source-decoding` is an
explicit optional mode, not an automatic fallback after reader failures.

Passing this lab closes reproducibility, input-validation and local
synchronization checks. It does not establish external efficacy. Controlled
operational telemetry, valid posting/claim labels, frozen prospective framework
forecasts, and comparative analyst/learning outcomes remain separate needs.
