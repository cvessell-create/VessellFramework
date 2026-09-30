# How an Unverified Sentence Became System Behavior — and How to Stop It

**A VessellFramework case study in claim provenance, correction propagation, and lawful correction**
*Christopher R. Vessell — September 30, 2026*

---

## 1. The incident, end to end

**September 24, 2026 — the first word.** An intake note recorded that the subject of a career-transition project "reports that federal hiring, security clearances, and Intelligence Community paths are all unavailable to him because he is 'blacklisted.'" The note itself carried a caveat: *treat that as his stated constraint, not an independently verified fact.* One sentence. One source. Explicitly unverified.

**September 24–29 — the hardening.** The caveat did not survive contact with the system. The maybe became a must:

- The project goal file encoded it as a hard constraint: *"No federal hiring and no clearance-required roles — user states blacklisted from all IC paths."*
- The nightly job hunt excluded federal, clearance, defense, and IC-pedigree employers.
- Both daily news editions carried the same exclusions in their job-matching rules.
- Long-term memory repeated it as settled fact.

No new evidence arrived at any point. The claim was never corroborated, never re-examined, never re-sourced. Each downstream process trusted the stored constraint because the system had stored it — and the system had stored it because an earlier process had written it down.

**September 29** — a second single-source directive ("done with the fraud shot") was layered on through the identical mechanism: one statement, immediately operationalized across the whole system, no corroboration step.

**September 30, 2026 — the disavowal.** The subject rejected the original claim outright: it came, he said, from "the start of an LLM thread" — *someone typing in 'I'm blacklisted,' that could have been someone else* — and was not his reality. Six days of narrowed job searching had rested on a sentence nobody could source.

**September 30 — the correction.** Done manually, under pressure:

1. Three scheduled-job configurations rewritten (hunt + both editions).
2. The goal file's constraints, description, and target families rewritten.
3. Long-term memory corrected, with the disavowal recorded as superseding — not erasing — the original note.
4. A new framework module (`vessell/provenance.py`) built so the failure mode becomes structurally impossible instead of manually repaired.

The manual correction worked. It also proved the point: **a system that cannot propagate a retraction to every dependent of a claim is a system that cannot correct itself.** Everything that follows is about making that structural.

---

## 2. What happened, in the language of the field

This was not a exotic failure. Four established literatures describe exactly what occurred, and each names a piece of the prevention.

### 2.1 Provenance failure at intake

The claim entered the system without machine-usable provenance: no recorded source tier, no corroboration state, no expiry, no link between the caveat ("not independently verified") and the constraint it became. In data-provenance terms, the system kept the *value* and discarded the *lineage*. A claim without provenance is indistinguishable from a fact to every process downstream of intake — which is precisely what happened.

**Prevention:** every claim is tagged at intake with source, source tier, date, and corroboration state. An untagged claim can never become an operational constraint. (Framework: `intake_claim()` — status `UNVERIFIED` unless the source is a tier-1 official record.)

### 2.2 Automation misuse: overreliance on the system's own output

Parasuraman and Riley (1997), in the foundational treatment of human-automation interaction, define **misuse** as *overreliance on automation* — failures of monitoring and decision bias that follow when operators trust automated cues at the expense of disconfirming evidence ("Humans and Automation: Use, Misuse, Disuse, Abuse," *Human Factors*, 39(2)). The mechanism transfers directly: each component of this system (goal file, hunt, editions, memory) treated the stored constraint as vetted output rather than as an unexamined input. The caveat written on September 24 was the disconfirming evidence. Nobody — human or process — was positioned to see it, because no process was assigned to re-examine stored claims.

**Prevention:** consequential uses of a claim require corroboration or a *named, dated, explicit waiver* — never silent trust. (Framework: `gate_for_use(record, stakes="consequential")`, `record_waiver()`.)

### 2.3 Data cascade

Sambasivan et al. (2021), studying high-stakes AI practice, define a **data cascade** as *"compounding events causing negative, downstream effects from data issues, that result in technical debt over time"* ("'Everyone wants to do the model work, not the data work': Data Cascades in High-Stakes AI," Proc. CHI 2021). Their findings map point for point: the issue originated upstream (intake), was **opaque in diagnosis** (nothing looked wrong — the constraint was neatly written everywhere), and its costs compounded the longer it ran (six days of a narrowed job search; every edition built on it). Cascades, they note, are rarely fixed by better models — only by better data work.

**Prevention:** treat claim quality as the load-bearing work. Corroboration thresholds before operational use; periodic re-validation of consequential claims, because claims decay.

### 2.4 The belief-revision problem

When the disavowal arrived, the real work was not changing one belief — it was finding *every belief that depended on it*. Artificial intelligence named this problem in 1979. Doyle's **Truth Maintenance System** maintains propositions together with their **justifications**; each node is IN (believed) or OUT (retracted), and retracting a premise triggers **dependency-directed backtracking**: the retraction propagates to every dependent whose justification has become invalid (Doyle, "A Truth Maintenance System," *Artificial Intelligence*, 12(3), 1979; de Kleer's assumption-based generalization, 1986). The manual correction on September 30 — enumerating the three cron configs, the goal file, and memory, and updating each — was dependency-directed backtracking performed by hand.

**Correction, made structural:** a dependents registry. Every operational use of a claim registers itself; disavowal returns the complete list of artifacts requiring update. (Framework: `register_dependent()`, `propagate_correction()`.) Retraction becomes an operation, not a scavenger hunt.

### 2.5 Tradecraft violation

The subject's own field has a doctrine for this. Intelligence Community Directive 203 (ODNI, revalidated January 2015) sets nine analytic tradecraft standards, three of which this incident violated directly:

1. **Properly describe the quality and credibility of underlying sources** — a single self-report of unknown provenance drove consequential decisions.
2. **Properly express and explain uncertainties** — the one uncertainty label that existed was dropped in transmission.
3. **Properly distinguish between underlying information and analysts' assumptions and judgments** — an intake note hardened into a system constraint with no judgment step in between.

ICD 203 exists because the Intelligence Community learned — at high cost — that these are not stylistic preferences. They are the difference between a system that knows what it knows and one that merely repeats what it stored.

---

## 3. The framework answer: what was built

`vessell/provenance.py` implements the prevention as code. Each mechanism answers one failure above:

| Failure (§2) | Mechanism | Behavior |
|---|---|---|
| Provenance failure at intake | `intake_claim()` | Every claim tagged with source, tier, date; status `UNVERIFIED` by default |
| Silent hardening | `add_corroboration()` | `CORROBORATED` only at 2+ independent roots (shared-root discount applied) or one official record |
| Automation misuse | `gate_for_use()` | Consequential use blocked unless `CORROBORATED` or a named, dated waiver is recorded |
| Opaque cascade | Status attachment | `UNVERIFIED` status travels with the claim; low-stakes use permitted but labeled |
| Manual retraction hunt | `register_dependent()` / `propagate_correction()` | The TMS dependents registry; disavowal yields the full update list |
| Erasure vs. correction | `disavow()` | Original kept, marked `DISAVOWED`, never deleted; correction record links `supersedes` → original; full audit trail |

The September 30 incident is the module's worked example, in its docstring and its test suite: intake → gate blocks operational use → (in the real incident, no gate existed, so the claim went operational) → disavowal → propagation list → verified correction.

---

## 4. Prevention and correction playbook

For people and teams, not just code. This is the operating procedure the incident implies:

1. **Tag at intake, or it didn't happen.** Source, tier, date, corroboration state — recorded with the claim, not beside it. An untagged claim constrains nothing.
2. **Corroborate before operationalizing.** One source is a lead, not a constraint. Consequential decisions require two independent roots or an official record — the same bar the framework's verification doctrine already applies to news claims.
3. **Waivers are explicit or they don't exist.** If urgency demands acting on an unverified claim, record who accepted the risk, when, and why. Silent trust is how §2.2 happens.
4. **Disavow by supersession, never by erasure.** Record who retracted, when, and why; keep the original marked `DISAVOWED`. Erasure destroys the audit trail and invites the claim to re-enter later through the same door. *Operate in law and order: the record shows what was believed, when, and on what basis — including the correction.*
5. **Propagate, then verify.** Enumerate every dependent of the retracted claim, update each, and confirm the update. A correction that misses one dependent is a cascade waiting to resume.
6. **Re-validate consequential claims on a schedule.** Claims decay; sources change; people's circumstances change. What was true at intake is not true by default six months later.

---

## 5. Why this matters beyond one job search

The pattern generalizes to every domain where systems act on stored claims about people: hiring filters, fraud investigations, watchlists, eligibility determinations, intelligence databases. In each, the failure mode is identical — an unverified or stale claim hardens into a constraint, propagates silently, and resists correction because no registry links the claim to its dependents. The harm compounds with the stakes, exactly as the data-cascade literature predicts.

The fix is correspondingly general: **provenance at intake, corroboration before operational use, explicit waivers, supersession-based correction, and dependency-tracked propagation.** That is what the framework now implements, and this incident — real, dated, fully documented — is the proof that the mechanism is not theoretical.

---

## References

- Office of the Director of National Intelligence. *Intelligence Community Directive 203: Analytic Standards* (revalidated January 2, 2015). https://www.dni.gov/files/documents/ICD/ICD-203.pdf
- Doyle, J. (1979). A Truth Maintenance System. *Artificial Intelligence*, 12(3), 231–272.
- de Kleer, J. (1986). An Assumption-Based Truth Maintenance System. *Artificial Intelligence*, 28, 127–162.
- Parasuraman, R., & Riley, V. (1997). Humans and Automation: Use, Misuse, Disuse, Abuse. *Human Factors*, 39(2), 230–253. https://journals.sagepub.com/doi/10.1518/001872097778543886
- Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. In *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems*. https://dl.acm.org/doi/abs/10.1145/3411764.3445518
- VessellFramework: `vessell/provenance.py` (claim lifecycle), `vessell/verify.py` (verification doctrine), `docs/grad-school-prospectus.md`, `docs/commercialization-strategy.md`.
