# Contributing to VessellFramework

Thanks for your interest. This is a learning-in-public project: an analyst
building real software engineering habits. Good-faith contributions are
welcome.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev,core,orchestrator]"
python -m pytest tests/ -q
```

Python 3.13+ is required.

## What merge-ready looks like

1. **Tests** — new behavior ships with regression tests in `tests/`.
2. **Clean gates** — `mypy` and `ruff` pass on every touched file.
3. **Schemas** — new machine-readable records get a JSON schema in
   `schemas/` plus a validation test.
4. **Provenance honesty** — never weaken the provenance firewall, the
   harm gate, or the rule that the framework structures evidence but does
   not invent conclusions.
5. **Docs** — update the relevant `*_SKILL_*.md` and/or `README.md`.
6. **Integrity manifest** — if you touch a file tracked in
   `VessellFramework_v3.8.1_SHA256_Manifest.json`, regenerate it and confirm
   `python verify_manifest.py` passes.

The `VessellFramework_Community_SKILL_v1.0.md` skill file is the detailed,
assistant-executable version of this guide.

## Filing issues

One issue per problem. Include what you ran, what you expected, what
happened, the full error, and your Python version.

## License

By contributing, you agree your work is licensed under the Apache License
2.0, like the rest of the project.
