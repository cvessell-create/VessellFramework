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

**The method, turned on the research itself.** On September 30, while verifying this section's arXiv references, the analyst searched the literal string "Jonathan Castillo," found nothing, and reported no such author — handing the identification work back to the user. A negative existential ("no such paper exists"), operationalized after a single unwitnessed search path. The user photographed his screen: the paper was there all along — "Inductive Diagrams for Causal Reasoning" by Jonathan **Castello**, Patrick Redmond, and Lindsey **Kuper** (arXiv:2307.10484). One letter off, and one letter wrong. The analyst held two correct co-author names and never searched them.

The miss maps onto Section 2 exactly: a provenance failure (the negative result kept its value — "zero hits" — while its lineage, "one literal spelling checked," was discarded); automation misuse (the search tool's output treated as authoritative); a causal-path failure (the claim traveled one unwitnessed path; the witnessed paths — spelling variants, co-author cross-check — were never walked). It was corrected the way Section 4 prescribes: by supersession, not erasure — the miss stays in this record — and by propagation into the framework itself, which now gates every negative finding until two independent search paths corroborate the absence, with each attempted path recorded as the claim's provenance (`vessell/verify.py`: `record_search_path()`, `gate_negative_finding()`).

This paper was therefore written the way it prescribes. The framework under construction on GitHub was the instrument that verified the paper's own citations; the paper's Section 4 rewrite drove the framework's newest mechanisms; and when the method caught its own analyst, the catch became part of both. The case study is the doctrine and the demonstration.

---

## 2. What happened, in the language of the field

This was not an exotic failure. Four established literatures describe exactly what occurred, and each names a piece of the prevention. Redescribed in the causal-order language this paper adopts in Section 4, every one of them is a failure of witnessed paths — information moving, or failing to move, along routes nobody recorded. That redescription is what makes Section 4 the direct answer to Section 2, mechanism by mechanism.

### 2.1 Provenance failure at intake

The claim entered the system without machine-usable provenance: no recorded source tier, no corroboration state, no expiry, no link between the caveat ("not independently verified") and the constraint it became. In data-provenance terms, the system kept the *value* and discarded the *lineage*. A claim without provenance is indistinguishable from a fact to every process downstream of intake — which is precisely what happened. In Section 4's terms, the claim traveled downstream along paths with no witness: the intake edge — the single most load-bearing event in the claim's history — was the one event nobody recorded.

**Prevention:** every claim is tagged at intake with source, source tier, date, and corroboration state. An untagged claim can never become an operational constraint. (Framework: `intake_claim()` — status `UNVERIFIED` unless the source is a tier-1 official record.)

### 2.2 Automation misuse: overreliance on the system's own output

Parasuraman and Riley (1997), in the foundational treatment of human-automation interaction, define **misuse** as *overreliance on automation* — failures of monitoring and decision bias that follow when operators trust automated cues at the expense of disconfirming evidence ("Humans and Automation: Use, Misuse, Disuse, Abuse," *Human Factors*, 39(2)). The mechanism transfers directly: each component of this system (goal file, hunt, editions, memory) treated the stored constraint as vetted output rather than as an unexamined input. The caveat written on September 24 was the disconfirming evidence. Nobody — human or process — was positioned to see it, because no process was assigned to re-examine stored claims.

**Prevention:** consequential uses of a claim require corroboration or a *named, dated, explicit waiver* — never silent trust. (Framework: `gate_for_use(record, stakes="consequential")`, `record_waiver()`.) Silent trust is an unwitnessed causal edge: information flowing with no path anyone can audit.

### 2.3 Data cascade

Sambasivan et al. (2021), studying high-stakes AI practice, define a **data cascade** as *"compounding events causing negative, downstream effects from data issues, that result in technical debt over time"* ("'Everyone wants to do the model work, not the data work': Data Cascades in High-Stakes AI," Proc. CHI 2021). Their findings map point for point: the issue originated upstream (intake), was **opaque in diagnosis** (nothing looked wrong — the constraint was neatly written everywhere), and its costs compounded the longer it ran (six days of a narrowed job search; every edition built on it). Cascades, they note, are rarely fixed by better models — only by better data work.

**Prevention:** treat claim quality as the load-bearing work. Corroboration thresholds before operational use; periodic re-validation of consequential claims, because claims decay. A cascade is causal propagation along many unwitnessed paths at once — which is why the correction must be broadcast along every one of them (Section 4, rule 5).

### 2.4 The belief-revision problem

When the disavowal arrived, the real work was not changing one belief — it was finding *every belief that depended on it*. Artificial intelligence named this problem in 1979. Doyle's **Truth Maintenance System** maintains propositions together with their **justifications**; each node is IN (believed) or OUT (retracted), and retracting a premise triggers **dependency-directed backtracking**: the retraction propagates to every dependent whose justification has become invalid (Doyle, "A Truth Maintenance System," *Artificial Intelligence*, 12(3), 1979; de Kleer's assumption-based generalization, 1986). The manual correction on September 30 — enumerating the three cron configs, the goal file, and memory, and updating each — was dependency-directed backtracking performed by hand. A TMS justification is a witnessed path: the recorded route by which a premise supports a belief. Dependency-directed backtracking is propagation along those paths — the manual version of what Section 4, rule 5 makes structural.

**Correction, made structural:** a dependents registry. Every operational use of a claim registers itself; disavowal returns the complete list of artifacts requiring update. (Framework: `register_dependent()`, `propagate_correction()`.) Retraction becomes an operation, not a scavenger hunt.

### 2.5 Tradecraft violation

The subject's own field has a doctrine for this. Intelligence Community Directive 203 (ODNI, revalidated January 2015) sets nine analytic tradecraft standards, three of which this incident violated directly:

1. **Properly describe the quality and credibility of underlying sources** — a single self-report of unknown provenance drove consequential decisions.
2. **Properly express and explain uncertainties** — the one uncertainty label that existed was dropped in transmission.
3. **Properly distinguish between underlying information and analysts' assumptions and judgments** — an intake note hardened into a system constraint with no judgment step in between.

ICD 203 exists because the Intelligence Community learned — at high cost — that these are not stylistic preferences. They are the difference between a system that knows what it knows and one that merely repeats what it stored.

The framework implements these standards as code rather than as aspiration: the corroboration gate cites ICD 203 in its docstrings (`vessell/verify.py`, `vessell/provenance.py`), and the propagate-and-verify mechanism cites the Intelligence Community's own recall procedures (ICPM-2020-200-01) — tradecraft rules, executable, with the citations traveling in the code. Section 4 shows how each rule is used.

---

## 3. The framework answer: what was built

Two frameworks are in play in this paper, and this section is where their relationship has to be made explicit — because the back-and-forth between them is the method of the research.

The first is the cited authors' framework: Castello, Redmond, and Kuper's causal separation diagrams. The Section 2 diagnosis was performed through that lens, and Section 4 is that lens operationalized — every failure in Section 2 is redescribed as a broken or unwitnessed causal path, and every rule in Section 4 is a rule about which paths information may follow. When this paper says "silent trust is an unwitnessed causal edge," that is the diagrams' central claim — a causal relationship exists only where a path witnesses it — applied to an intake note.

The second is the framework under construction on GitHub through the entire research period. The paper was not written and then implemented; the two were developed against each other. The code was the instrument that checked the paper, and the paper was the specification that drove the code. The Section 4 references were verified under the framework's own corroboration discipline — which is how the analyst's miss in Section 1 surfaced. And the Section 4 rewrite drove new code in the other direction: corrections now carry `causal_path` (the witnessed path from the originating claim), dependents register `via` paths, and `deliver_correction()` refuses out-of-order application — the causal-broadcast guarantee of Redmond et al. (2022) as an executable check.

That loop — write the rule, build the mechanism, turn both on your own work, keep the miss in the record — is the interaction of the research. Each mechanism below answers one failure from Section 2, and each was tested against this paper's own production:

| Failure (Section 2) | Mechanism | Behavior |
|---|---|---|
| Provenance failure at intake | `intake_claim()` | Every claim tagged with source, tier, date; status `UNVERIFIED` by default |
| Silent hardening | `add_corroboration()` | `CORROBORATED` only at 2+ independent roots (shared-root discount applied) or one official record |
| Automation misuse | `gate_for_use()` | Consequential use blocked unless `CORROBORATED` or a named, dated waiver is recorded |
| Opaque cascade | Status attachment | `UNVERIFIED` status travels with the claim; low-stakes use permitted but labeled |
| Manual retraction hunt | `register_dependent()` (with `via` witnessed path) / `propagate_correction()` + `deliver_correction()` (causal-order delivery) / `confirm_dependent_update(..., correction_id=...)` (ordering-violation guard) | The TMS dependents registry with causal broadcast: each dependent records how the claim reached it; corrections are delivered along every dependency path in causal order, and out-of-order application raises `CausalOrderingError` instead of being silently marked complete |
| Erasure vs. correction | `disavow()` | Original kept, marked `DISAVOWED`, never deleted; correction record links `supersedes` → original and carries `causal_path` — the witnessed path from the originating claim; full audit trail |
| Unwitnessed negative findings | `record_search_path()` / `gate_negative_finding()` | "No X exists" stays `UNVERIFIED` until two independent search paths corroborate the absence; the analyst's search history is the witnessed path |

The September 30 incident is the module's worked example, in its docstring and its test suite: intake → gate blocks operational use → (in the real incident, no gate existed, so the claim went operational) → disavowal → propagation list → verified correction.

---

## 4. Prevention and correction: a causal-order playbook

For people and teams, not just code. The incident was a concurrent system: intake, hardening, disavowal, and correction were events, and the failure was a failure of causal order. Leslie Lamport defined the terms in 1978: in a distributed system, event *a* happens-before event *b* (written *a → b*) when information could have flowed from *a* to *b* — and correct reasoning about the system must respect that order. Castello, Redmond, and Kuper (2024) sharpened the idea into something enforceable: in their causal separation diagrams, a causal relationship is not an abstract ordering but is *witnessed by the path that information follows* between events — happens-before modeled as paths, mechanized in Agda. And Redmond, Shen, Vazou, and Kuper (2022) proved, machine-checked, that a causal broadcast protocol can guarantee messages are never delivered in an order violating causality. The playbook below is that theory operationalized: every rule is a rule about causal paths — which events may follow which, and what must travel the path between them. This playbook was reformed the way the paper was researched: each rule had to be enforceable in the framework on GitHub, and each framework mechanism had to answer a failure named in Section 2. Two rules are additionally grounded in published intelligence tradecraft — cited in the framework's code and cited here as used.

1. **Tag at intake, or it didn't happen.** Source, tier, date, corroboration state — recorded with the claim, not beside it. In causal terms, the intake event anchors the claim's history, and every downstream event must be causally after (*→*) it. An untagged claim has no causal anchor, so nothing may follow from it: it constrains nothing.
2. **Corroborate before operationalizing.** One source is a lead, not a constraint. A consequential decision must be causally after corroboration — two independent roots or an official record — because only corroboration completes a witnessed path from evidence to decision. The framework's verification doctrine already applies this bar to news claims; claims about people deserve no less. This is also codified tradecraft: ICD 203, the Intelligence Community's analytic standards, requires analysts to describe the quality and credibility of underlying sources and to express and explain uncertainties (Office of the Director of National Intelligence, 2015) — the standard the framework's corroboration gate implements as code.
3. **Waivers are explicit or they don't exist.** If urgency demands acting on an unverified claim, the waiver is itself an event on the causal path: record who accepted the risk, when, and why. Silent trust is an *unwitnessed* causal edge — information flowing with no path anyone can audit — which is exactly the Section 2.2 failure.
4. **Disavow by supersession, never by erasure.** The correction event is causally after the claim it corrects, and the *supersedes* link is the witnessed path between them — the route the correction must travel to reach every dependent. Erasure destroys the path: with no recorded route from claim to correction, the claim can re-enter later through the same door, unwitnessed. *Operate in law and order: the record shows what was believed, when, and on what basis — including the correction.*
5. **Propagate, then verify.** Deliver the correction along every dependency path, in causal order, and confirm receipt at each dependent. This is causal broadcast: no dependent applies a correction for a claim it never received, and no dependent keeps acting on a claim after its retraction without receiving the retraction. Redmond et al. proved the delivery guarantee machine-checked; the framework's dependents registry is the same guarantee in miniature — enumerate every path the claim's information followed, walk each one with the correction, and verify. A correction that misses one dependent is a cascade waiting to resume. The Intelligence Community's own recall procedures require that revision or recall notices go to all recipients of the original product (ICPM-2020-200-01; Office of the Director of National Intelligence, 2020) — propagate, then verify, as institutional procedure.
6. **Re-validate consequential claims on a schedule.** Claims decay; sources change; people's circumstances change. Lamport's clock condition showed causal relationships can be reified as data — logical clocks make "happened before" visible to the system itself. Claim versions and status timestamps are the same move: reify the claim's causal history as data, so staleness is detectable rather than assumed away. What was true at intake is not true by default six months later.

---

## 5. Why this matters beyond one job search

The pattern generalizes to every domain where systems act on stored claims about people: hiring filters, fraud investigations, watchlists, eligibility determinations, intelligence databases. In each, the failure mode is identical — an unverified or stale claim hardens into a constraint, propagates silently along unwitnessed paths, and resists correction because no registry links the claim to its dependents. The harm compounds with the stakes, exactly as the data-cascade literature predicts.

The fix is correspondingly general: **provenance at intake, corroboration before operational use, explicit waivers, supersession-based correction, and dependency-tracked propagation** — each rule a constraint on causal paths, each mechanism executable as code. That is what the framework now implements, and this incident — real, dated, fully documented — is the proof that the mechanism is not theoretical.

And the method of this paper generalizes with it: doctrine and code developed against each other, each tested by the other, with the misses kept in the record. Write the rule, build the mechanism, turn both on your own work. That loop is the template — for a graduate project, for a team, for anyone whose system acts on claims about people.

---

## References

- Castello, J., Redmond, P., & Kuper, L. (2024). Inductive diagrams for causal reasoning. arXiv:2307.10484 [cs.PL]. https://arxiv.org/abs/2307.10484
- de Kleer, J. (1986). An Assumption-Based Truth Maintenance System. *Artificial Intelligence*, 28, 127–162.
- Doyle, J. (1979). A Truth Maintenance System. *Artificial Intelligence*, 12(3), 231–272.
- Lamport, L. (1978). Time, clocks, and the ordering of events in a distributed system. *Communications of the ACM*, 21(7), 558–565. https://doi.org/10.1145/359545.359563
- Office of the Director of National Intelligence. (2015). *Intelligence Community Directive 203: Analytic standards.* https://donohueintellaw.ll.georgetown.edu/sites/default/files/assets/ICD%20203%20Analytic%20Standards.pdf
- Office of the Director of National Intelligence. (2020). *Intelligence Community policy memorandum 2020-200-01: Standards and procedures for revised or recalled intelligence products.* https://www.dni.gov/files/documents/ICPM/ICPM-2020-200-01-Redacted.pdf
- Parasuraman, R., & Riley, V. (1997). Humans and Automation: Use, Misuse, Disuse, Abuse. *Human Factors*, 39(2), 230–253. https://journals.sagepub.com/doi/10.1518/001872097778543886
- Redmond, P., Shen, G., Vazou, N., & Kuper, L. (2022). Verified causal broadcast with Liquid Haskell. arXiv:2206.14767 [cs.PL]. https://arxiv.org/abs/2206.14767
- Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data Cascades in High-Stakes AI. In *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems*. https://dl.acm.org/doi/abs/10.1145/3411764.3445518
- VessellFramework: `vessell/provenance.py` (claim lifecycle), `vessell/verify.py` (verification doctrine), `docs/grad-school-prospectus.md`, `docs/commercialization-strategy.md`.
