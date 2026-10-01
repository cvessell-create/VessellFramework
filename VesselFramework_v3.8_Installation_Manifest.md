# VesselFramework v3.8.1 Installation / Synchronization Manifest

## Objective

Provide an auditable mechanism that can synchronize the canonical package with registered live skill/private continuity paths **only when explicitly applied**.

**State rule:** package presence, extraction, or dry-run does not constitute installation. A target is synchronized only after a successful write and post-write verification.

## Registered targets

- `/mnt/skills/user/vessel-framework-analyst/SKILL.md`
- `/areas/vessel-framework.md`
- `/areas/maskirovka-paper.md`
- `/areas/bottleneck-thesis.md`
- `/topics/writing-style.md`

## Package files

- `VesselFramework_MetaMatrix_Framework_v3.8_v3.9_Combined.md`
- `SKILL.md`
- `VesselFramework_Forecasting_SKILL_v1.0.md`
- `vesselframework_reference_v1.1_provenance_firewall.py`
- `VesselFramework_Hardening_Patch_Registry_v3.8.md`
- `install_vesselframework_v3_8.py`
- `memory_payloads/*.managed.md`

## Installation behavior

The installer is dry-run by default.

Dry run:

```bash
python3 install_vesselframework_v3_8.py
```

Apply only to existing registered paths:

```bash
python3 install_vesselframework_v3_8.py --apply
```

Allow creation of missing registered paths:

```bash
python3 install_vesselframework_v3_8.py --apply --create-missing
```

Every attempt writes `VesselFramework_Path_Sync_Log.jsonl` containing target, source, action, timestamp, pre-hash, post-hash, backup, status, and error.

The live skill is atomically replaced. Continuity files use managed-block replacement so unrelated text is preserved.

## Runtime verification

Reference firewall tests:

```text
[PASS] Cross-set children of same root are detected as shared
[PASS] Missing parent returns unresolved provenance
[PASS] Unresolved provenance blocks eligibility
[PASS] Cycle is surfaced
[PASS] Conflicting parents are surfaced
[PASS] Fractured provenance graphs block convergence

ALL FIREWALL REGRESSION TESTS PASSED
```

Installer dry-run in this packaging environment:

```text
VesselFramework Path Synchronizer v3.8
MODE: DRY RUN
[MISSING_TARGET] /mnt/skills/user/vessel-framework-analyst/SKILL.md
[MISSING_TARGET] /areas/vessel-framework.md
[MISSING_TARGET] /areas/maskirovka-paper.md
[MISSING_TARGET] /areas/bottleneck-thesis.md
[MISSING_TARGET] /topics/writing-style.md
FRAMEWORK STATE: DEGRADED — RUNTIME PATH NOT SYNCHRONIZED
```

A dry-run result does not prove that private runtime paths are writable. Runtime validation requires executing `--apply` in the environment that owns those paths and inspecting the generated sync log.

## Authority rule

A path is not considered synchronized until the log records `UPDATED` and a post-write SHA-256 hash.

Private continuity files are non-authoritative. Canonical doctrine remains in the framework artifact; runtime behavior comes from the installed `SKILL.md`.

## v3.8.1 stale-state rule

Do not report `live skill: v3.8.x` or `private paths synchronized` solely from package contents. Runtime state must be established from an actual successful apply operation plus verification evidence. If that evidence is absent, report `UNVERIFIED/NOT APPLIED`.

## Internal-method boundary

The installer/package may contain proprietary analytical doctrine. Its presence does not authorize disclosure of that doctrine in external academic or professional deliverables. Findings may be translated into domain-standard terminology. This boundary does not supersede required disclosure of external tools, sources, or generative-AI assistance.
