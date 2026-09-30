---
name: vessell-framework-portfolio-showcase
description: >
  Give a guided, runnable tour of the VessellFramework repository as a
  portfolio piece. Runs the live demos (case intake, CISA KEV case,
  EvilTwin recognition gate, Llama-calibrated evidence weighting),
  explains what each proves about the author's engineering and analytic
  tradecraft, and produces a shareable showcase summary.
---

# VessellFramework Portfolio Showcase Skill
## Version 1.0

## 1. Purpose

Turn this repository into a five-minute portfolio demonstration. The skill
runs the framework's self-contained demos, narrates what each one proves,
and emits a short showcase summary a hiring manager or reviewer can read
without running anything.

Audience: recruiters, hiring managers, and peer reviewers with no prior
context on the project.

## 2. Demo Sequence

Run in this order. Every step must pass before narrating the next.

### Step 1 — Test suite (engineering discipline)

```bash
python -m pytest tests/ -q
```

Expected: all tests pass (73 at v3.8.1+weights). Narration point: the repo
ships a regression suite covering provenance, validation, preflight, scanner
adapters, malware triage, defense planning, remediation orchestration, the
agentic SOC adapter, the EvilTwin gate, and the Llama weighting engine.

### Step 2 — Case intake (core analytic loop)

```bash
python vesselframework_case_runner.py example_case.json --output /tmp/showcase_case.md
```

Narration point: structured evidence intake with a provenance firewall,
maskirovka (deception) check gates, a harm gate, and an analyst-ready
Markdown report. The report explicitly states it structures supplied
evidence and does not invent conclusions — that boundary is the point.

### Step 3 — Live CISA KEV case (real data, offline-safe)

```bash
python run_live_kev_case.py
```

Narration point: pulls live CISA Known Exploited Vulnerabilities data and
runs it through the same case pipeline. Proves the framework works on real
feed data, not just fixtures.

### Step 4 — EvilTwin recognition gate (identity provenance)

```bash
python VesselFramework_SingleFile_EvilTwin_v0.2.py selftest
```

Narration point: quarantines name-only matches and counts independent
provenance roots instead of search-result quantity. The example subject is
fictional (`Alex Cvessell`).

### Step 5 — Llama-calibrated evidence weighting (newest module)

```bash
python -m pytest tests/test_weights.py tests/test_weighter.py -q
```

Narration point: `vessell/weights.py` scores evidence with an
LLM-calibrated static weight table (`llama-calibrated-v1`), applies
provenance multipliers, discounts shared-root items for independence, and
stamps every weight with its own provenance (model, table version,
rationale, flags). `vessell/weighter.py` batches a whole evidence set into
one model call, retries with backoff, and falls back to the static table
with an audit flag when no endpoint is reachable.

## 3. Showcase Summary Template

After the demos, write `SHOWCASE.md` (do not commit it unless asked):

- One paragraph: what the framework is.
- Bullet list: the five demos and what each proved, with pass/fail.
- "Engineering signals" section: typed Python, mypy + ruff gates, JSON
  schemas for machine-readable contracts, SHA-256 integrity manifest,
  CI on Python 3.13.
- "Analytic signals" section: provenance firewall, deception checks, harm
  gate, calibrated weighting, explicit do-not-invent boundary.

## 4. Rules

- Never claim a demo passed without running it.
- If a demo fails, say so plainly and show the error; do not narrate
  around it.
- Keep the narration non-technical enough for a hiring manager and
  precise enough for a peer reviewer.
- Do not expose secrets, tokens, or personal data during the tour.
