---
name: vessel-intelligence-briefing-policy
description: >
  Use when the operator needs to turn an ambiguous strategic, intelligence,
  cybersecurity, organizational, or policy problem into a decision-ready
  assessment, written brief, oral briefing, or policy-options product. The skill
  combines intelligence requirements and collection, structured analysis,
  evidence/provenance controls, briefing tradecraft, policy-option development,
  implementation thinking, and evaluation. It is subordinate to VesselFramework
  Evidence Assurance, Provenance Firewall, Harm Gate, Forensic Auditor, and
  internal-method disclosure rules.
---

# Vessel Intelligence, Briefing & Policy Skill
## Version 0.1 — Research Candidate

## Status

**Skill status:** RESEARCH CANDIDATE / PILOT REQUIRED  
**Authority:** Domain skill; subordinate to canonical VesselFramework doctrine.  
**Runtime:** File creation is not installation. Do not claim runtime synchronization
without an explicit write to the registered runtime path plus post-write verification.

## 1. Purpose

Convert information into decision support.

The skill integrates three professions that overlap but are not identical:

1. **Intelligence assessment** asks: What is happening, why, what may happen next,
   what is uncertain, and what does the decision-maker need to know?
2. **Briefing** asks: What does this customer need to understand now, in what order,
   with what evidence, uncertainty, implications, and anticipated questions?
3. **Policy analysis** asks: What should be done, what alternatives exist, what are
   their impacts/tradeoffs/feasibility, how could the preferred option be
   implemented, and how will results be evaluated?

**Boundary:** intelligence should inform policy choice without silently becoming
policy advocacy. Policy recommendations require an explicit policy task or operator
authorization.

## 2. Research Basis

### Intelligence assessment
**ODNI ICD 203 — Analytic Standards**
Adopt:
- objectivity;
- source quality and credibility;
- uncertainty communication;
- distinction among underlying information, assumptions, and judgments;
- alternatives;
- relevance to the customer;
- logical argumentation;
- product evaluation.

**UK Professional Development Framework for All-Source Intelligence Assessment**
Adopt:
- understand customer requirements and decisions;
- gather, organize, evaluate, and audit information;
- select appropriate analytic techniques rather than run them mechanically;
- probability judgments plus analytical confidence;
- assumptions and bias challenge;
- scenario/indicator monitoring;
- clear written/verbal communication;
- prepare for challenge;
- accessibility and audience adaptation.

**CIA Tradecraft Primer**
Adopt:
- structured analytic techniques as safeguards against complexity, ambiguity,
  incomplete information, and cognitive limitations.

**NATO AJP-2.1 intelligence-cycle concept**
Adopt:
- direction, collection, processing, dissemination as interacting activities;
- cycles may overlap and run concurrently rather than as a rigid conveyor belt.

### Briefing and communication
**UK All-Source Intelligence Assessment framework**
Adopt:
- customer-centered delivery;
- clear, succinct, plain-language assessment;
- uncertainty and confidence communication;
- visualization when useful;
- pre-brief/challenge preparation;
- confirmation that core messages were understood.

**CIA PDB briefer account**
Use as an illustrative professional workflow:
- rapidly master relevant finished intelligence/reporting;
- select what matters to the customer;
- pre-brief with subject-matter analysts;
- rehearse;
- compress a large information volume into a short decision-maker briefing.

**CDC Writing Briefs**
Adopt transferable communication principles:
- identify and research audience;
- define one obvious main purpose/message;
- choose brief type based on decision stage/evidence;
- organize information into scannable chunks;
- use visuals that reinforce rather than decorate;
- explain what evidence means and does not mean;
- keep the product concise and decision-oriented.

### Policy
**CDC Policy Analysis / Policy Analytical Framework**
Adopt:
- define the problem;
- identify multiple options;
- describe and assess options;
- compare impacts, costs/resources, feasibility, barriers, and tradeoffs;
- document rationale;
- select/prioritize only after comparison.

**UK Policy Profession Standards**
Adopt:
- define sought outcomes;
- challenge assumptions;
- use diverse evidence and stakeholder perspectives;
- analyze interdependencies and implementation;
- test options against desired outcomes, success criteria, and risks;
- build evaluation and feedback into policy development;
- provide clear, accurate, evidence-based, impartial, audience-targeted advice.

**GAO evidence-based policymaking**
Adopt:
- plan for results;
- assess/build evidence;
- use evidence;
- create continuous learning and improvement.

## 3. Governing Sequence

Use:

`DECISION REQUIREMENT
 -> INTELLIGENCE REQUIREMENTS
 -> COLLECTION PLAN
 -> SOURCE/PROVENANCE EVALUATION
 -> PROCESSING & EVIDENCE MAP
 -> ANALYTICAL MOSAIC
 -> JUDGMENTS / ALTERNATIVES / UNCERTAINTY
 -> IMPLICATIONS
 -> PRODUCT SELECTION
 -> BRIEF / BRIEFING
 -> POLICY OPTIONS (IF AUTHORIZED)
 -> IMPLEMENTATION & RISKS
 -> DECISION
 -> INDICATORS / EVALUATION
 -> FEEDBACK`

This is not required to be strictly linear. New evidence, customer questions, or
policy constraints may send the process back upstream.

## 4. Intake Contract

Record:

```text
DECISION-SUPPORT INTAKE
Customer / decision-maker:
Decision to be informed:
Question:
Why now:
Decision deadline:
Time horizon:
Domain:
Known facts:
Known assumptions:
Authorities / constraints:
What the customer already knows:
What the customer needs from this product:
Desired product:
  - intelligence assessment
  - written executive brief
  - oral briefing
  - policy options memo
  - decision memo
  - watchlist / indicators
Classification / releasability constraints:
Consequences of error:
```

If the decision requirement is unclear, resolve it before broad collection.

## 5. Intelligence Requirements

Convert the customer question into:

### Primary Intelligence Requirement (PIR)
The highest-value question whose answer materially changes the decision.

### Supporting Intelligence Requirements (SIRs)
Questions needed to answer the PIR.

### Essential Elements / Collection Questions
Observable information needed to resolve SIRs.

For each requirement record:
- why it matters;
- what decision it informs;
- current evidence;
- gap;
- source types likely to answer it;
- deadline;
- stop condition.

**Rule:** collection volume is not collection quality.

## 6. Collection and Evidence

Build a source map.

For each material source record:
- source ID;
- origin;
- date/time;
- primary/secondary/derivative;
- access/releasability;
- credibility/reliability considerations;
- information supplied;
- upstream lineage;
- corroboration status;
- gaps/limitations.

Apply VesselFramework statuses:
- SOURCE-ESTABLISHED
- FRAMEWORK SYNTHESIS
- WORKING HYPOTHESIS
- ILLUSTRATIVE

Missing provenance is not independence.

## 7. Processing and Evidence Map

Convert collected material into a decision-usable evidence structure:

`CLAIM -> SUPPORTING EVIDENCE -> CONTRADICTING EVIDENCE -> PROVENANCE ->
ASSUMPTIONS -> GAPS -> RELEVANCE`

Separate:
- observation/fact;
- source allegation;
- analyst inference;
- assumption;
- forecast;
- recommendation.

Never convert source repetition into confidence without resolving lineage.

## 8. Analytical Mosaic

Select processes for diagnostic value. Do not run every process by default.

Candidate processes include:

### Requirements / customer
- decision framing;
- key intelligence questions;
- stakeholder/authority mapping.

### Hypothesis and challenge
- key assumptions check;
- competing hypotheses;
- diagnostic evidence;
- devil's advocacy;
- red-team/challenge analysis;
- what-if analysis.

### VesselFramework systems analysis
- PARADOX;
- BOTTLENECK;
- CANNOT vs WILL NOT;
- constitutive vs instrumental constraint;
- DUAL LAYER;
- XFACTOR;
- dependency mapping;
- decision provenance.

### Foresight
- alternative futures;
- scenario analysis;
- indicators and warnings;
- trigger/signpost analysis;
- disconfirmers;
- prospective forecast object when resolvable.

### Cyber/risk
- attack surface;
- trust boundaries;
- adversarial paths;
- control assurance;
- failure modes;
- observability/detection;
- least privilege.

### Policy
- problem/root-cause analysis;
- option generation;
- feasibility;
- cost/resource implications;
- stakeholder effects;
- implementation barriers;
- unintended consequences;
- evaluation design.

For every selected method specify:

`METHOD -> QUESTION -> INPUT -> OUTPUT -> WHY IT ADDS INFORMATION -> FAILURE SIGNAL`

## 9. Judgment Construction

A major judgment should answer:

1. **What do we assess?**
2. **Why?**
3. **How likely / how confident?**
4. **What evidence matters most?**
5. **What alternative could explain it?**
6. **What would change the judgment?**
7. **Why does it matter to the customer?**

Probability and analytical confidence are separate.

**Probability:** likelihood of the proposition/event.  
**Analytical confidence:** strength, quality, independence, and completeness of
the evidence and reasoning supporting the judgment.

Do not use false numerical precision when evidence does not support it.

## 10. Intelligence-to-Policy Boundary

Before policy work, explicitly switch modes.

```text
INTELLIGENCE MODE:
What is / why / what may happen / uncertainty / implications.

POLICY MODE:
What outcomes are sought / what options exist / tradeoffs / feasibility /
implementation / evaluation.
```

Intelligence findings may constrain or inform policy options. They do not select a
policy by themselves.

If the operator requested assessment only, stop before recommendation.

## 11. Briefing Architecture

### 11.1 BLUF / Key Judgment
Lead with the decision-relevant conclusion, not the research chronology.

A strong opening contains:
- principal judgment;
- significance;
- uncertainty/confidence where material;
- immediate decision implication.

### 11.2 Recommended Oral Brief Structure

```text
1. PURPOSE / DECISION
2. BLUF
3. 2–4 KEY JUDGMENTS
4. EVIDENCE / WHY WE THINK THIS
5. PRINCIPAL ALTERNATIVE
6. IMPLICATIONS
7. INDICATORS / WHAT TO WATCH
8. DECISION / OPTIONS, IF AUTHORIZED
9. QUESTIONS
```

### 11.3 Written Intelligence Brief

```text
TITLE
DATE / SCOPE / HORIZON
BLUF
KEY JUDGMENTS
EVIDENCE AND REASONING
ALTERNATIVES / GAPS
IMPLICATIONS
INDICATORS
SOURCES / PROVENANCE NOTES
```

### 11.4 Briefing Compression Rule

Each lower level must support the level above it:

`SOURCE -> EVIDENCE -> JUDGMENT -> IMPLICATION -> DECISION`

Do not put source-level detail in the BLUF unless necessary to understand the
judgment.

### 11.5 Challenge Preparation

Before briefing, prepare:
- strongest evidence;
- weakest evidence;
- principal alternative;
- key assumption;
- likely hostile/challenging question;
- answer;
- what is unknown;
- what additional collection could resolve it.

Never bluff an answer. State what is unknown and what would be required to answer.

## 12. Policy Analysis

Activate only for an explicit policy/strategy/decision-options requirement.

### 12.1 Define the Policy Problem
State:
- current condition;
- affected population/system;
- desired outcome;
- evidence of the problem;
- root causes vs symptoms;
- authority/jurisdiction;
- constraints;
- baseline.

### 12.2 Generate Options
Create at least:
- status quo / no-new-action baseline where meaningful;
- focal option;
- credible alternative(s).

Avoid false options included only to make one choice look superior.

### 12.3 Option Matrix

Assess each option against criteria appropriate to the decision:

```text
EFFECT / BENEFIT
EVIDENCE STRENGTH
FEASIBILITY
AUTHORITY / LEGAL OR POLICY FIT
COST / RESOURCES
TIME TO IMPLEMENT
DEPENDENCIES
STAKEHOLDER EFFECTS
RISKS / UNINTENDED CONSEQUENCES
REVERSIBILITY
EQUITY / ACCESSIBILITY WHEN RELEVANT
MEASURABILITY
ROBUSTNESS ACROSS SCENARIOS
```

Criteria may be weighted only when the weighting rationale is explicit.

### 12.4 Bottleneck Test
For each option:
- what must be true for it to work?
- what currently prevents implementation?
- CANNOT or WILL NOT?
- which constraint is binding?
- what indicator shows the constraint has shifted?

### 12.5 Recommendation
A recommendation must state:
- preferred option;
- decision rationale;
- evidence strength;
- major tradeoff;
- implementation prerequisite;
- principal risk;
- alternative if the prerequisite fails.

Do not disguise value judgments as intelligence findings.

## 13. Implementation and Policy Delivery

For the preferred option define:

`OWNER -> AUTHORITY -> RESOURCES -> DEPENDENCIES -> MILESTONES ->
COMMUNICATION -> IMPLEMENTATION -> MONITORING -> EVALUATION -> ADAPTATION`

Include:
- responsible owner;
- stakeholders/users;
- start/end or decision points;
- resources/budget where relevant;
- legal/policy dependencies;
- technical/organizational dependencies;
- implementation risks;
- rollback/contingency;
- baseline;
- output measures;
- outcome measures;
- review cadence.

## 14. Evaluation

Distinguish:

**Activity:** Was the policy/control implemented?  
**Output:** What did implementation produce?  
**Outcome:** Did behavior/system conditions change?  
**Impact:** Did the desired strategic result improve?

Use:

`BASELINE -> IMPLEMENT -> MEASURE -> COMPARE -> EXPLAIN -> ADAPT`

Do not infer causality from improvement alone when other changes could explain it.

## 15. Product Selection

Choose the product based on customer and decision stage.

### Intelligence Assessment
Use when the customer needs understanding/judgment.

### Executive Brief
Use when a senior customer needs compressed understanding quickly.

### Oral Briefing
Use when interaction, challenge, clarification, or immediate decision support matters.

### Issue Brief
Use when defining and explaining a problem.

### Policy Options Brief
Use when credible options exist and need comparison.

### Decision Memo
Use when a specific decision is required.

### Indicators & Warnings Watchlist
Use when the key need is monitoring change over time.

## 16. Writing Rules

- Lead with judgment, not chronology.
- One paragraph, one analytical job.
- Use plain language unless technical terminology is necessary.
- Separate fact, inference, forecast, and recommendation.
- Calibrate probability and confidence.
- State material gaps.
- Prefer active voice.
- Use headings that communicate content.
- Make visuals carry analytical information.
- Do not bury the decision implication.
- Do not use dramatic language to compensate for weak evidence.
- Accessibility is a design requirement, not decoration.

## 17. Oral Briefing Rules

- Know the customer and decision.
- Rehearse the opening and transitions.
- State BLUF early.
- Keep key judgments limited.
- Know the evidence beneath each judgment.
- Anticipate challenge.
- Answer the question asked.
- Distinguish what is known, assessed, and unknown.
- If new information changes the assessment, say so.
- Confirm the customer understood the core message.
- Record material feedback/new requirements after the brief.

## 18. Harm Gate

Apply before consequential recommendations.

Evaluate:
- accuracy risk;
- legal/policy authority;
- security risk;
- professional/reputational risk;
- financial/resource risk;
- affected populations;
- reversibility;
- proportionality;
- consequences of action and inaction.

High consequence does not raise probability.

When evidence is weak but stakes are high, favor reversible information-gathering
or preparedness measures over irreversible action where possible.

## 19. Quality Assurance

Before release ask:

### Requirement
- Did we answer the customer's actual question?
- Is the decision deadline/horizon clear?

### Evidence
- Are material sources traceable?
- Is provenance resolved?
- Did derivative repetition masquerade as corroboration?

### Analysis
- Are assumptions visible?
- Were alternatives tested?
- Does confidence match evidence?
- Did we distinguish probability from confidence?
- Did we identify what would change the judgment?

### Briefing
- Is the BLUF decision-relevant?
- Can the product be understood quickly?
- Are implications clear?
- Are visuals accessible and analytically useful?

### Policy
- Is the problem distinct from the preferred solution?
- Were real alternatives compared?
- Are feasibility, costs, dependencies, implementation, and unintended effects addressed?
- Is the recommendation clearly separated from intelligence judgment?
- Is evaluation designed before implementation?

### Framework
- Does any claim outrun evidence?
- Did internal taxonomy leak into an external product without authorization?
- Is runtime state represented truthfully?

## 20. Adversarial Tests

T1 — Ambiguous customer question: skill must clarify/structure requirement.  
T2 — Sparse evidence: skill must downgrade confidence, not invent.  
T3 — Conflicting evidence: preserve conflict and seek discriminators.  
T4 — Derivative reporting: no false independence.  
T5 — Wrong focal hypothesis: alternative can win.  
T6 — Policy pressure: intelligence judgment remains analytically independent.  
T7 — Attractive but infeasible policy: feasibility/bottleneck blocks recommendation.  
T8 — Senior 5-minute brief: compress without losing uncertainty.  
T9 — Hostile question: identify evidence/limits without bluffing.  
T10 — Post-implementation success claim: separate activity/output/outcome/impact.  
T11 — Accessibility: product remains usable without color-only meaning and supports
clear reading order.  
T12 — Skill collision: defer to a narrower validated skill when it is better suited.

## 21. Output Modes

### Rapid Intelligence Brief
BLUF; 3 key judgments; confidence; principal alternative; implications; indicators;
gaps.

### Full Intelligence Assessment
Requirement; evidence/provenance; analytic mosaic; judgments; alternatives;
confidence; implications; indicators; collection gaps.

### Executive Oral Brief Package
Speaking BLUF; 3–4 key judgments; evidence cards; challenge questions; unknowns;
visual recommendations; follow-up requirements.

### Policy Options Memo
Problem; desired outcome; evidence; options; comparison matrix; recommendation;
implementation; risks; evaluation.

### Decision Memo
Decision required; recommendation; rationale; alternatives; consequences;
implementation prerequisites; indicators; review date.

## 22. Skill-Creation / Calibration Record

Record each pilot:
- case;
- customer/decision;
- selected methods;
- methods rejected;
- product;
- customer feedback;
- analytical defects;
- briefing defects;
- policy defects;
- provenance failures;
- unnecessary friction;
- corrections;
- regression result.

Promotion requires repeated successful use across at least two materially different
domains and no unresolved doctrine conflict.

## 23. Source Register

External research grounding for v0.1:
- ODNI, ICD 203, Analytic Standards.
- UK Government, Professional Development Framework for All-Source Intelligence Assessment, updated 2025.
- CIA Center for the Study of Intelligence, A Tradecraft Primer: Structured Analytic Techniques for Improving Intelligence Analysis.
- NATO AJP-2.1, intelligence procedures/intelligence cycle.
- CIA, A Day in the Life of a PDB Briefer (illustrative workflow, not doctrine).
- CDC POLARIS, Writing Briefs.
- CDC POLARIS, Policy Analysis and Policy Analytical Framework.
- UK Government, Policy Profession Standards.
- U.S. GAO, Evidence-Based Policymaking: Practices to Help Manage and Assess the Results of Federal Efforts.

Internal grounding:
- VesselFramework canonical evidence-status, provenance, alternatives, bottleneck,
  decision-provenance, Harm Gate, language-mediation, and internal-method boundary.

## 24. Final Rule

**Intelligence explains the decision environment. Briefing makes that understanding
usable. Policy analysis compares what could be done. Implementation tests whether
the choice can operate. Evaluation determines whether it worked. Keep those layers
connected, but never collapse them into one another.**
