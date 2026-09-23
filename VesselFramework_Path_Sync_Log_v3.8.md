# VesselFramework Path Sync Log — v3.8

This Markdown file documents the synchronization state. Actual installer events are written as JSONL by `install_vesselframework_v3_8.py`.

## Registered paths

| Target | Role | Current package action |
|---|---|---|
| `/mnt/skills/user/vessel-framework-analyst/SKILL.md` | live skill | atomic replace |
| `/areas/vessel-framework.md` | continuity | managed-block update |
| `/areas/maskirovka-paper.md` | continuity | managed-block update |
| `/areas/bottleneck-thesis.md` | continuity | managed-block update |
| `/topics/writing-style.md` | continuity | managed-block update |

## Truth condition

No target is marked synchronized in this document merely because it appears in the package.

Successful synchronization requires an installer event with:
- `status = UPDATED`
- readable `post_hash`
- no error.

## Initial package state

`PACKAGED — RUNTIME SYNC NOT YET PROVEN`
