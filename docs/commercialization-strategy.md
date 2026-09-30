# VessellFramework — Commercialization Strategy

**Prepared:** September 30, 2026
**Status:** Private working document. No traction, no revenue, no users — everything below is a plan, not a claim.

---

## 1. What it actually is today

Strip the framing and the framework is:

- A **rules-based verification toolkit** in typed Python: planted-news corroboration checks, hostile-spread indicators, ghost-job filtering, and an LLM-assisted evidence weighter.
- Deterministic where it counts: every verdict reproduces byte-identically from its sightings; thin intake degrades to labeled UNVERIFIABLE instead of guessing.
- Engineering hygiene is real: 99 tests, mypy + ruff gates, JSON schemas, SHA-256 manifest, Apache-2.0.
- **What it is not:** a product, a dataset, a user base, a moat, or a business. The verify path performs no network calls and no model inference — it judges only the sightings it is given. There is no collection layer, no hosted service, no distribution, no revenue.

That honesty is the foundation. Everything below follows from it.

## 2. Three honest findings

**Finding 1 — There is no moat, and rules are not defensible.**
The entire deterministic doctrine (tier weights, independence discount, burst/clone/laundering indicators, ghost-job signals) can be reimplemented by a competent engineer in a weekend from the skill docs alone. Publishing the method — which the capstone and the reputation path both require — dissolves what little obscurity exists. Defensibility, if it ever comes, must come from **data** (a labeled corpus nobody else has), **distribution** (users inside a workflow), or **workflow embedding** (the verification step living inside someone else's pipeline). None of those exist yet. Any plan that assumes the code itself is the asset is wrong.

**Finding 2 — The most valuable asset is the evaluation corpus, not the code.**
The capstone's labeled claim set (60–100 ground-truthed claims: authentic-with-burst, manufactured spread, orphaned, single-source) is the closest thing to a data moat available. Labeled disinformation-spread data with provenance metadata is genuinely scarce, expensive to build, and useful to newsrooms, trust & safety teams, and researchers. If anything here becomes commercially valuable, it starts there — which is why the 90-day plan prioritizes corpus construction over feature work.

**Finding 3 — The realistic "sell to Meta" is employment, not acquisition.**
Acquirers buy teams, user bases, proprietary data, or revenue. A solo rules engine with no users is not an acquisition target at any price a founder would want, and shopping it as one wastes the asset. What *is* real: integrity / trust & safety / threat-intel hiring managers buy demonstrated capability. The framework's actual near-term commercial value is as a **hiring asset** — proof of work that converts into an intel-adjacent role at a commercial employer (which is also the stated career goal). Treat acquisition as a 3–5-year possibility contingent on data + distribution, and treat employment as the 6–12-month path.

## 3. Path A — Open-source reputation → consulting / productized service

**The shape:** public repo + demo + written case studies → credibility with newsrooms, corporate comms teams, brand-safety functions, OSINT trainers, and job boards (ghost-job filtering is a natural wedge for recruiting platforms drowning in stale listings). Revenue as project consulting: verification audits, custom adapter builds, team training. Realistic shape is 5-figure engagements, slow ramp, founder-led sales.

**What it actually requires:**
1. Repo goes public (the founder's call; currently private by his decision).
2. The interactive demo live and linked (built — Claim Verifier).
3. 3+ written case studies with real worked examples (Wauna, bridge-closure burst, Uline — all exist as fixtures; they need narrative write-ups, not more code).
4. 6–12 months of visible work: writing, talks, answering questions in practitioner communities. Reputation compounds slowly or not at all.

**Honest economics:** consulting is a job, not a company. It pays, it builds the name, and it funds the next step — but it does not scale and it competes with the founder's own job search for hours. Price it accordingly and do not mistake it for a startup.

## 4. Path B — Startup funding

**What investors need to see:** (a) 10x technology or proprietary data, (b) traction (users, pilots, revenue, or LOIs), (c) a team that can ship and sell. Current score: 0 for 3.

**The gap, plainly:**
- Technology: deterministic rules are a feature for auditability but a weakness for defensibility. The LLM weighter is a thin wrapper over commodity models.
- Data: no corpus yet — the capstone set is the seed, and it does not exist yet.
- Traction: no users, no pilots, no LOIs.
- Team: solo, and the founder is job-hunting (correctly) in parallel.

**What would close the gap (in order):** a labeled corpus with provenance metadata (data moat seed) → an automated collection layer so the tool ingests rather than waits for intake (this is the single biggest engineering gap) → a wedge product with 10+ real users (e.g., a verification API or a ghost-job filter for a job board) → then, and only then, a pitch. Do not pitch before the wedge exists; a pre-traction pitch for rules-based tooling will not clear a partner meeting.

**Funding reality check:** pre-seed for dev-tools without traction is raised on team + thesis. The credible version of this founder's thesis is "deterministic, auditable verification for an industry being eaten by black-box classifiers" — that is a real wedge, but it needs the corpus and the collection layer to be more than words.

## 5. Path C — Acquisition

Covered in Finding 3. Not a plan; a possible outcome in 3–5 years *if* data and distribution materialize. The actionable version today: build the corpus, publish the work, get hired into the industry the acquirers live in. Being inside trust & safety at a platform company teaches what those teams actually buy — that knowledge is worth more than any pitch deck written from outside.

## 6. 90-day milestone plan

| Weeks | Milestone | Done looks like |
|---|---|---|
| 1–2 | Public surface | Demo live; repo public-or-not decision made; one LinkedIn write-up on the doctrine (the skill docs are the draft) |
| 3–6 | Proof of work | 3 narrative case studies published (Wauna / bridge scare / Uline); each ends with the audit record, not adjectives |
| 7–10 | Data moat seed | Capstone evaluation set v1: 60+ labeled claims with provenance metadata, versioned and citable |
| 11–12 | The decision | Consulting landing page (Path A) **or** full job-market push using the framework as portfolio (Path C-employment). Pick one; kill criteria: if no inbound consulting interest by week 12, the consulting path pauses and the framework stays a career asset |

**Engineering explicitly deferred:** the automated collection layer (biggest gap, biggest cost) waits until the corpus exists — building intake automation for a tool with no users is premature optimization.

## 7. Guardrails

1. **Do not quit the day job.** The framework is a career asset first, a product second, a company maybe never. The job hunt stays the priority.
2. **No invented traction.** Never describe plans as users, pilots, or revenue — in writing, in pitches, or on LinkedIn. The credibility this project sells is honesty about evidence; faking traction destroys the only real asset.
3. **Keep IP clean.** Apache-2.0, copyright headers, no employer IP entangled (the framework was built independently; keep it that way).
4. **Kill criteria are features.** The week-12 decision exists so this does not become a zombie project. A clean "not yet" beats a slow bleed.
5. **Skill-building stays skill-building.** The framework work is practice and portfolio. Do not let product fantasy distort the capstone: the degree comes first, and the capstone's evaluation set is valuable *because* it is rigorous, not because it might make money.
