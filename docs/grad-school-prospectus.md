# Capstone Prospectus — Automated Detection of Planted News and Hostile Information Spread Using Structured Verification

**Candidate:** Christopher R. Vessell
**Program:** M.S. in Strategic Intelligence, Saint Louis University (School for Professional Studies)
**Target completion:** Spring 2027
**Status:** Prospectus draft for advisor review — prepared September 30, 2026

---

## 1. Working title

*Deterministic Verification Doctrine for Detecting Manufactured News Spread: A Structured Analytic Method with an Executable Reference Implementation*

## 2. Research question

Can a deterministic, auditable set of verification rules reliably distinguish **manufactured information spread** (planted news) from authentic reporting at intake scale — and can it do so without black-box classification, such that every verdict reproduces byte-identically from its evidence?

Sub-questions:
1. Which spread-pattern indicators (synchronized publication bursts, text-clone armies, single-origin laundering, orphaned circulation) discriminate manufactured from authentic spread, and at what thresholds?
2. Does an independence discount — counting shared evidentiary roots once — materially change corroboration judgments versus naive source counting?
3. Where does a deterministic method honestly degrade (thin intake, missing timestamps), and can that degradation itself be a labeled output rather than a silent failure?

## 3. Background and literature

The project sits at the intersection of three literatures, all represented in the SLU curriculum:

- **Structured analytic techniques (SATs).** Heuer & Pherson's *Structured Analytic Techniques for Intelligence Analysis* establishes that analytic rigor comes from making reasoning explicit, checkable, and reproducible. This project operationalizes that principle: the verification doctrine is expressed as executable rules with audit records, not as analyst guidance alone. Directly extends coursework in INTL 5250 (Structured Analytical Techniques for Intelligence).
- **Information disorder and disinformation studies.** Wardle & Derakhshan's "information disorder" framework (Council of Europe, 2017) distinguishes mis-, dis-, and mal-information by intent and spread mechanics. This project takes the spread-mechanics half of that framework and asks which mechanics are machine-detectable from publication metadata and text alone.
- **OSINT verification tradecraft.** Practitioner literature (e.g., the *Verification Handbook*, European Journalism Centre) treats verification as corroboration across independent sources with provenance discipline. The method formalizes two practitioner rules that are usually informal: *an official record settles the question* and *ten outlets running one wire copy are one source, not ten*.

The contribution is not a new theory of disinformation. It is a **formalized, tested, executable method** for one slice of the problem — spread-pattern verification — with measured performance.

## 4. The method: VessellFramework `vessell/verify.py`

The candidate has built and tested the method as a Python package (VessellFramework, Apache-2.0, 99-test regression suite, type-checked and lint-gated). The capstone treats this implementation as the method under evaluation, not as a product pitch. Three components:

**4a. Corroboration check (`verify_claim`).** A claim plus its source sightings (each carrying a source tier, evidentiary root, publish time, wording excerpt, and official-record flag) is scored by tier-weighted independent roots:
- Tier weights: established source 1.00, framework synthesis 0.60, working hypothesis 0.35, illustrative 0.10.
- **Independence discount:** sightings sharing an evidentiary root (e.g., one wire copy) count once, at the strongest tier present.
- **Official-record rule:** an authoritative record (USGS event page, employer's own listing) settles the claim as VERIFIED; distribution is not manufacture.
- Verdict ladder: VERIFIED (official record, or ≥2 independent established roots) → CORROBORATED (score ≥ 0.60 across roots) → SINGLE_SOURCE → UNCORROBORATED → CONTRADICTED (established denial).

**4b. Hostile-spread analysis (`analyze_planted_news`).** Runs the corroboration check, then hunts spread indicators: synchronized low-tier bursts (≥4 outlets, near-identical text, inside a 90-minute window), text-clone armies (≥5 distinct sources, near-identical wording via difflib ≥ 0.92), single-origin laundering (every sighting traces to one non-established root), orphaned circulation (no official record and no established outlet), and established denial. Two or more hostile indicators (or an established denial) → LIKELY_PLANTED; one → SUSPECT; clean corroboration or an official record → AUTHENTIC; otherwise UNVERIFIABLE — "do not assert" is itself a verdict.

**4c. Evidence weighting (`vessell/weighter.py`).** A calibrated LLM-assisted weighter scores evidence on four auditable sub-factors (reliability, corroboration, directness, timeliness), combined deterministically in code, with confidence-scaled influence and versioned prompts stamped on every weight. Relevant as the framework's answer to "how much does each piece of evidence count" — the capstone evaluates the deterministic path (4a–4b); the weighter is documented as the hybrid extension.

**4d. Companion application: ghost-job filtering.** The same doctrine applied to job-posting fraud (`detect_ghost_job` / `filter_ghost_jobs`): identical posting text across ≥3 sources, ≥3 listing IDs, ≥60 days circulation, or claimed-posted dates ≥30 days later than first observation → LIKELY_GHOST. Included as a second evaluation domain showing the doctrine generalizes beyond news.

## 5. Evaluation plan

**Pilot (already built, in `tests/test_verify.py`):** 26 fixture-based tests, no network access, covering the Wauna M4.2 earthquake (USGS official record → AUTHENTIC; the worked example where suspicion was the error), a manufactured bridge-closure scare (synchronized burst + clone army + no primary → LIKELY_PLANTED), a laundering chain, and the Uline Operations Manager posting (identical text across 4 aggregator sightings, 60+ day circulation, freshness masking → LIKELY_GHOST). All verdicts reproduce byte-identically from stored sightings.

**Proposed capstone evaluation:**
1. **Labeled claim set.** Collect 60–100 real-world claims over Fall 2026 across local, national, and wire-driven stories. Ground truth established from official records (USGS, agency releases, primary documents) or established-outlet denial. Stratify: authentic-with-burst (the hard negative — real stories that *look* coordinated, e.g., the Wauna case), manufactured spread, single-source developing stories, orphaned claims.
2. **Metrics.** Precision/recall on LIKELY_PLANTED verdicts; false-positive rate on the authentic-with-burst stratum (the failure mode that matters); calibration of the corroboration score against analyst judgment; ablation study removing the independence discount to measure its contribution.
3. **Analyst-panel agreement.** A small panel (2–3 raters, e.g., faculty or practitioner contacts) independently judges a 30-claim subset; report module-vs-panel agreement and disagreement cases as findings, not as embarrassments.
4. **Ghost-job domain replication.** 30–50 job postings with known outcomes (verified live on employer sites vs. aged-out aggregator ghosts); report precision/recall of LIKELY_GHOST.

**Honest limitations (stated up front, not discovered at defense):** the method judges only the sightings it is given — intake quality bounds output; burst detection requires observed (never inferred) timestamps and degrades silently-with-a-label when they are absent; text clustering is English-tuned; there is no automated collection layer yet (intake is manual or fixture-driven). These are scope boundaries, not flaws to hide.

## 6. Timeline to Spring 2027

| Window | Milestone |
|---|---|
| Fall 2026 | Prospectus approval; literature review; evaluation-set collection begins (claims + postings with ground truth); method frozen at v0.2 |
| Late Fall 2026 | Evaluation runs; analyst-panel subset judged; ablation study |
| Early Spring 2027 | Write-up: method, results, limitations, disagreement cases |
| Spring 2027 | Defense/presentation; final artifact + audit records delivered |

Course sequencing (INTL 5961 / 5962 Intel Masters Research Project, or INTL 5960 Applied Research Project per catalog) to be confirmed with the advisor — the timeline above assumes the research-project course spans the final two terms.

## 7. Capstone fit

Per the SLU catalog, the M.S. culminates in an applied research project (INTL 5960, or the INTL 5961/5962 sequence): an original, applied analytic product demonstrating mastery of the intelligence cycle, structured techniques, and evidence-based judgment. This project delivers exactly that — an original method, implemented, tested, and evaluated against ground truth, with a written analysis of where it works and where it fails. No human subjects; all sources are public. No IRB requirement anticipated (advisor to confirm).

## 8. What the candidate needs from the advisor

1. Confirm the correct research-project course sequence and credit mapping for a Spring 2027 finish.
2. Scope check: is a 60–100 claim evaluation set appropriately sized, or should it be narrowed?
3. Introductions (if available) to 1–2 practitioner raters for the analyst-panel subset — newsroom verification desks or OSINT practitioners.
4. Any program constraints on publishing the method and evaluation openly (candidate intends open publication; currently private pending advisor input).

## 9. References (starting set)

- Heuer, R. J., & Pherson, R. H. *Structured Analytic Techniques for Intelligence Analysis.* CQ Press.
- Heuer, R. J. *Psychology of Intelligence Analysis.* Center for the Study of Intelligence, CIA.
- Wardle, C., & Derakhshan, H. (2017). *Information Disorder: Toward an Interdisciplinary Framework for Research and Policy Making.* Council of Europe.
- Silverman, C. (Ed.). *Verification Handbook.* European Journalism Centre.
- SLU Catalog — Strategic Intelligence, M.S. (School for Professional Studies): program requirements, INTL 5250, INTL 5270, INTL 5960/5961/5962.
- Vessell, C. R. (2026). VessellFramework v3.8.1 — method implementation and test suite (private repository; access available to advisor on request).
