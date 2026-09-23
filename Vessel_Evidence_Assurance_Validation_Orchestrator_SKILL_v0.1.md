---
name: vessel-evidence-assurance-validation-orchestrator
description: >
  Use as the mandatory assurance wrapper around substantive VesselFramework analyses,
  domain skills, forecasts, policy products, framework revisions, executable changes,
  and new skill creation. It forces every consequential output to carry an auditable
  evidence base, claim-evidence trace, alternative/disconfirmation check, test or
  validation status, confidence ceiling, residual uncertainty, and feedback record.
  It is not a substitute for the domain skill; it verifies what the domain skill is
  justified in claiming.
---

# VesselFramework Evidence Assurance & Validation Orchestrator
## Version 0.1 — Research Candidate

## Status

**Skill status:** RESEARCH CANDIDATE / META-ASSURANCE LAYER / PILOT REQUIRED  
**Authority:** Subordinate to Operator Protection/Harm Gate and canonical
VesselFramework doctrine; superior to domain-skill claims when evidence assurance
is weaker than the domain skill's conclusion.  
**Runtime state:** File creation is not installation or synchronization.

# 1. Why This Exists

A plausible analysis is not an evidence-based product.

A passing test is not validation.

A source list is not provenance.

A skill that produces the expected answer on the case that inspired it may be
overfit to that case.

The Orchestrator exists to force a repeatable evidence-and-validation package
around every substantive use of VesselFramework.

Core rule:

`NO MATERIAL CLAIM WITHOUT TRACEABLE SUPPORT OR AN EXPLICIT HYPOTHESIS LABEL`

Operational objective:

`QUESTION
 -> REQUIREMENT
 -> EVIDENCE
 -> PROVENANCE
 -> CLAIM
 -> ARGUMENT
 -> ALTERNATIVES
 -> TEST
 -> RESULT
 -> CONFIDENCE
 -> DECISION
 -> OUTCOME
 -> FEEDBACK
 -> HARDENING`

# 2. Research Basis

This skill synthesizes several external assurance traditions while keeping them
attributed and bounded.

## ODNI ICD 203 — Analytic Standards
Adopt:
- source quality and credibility;
- uncertainty;
- distinction among intelligence/information, assumptions, and judgments;
- alternatives;
- customer relevance;
- logical argumentation;
- supporting and contrary information;
- explanation of changes to previous judgments.

## UK All-Source Intelligence Assessment Framework
Adopt:
- customer requirement first;
- source evaluation;
- robust analytical audit trail;
- evidence-and-reason judgment;
- falsifiable hypotheses;
- probability separated from analytical confidence;
- structured challenge;
- explicit unresolved disagreement.

## NIST Assurance Case
Adopt:
- important conclusions should be expressible as claims supported by a reasoned,
  auditable argument, underlying evidence, and explicit assumptions.

This becomes the internal **Claim-Argument-Evidence (CAE) record**.

## NIST Security-Control Assessment
Adopt:
- define assessment objectives;
- identify determination statements;
- select assessment methods and objects;
- tailor assessment depth to risk;
- evidence collection should support an objective determination, not merely document
  that a control or process exists.

## NIST AI RMF / TEVV
Adopt:
- Test, Evaluation, Verification, and Validation are distinct assurance activities;
- measurements, methods, tools, test sets, and deployment-relevant conditions should
  be documented;
- evaluation should include independent or non-developer review when risk warrants it;
- production behavior should be monitored after initial evaluation.

## NIST TEVV-Athlon (2026 draft)
Use as a research input, not settled doctrine:
- evaluation should be purpose-specific and customizable;
- testing events and tools should generate evidence tied to measurement concepts;
- assess real-world impact/outcome, not merely laboratory behavior.

## GAO Evidence-Based Policymaking
Adopt:
- plan for results;
- assess and build evidence;
- use evidence;
- create continuous learning and improvement.

# 3. Governing Order

1. Operator Protection / Harm Gate
2. Evidence Assurance / Provenance Firewall
3. Canonical VesselFramework doctrine
4. Evidence Assurance & Validation Orchestrator
5. Forensic Framework Auditor / Adaptive Hardening
6. Domain skill
7. Executable reference
8. Calibration and continuity records

If a domain skill claims HIGH confidence but the evidence package supports only
LOW or MODERATE, the lower assurance ceiling governs.

# 4. Trigger Conditions

Run this wrapper for:

- substantive analytical reports;
- intelligence assessments;
- policy recommendations;
- cybersecurity control comparisons;
- forecasts;
- OSINT assessments;
- framework changes;
- new skills;
- skill revisions;
- executable/reference-code changes;
- claims of validation;
- academic/professional products where evidence matters;
- consequential operational recommendations.

A lightweight mode may be used for low-stakes study explanations, but the core
claim/evidence distinction remains mandatory.

# 5. Assurance Modes

## RAPID
Use for ordinary study/research tasks.

Minimum:
- decision/question;
- 3-5 material claims;
- sources;
- claim-evidence links;
- assumptions;
- principal alternative;
- confidence;
- unresolved gaps.

## STANDARD
Default for research, academic, professional, and skill-generated products.

Includes:
- Evidence Dossier;
- provenance map;
- CAE matrix;
- alternative/disconfirmation matrix;
- confidence basis;
- validation/test status;
- residual-risk/gap statement;
- audit trail.

## HIGH ASSURANCE
Use for framework promotion, consequential recommendations, strong allegations,
external publication, security/financial/legal/reputational significance, or
claims of validated framework performance.

Adds:
- independent challenge/reviewer where feasible;
- analogous-case testing;
- out-of-sample or pre-registered test where applicable;
- reproducibility package;
- doctrine-conformance check;
- external validation attempt;
- monitoring plan;
- rollback/reversal criteria.

# 6. Phase A — Decision Requirement

Record:

```text
ASSURANCE INTAKE
Run ID:
Date/time:
Operator question:
Decision/customer:
Domain:
Skill(s) invoked:
Desired output:
Consequence of error:
Time horizon:
Evidence cutoff:
Assurance mode:
Success criterion:
```

Do not begin by searching for support for a preferred conclusion.

Translate the question into a testable requirement.

# 7. Phase B — Evidence Dossier

Every STANDARD/HIGH-ASSURANCE run creates an Evidence Dossier.

For each evidence item record:

```text
EVIDENCE ITEM
Evidence ID:
Claim(s) supported:
Description:
Source:
Author/organization:
Date/version:
URL/file reference:
Source type:
  primary / secondary / derivative / internal / experimental
Status:
  SOURCE-ESTABLISHED
  FRAMEWORK SYNTHESIS
  WORKING HYPOTHESIS
  ILLUSTRATIVE
Provenance parent:
Independence:
  ESTABLISHED / DEPENDENT / UNRESOLVED / CONFLICTING
Directness:
  direct / indirect
Timeliness:
Strengths:
Limitations:
Contrary evidence:
Last verified:
```

Rules:
- search result snippets are leads, not final evidence when a primary source is available;
- source prestige does not establish relevance;
- repeated derivative reporting is one lineage until proven otherwise;
- current claims require current evidence;
- a framework document is evidence about the framework, not external proof that the
  framework works.

# 8. Phase C — Provenance Firewall

Before evidence can increase confidence:

1. resolve source lineage;
2. identify shared roots;
3. quarantine unresolved/cyclic/conflicting lineage where material;
4. distinguish independent corroboration from repetition.

If material lineage is unresolved:

`ASSURANCE STATUS: INDETERMINATE ON INDEPENDENCE`

Do not count quantity of citations as quantity of independent evidence.

# 9. Phase D — Claim Inventory

Extract every material claim from the draft/output.

Classify each claim:

- FACT / OBSERVATION
- SOURCE CLAIM
- ANALYTICAL JUDGMENT
- ASSUMPTION
- CAUSAL CLAIM
- COMPARATIVE CLAIM
- FORECAST
- RECOMMENDATION
- VALIDATION CLAIM
- RUNTIME/STATE CLAIM

Each type has a different evidence burden.

Examples:
- "The file exists" requires direct observation.
- "The control is effective" requires effectiveness evidence.
- "This skill generalizes" requires cross-case performance.
- "This framework predicts" requires prospective forecasting results.
- "This version is installed" requires runtime write + post-write verification.

# 10. Phase E — Claim-Argument-Evidence (CAE) Matrix

For every material claim produce:

```text
CLAIM ID:
Claim:
Claim type:
Why it matters:
Supporting evidence IDs:
Contrary evidence IDs:
Argument linking evidence to claim:
Explicit assumptions:
Alternative explanation:
Evidence gap:
Testable/falsifiable:
Confidence:
Confidence ceiling:
Release status:
```

Allowed release statuses:
- SUPPORTED
- SUPPORTED WITH CAVEAT
- HYPOTHESIS ONLY
- INDETERMINATE
- NOT SUPPORTED
- BLOCKED FROM RELEASE

A claim with no evidence and no hypothesis label fails assurance.

# 11. Evidence-to-Claim Limit Rules

## Presence Rule
Evidence that something exists proves existence, not operation/effectiveness.

## Operation Rule
Evidence of operation proves activity, not desired outcome.

## Correlation Rule
Association does not establish causation.

## Authority Rule
A standard establishes guidance/requirements, not that a specific organization
implements them effectively.

## Case Rule
One successful case does not establish generalization.

## Test Rule
A test establishes only what its design actually measures.

## Model Rule
A model-generated explanation is not source-established evidence.

## Citation Rule
A citation supports only the proposition actually contained in that source.

## Runtime Rule
Packaged state is not installed/runtime state.

# 12. Phase F — Alternatives and Disconfirmation

For every major judgment, identify:

- focal explanation;
- strongest plausible alternative;
- evidence favoring each;
- evidence expected if each were true;
- missing discriminator;
- disconfirming evidence;
- what would change the judgment.

Do not create weak straw alternatives.

For high-impact/low-probability alternatives, record implications separately from
likelihood.

# 13. Phase G — Test, Evaluation, Verification, Validation

Use these terms separately.

## TEST
Does a component or claim behave under specified conditions?

## EVALUATION
How well does it perform against defined criteria?

## VERIFICATION
Was it built/implemented according to its specified requirements or doctrine?

## VALIDATION
Does it actually meet the intended real-world need in the relevant context?

A skill may be VERIFIED against doctrine but not VALIDATED in practice.

A framework may pass regression tests but remain externally unvalidated.

A forecast may be structurally valid but uncalibrated.

# 14. Validation Ladder

Use the strongest justified state only.

`L0 — ASSERTED`
Claim exists; no meaningful supporting test.

`L1 — INTERNALLY COHERENT`
Reasoning/code is self-consistent.

`L2 — DOCTRINE-CONFORMANT`
Skill/output matches governing framework requirements.

`L3 — REGRESSION-TESTED`
Known failure mode is reproducibly blocked.

`L4 — ANALOGOUS-CASE TESTED`
Works on materially different cases not used to create the rule.

`L5 — OUT-OF-SAMPLE / PROSPECTIVE TESTED`
Test was specified before outcome or on held-out cases.

`L6 — INDEPENDENTLY CHALLENGED`
A reviewer/process independent of the original construction tested the claim.

`L7 — EXTERNALLY VALIDATED`
Independent real-world evidence supports intended performance across relevant conditions.

Do not skip levels by rhetoric.

# 15. Anti-Overfitting Test for Every Skill

Before promotion ask:

1. What case inspired the skill?
2. Which rules were derived from that case?
3. Can the skill produce a different conclusion on a materially different case?
4. What input would cause the focal conclusion to reverse?
5. Has the skill been tested where its preferred answer is wrong?
6. Does it contain embedded assumptions that guarantee the original answer?
7. Does it duplicate the Master or another skill?
8. Does the skill survive cross-domain transfer?
9. What observable failure would show the skill should be revised or retired?

If the skill cannot generate a result contrary to its originating case when
evidence warrants it, classify:

`OVERFIT / NON-DISCRIMINATING`

# 16. Framework Hardening Integration

When a run exposes a defect:

`OBSERVE
 -> REPRODUCE
 -> LOCATE LAYER
 -> CLASSIFY DEFECT
 -> EVIDENCE PACKAGE
 -> MINIMAL PATCH
 -> REGRESSION TEST
 -> ANALOGOUS TEST
 -> DOCTRINE-CONFORMANCE TEST
 -> HARM CHECK
 -> PROMOTE / REVERT
 -> VERSION`

Every hardening event records:
- defect ID;
- triggering case;
- evidence;
- root cause;
- affected artifacts;
- minimal repair;
- regression test;
- analogous test;
- new failure introduced;
- final disposition.

A patch that only solves the trigger case remains local until broader testing.

# 17. Skill Promotion Integration

Every candidate skill must carry an Evidence Product Record:

```text
SKILL EVIDENCE PRODUCT
Skill:
Version:
Originating problem/case:
Research sources:
Provenance state:
Methods adopted:
Framework synthesis:
Assumptions:
Known limitations:
Normal-case tests:
Negative-case tests:
Reversal case:
Analogous cases:
Doctrine conformance:
Independent challenge:
Calibration state:
Validation level:
Open defects:
Promotion recommendation:
```

Promotion states:
- RESEARCH CANDIDATE
- DRAFT
- PILOT
- REGRESSION-PASS
- ANALOGOUS-PASS
- CALIBRATION-PENDING
- PROMOTED
- HOLD
- MERGE
- RETIRE

# 18. Reproducibility Package

For HIGH-ASSURANCE work preserve enough information that another analyst could
understand or rerun the analysis:

- exact question;
- source set/evidence cutoff;
- source versions/URLs/file refs;
- method/skill versions;
- relevant parameters;
- inclusion/exclusion rules;
- calculations/code if used;
- intermediate evidence table;
- claim matrix;
- tests;
- result;
- revisions;
- date/time.

Reproducibility does not guarantee correctness; it makes errors inspectable.

# 19. Independent Challenge Rule

When consequence warrants it, obtain challenge that is meaningfully independent
of the original construction.

Acceptable challenge can include:
- separate analyst;
- alternative model/process with independently specified instructions;
- blind/held-out case;
- adversarial test designed after the claim but before seeing the result;
- external reviewer;
- authoritative benchmark.

A second run of the same prompt on the same evidence is not automatically an
independent validation stream.

# 20. Confidence Model

Confidence is based on:
- source quality;
- source independence;
- directness;
- completeness;
- consistency;
- alternative discrimination;
- test quality;
- deployment/context match;
- recency;
- reproducibility.

Do not mechanically average these factors.

Report:
- probability/likelihood if applicable;
- analytical confidence;
- validation level;
- material gaps.

Example:

`Judgment: endpoint control is preferred in this specified case.`
`Confidence: MODERATE.`
`Validation: L4 analogous-case tested.`
`Gap: no organization-specific performance data.`

# 21. Product Release Gate

A STANDARD/HIGH-ASSURANCE product cannot be finalized until:

- material claims are inventoried;
- citations actually support those claims;
- provenance is resolved or caveated;
- contrary evidence is addressed;
- alternative explanation is considered;
- assumptions are visible;
- confidence is bounded;
- validation language matches actual validation;
- current-state claims are verified;
- consequence/Harm Gate is addressed;
- uncertainties and evidence gaps are stated.

If not:

`RELEASE STATUS: HOLD — ASSURANCE REQUIREMENTS NOT MET`

# 22. Evidence Product — Required Output

Every substantive Orchestrator run should end with an evidence product containing:

```text
EVIDENCE-BASED PRODUCT
1. Decision Question
2. Bottom Line / Judgment
3. Evidence Summary
4. Claim-Argument-Evidence Matrix
5. Provenance / Independence Status
6. Contrary Evidence
7. Principal Alternative
8. Assumptions
9. Test / Evaluation / Verification / Validation Performed
10. Validation Level
11. Analytical Confidence
12. Residual Gaps / Uncertainty
13. Decision / Recommendation (if authorized)
14. Indicators / Review Triggers
15. Audit Trail / Version
```

This is the minimum artifact that makes the product auditable rather than merely
persuasive.

# 23. Calibration and Outcome Feedback

After real-world resolution:

1. record outcome;
2. compare outcome to judgment/forecast/recommendation;
3. do not rewrite original claim;
4. diagnose failure or success;
5. determine whether evidence, method, assumptions, timing, or execution caused error;
6. update calibration;
7. create patch only if a reproducible defect exists.

For binary forecasts, use Brier scoring where appropriate.

For qualitative judgments, track:
- directionally correct/incorrect;
- confidence calibration;
- alternative missed;
- evidence gap materiality;
- decision usefulness.

# 24. Stale-Evidence Trigger

Mark a product for review when:

- governing standard changes;
- key source is superseded;
- material new evidence appears;
- environment/architecture changes;
- original assumption no longer holds;
- validation context differs from deployment context;
- runtime skill version changes;
- a related patch modifies doctrine.

Use:

`CURRENT -> CHANGE SIGNAL -> REVIEW REQUIRED -> REVALIDATE -> CURRENT`

# 25. Evidence Debt

Track unresolved evidence obligations as **Evidence Debt**.

Examples:
- missing primary source;
- unresolved provenance;
- no negative test;
- no analogous case;
- no external validation;
- stale source;
- unverified runtime state;
- unknown outcome.

Evidence Debt must be visible in promotion/release decisions.

A growing evidence-debt backlog is a framework-health signal.

# 26. Assurance Dashboard

For each skill/framework component track:

| Field | State |
|---|---|
| Version | current candidate/runtime |
| Doctrine conformance | PASS/PARTIAL/FAIL/UNTESTED |
| Regression tests | count/status |
| Analogous tests | count/status |
| Prospective/out-of-sample tests | count/status |
| Independent challenges | count/status |
| External validation | status |
| Open defects | count/severity |
| Evidence debt | count/severity |
| Last evidence review | date |
| Runtime verified | YES/NO/DEGRADED |
| Promotion state | state |

This dashboard prevents "lots of files" from being mistaken for accumulated
evidence of performance.

# 27. Meta-Tests

T1 — Citation mismatch:
A source is real but does not support the claim. Expected: claim downgraded.

T2 — Ten derivative sources:
All copy one parent. Expected: one evidence lineage.

T3 — Attractive originating case:
Skill produces expected result. Expected: no generalization claim yet.

T4 — Reversal case:
Inputs should favor the opposite conclusion. Expected: skill reverses.

T5 — Code unit tests all pass:
Doctrine mapping absent. Expected: L1 only, not validation.

T6 — Skill works in cyber but fails policy:
Expected: transfer limit recorded, not hidden.

T7 — Standard superseded:
Expected: stale-evidence trigger.

T8 — Package file newer than runtime:
Expected: runtime status UNVERIFIED/DEGRADED.

T9 — Independent reviewer disagrees:
Expected: disagreement preserved and discriminator sought.

T10 — Real outcome contradicts high-confidence assessment:
Expected: calibration failure recorded and root cause reopened.

T11 — User requests fast answer:
Expected: RAPID mode, not abandonment of evidence labels.

T12 — Consequential recommendation with weak evidence:
Expected: Harm Gate blocks or limits action.

# 28. Anti-Bloat Rule

Do not turn every assurance check into a new skill.

This Orchestrator owns cross-cutting:
- evidence package;
- provenance;
- CAE;
- validation level;
- overfitting check;
- release gate;
- evidence debt;
- calibration handoff.

Domain skills own domain-specific reasoning.

The Forensic Auditor owns defect reconstruction and repair.

The Skill Creator owns creation/promotion of new skills.

The Orchestrator connects them.

# 29. Relationship to Existing VesselFramework Components

`DOMAIN SKILL`
produces analysis.

`EVIDENCE ASSURANCE ORCHESTRATOR`
asks whether the claims are justified and produces the auditable evidence product.

`FORENSIC FRAMEWORK AUDITOR`
investigates defects or suspicious framework behavior.

`SKILL CREATOR`
creates/changes skills based on demonstrated need.

`EXECUTABLE REFERENCE`
tests selected machine-checkable rules.

`CALIBRATION LOG`
records prospective/real-world performance.

`SYNC/STATE CONTROLS`
prove which artifact is actually live.

Together:

`DOCTRINE
 -> DOMAIN SKILL
 -> EVIDENCE PRODUCT
 -> ASSURANCE GATE
 -> DECISION/RELEASE
 -> OUTCOME
 -> CALIBRATION
 -> DEFECT?
 -> AUDITOR
 -> PATCH/SKILL CREATOR
 -> REGRESSION + ANALOGOUS TEST
 -> VERSION`

# 30. Source Register

External research basis for v0.1:
- Office of the Director of National Intelligence, ICD 203, Analytic Standards.
- UK Government, Professional Development Framework for All-Source Intelligence Assessment.
- UK Government, Explaining Uncertainty in UK Intelligence Assessment.
- NIST SP 800-160 Vol. 1 Rev. 1 / NIST assurance-case definition.
- NIST SP 800-53A Rev. 5, security and privacy control assessment procedures.
- NIST SP 800-171A Rev. 3, assurance-case approach to assessment evidence.
- NIST AI Risk Management Framework and AI Resource Center TEVV guidance.
- NIST AI 200-2 initial public draft, TEVV-Athlon Framework (2026); research input,
  not final normative authority.
- NIST ARIA Pilot Evaluation Report (2025), multi-level AI evaluation example.
- U.S. GAO, Evidence-Based Policymaking: Practices to Help Manage and Assess the
  Results of Federal Efforts (GAO-23-105460).

Internal basis:
- VesselFramework provenance firewall.
- evidence-status rules.
- doctrine/code/test hierarchy.
- Forensic Framework Auditor.
- adaptive hardening loop.
- stale-state correction.
- Skill Creator promotion gates.
- Forecaster prospective calibration rules.
- Harm Gate / Operator Protection.

# 31. Final Rule

**Every important VesselFramework output must be able to answer five questions:**

1. **What exactly are we claiming?**
2. **What independent, traceable evidence supports it?**
3. **What alternative or contrary evidence could defeat it?**
4. **What has actually been tested or validated, at what level?**
5. **What outcome or new evidence will force us to revise it?**

If those questions cannot be answered, the product may still be useful as a
hypothesis, but it is not yet an evidence-based validated product.
