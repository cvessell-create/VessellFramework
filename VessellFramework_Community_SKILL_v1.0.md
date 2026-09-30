---
name: vessell-framework-community
description: >
  Guide for community contributors to VessellFramework. Covers how to file
  issues, propose changes, meet the code and test standards, and what kinds
  of contributions are welcome. Use when someone asks how to contribute.
---

# VessellFramework Community Skill
## Version 1.0

## 1. Purpose

Make it easy for others to contribute well. This skill is the executable
companion to `CONTRIBUTING.md`: it tells a contributor (or their assistant)
exactly what a merge-ready change looks like.

## 2. Ground Rules

- Be respectful and assume good intent. This is a learning-in-public
  project by an analyst learning software engineering.
- No harassment, no personal data in issues or PRs, no secret keys in
  code or fixtures.
- The maintainer's decision on scope is final.

## 3. What a Merge-Ready Change Looks Like

Every PR must satisfy all of these:

1. **Tests.** New behavior ships with regression tests under `tests/`.
   Run the full suite: `python -m pytest tests/ -q` — all green.
2. **Types and lint.** `mypy` and `ruff` must be clean on touched files.
   The repo's own `run_framework.py` health gate runs mypy on the
   installer; keep it passing.
3. **Schemas.** New machine-readable records get a JSON schema under
   `schemas/` and a validation test.
4. **Provenance honesty.** Framework code must never invent evidence,
   conclusions, or verification. The case report boundary ("structures
   supplied evidence; does not independently verify conclusions") is
   load-bearing — do not weaken it.
5. **Docs.** User-facing changes update the relevant `*_SKILL_*.md`
   and/or `README.md`.
6. **Integrity manifest.** If you touch a file tracked in
   `VesselFramework_v3.8.1_SHA256_Manifest.json`, regenerate the manifest
   and confirm `python verify_manifest.py` passes.

## 4. Welcome Contributions

- New scanner adapters under `vessell/app/` (follow the existing
  adapter pattern + tests).
- Additional weight-table calibrations with documented methodology.
- Forecast calibration studies using the forecasting skill.
- Documentation, examples, and typo fixes.
- Bug reports with a minimal reproduction.

## 5. Out of Scope

- Changes that weaken the provenance firewall, harm gate, or the
  do-not-invent boundary.
- New network integrations without an offline fixture and test.
- Breaking the `vessell` package's Python >= 3.13 floor without
  discussion in the issue first.

## 6. Filing Issues

Include: what you ran, what you expected, what happened, the full
error output, and your Python version. One issue per problem.
