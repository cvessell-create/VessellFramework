# VesselFramework — Complete Meta Matrix Framework
## Version 3.8.1 (Rough Working Candidate for Graduate Review) | NIST SP 800-50 Rev. 1 Integrated

This file supersedes the contaminated v3.6 bundle as the clean integrated candidate.

## v3.8.1 State and Disclosure Correction

This patch corrects a stale-state ambiguity in v3.8:

1. A packaged skill or continuity payload is not evidence that the corresponding live/private path has been updated.
2. Runtime synchronization may be claimed only after an explicit write succeeds and post-write verification confirms the target hash/state.
3. Until verified, runtime installation state is `UNVERIFIED/NOT APPLIED`.
4. Proprietary/original analytical methods are internal by default. External deliverables should communicate findings in the target domain's accepted terminology unless the operator explicitly authorizes framework disclosure.
5. Internal-method confidentiality does not override academic-integrity, citation, external-source, or generative-AI disclosure obligations.
6. Tool disclosure must be accurate: do not name a generative-AI system or external source that was not actually consulted.


## v3.9 Changelog — NIST SP 800-50 Rev. 1 Integration

- Added SP 800-50 Rev. 1 as an external authoritative cybersecurity-domain reference, not VesselFramework doctrine.
- Added a provenance-preserving CPLP/Decision Provenance crosswalk.
- Added audience segmentation, learning-control assurance, behavioral-effectiveness, bottleneck, and stale-standard tests.
- Added a guardrail against categorical Structural Maskirovka attribution to NIST.
- Runtime/private installation remains `UNVERIFIED/NOT APPLIED`.

It incorporates:
- current Master / meta-framework content;
- the v3.6 Provenance Firewall;
- adaptive hardening / patch logic;
- a complete operational analyst skill;
- executable-reference binding;
- the doctrine/code/test hierarchy;
- the runtime/memory/patch cross-reference matrix.

The PF-001–PF-005 controls remain **validated implementation hardening controls**, not automatically promoted universal doctrine. Their constitutional effect is limited to the provenance firewall behavior needed to prevent false independence.


---

# VesselFramework Meta-Framework — v3.8.1 Working Candidate

This document is the complete single-file edition of VesselFramework v3.8.1.
It consolidates the canonical master framework, calibration log, executable
reference layer, provenance firewall, adaptive hardening controls, operational
analyst skills, shared-path synchronization policy, and runtime/meta-matrix
cross-references into one portable reference document.

It is intended to function as the full integrated framework for upload, review,
versioning, and controlled runtime use. The sections below preserve the
framework's internal layer boundaries: doctrine defines intended behavior,
skills apply that doctrine, executable code tests selected rules, the forensic
auditor identifies defects, and calibration records what has and has not been
validated. Inclusion in this file does not by itself prove that a live/private
runtime path has been installed or synchronized.

Load order:
1. Core / Master
2. Calibration Log
3. Skill Pack

The v3.4 revision adds the Forensic Framework Auditor as a meta-skill. It is used to inspect the framework itself for defects, version drift, inherited assumptions, prompt bloat, coding barriers, style capture, calibration contamination, and other structural failures.

---

# VesselFramework Core — v3.4

This file combines the canonical Master Framework and Calibration Log into one portable core document.

Load this core before any skill document.

---

# VesselFramework_Master.md

**Grounded Master Reference — v3.3**

## NO EMPTY MIRRORING / NO STYLE CAPTURE — Language Mediation Principle

VesselFramework uses the LLM as an intermediary analytical device, not as an
authorial substitute and not as a mimic.

The system must distinguish **semantic intent** from **surface form**. Spelling,
grammar, punctuation, capitalization, fragments, repetition, and other surface
features may be intentionally noisy, adversarial, diagnostic, rushed, dictated,
copied, or otherwise unrepresentative. They shall not be treated as evidence of
the operator's preferred voice without corroboration.

The LLM must not return the operator's input as polished LLM prose and call that
analysis. A useful transformation must add a distinction, dependency, test,
counterexample, correction, evidence connection, decision rule, or other
analytical value.

Internal framework language may be used for reasoning. User-facing output must be
translated into the operator's actual language while preserving necessary
technical terms.

**Style inference hierarchy**
1. explicit operator instruction;
2. repeated stable patterns across verified examples;
3. operator-approved writing;
4. task requirements;
5. never a single noisy/adversarial sample.

**Anti-echo check**
- Did the system add analytical value?
- Did it separate meaning from form?
- Did it avoid imitating deliberate errors?
- Did it translate rather than impersonate?

If the output merely mirrors or polishes the input, rerun the reasoning layer.


**Layer 1 of 4. Read this first, every session, before touching any other document.**
**Author:** Christopher R. Vessell · M.S. Candidate, Strategic Intelligence, Saint Louis University, 2027
**Status:** This file supersedes `vessel-framework-analyst_SKILL_updated.md` (v1 — folded into this version, initially expanded to a three-variant Maskirovka check architecture replacing the single "Budgetary Maskirovka (Original Contribution)" section, now extended to four variants with Brute-Force Stealth as a developing doctrine) and consolidates `vessel-framework-analyst_SKILL_updated_1.md`, `lotl-cyber-analyst.skill`, `platform-rerender-analyst.skill`, `pillar-applications_1.md`, `VesselFramework_Decision_Provenance_Extension.md`, and `VesselFramework_Thesis_Prospectus.docx` into one canonical document. Redundant duplicate examples (the LOTL pillar walkthroughs appeared near-identically in three source files) are kept once, in their fullest form.

**v2 changelog (this revision):** (1) Closed the Section 4 "pending independent read-and-converge review" flag — see 4.1 below; Decision Provenance Chain status moves from *candidate* to *converged*. (2) Added Section 11, a full provenance record for the non-analytical files in the workspace (duplicate zips, `.pyz` builds, the `.sln`, and the Applied Analytics coursework thread), so file status doesn't have to be reconstructed by hand again.

---

## 0. What VesselFramework Is

VesselFramework is a four-pillar structured analytical method intended for cross-domain use — political, intelligence, organizational, cybersecurity, and statistical/measurement problems. It is presented as an **authorial synthesis** of several established traditions: Structured Analytic Techniques and hypothesis testing in intelligence analysis; the opportunity–willingness framework in international relations; Theory of Constraints and organizational/bureaucratic analysis; open-source collection and verification practice; and strategic foresight/net assessment.

The framework's integration, terminology, Maskirovka extensions, and Decision Provenance Chain are **VesselFramework constructions unless a source is explicitly named**. The framework must not claim that no prior literature has ever combined similar traditions unless that novelty claim is supported by a documented systematic literature review. The defensible claim is narrower: *VesselFramework combines these traditions in this specific named architecture and applies them through a common evidence-to-decision pipeline.*

**Active domains:** Geopolitical / Military · Organizational / Bureaucratic · AI / Technology · Cybersecurity / Nation-State Threats · Supply Chain / Operations · Policy / Compliance · Platform/Digital Forensics · Statistical Measurement

**Core diagnostic question that runs underneath all four pillars (thesis formalization):** Is observed inaction or dysfunction **structural (CANNOT — a genuine incapacity)** or **volitional (WILL NOT — a political or strategic choice)**? This determination drives every downstream conclusion about intent, resource allocation, and strategic trajectory.

---

## 0.1 Evidence Assurance & Source Discipline

Every substantive claim receives one of four statuses:

- **SOURCE-ESTABLISHED** — directly supported by a primary or strong secondary source.
- **FRAMEWORK SYNTHESIS** — a VesselFramework inference or integration built from established sources.
- **WORKING HYPOTHESIS** — plausible but not yet adequately verified; requires collection/testing.
- **ILLUSTRATIVE** — hypothetical example used to explain the method, not evidence about the real world.

Rules:

1. A framework label does not convert an inference into a fact.
2. Corroboration counts only when sources are meaningfully independent.
3. Vendor telemetry is evidence about that vendor's observed population, not automatically the whole threat landscape.
4. Retrospective cases with known outcomes validate explanatory fit; they do **not** calibrate predictive performance.
5. Absence is evidence only when the collection opportunity was adequate and the missing signal was reasonably expected to be observable.
6. Legal, statistical, compliance, and technical claims must preserve the scope of the source rather than generalizing beyond it.
7. Confidence is based on source reliability, independence, directness, diagnosticity, assumption sensitivity, and alternative explanations — not on a raw source count alone.

## 0.2 Operator Protection Principle — NO UNEXAMINED HARM

**Status: FRAMEWORK DOCTRINE.**

VesselFramework must evaluate both whether an assessment is defensible and
whether converting that assessment into action creates reasonably foreseeable
harm for the operator. Correctness and usefulness are necessary but not
sufficient conditions for a recommendation.

**Core rule:** VesselFramework shall not optimize an output solely for
correctness, persuasion, reach, speed, or analytical elegance. Before
consequential action, publication, submission, or communication, it must identify
reasonably foreseeable operator harms, distinguish reversible from
difficult-to-reverse consequences, and adjust the posture to the level of
evidence and exposure.

### HARM GATE

Run immediately before DECISION when material operator exposure is possible:

1. **Accuracy harm** — Could an unsupported, overstated, or misunderstood claim
   damage credibility or produce a bad decision?
2. **Academic harm** — Could the output cross course, assessment, authorship, or
   academic-integrity boundaries?
3. **Professional / reputational harm** — Could publication reasonably damage
   professional identity, relationships, employability, or institutional standing?
4. **Legal / ethical harm** — Could the action create foreseeable compliance,
   disclosure, privacy, attribution, defamation, contractual, or ethical problems?
5. **Financial / security harm** — Could acting expose money, credentials,
   systems, sensitive information, physical safety, or protected assets?
6. **Irreversibility** — If wrong, misunderstood, or misused, how difficult is
   the action to undo?
7. **Benefit proportionality** — Is the expected benefit proportionate to the
   residual risk after reasonable safeguards?

The Harm Gate does not automatically prohibit action. It changes the required
assurance, safeguards, wording, review, or reversibility of the action.

### Operator Exposure (OE)

Operator Exposure is introduced as a **candidate decision variable**, not yet a
production-engine weight.

- **LOW OE** — ordinary evidence threshold and normal review.
- **MODERATE OE** — explicit Harm Gate plus at least one viable mitigation or
  alternative.
- **HIGH OE** — stronger provenance, alternatives testing, claim calibration,
  safeguards, and pre-action verification.
- **SEVERE / IRREVERSIBLE OE** — where feasible, deliberate human review or
  independent verification before action.

**Assurance rule:** As consequence rises and reversibility falls, the evidence
assurance required before action rises.

**Feedback rule:** Calibration should record whether the Harm Gate identified the
material risk, whether safeguards worked, whether it over-constrained useful
action, and whether a missed harm warrants doctrine or future weight revision.

### Forward-Posture Extension for Digital Integration

**Purpose:** Convert the Harm Gate from a retrospective warning into a forward
posture decision for digital, cyber, platform, data, and AI-enabled actions.

The following register is a **FRAMEWORK SYNTHESIS** inspired by the supplied
positive/negative register guide. The guide is not treated as a source for
cybersecurity, legal, medical, military, or predictive claims. Its useful
contribution is structural: the same action can be beneficial in a context that
supports it and harmful in a context that does not.

#### Positive Registers: When Decisive Action Is Supportable

Activate a positive register only when the action is authorized, evidence is
adequate, the objective is legitimate, and a rollback or containment path exists.

| Digital context | Forward posture | Minimum safeguards |
|---|---|---|
| Confirmed credential theft or active account compromise | Contain, revoke, reset, preserve evidence, and recover access | Identity verification, incident record, least-privilege recovery, audit trail |
| Confirmed malicious persistence or destructive activity | Isolate affected systems and block the activity | Scope confirmation, business-continuity plan, forensic preservation, restoration test |
| Verified data exfiltration or privacy breach | Contain disclosure and begin required notification/escalation workflow | Data classification, legal/privacy review, notification authority, chain of custody |
| Material control failure with an available tested replacement | Restrict the failing path and move to the compensating control | Change approval, monitoring, rollback, owner, post-change verification |
| Repeated high-confidence abuse of a platform or workflow | Remove, rate-limit, or gate the abusive capability | Proportionality review, appeal path, false-positive monitoring, documented criteria |

These are not automatic permissions. They identify contexts in which delay may
increase harm and a forward posture may reasonably shift from `OBSERVE` toward
`CONTAIN`, `RECOVER`, or `RESTRICT`.

#### Negative Registers: When Action Is Likely to Create More Harm

Use a negative register when evidence is weak, the action is difficult to undo,
or the intervention can amplify the original problem.

| Digital context | Likely harm | Required posture |
|---|---|---|
| Unverified attribution or ambiguous anomaly | Misidentification, wrongful restriction, or evidence contamination | Preserve, observe, collect discriminating evidence; do not escalate attribution |
| Broad blocking based on a single indicator | Service disruption, accessibility loss, or collateral denial | Narrow scope, test alternatives, time-limit the control, monitor exceptions |
| Public accusation before provenance is established | Reputational, legal, diplomatic, or investigative harm | Use calibrated language and private verification before publication |
| Automated enforcement affecting access, employment, benefits, or safety | Discrimination, due-process failure, or unreviewable error | Human review, explanation, appeal, override, and proportionality check |
| Destructive remediation without a tested recovery path | Permanent data loss or operational outage | Pause, back up, preserve, test restoration, then authorize staged action |
| Training or compliance intervention used to conceal a design or authority failure | False assurance and continued exposure | Reopen BOTTLENECK analysis; test technical, process, incentive, and authority alternatives |

Negative-register findings do not require inaction. They require a safer
sequence, narrower scope, stronger evidence, human review, or a reversible
intervention.

#### Context Alignment: Native, Adjacent, and Misaligned Action

Replace the guide's metaphysical alignment language with an operational test of
fit between the proposed action and the system context:

- **Native alignment:** The action directly addresses a verified failure in the
    same system, authority domain, and time window. Decisive action may be
    proportionate if safeguards are present.
- **Adjacent alignment:** The action affects a connected dependency, supplier,
    identity provider, data flow, or partner system. Require dependency mapping,
    owner coordination, and collateral-impact testing.
- **Misalignment:** The action targets a proxy, symptom, unrelated population,
    or unsupported attribution. Treat the action as high-risk regardless of its
    apparent urgency.

**Alignment test:** *Does this action operate on the verified cause, or only on
the nearest visible proxy?* A mismatch increases the Harm Gate level and favors
`OBSERVE`, `VERIFY`, or `CONTAIN` over irreversible enforcement.

#### Forward-Posture Decision Ladder

Record one posture before implementation. Movement to the right requires a
stronger evidence, authority, and accountability record:

`OBSERVE -> VERIFY -> CONTAIN -> RECOVER -> RESTRICT -> ESCALATE`

| Posture | Use when | Required record |
|---|---|---|
| `OBSERVE` | Signal is weak or consequences of error are high | Collection plan and review time |
| `VERIFY` | A plausible threat or failure needs confirmation | Discriminating test and evidence owner |
| `CONTAIN` | Delay could increase active harm, but scope can be limited | Scope, duration, exception path, monitoring |
| `RECOVER` | Access, integrity, or availability must be restored | Authorized recovery plan and evidence preservation |
| `RESTRICT` | A verified harmful capability must be limited | Rule, affected population, proportionality, appeal/override |
| `ESCALATE` | Authority, consequence, or uncertainty exceeds local control | Decision authority, independent review, notification path |

#### Forward-Posture Record

Every material digital Harm Gate should append:

```text
FORWARD POSTURE:
Register: POSITIVE / NEGATIVE / MIXED
Alignment: NATIVE / ADJACENT / MISALIGNED
Current posture: OBSERVE / VERIFY / CONTAIN / RECOVER / RESTRICT / ESCALATE
Verified cause or proxy:
Action authorized by:
Evidence threshold met:
Reversibility and rollback:
Collateral-impact watchlist:
Human review required:
Stop condition:
Next review time:
Outcome and feedback:
```

**Default rule:** A positive register supports a posture; it does not establish
that the posture is safe. A negative register raises the assurance requirement;
it does not establish that action is prohibited. When positive and negative
registers conflict, use the more restrictive posture until the conflict is
resolved or an authorized reviewer accepts the residual exposure.


## 1. The Four Analytical Pillars

### PARADOX
**Grounding:** Structured Analytic Techniques, especially hypothesis comparison, diagnostic evidence, and challenge analysis (Heuer, 1999; Heuer & Pherson, 2014). **PARADOX is a VesselFramework synthesis inspired by these practices; it is not identical to ACH.**

**Definition:** The analytical move that identifies where the stated narrative contradicts the observable data — where what an actor *says* is structurally incompatible with what the actor *does, funds, or deploys*. PARADOX maps contradictions across a structured evidence matrix and ranks competing hypotheses by diagnostic weight. It is not about catching lies; it is about finding the constraint the lie reveals.

**Operational question:** *What claim, if true, would make the observable behavior impossible?*

**Critical distinction:** PARADOX can reveal a *category error* (the claim and the observable are answering different questions) as well as an outright contradiction. Category errors compound silently because no individual actor is lying — e.g., a security claim defines "protected" one way while the adversary operates entirely outside that definition.

**Output format:** "PARADOX: [Stated claim]. [Observable contradiction]. This means [structural implication]."

---

### BOTTLENECK
**Grounding:** Theory of Constraints (Goldratt & Cox, 1984; Goldratt, 1990); Most & Starr's **opportunity–willingness** framework (1989); and bureaucratic effort/principal-agent literature (Brehm & Gates, 1997). **CANNOT/WILL NOT is VesselFramework's synthesis, not a verbatim taxonomy from any one source.**

**Definition:** The binding constraint in a system — the single point where capability or will breaks down, causing everything downstream to stall. BOTTLENECK asks not what an actor wants, but what limits their ability to do what they want. This pillar operationalizes the framework's core CANNOT/WILL-NOT diagnostic.

**Operational question:** *What is the one thing, if it failed or was removed, that stops everything else?*

**Three bottleneck types:**
1. **Capability bottleneck** — lacks the means: training, equipment, infrastructure, data, or *methodology* (not just volume/scale)
2. **Will bottleneck** — has the means but not the authorization, incentive, or political cover
3. **Coordination bottleneck** — capability and will exist at different levels of the same org, and they are not connected (principal-agent failure)

**Constitutive vs. Instrumental distinction (core to VesselFramework):**
- **Instrumental bottleneck:** A process failure within a settled, correct structure. Fix = improve the process.
- **Constitutive bottleneck:** The structure itself is built for the wrong problem. Fix = replace the architecture. Treating a constitutive bottleneck as instrumental produces investment without capability gain — more of the same capability applied to a model that cannot see the threat.

**CANNOT vs. WILL NOT Diagnostic (formal version):**

| Dimension | CANNOT — Structural Constraint | WILL NOT — Volitional Choice |
|---|---|---|
| Framework meaning | Available opportunity/capability is insufficient because of a binding constraint. | Sufficient opportunity/capability appears to exist, but action is withheld, redirected, or deprioritized. |
| Source lineage | Theory of Constraints helps identify binding constraints; opportunity–willingness literature separates opportunity to act from willingness to act. | Opportunity–willingness and bureaucratic-behavior literature help frame volitional explanations. |
| Brehm & Gates | Their work/shirk/sabotage categories may inform alternative explanations for bureaucratic effort, but they are **not equivalents** of WILL NOT. | Treat shirking or sabotage as hypotheses requiring evidence of incentives, authority, and behavior. |
| Maskirovka test | A documented structural constraint supports a CANNOT assessment. | If evidence shows capability exists **and** a public explanation presents volitional non-action as incapacity, test a Budgetary Maskirovka hypothesis; do not declare it automatically. |

**In practice:** Iran's missile output declined 90% by Day 7 → BOTTLENECK: stockpile depletion (CANNOT), not diminished will. A BI dashboard exists but insights never reach decisions → BOTTLENECK is last-mile coordination, not data quality. Signature-based detection cannot flag adversaries using native tools → constitutive capability bottleneck: the constraint is detection *methodology*, not detection *volume*.

**Output format:** "BOTTLENECK: [System/actor]. [Constraint type — capability/will/coordination]. [Constitutive or instrumental]. [CANNOT or WILL NOT]. [Implication for behavior]."

---

### DUAL LAYER
**Grounding:** open-source collection/verification practice (Steele, 2002; Higgins, 2021) and OPSEC indicator analysis (NSDD-298, 1988). **NSDD-298 defines a five-step OPSEC process; it is not a five-step prepublication-review doctrine.**

**Definition:** The distinction between the *public signal layer* (what an actor says, posts, announces, or allows to be seen) and the *operational layer* (what the actor's infrastructure, budget, physical posture, or behavior actually reveals). Both layers are treated as real; the gap between them is the most important data. In publication contexts, DUAL LAYER also governs dual-format synthesis — producing both an IC-standard analytical product and a public-ready version, each cleared through the NSDD-298 review.

**Operational question:** *What does the public layer claim? What does the operational layer show? What is the gap telling us?*

**Advanced technique — Dual-Subject DUAL LAYER:** When two actors in the same system are each running their own dual layers, analyze both simultaneously and look for structural complementarity. The defender's blind spot and the adversary's operational layer may be *made for each other* — not by coincidence, but by doctrine. This complementarity is itself a finding: it means the adversary studied the defender's architecture before choosing their technique.

**In OSINT context:** DUAL LAYER = platform-stated identity vs. cross-platform behavioral data — what a target says about themselves vs. what their digital infrastructure reveals.

**Output format:** "DUAL LAYER — Public: [claim]. Operational: [observable]. Gap: [implication]." For dual-subject: run both analyses, then state the complementarity finding.

---

### XFACTOR
**Grounding:** Strategic Foresight and scenario planning (Kahn & Wiener, 1967; Schwartz, 1991) and net assessment/long-term competitive analysis (Marshall, 1972; Krepinevich & Watts, 2015; Angevine & McKitrick, 2023). Kondratiev long-wave analysis may be used only as a **contested heuristic**, never as a primary confirmation instrument; the empirical status of long waves remains disputed.

**Definition:** The asymmetric, low-probability, high-consequence variable that conventional analysis excludes because it doesn't fit the dominant scenario — and which, when it arrives, restructures the entire picture. XFACTOR is not speculation; it is systematic accounting for the variable the current analytical frame cannot see, forced onto a long analytical horizon rather than the next budget or news cycle.

**Operational question:** *What single event, actor entry, or capability revelation would make the current analysis obsolete? How would we know it was happening?*

**XFACTOR pattern — Static threat as precondition:** When the observable threat is a persistent, dormant capability (pre-positioned access, stockpiled weapons, pre-negotiated agreements), the XFACTOR is often not the capability itself but the *activation trigger* — the geopolitical, fiscal, or operational condition that converts dormant capability into active threat. Identify the trigger condition and the timeline-compression problem: response doctrine built on a weeks-to-months timeline cannot address an hours-timeline activation.

**Output format:** "XFACTOR: [The variable]. [Why current analysis misses it]. [Detection signal]." For precondition XFACTORs: name the trigger condition and the timeline compression problem explicitly.

---

## 2. Maskirovka Check Architecture (Original Contributions)

**Author:** Christopher R. Vessell (2025–present) · **Grounding:** Maskirovka doctrine (Russian military deception, Thomas 2004; Grau & Bartles 2016), extended across four distinct domains of application, and integrated with long-cycle foresight (Kondratiev/Marshall) as its primary confirmation instrument.

**Primary check posture (current package):** Brute-Force Stealth Maskirovka is the lead check in this architecture, developed by Christopher R. Vessell.

Four VesselFramework variants are defined below. Brute-Force Stealth is primary in this package; Budgetary, Structural, and Operational are retained as reference checks. **Multiple variants do not automatically create high confidence** because they may depend on the same underlying evidence; confidence rises only when the supporting evidence streams are independent and diagnostically consistent.

### Primary Check: Brute-Force Stealth Maskirovka (Developing)
**Definition:** A developing VesselFramework extension in which persistence, volume, and recurrence are used as concealment. The actor is not hidden by rarity; the actor is hidden by saturation. Repeated activity blends into expected operational noise, alert fatigue, and threshold-calibrated monitoring.

**Trigger conditions:** High-frequency retries/probes are distributed across accounts, hosts, services, or geographies while each individual event remains plausibly legitimate; activity clusters just below or around enforcement thresholds; campaign pacing is persistent enough to normalize as background churn.

**Detection protocol:** Build baseline for normal retry/probe/error cadence by asset and identity class -> aggregate repeated events into campaign views (not single alerts) -> detect temporal clustering and synchronized cadence shifts across telemetry domains -> test whether observed persistence exceeds business-operational necessity -> confirm with control-plane and identity context.

**Output format:** "BRUTE-FORCE STEALTH MASKIROVKA: [Campaign pattern]. [How saturation masks intent]. [Cross-domain correlation signal]. [Containment/detection requirement]."

### Reference Check: Budgetary Maskirovka
**Definition:** The strategic concealment of resource reallocation behind claims of budget constraint — the use of legitimate-appearing budgetary or resource allocation behaviors to conceal actual strategic intent. This is VesselFramework's original scholarly contribution, extending Soviet Maskirovka doctrine into organizational and financial intelligence analysis.

**Trigger conditions:** Stated priorities and actual spend pattern don't match; budget line items technically comply with stated purpose but operationally serve a different one; off-budget mechanisms concentrate in areas the actor never discusses publicly; public capability claims are unsupported by infrastructure, personnel, or procurement spend.

**Five-Step Detection Protocol:**
1. **Baseline** — what does legitimate spending for the stated mission look like?
2. **Map actuals** — what is actually being spent, on what, in what sequence?
3. **Gap analysis** — where do actuals diverge from baseline, and in what direction?
4. **Intent inference** — what strategic posture is consistent with the actual pattern?
5. **Confirmation seek** — find non-financial data that confirms or contradicts inferred intent

**The Maskirovka–Foresight Nexus (framework synthesis):** Financial/resource-allocation patterns that are ambiguous in a single budget cycle may become more interpretable when mapped longitudinally against procurement, staffing, doctrine, and operational behavior. Net-assessment-style long-horizon comparison can strengthen or weaken the hypothesis. Kondratiev-style long-wave claims, if used at all, must be labeled contested and cannot serve as confirmation by themselves.

**Output format:** "BUDGETARY MASKIROVKA: [Stated mission]. [Actual spend pattern]. Gap: [what the actuals reveal]. Confirmation: [non-financial corroboration]."

### Reference Check: Structural Maskirovka
**Definition:** A condition in which a governing architecture — a compliance framework, audit standard, reporting structure, or oversight mechanism — produces outputs that accurately represent performance against its own stated standard while systematically leaving the actual mission unaddressed. **No individual actor is deceiving anyone.** The deception is produced by the architecture itself.

**Why it is more dangerous than Budgetary Maskirovka:** It cannot be fixed by finding and replacing bad actors. The architecture itself must be replaced or supplemented. Every oversight body that reviews the system will confirm it is performing correctly — because it is performing correctly against the wrong standard. Full compliance coexists with total mission failure, and the compliance record actively obscures that failure.

**Detection protocol:**
1. Identify the standard the architecture operates under.
2. Map what the standard validates — existence, process, or outcome?
3. Identify the actual mission requirement the standard does not measure.
4. Find the gap — an actor scoring 100% on the standard while failing entirely on the mission requirement.
5. Confirm with an observable case where full compliance coexisted with mission failure.

**Signature patterns:** A compliance framework that validates control existence but not efficacy against a specific adversary methodology (NIST CSF / FISMA / SOC2 vs. LOTL detection is the canonical case); an audit standard that measures whether a process was followed, not whether it worked; a performance metric that becomes the goal rather than the proxy (Goodhart's Law at the institutional level); a certification that is valid, earned, and operationally meaningless for the actual threat.

**Domain applications:** Cybersecurity (NIST CSF/FISMA certify control existence, not LOTL detection capability) · Intelligence/Oversight (congressional oversight certifies program/budget compliance, not analytical accuracy) · Organizational/BI (maturity frameworks certify pipelines exist, not that insights reach decisions) · Supply Chain (ISO 9001 certifies process, not product quality) · Policy/Regulation (disclosure requirements certify terms were disclosed, not that power asymmetry was surfaced).

**Output format:** "STRUCTURAL MASKIROVKA: [The governing architecture]. [What it validates]. [What it does not validate]. [The mission requirement that falls through the gap]. This is not negligence or deception — it is architectural. The fix is not compliance; it is replacing or supplementing the standard itself."

### Reference Check: Operational Maskirovka
**Definition:** The use of legitimate-appearing operational activity — tool usage, process execution, personnel deployment, resource expenditure — to conceal hostile intent or capability. The observable behavior is indistinguishable from legitimate activity at the surface layer; the maskirovka operates at the activity level, not the fiscal level.

**Trigger conditions:** An actor's operational activity is identical in form to legitimate activity but hostile in intent; the concealment mechanism is mimicry, not secrecy — the activity is visible, its nature is not; detection requires behavioral context (baseline, timing, lineage, sequence), not signature matching.

**Detection protocol:** Establish a behavioral baseline for the activity type in legitimate use → map actual activity against baseline (timing, volume, sequence, credential context, process lineage) → flag deviations that cannot be explained by legitimate need → confirm with non-operational data (geopolitical context, infrastructure correlation, anomalous access pattern).

**Canonical example:** Living-off-the-land (LOTL) tradecraft — see Section 3.1.

**Output format:** "OPERATIONAL MASKIROVKA: [The activity]. [Why it appears legitimate]. [What baseline deviation reveals]. [Detection requirement]."

**Four-variant convergence (framework hypothesis):** If independently evidenced operational mimicry, governance/measurement mismatch, resource-allocation mismatch, and saturation-based concealment coexist, treat the pattern as a strong prompt for architectural review. Do not infer systemic incapacity merely from applying multiple labels to the same evidence.

---

## 3. Domain Extensions

### 3.1 LOTL / Nation-State Cyber Threat Analysis

This extension applies VesselFramework to living-off-the-land (LOTL) activity and the Volt Typhoon case. It separates **source-established facts** from framework interpretation.

**SOURCE-ESTABLISHED definition:** LOTL techniques abuse legitimate credentials, built-in tools, scripts, applications, or administrative functions so malicious activity can resemble normal operations. LOTL activity can coexist with malware or other techniques; therefore, "no foreign code" is **not** a universal definition.

**Source-established observations:**
- CISA and partner agencies describe LOTL and valid-account use as hallmarks of Volt Typhoon activity and reported indications of access in some victim IT environments for **at least five years**.
- Bitdefender reported that **84% of major/high-severity incidents** in its 700,000-incident GravityZone analysis involved LOTL binaries; its MDR validation set showed **85%** of incidents involved LOTL techniques. These percentages describe Bitdefender's observed populations and should not be generalized to all attacks without qualification.
- CrowdStrike's 2025 Global Threat Report stated that **79% of detections in 2024 were malware-free**. "Malware-free" is not synonymous with LOTL; the number is contextual evidence for hands-on-keyboard and credential/tool abuse, not a LOTL prevalence statistic.
- The community-maintained LOLBAS project currently catalogs hundreds of Windows binaries/scripts/libraries and maps entries to MITRE ATT&CK. LOLBAS is **not a MITRE project**.

**Metrics removed from canonical doctrine pending a traceable primary methodology:** "PowerShell appears in 71% of LOTL cases" and "behavioral analytics improves LOTL detection by 62%." These figures appear in secondary/industry summaries, but this audit did not locate an adequate primary methodology that justifies treating them as canonical.

**Detection architecture:** File/hash signatures remain useful for known malicious artifacts and some known command/content patterns, but signature-only logic is insufficient for activity performed with legitimate binaries and valid accounts. Defenders therefore need contextual telemetry such as process lineage, command-line/script logging, identity and privilege context, network behavior, baselines, and threat hunting. The claim is **insufficiency**, not literal invisibility to every signature-based control.

**Four-pillar application (framework synthesis):**
- **PARADOX:** A broad claim such as "the environment is protected because endpoint/perimeter controls are deployed" may exceed what those controls actually validate against authenticated native-tool abuse. Test the exact protection claim before calling it a contradiction.
- **BOTTLENECK:** If detection depends primarily on indicators that LOTL does not generate, the limiting factor may be **detection methodology** rather than sensor quantity. Determine whether the bottleneck is constitutive or merely an implementation gap by testing what the deployed stack can actually observe.
- **DUAL LAYER:** Compare declared security posture with operational telemetry and validation results. On the adversary side, compare legitimate-looking activity with sequence, credential context, process lineage, and mission effects.
- **XFACTOR:** In pre-positioning cases, the key uncertainty may be the activation condition and timeline rather than persistence alone. Treat crisis-linked activation as a scenario requiring indicators, not as a prediction.

**Maskirovka application:** "Operational Maskirovka" is a VesselFramework label for mimicry/legitimate-tool abuse. "Structural Maskirovka" should **not** be attributed categorically to NIST CSF, FISMA, or SOC 2. NIST CSF 2.0 is an outcomes-oriented risk framework and does not certify organizations. A structural-mismatch finding must be demonstrated at the level of how an organization implements, measures, or audits a framework. Likewise, SOC 2 is an attestation regime, not a NIST-style certification, and FISMA includes risk-management and continuous-monitoring requirements. The valid analytical question is whether the organization's assurance process measures efficacy against the threat being claimed.

**Analytical sequence:** Identify subject → establish source facts → classify relevant LOTL behavior → trace Decision Provenance → PARADOX → BOTTLENECK → DUAL LAYER → XFACTOR → test Maskirovka hypothesis only if its trigger conditions are independently evidenced → synthesis → calibrated posture.

### 3.2 Platform Silent Re-Render Analysis — Hypothesis Protocol

**Status: WORKING HYPOTHESIS, not established platform architecture.**

This extension originated from an observed before/after change associated with a LinkedIn profile edit. The operational record supports the fact that a visible asset changed after an edit to another field; it does **not**, by itself, prove the server-side mechanism that caused the change.

The prior version overstated several unverified claims as facts — including a specific cache invalidation pipeline, "current rules" being retroactively re-applied, a list of known trigger fields, and a confirmed white-fill compositing mechanism. Those claims are removed from doctrine until reproduced experimentally or supported by platform documentation/telemetry.

**Operational Record Gap (retained as a framework concept):** An analyst may observe before/after states while the operator knows what actions were actually taken. The operator's action log is strong evidence about what the user did, but it is **not ground truth about hidden server-side causation**.

**Protocol:**
1. Establish a timestamped pre-change baseline.
2. Record the exact action performed.
3. Capture the post-change state.
4. Enumerate competing explanations: client rendering, cache invalidation, asset recompression, A/B test, platform-side rule change, account-setting change, unrelated update, or observation error.
5. Reproduce with controlled edits where feasible.
6. Seek independent confirmation from documentation, network/asset metadata, another account, or repeated trials.
7. Assign confidence only after alternatives are discriminated.

**Four-pillar application:**
- **PARADOX:** Use only if a documented platform claim is actually inconsistent with observed behavior.
- **BOTTLENECK:** The primary bottleneck is often observability of the hidden processing pipeline, not proof that the pipeline is architecturally coupled.
- **DUAL LAYER:** Public UI/documentation can be compared with observed behavior, but silence in documentation is not proof of concealed implementation.
- **XFACTOR:** Unobserved platform-side processing is a hypothesis class that can change attribution. It must be tested, not asserted.
- **Structural Maskirovka:** Do not apply merely because documentation omits backend details. The variant requires evidence that a governing standard systematically validates the wrong thing while obscuring mission failure.

**Canonical posture:** preserve the case as a useful example of **causal underdetermination and the operational-record gap**, not as proof of LinkedIn's backend architecture.


---

# 3.3 NIST SP 800-50 Rev. 1 — Cybersecurity and Privacy Learning Program Extension

**Status:** EXTERNAL AUTHORITATIVE REFERENCE / CYBERSECURITY DOMAIN EXTENSION  
**Primary source:** Merritt et al. (2024), *Building a Cybersecurity and Privacy Learning Program*, NIST SP 800-50 Rev. 1.  
**Framework relationship:** NIST concepts remain NIST-attributed. Crosswalks, assurance tests, and analytical extensions below are **FRAMEWORK SYNTHESIS** unless identified as source-established.

## 3.3.1 Source-Established NIST Model

NIST SP 800-50 Rev. 1 describes a life-cycle approach for a Cybersecurity and Privacy Learning Program (CPLP):

`PLAN & STRATEGY → ANALYSIS & DESIGN → DEVELOPMENT & IMPLEMENTATION → ASSESSMENT & IMPROVEMENT ↺`

The phases may occur sequentially or simultaneously. The CPLP is treated as an adaptive, continuous learning program connected to organizational cybersecurity/privacy risk management, measurement, feedback, and behavior change.

## 3.3.2 NIST Audience Segmentation

NIST identifies three overlapping learning-program audience segments:

1. **All users**
2. **Privileged access account holders**
3. **Personnel with significant cybersecurity and/or privacy responsibilities**

**Framework use:** Do not assume a homogeneous workforce. Map learning needs to access, authority, mission dependency, data sensitivity, and consequence. A learner may belong to multiple segments.

## 3.3.3 Decision Provenance Crosswalk

**FRAMEWORK SYNTHESIS — not a NIST-defined equivalence.**

| NIST CPLP phase | VesselFramework analytical emphasis |
|---|---|
| Plan & Strategy | CONTEXT → AUTHORITY → CONSEQUENCE; mission, risk, governance, resources, goals, outcomes |
| Analysis & Design | SIGNAL → PROVENANCE → TRANSFORMATION → ALTERNATIVES → BOTTLENECK; needs, audiences, dependencies, design |
| Development & Implementation | AUTHORITY → HARM GATE → DECISION; materials, delivery, testing, implementation, safeguards |
| Assessment & Improvement | CONSEQUENCE → CONFIDENCE → FEEDBACK; measurements, metrics, effectiveness, leadership review, revision |

**Cycle rule:** FEEDBACK may alter CONTEXT, assumptions, audience segmentation, priorities, content, resources, or implementation.

## 3.3.4 Learning-Control Assurance Chain

**FRAMEWORK SYNTHESIS informed by NIST measurement/effectiveness guidance.**

Do not collapse:

`Program exists → Element delivered → Learner participated → Knowledge/skill changed → Behavior changed → Cybersecurity/privacy risk outcome improved`

Evidence at an earlier stage does not automatically establish a later stage.

This instantiates the broader VesselFramework distinction:

`Control exists → Control operates → Control is effective → Security outcome improves`

**Decision rule:** Match the measurement to the claim. Completion supports participation/implementation claims; it does not independently prove behavior change or risk reduction.

## 3.3.5 Measurement and Behavioral Effectiveness

NIST distinguishes measurements from metrics and uses them to evaluate implementation, effectiveness, efficiency, and improvement. NIST specifically gives appropriate reporting of a phishing test email as an example of behavior-change measurement.

When evidence permits, evaluate:
- reach / implementation;
- learning or skill acquisition;
- observable behavior;
- operational effect on the targeted risk;
- feedback into the next program decision.

**Anti-Goodhart rule:** Compliance measures may be necessary, but the easiest-to-count measure must not silently replace the mission outcome.

## 3.3.6 Human-Risk and Human-Contribution Model

NIST distinguishes technical and human risks and emphasizes the workforce's role in identifying, responding to, and managing risk.

VesselFramework therefore shall not model people only as vulnerabilities. Personnel may function as a risk source, control operator, sensor/reporting channel, decision authority, recovery dependency, or feedback source.

This extends **Human Dependency Relocation**: technical controls may reduce exposure while relocating human dependency to recognition, verification, reporting, escalation, or response.

## 3.3.7 CPLP Bottleneck Tests

Before concluding that "users need more training," test alternatives:

- **Capability:** knowledge/skill is insufficient.
- **Design:** content does not match audience, task, threat, or context.
- **Delivery:** learners cannot access, understand, or engage with the material.
- **Authority/process:** learners recognize the issue but lack a usable reporting/escalation path or permission to act.
- **Incentive/culture:** organizational incentives suppress desired behavior.
- **Measurement:** participation is measured instead of the intended outcome.
- **Technical architecture:** the system creates a failure training cannot reasonably compensate for.

**Mission-dependent rule:** Training is not the default fix for a technical, governance, authority, or architecture problem.

## 3.3.8 Structural-Mismatch Guardrail

NIST SP 800-50 Rev. 1 must not be labeled categorically as Structural Maskirovka. It explicitly includes behavior change, measurements, metrics, effectiveness evaluation, leadership review, and continual improvement.

A structural-mismatch hypothesis may be tested only against a specific organization's implementation or assurance process, with evidence that the measurement architecture validates one thing while the mission requires another.

Testable question: *Does the organization measure only completion, or does it also evaluate whether the targeted behavior and risk outcome changed?*

## 3.3.9 Provenance Firewall — NIST Integration

1. Preserve NIST terminology when describing NIST.
2. Label VesselFramework crosswalks/extensions as **FRAMEWORK SYNTHESIS**.
3. Do not convert NIST recommendations into universal mandates.
4. Preserve scope: SP 800-50 Rev. 1 is written for federal organizations; nongovernmental organizations may use it voluntarily.
5. Do not attribute VesselFramework pillars, CANNOT/WILL NOT, Maskirovka, Decision Provenance Chain, Harm Gate, or this Learning-Control Assurance Chain to NIST.
6. Cite NIST directly when its concepts materially support an external deliverable.
7. If NIST guidance changes, mark this module potentially stale until the source and mappings are reviewed.

## 3.3.10 Stale-State Trigger for External Standards

**FRAMEWORK SYNTHESIS.**

Enter `REVIEW REQUIRED` when NIST publishes a revision, erratum, withdrawal, or superseding publication; a materially relied-on companion standard changes; a relevant regulatory requirement changes; or a crosswalk no longer matches source terminology/scope.

`CURRENT SOURCE VERIFIED → CHANGE SIGNAL → REVIEW REQUIRED → CROSSWALK REVALIDATED → CURRENT`

An old citation or packaged copy is not evidence that an external-standard module remains current.

## 3.3.11 CPLP Analytical Sequence

`SOURCE & SCOPE CHECK → MISSION/RISK → AUDIENCE SEGMENTATION → EXPECTED BEHAVIOR/OUTCOME → CURRENT CONTROLS → BOTTLENECK & ALTERNATIVES → PLAN & STRATEGY → ANALYSIS & DESIGN → DEVELOPMENT & IMPLEMENTATION → MEASUREMENT/METRICS → ASSESSMENT & IMPROVEMENT → LEADERSHIP DECISION → FEEDBACK`

Run the four pillars only after source facts and NIST/VesselFramework boundaries are established.

## 3.3.12 Canonical Reference

Merritt, M., Hansche, S., Ellis, B., Sanchez-Cherry, K., Snyder, J. N., & Walden, D. (2024). *Building a cybersecurity and privacy learning program* (NIST Special Publication 800-50 Rev. 1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-50r1

## 3.3.13 Operational CPLP Decision Record

**Purpose:** Convert the NIST/VesselFramework crosswalk into a repeatable record for planning, approving, measuring, and revising a cybersecurity or privacy learning intervention.

### Required Record

Complete one record for each material learning intervention or review cycle:

```text
CPLP DECISION RECORD

Record ID:
Date opened:
Owner:
Review date:
Source and scope verified: YES / NO / REVIEW REQUIRED

1. MISSION AND RISK
Mission or business function:
Risk statement:
Affected asset, process, population, or data:
Consequence if the risk persists:
Baseline evidence and provenance:

2. AUDIENCE AND EXPECTED BEHAVIOR
Audience segment: ALL USERS / PRIVILEGED ACCESS / SIGNIFICANT RESPONSIBILITY / MULTIPLE
Target task or decision:
Current observable behavior:
Required observable behavior:
Behavior owner and authority:

3. BOTTLENECK AND ALTERNATIVES
Primary bottleneck: CAPABILITY / DESIGN / DELIVERY / AUTHORITY-PROCESS / INCENTIVE-CULTURE / MEASUREMENT / TECHNICAL ARCHITECTURE
Evidence for bottleneck:
Non-training alternatives considered:
Chosen intervention and rationale:
Residual uncertainty:

4. IMPLEMENTATION
Responsible roles:
Resources and dependencies:
Delivery method and accessibility requirements:
Completion or participation evidence:
Implementation exceptions:

5. MEASUREMENT PLAN
Knowledge or skill measure:
Behavior measure:
Risk or operational outcome measure:
Baseline date and value:
Follow-up dates:
Success threshold:
Disqualifying evidence or harm signal:

6. DECISION AND FEEDBACK
Decision: CONTINUE / MODIFY / REDESIGN / PAUSE / RETIRE / INDETERMINATE
Evidence supporting decision:
Harm Gate completed: YES / NO / NOT MATERIAL
Decision authority:
Next action and owner:
Feedback to next cycle:
```

### Phase Gates

Advance only when the applicable exit evidence exists:

| Phase | Entry question | Minimum exit evidence |
|---|---|---|
| Plan & Strategy | What mission risk requires intervention? | Approved risk statement, objective, owner, resources, and consequence |
| Analysis & Design | What behavior must change for which audience? | Audience/task map, baseline, bottleneck finding, and alternatives review |
| Development & Implementation | Is the intervention usable, authorized, and delivered? | Tested intervention, delivery record, exceptions, and responsible roles |
| Assessment & Improvement | Did knowledge, behavior, or risk change? | Measurements matched to claims, decision record, and improvement action |

Failure to meet an exit criterion produces `REVIEW REQUIRED`, not an implied success claim.

### Evidence-to-Claim Limits

| Evidence observed | Permitted claim | Claim not established by itself |
|---|---|---|
| Completion or attendance record | The element was delivered or participation occurred | Knowledge, behavior, or risk reduction |
| Assessment score or practical demonstration | Knowledge or skill was demonstrated under the test conditions | Sustained workplace behavior or risk reduction |
| Repeated behavior observation | The targeted behavior changed in the observed setting and period | Causation or broad organizational improvement |
| Control, incident, or operational data | The targeted risk indicator changed or did not change | Attribution to training without alternatives testing |
| Longitudinal comparison with adequate baseline | A trend can be evaluated | Certainty that the intervention alone caused the trend |

### Decision Thresholds

- **Low completion or access:** repair delivery, scheduling, accessibility, or authorization before judging content effectiveness.
- **High completion with low knowledge or skill:** redesign content, practice, assessment, or task alignment.
- **High knowledge or skill with poor behavior:** investigate workflow, authority, incentives, usability, supervision, and technical architecture before adding training.
- **Improved behavior with unchanged risk indicators:** test whether the intervention targeted the correct risk, whether the measure is valid, and whether another bottleneck dominates.
- **Insufficient or conflicting evidence:** record `INDETERMINATE` and specify the collection needed to resolve it.
- **Material operator, privacy, security, legal, or academic exposure:** run the Harm Gate before implementation or external reporting.

### Roles and Cadence

At minimum, assign an intervention owner, risk or mission owner, system/data owner where applicable, security/privacy reviewer, delivery owner, and decision authority. One person may hold multiple roles only when the concentration of authority is recorded as a risk.

Use a baseline before implementation, an immediate implementation or learning check, a behavior follow-up at approximately 30/60/90 days when feasible, and a formal improvement review at least annually or after a material incident, system change, audience change, or source revision.

---

## 4. The Decision Provenance Chain (Cross-Domain Extension)

Developed by applying the four pillars to two unrelated problems in the same week — a facial-recognition case study and a Likert-scale measurement question — and finding they shared one underlying structure. Promoted to a standing VesselFramework layer that runs alongside, not instead of, the four pillars: use it to trace *how a signal becomes a decision* before running PARADOX/BOTTLENECK/DUAL LAYER/XFACTOR on what you find.

**The chain:**
```
SIGNAL → PROVENANCE → TRANSFORMATION → CONTEXT → CONTRADICTION →
ALTERNATIVES → BOTTLENECK → AUTHORITY → CONSEQUENCE → CONFIDENCE →
HARM GATE → DECISION → FEEDBACK
```

| Step | Question |
|---|---|
| Signal | What happened? |
| Provenance | Where did this information come from? |
| Transformation | What happened to it before we saw it? |
| Context | Under what environmental, organizational, technical, or human conditions was it produced? |
| Contradiction | What evidence doesn't fit? |
| Alternatives | What competing explanations survive? |
| Bottleneck | Which dependency currently limits the desired outcome? |
| Authority | Who or what can convert this assessment into action? |
| Consequence | What happens if the assessment is wrong? |
| Confidence | How much certainty does the evidence actually permit? |
| Harm Gate | What foreseeable operator harm could follow; how reversible is the action; what safeguards are proportionate? |
| Decision | What action is justified — not merely possible? |
| Feedback | What evidence would show the decision worked, failed, or needs revision? |

**Diagnostic resolution** (locate *where* a failure sits, rather than issuing a single verdict): chain reconstructable but evidence weak → **epistemic problem**. Evidence strong but nobody can act → **authority/bottleneck problem**. Action occurs but doesn't produce the intended outcome → **effectiveness problem**. Outcome works technically but creates unacceptable secondary consequences → **risk/legitimacy problem**. Chain not reconstructable at all → **governance problem**.

**Domain instances:** Cybersecurity (telemetry → SIEM → detection rule → analyst → incident classification → incident commander → containment → business impact → lessons learned) · Facial recognition (face → camera → representation → algorithm → match → analyst → authority → intervention → consequence → review) · Intelligence (source → collection → processing → analyst → assessment → policymaker → decision → effect → reassessment) · Operations (demand signal → forecast → procurement → inventory → distribution → delivery → KPI → corrective decision) · Statistical measurement (participant → item responses → numeric coding → aggregation → composite score → treated as interval → statistics calculated → conclusions drawn).

**Supporting principles:**
- **Assurance Ceiling:** Downstream authentication (or downstream statistical treatment) cannot provide greater assurance than the identity-binding (or measurement-construction) process supporting it. General form: *the analytical authority of an output cannot exceed the quality of the process that produced its inputs.*
- **Context-Bound Effectiveness:** A control or scale validated in one environment cannot be assumed effective when population, scale, environment, mission, or architecture changes.
- **Tradeoff Vector:** "More secure" or "more precise" is not a scalar quantity — evaluate across multiple objectives rather than collapsing to a single better/worse axis.
- **Human Dependency Relocation:** Automation does not eliminate human dependency; it relocates it (upstream to design/enrollment, or downstream to interpretation/action authority).
- **Mission-Dependent Bottleneck:** The binding constraint changes with the use case — a better algorithm won't fix compromised enrollment; more training won't fix an unlawful collection model; better visualization won't fix a poorly constructed scale.
- **Control Authority Gradient:** `Observe → Alert → Recommend → Restrict → Act` — as authority moves rightward, the evidentiary bar (confidence, explainability, authorization, accountability) should rise before the system is allowed to trigger the next stage. **Operator Protection extension:** as operator exposure rises and reversibility falls, assurance, safeguards, and review should also rise.
- **Four Non-Interchangeable Claims** (same shape across domains — the recurring error is treating an earlier step as proof of a later one):
  - Controls: `Control exists → Control operates → Control is effective → Security outcome improves`
  - Measurement: `Item responses exist → Items are aggregated → Composite is reliable/valid → Composite justifies the intended statistical inference`
  - Legitimacy: `Technical effectiveness ≠ operational effectiveness ≠ organizational acceptance ≠ legitimacy`

**Working method:** KNOW (what does the source material teach?) → CONNECT (how do the elements interact?) → CHALLENGE (what assumption is being made?) → ANALYZE (run the chain + four pillars) → EVALUATE (what evidence distinguishes claimed capability from actual effectiveness?) → JUDGE (what should a practitioner do?) → DEFEND (can the conclusion survive graduate-level scrutiny?).

### 4.1 Independent Read-and-Converge Review — Bridges Validation Case

**Status: RETROSPECTIVE VALIDATION CASE. It is not a prospective calibration hit.**

The Decision Provenance Chain can be tested for explanatory usefulness against *R (Bridges) v Chief Constable of South Wales Police* [2020] EWCA Civ 1058.

**SOURCE-ESTABLISHED:** AFR Locate captured faces from live video, transformed them into biometric templates, compared them with a watchlist, generated similarity scores, and produced alerts that were reviewed by officers before any intervention. The Court of Appeal allowed the appeal on Grounds 1, 3, and 5: deficiencies in the legal framework left impermissibly broad discretion over watchlist inclusion and deployment locations; the DPIA did not adequately address the resulting risks; and South Wales Police had not taken reasonable steps to satisfy the Public Sector Equality Duty concerning potential race/sex bias.

**Decision Provenance mapping:**
`live image → biometric template → comparison/similarity score → operator review → officer judgment → intervention authority → legal/data-protection/equality consequences → judicial review`

**Framework synthesis:** The case supports the **Assurance Ceiling** idea: technical matching output does not by itself justify downstream coercive authority. Governance, watchlist provenance, deployment rules, human review, legal authority, and equality obligations are independent dependencies in the decision chain.

**Important correction:** The prior version overreached by describing the case as primarily a missing "population-specific false-positive/false-negative validation" problem. The judgment's holdings were broader and more specific to legal discretion, DPIA compliance, and the Public Sector Equality Duty. Do not substitute a machine-learning accuracy critique for the court's actual reasoning.

**Convergence finding:** The chain is useful for reconstructing where authority enters a socio-technical system. That is a **methodological validation**, not evidence that the framework predicted the court's outcome.

## 5. Cross-Domain Pillar Example Bank

*(Non-LOTL examples — the LOTL example set lives in Section 3.1 and is not repeated here.)*

**PARADOX**
- *Intelligence/Military:* Public — "We are open to negotiations." Observable — strike packages at full alert, no drawdown. PARADOX: negotiating posture is reputational signaling, not operational intent.
- *Organizational/BI:* Public — "Our BI platform delivers insights to every decision-maker." Observable — 12% dashboard adoption; C-suite receives human-analyst summaries. PARADOX: the "last mile" claim is false — the human is still the intelligence layer.
- *AGI/AI Accountability:* Claim — "Our AI system is auditable and explainable." Observable — no audit trail for training-data selection. PARADOX: auditability is claimed at the output layer but structurally impossible without input documentation.

**BOTTLENECK**
- *State actor capability:* Iran's 90% missile output decline (Day 7) → stockpile, not will — a rationing strategy, not defeat.
- *Organizational/bureaucratic:* Intelligence exists but never reaches the decision → coordination (last-mile) bottleneck; the fix is architectural (embed the insight), not training.
- *AI systems:* Model produces correct outputs but humans override without cause → trust/authorization-structure bottleneck, not model accuracy.

**DUAL LAYER**
- *Geopolitical:* Public — Pezeshkian announces a halt to strikes on neighbors. Operational — IRGC reaffirms the right to strike US installations within hours. Gap: civilian government and IRGC are running separate foreign policies simultaneously.
- *Corporate/government:* Public — agency announces a $200M AI modernization initiative. Operational — $12M actually allocated; the rest is unappropriated multi-year authorization. Gap: the announcement is political positioning at ~6% of the stated commitment.
- *OSINT identity analysis:* Platform-stated — "independent researcher and consultant." Infrastructure — domain registered same day as a known state-affiliated outlet, hosting shared with known IO accounts. Gap: "independent" is the cover; the infrastructure reveals a coordinated operation.

**XFACTOR**
- *Third-party entry:* Frame — bilateral US-Iran conflict. XFACTOR — Russia provides Iran ISR intelligence on US force positions, making the 90% missile-output decline ambiguous (rationing vs. improved targeting via Russian ISR).
- *Technological:* Frame — AI augments human analysts. XFACTOR — plausible-but-wrong AI outputs that pass all human review filters, since review catches only *obvious* errors, not confident-but-wrong ones.
- *Fiscal:* Frame — an organization is under-resourced for its mission. XFACTOR — off-budget mechanisms (inter-agency transfers, revolving funds, contractor vehicles) not visible in the stated budget; actual capability may exceed the stated budget by 40–60%.

**Budgetary Maskirovka — worked example (hypothetical state actor claiming defensive posture)**
1. *Baseline:* Defensive posture → expected spend on border fortification, reserve mobilization, ISR, civil defense; NOT heavy spend on power projection or expeditionary logistics.
2. *Actuals:* 70% on forward-deployed strike systems, expeditionary logistics, port access agreements; border infrastructure only 8% of total.
3. *Gap:* Actuals are the inverse of a defensive baseline — the spend pattern matches power-projection preparation, not defense.
4. *Intent inference:* The actual posture is offensive, using the defensive claim as diplomatic cover.
5. *Confirmation:* Doctrine revisions emphasizing "proactive deterrence"; training exercises simulating offensive operations in foreign territory.
**Assessment:** Budgetary Maskirovka confirmed — the defensive claim is the maskirovka; the offensive capability is the actual investment.

---

## 6. Analytical Sequence (Master)

1. **State the subject** — one sentence on what/who is being analyzed and why.
2. **Declare the domain** — which active domain applies; note if dual-domain.
3. **PARADOX pass** — central contradiction? Outright contradiction or category error?
4. **BOTTLENECK pass** — binding constraint, typed (capability/will/coordination), constitutive or instrumental, CANNOT or WILL NOT.
5. **DUAL LAYER pass** — each layer's claim, the gap; run dual-subject if two actors are present.
6. **XFACTOR pass** — the variable the current frame can't see; is the threat a precondition?
7. **Maskirovka check** — run the Primary Brute-Force Stealth check first, then apply reference variants as needed (Budgetary / Structural / Operational); note convergence.
8. **Decision Provenance Chain** (when the question involves converting evidence into an action or authority decision) — trace signal → provenance → …→ decision → feedback; locate the diagnostic failure type if applicable.
9. **Synthesis** — where does the convergence point?
10. **HARM GATE / Operator Exposure** — before consequential action, publication, submission, or communication, identify foreseeable harms, reversibility, safeguards, and OE level.
11. **Posture statement** — not a prediction; a posture: "Given the convergence of these signals and assessed operator exposure, the analytical posture is…"

---

## 7. Voice Standards

**Precision over vagueness; calibration over bravado.** State the claim at exactly the level the evidence supports. If the evidence only supports "possible command-authority friction," do not write "command authority is fractured."

**Decision-maker framing.** End analysis with an implication for posture or collection, while keeping posture distinct from prediction.

**Confidence discipline.** Do not use a raw rule such as "three sources = high confidence." Evaluate:
- source reliability and access,
- source independence,
- directness/proximity to the event,
- diagnosticity of the evidence,
- consistency across streams,
- sensitivity to key assumptions,
- viable alternative explanations,
- important collection gaps.

Use HIGH / MODERATE / LOW only after documenting the basis. Three sources repeating one original report count as **one evidentiary stream**, not three.

**Alternative assessment discipline.** When a claim depends on an assumption, state the assumption and what evidence would change the assessment.

**Absence discipline.** "Silence" is data only when the source would reasonably be expected to observe/report the event and collection conditions were adequate. Otherwise it is simply missing information.

**Constitutive/instrumental discipline.** State whether the evidence supports an architectural or process-level failure. Do not prescribe architecture replacement until a constitutive failure has actually been demonstrated.

**Source-status discipline.** Distinguish SOURCE-ESTABLISHED, FRAMEWORK SYNTHESIS, WORKING HYPOTHESIS, and ILLUSTRATIVE material in substantive products.

## 8. Output Formats (Master Table)

| Request type | Output format | Length |
|---|---|---|
| Full analysis | All four pillars + Maskirovka + synthesis + posture | 1,500–3,000 words |
| Quick assessment | PARADOX + BOTTLENECK only | 200–400 words |
| OSINT brief | Decrypting Loyalty Sit-Rep format | 1,500–3,000 words |
| Organizational diagnosis | BOTTLENECK + DUAL LAYER focus | 500–1,000 words |
| Brute-Force Stealth Maskirovka audit (primary) | Saturation baseline → recurrence aggregation → cadence-shift detection → cross-domain confirmation | 600–1,200 words |
| Budgetary Maskirovka audit (reference) | 5-step protocol: baseline → actuals → gap → intent → confirm | 600–1,200 words |
| Structural Maskirovka audit (reference) | Framework ID → existence/efficacy gap → mission-failure confirmation | 500–1,000 words |
| Operational Maskirovka audit (reference) | Baseline → deviation map → behavioral context → confirmation | 400–800 words |
| Cybersecurity/LOTL threat assessment | All four pillars + Maskirovka + detection architecture | 2,000–3,000 words |
| LOTL incident analysis | PARADOX + BOTTLENECK + DUAL LAYER | 800–1,200 words |
| LOTL defensive posture audit | BOTTLENECK (constitutive) + Maskirovka variants | 600–1,000 words |
| XFACTOR activation brief | XFACTOR + indicator set + posture statement | 400–700 words |
| Platform re-render full analysis | All four pillars + Structural Maskirovka + AI-deception pattern | 800–1,500 words |
| Platform re-render quick check | PARADOX + operational record verification | 200–400 words |
| Platform re-render pre-edit protocol | Detection protocol output | 5-step checklist |

Save full analyses as: `VF_[Topic]_[YYYYMMDD].md`

---

## 9. Reference & Canonical Files Index

This package's canonical review set is limited to files included in this workspace.

**Canonical in-package references:**
- `VesselFramework_MetaMatrix_Framework_v3.8_v3.9_Combined.md` — integrated framework, doctrine, calibration, executable appendix, and skills pack
- `SKILL.md` — operational analyst skill
- `VesselFramework_Forecasting_SKILL_v1.0.md` — forecasting skill
- `vesselframework_reference_v1.1_provenance_firewall.py` — executable provenance firewall reference
- `vesselframework_case_runner.py` — deterministic case intake/report runner

**External or historical references not bundled in this package:**
- prior standalone LOTL and platform case writeups
- prior thesis prospectus artifacts
- prior superseded single-skill drafts

Use this section as a package-local index for graduate review, not as a claim that all historical artifacts are present.

---

## 10. Key Literature & Source Ledger

The list below separates intellectual foundations from empirical validation sources. Bibliographic details should be checked against the edition actually cited in academic work.

### Intelligence analysis / structured techniques
- Heuer, R. J., Jr. (1999). *Psychology of intelligence analysis*. Central Intelligence Agency, Center for the Study of Intelligence.
- Heuer, R. J., Jr., & Pherson, R. H. (2014). *Structured analytic techniques for intelligence analysis* (2nd ed.). CQ Press/SAGE.

**Use:** grounding for cognitive-bias awareness, hypothesis comparison, diagnostic evidence, challenge analysis.  
**Caveat:** PARADOX is VesselFramework's synthesis; it is not a published Heuer/Pherson technique under that name.

### Opportunity, willingness, organizations, and constraints
- Most, B. A., & Starr, H. (1989). *Inquiry, logic, and international politics*. University of South Carolina Press.
- Cioffi-Revilla, C., & Starr, H. (1995). Opportunity, willingness and political uncertainty: Theoretical foundations of politics. *Journal of Theoretical Politics, 7*(4).
- Goldratt, E. M., & Cox, J. (1984). *The goal*. North River Press.
- Goldratt, E. M. (1990). *What is this thing called Theory of Constraints and how should it be implemented?* North River Press.
- Brehm, J., & Gates, S. (1997). *Working, shirking, and sabotage: Bureaucratic response to a democratic public*. University of Michigan Press.

**Use:** opportunity/constraint vs willingness, system constraints, bureaucratic effort and principal-agent alternatives.  
**Caveat:** "CANNOT/WILL NOT" and constitutive/instrumental bottlenecks are framework syntheses, not direct quotations of these literatures.

### OSINT / verification / OPSEC
- Steele, R. D. (2002). *The new craft of intelligence: Achieving asymmetric advantage in the face of nontraditional threats*. Strategic Studies Institute, U.S. Army War College.
- Higgins, E. (2021). *We are Bellingcat: An intelligence agency for the people*. Bloomsbury.
- National Security Decision Directive 298. (1988). *National Operations Security Program*.

**Use:** open-source exploitation/verification and observable-indicator discipline.  
**Correction:** NSDD-298's five steps are the OPSEC process (critical information, threats, vulnerabilities, risks, countermeasures), not a prepublication-review process.  
**Caveat:** Heuer explicitly criticizes a naive "mosaic theory" of analysis; therefore VesselFramework should not present "Mosaic OSINT methodology" as an uncontested parent discipline.

### Strategic foresight / net assessment
- Kahn, H., & Wiener, A. J. (1967). *The year 2000: A framework for speculation on the next thirty-three years*. Macmillan.
- Schwartz, P. (1991). *The art of the long view*. Doubleday/Currency.
- Marshall, A. W. (1972, March 15). *Net assessments* [Memorandum to Henry Kissinger], reproduced in *Foreign Relations of the United States, 1969–1976, Vol. II*, Document 266.
- Krepinevich, A. F., Jr., & Watts, B. D. (2015). *The last warrior: Andrew Marshall and the shaping of modern American defense strategy*. Basic Books.
- Angevine, R. G., & McKitrick, J. S. (2023). Andrew Marshall and net assessment. *Journal of Strategic Studies, 46*(5).

**Use:** scenarios, long-horizon competition, diagnostic comparison.  
**Correction:** "Marshall, 1972–1997, Net Assessment Monographs" is too vague to function as a scholarly citation.

### Long-wave analysis — contested
- Kondratiev, N. D. (1920s). Long-wave economic-cycle work.
- Focacci, A. (2017). Controversial curves of the economy: An up-to-date investigation of long waves. *Technological Forecasting and Social Change, 116*, 271–285.
- Hecht, J. (2025). Are long waves 50 years? Reexamining economic and financial long wave periodicities in Kondratieff and Schumpeter. *Review of Political Economy, 37*(4).

**Use:** optional exploratory heuristic only.  
**Caveat:** empirical validity is contested; long-wave positioning must not be treated as confirmation of a strategic-intent hypothesis.

### Russian military concepts / Maskirovka lineage
- Thomas, T. L. (2004). Russia's reflexive control theory and the military. *The Journal of Slavic Military Studies, 17*(2), 237–256.
- Grau, L. W., & Bartles, C. K. (2016). *The Russian way of war: Force structure, tactics and modernization of the Russian Ground Forces*. Foreign Military Studies Office.

**Use:** background on Russian deception/reflexive-control and military practice.  
**Caveat:** Brute-Force Stealth (primary), Budgetary, Structural, and Operational Maskirovka are **VesselFramework extensions**. Their novelty and utility should be evaluated separately from established Russian doctrine.

### Cyber / LOTL empirical sources
- CISA et al. (2024). Joint Cybersecurity Advisory AA24-038A on PRC state-sponsored actors/Volt Typhoon and U.S. critical infrastructure.
- Bitdefender. (2025). Analysis of 700,000 security incidents and LOTL tactics.
- CrowdStrike. (2025). *Global Threat Report*.
- LOLBAS Project. Current community catalog of Living Off The Land Binaries, Scripts and Libraries.

**Use:** CISA for Volt Typhoon behavior/persistence; Bitdefender for its incident-corpus LOTL prevalence; CrowdStrike for malware-free detection prevalence; LOLBAS for catalogued legitimate-tool abuse techniques.  
**Caveat:** malware-free ≠ LOTL. Vendor telemetry is population-bounded.

### Cybersecurity governance
- National Institute of Standards and Technology. (2024). *The NIST Cybersecurity Framework (CSF) 2.0* (NIST CSWP 29).

**Correction:** NIST CSF 2.0 is an outcomes-oriented risk-management framework and does not "certify control existence." Structural Maskirovka analysis must target an organization's implementation/measurement architecture, not mischaracterize the CSF itself.

### Automated facial recognition validation case
- *R (Bridges) v Chief Constable of South Wales Police* [2020] EWCA Civ 1058.

**Use:** retrospective validation of the Decision Provenance/Assurance Ceiling reasoning pattern.  
**Caveat:** known-outcome cases belong in a validation set, not a prospective calibration score.

### Originality / authorship status
VesselFramework, the Decision Provenance Chain, and its named Maskirovka extensions are attributed here to Christopher R. Vessell as framework-specific constructs. This document makes an **authorship claim, not a legal determination of intellectual-property rights or a verified literature-wide novelty finding**.

## 11. File & Build Artifact Provenance (Consolidation Record)

**Audit status:** Historical hash/diff claims in this section came from prior workspace analysis. This cleanup did not receive every binary/archive listed below in the active sandbox, so those exact-duplicate and "safe to delete" claims are **not re-certified here**. Do not delete an artifact solely because this document says it is redundant; re-run hash/diff verification against the actual files first.

### 11.1 Analytical content (skills / doctrine)

| File | Status | Basis |
|---|---|---|
| `VesselFramework_Master.md` (this file) | **Canonical** | Declares and demonstrates supersession of all rows below |
| `vessel-framework-analyst_SKILL_updated_1.md` | Superseded — folded into Section 2 | Confirmed superset of `_updated.md`: adds the Structural and Operational Maskirovka variants verbatim-matched into Section 2 |
| `vessel-framework-analyst_SKILL_updated.md` | Superseded — archive-safe | Confirmed subset of `_updated_1.md` (diff shows no unique content) |
| `VesselFramework_Decision_Provenance_Extension.md` | Superseded — folded into Section 4 | Content matches Section 4 almost verbatim; 4.1 above closes the "pending review" status the source file carried |

### 11.2 Code / build lineage (`VessellFramework_*` executables and archives)

Diff-verified lineage, oldest to newest:

| File | Status | Basis |
|---|---|---|
| `VessellFramework_Full_Custom_Architecture_Source_and_Visual_v2.zip` | Superseded — archive-safe | `vessell_framework.py` is byte-identical to the copy inside the v3 package; v3 adds the OSINT module, tests, and a changelog on top with no removals |
| `VessellFramework_Full_Custom_Architecture_v3_OSINT_Source_Visual.zip` | Superseded by the Runnable Demo Package — archive-safe | Byte-identical copy is nested unchanged inside `VessellFramework_Full_Runnable_Demo_Package.zip`; nothing here isn't in that package |
| `VessellFramework_Full_Runnable_Demo_Package.zip` | **Keep — illustrative/demo tier** | Superset of v2 and v3; adds a runnable Linux binary, a portable `.pyz`, native C source, and one hardcoded worked scenario. Useful as a demonstration artifact, not as the current build |
| `VessellFramework_Demo_Executable.pyz` (top-level upload) | Duplicate of the copy inside the Demo Package — archive-safe | Byte-identical (MD5 match) |
| `VessellFramework_Demo_Linux_x86_64` | Part of the Demo Package tier | Compiled companion to the demo `.pyz`; same status as the Demo Package |
| `VessellFramework_Production_v4.pyz` | Historical build reference — not bundled in this submission package | Prior notes describe this as a production-architecture artifact; this package does not re-certify or include that artifact for current review |
| `VesselFramework.sln` (top-level upload) | Superseded — archive-safe | A one-project shell referencing only `VesselFramework_Master.md`; the `.sln` inside `VesselFramework_Workspace.zip` does the same job as part of a fuller solution structure |
| `VesselFramework_Workspace.zip` | Superseded — archive-safe, low-priority | A memory/workspace snapshot (Areas/, Topics/, Profile.md) whose embedded `VesselFramework_Master.md` differs from canonical only in three cosmetic name-spelling edits ("Vescovi" vs. "Vessell"); no unique substantive content |

**Historical cleanup note (not re-certified in this package):**
`VessellFramework_Full_Custom_Architecture_Source_and_Visual_v2.zip`, `VessellFramework_Full_Custom_Architecture_v3_OSINT_Source_Visual.zip`, top-level `VessellFramework_Demo_Executable.pyz`, `VesselFramework.sln`, `VesselFramework_Workspace.zip`, `vessel-framework-analyst_SKILL_updated.md`, `VesselFramework_Decision_Provenance_Extension.md`, `vessel-framework-analyst_SKILL_updated_1.md`.

**Historical retention note:** `VessellFramework_Full_Runnable_Demo_Package.zip` and `VessellFramework_Production_v4.pyz` were previously tracked as separate demo/production tiers; evaluate against current artifact availability before using this distinction operationally.

### 11.3 Applied Analytics coursework thread (separate from VesselFramework proper)

This thread (`Applied_Analytics_*`, both Rmd files, both docx files) is a **different project** — a Teacher Model / Mother Framework pair for a statistics course, per its own `Applied_Analytics_Postmortem.md`. It converges with VesselFramework only at one seam: the postmortem's four-part chain (**Human Question → R Computation → Statistical Evidence → Human Decision**) is a domain instance of the same Decision Provenance pattern now converged in Section 4 — the statistical-measurement row in Section 4's domain-instance list already covers it. Its own duplicate problem (two near-identical `Applied_Analytics_Adaptive_Learning_SKILL.md` uploads plus a `_v3.md`) is a separate cleanup and is not folded into this framework document; flag separately if you want it consolidated the same way.
---
---


## v3.3 Language Mediation Revision

The canonical framework now treats the LLM as an intermediary analytical device. Surface spelling, grammar, punctuation, fragments, or other noisy input must not be learned as operator voice from a single sample. Semantic intent is recovered first; output must add analytical value rather than merely polish or mirror input.

---

# VesselFramework_Calibration_Log.md
**Layer 4 of 4. Feedback system.**

## Purpose

Separate **retrospective validation** from **prospective calibration**.

A known-outcome case can test whether the framework reconstructs a problem coherently, but it cannot honestly be counted as a predictive HIT. Calibration requires a posture recorded **before** the outcome is known.

## A. Validation Case schema

Use when the outcome is already known.

**Case ID:**  
**Known outcome/source:**  
**Framework applied without hiding the outcome?**  
**What the framework successfully reconstructed:**  
**What it distorted or missed:**  
**Doctrine implication:**  
**Status:** explanatory validation only — not a hit-rate datapoint.

### V-001 — Bridges v South Wales Police, reviewed 2026-09-04

**Known outcome/source:** Court of Appeal judgment [2020] EWCA Civ 1058.  
**Successful reconstruction:** Decision Provenance correctly exposes that a technical match sits inside a larger chain involving watchlist provenance, governance, human review, intervention authority, and consequences. Assurance Ceiling is a useful way to express why algorithmic output does not independently authorize coercive action.  
**Correction produced by this audit:** The earlier framework over-centered population-specific accuracy testing and then labeled the retrospective match a "HIT." The judgment actually turned on Article 8 legal-framework defects, DPIA deficiencies, and Public Sector Equality Duty failures.  
**Doctrine implication:** Retain the case as validation of chain reconstruction; remove it from predictive calibration statistics.

## B. Prospective Calibration Entry schema

Create this entry **before the outcome is known**.

**Calibration ID:**  
**Timestamp:**  
**Decision question:**  
**Posture:**  
**Probability or confidence:**  
**Evidence streams and independence:**  
**Key assumptions:**  
**Disconfirming indicators:**  
**Expected resolution date/window:**  
**Outcome:** *(later)*  
**Score/verdict:** *(later)*  
**Diagnostic:** *(later)*  
**Revision triggered:** *(later)*

## Calibration metrics

If numerical probabilities are used, prefer proper calibration measures such as:
- Brier score for binary outcomes,
- calibration/reliability bins,
- sharpness/resolution,
- domain-specific performance,
- error analysis by assumption and source type.

If only ordinal HIGH/MODERATE/LOW labels are used, track empirical outcome frequencies by label and domain, but do not pretend the labels are probabilities unless thresholds are explicitly defined.

## Revision rule

A doctrine change requires:
- a clear causal miss/near-miss,
- repeated pattern,
- or strong validation evidence that reveals a structural flaw.

Every revision must cite a Validation ID or Calibration ID. No framework change is justified merely because a new concept sounds useful.

## Entries

No prospective calibration entries are carried forward from the prior file. Begin at **C-001** with the next real, time-stamped, unresolved assessment.


## C-001 — Acorns / LinkedIn Reputation-Safe Referral Strategy
**Type:** Prospective calibration entry  
**Status:** Outcome pending / not graded as hit or miss  
**Posture:** Transparent disclosure + personal-goal framing + restrained promotion should better preserve professional credibility than a direct sales/referral pitch.  
**Outcome variables:** referral conversions; engagement quality; negative/positive reactions; profile/network effects; consistency with professional identity.  
**Revision rule:** No weight change until outcome is observed and graded HIT / PARTIAL / MISS with cause.

## V-002 — Applied Analytics Assignment 3: Independent-Work Diagnostic
**Type:** Internal validation / known-outcome learning case  
**Observed pattern:** Downstream p → alpha → significance → course hypothesis decision → effect-size reasoning was comparatively stable; errors clustered earlier in natural-language design recognition and visualization selection.  
**Diagnosis:** Upstream classification can constrain several downstream answers.  
**Framework response:** Added front-end classification and transformation-loss checks to the Applied Analytics learning framework.  
**Validation limit:** One assignment is evidence of a learner-specific failure pattern, not proof of a universal statistical-learning rule.

## V-003 — Adversarial Surface-Form / Language-Mediation Test
**Type:** Framework validation case  
**Trigger:** Operator intentionally supplied spelling and grammar errors to test whether the LLM would mistake surface form for operator voice.  
**Observed failure:** The system risked treating intentionally noisy input as style evidence and returning polished/mirrored versions rather than performing the intended analytical mediation.  
**Diagnosis:** Style inference was insufficiently separated from semantic interpretation.  
**Framework response:** v3.3 added NO EMPTY MIRRORING / NO STYLE CAPTURE, an explicit style-evidence hierarchy, adversarial-input check, and anti-echo final response gate.  
**Success criterion:** Future noisy/adversarial inputs do not cause style capture; responses recover meaning, add analytical value, and translate without impersonating surface errors.  
**Engine weights:** No production analytical weights changed.

## V-004 — Forensic Framework Auditor Skill
**Type:** Prospective framework validation entry  
**Status:** New skill; not yet validated  
**Trigger:** A forensic review protocol exposed the need for a repeatable method to inspect the framework itself rather than only domain problems.  
**Hypothesis:** A dedicated meta-audit skill will detect structural, language, calibration, portability, and coding defects that ordinary domain analysis can miss.  
**Success criteria:**  
1. identifies at least one non-trivial defect with exact evidence;  
2. separates artifact evidence from speculation about model intent;  
3. proposes a minimal repair;  
4. repair survives the original failure case and at least one new analogous test;  
5. does not create greater prompt bloat or overconstraint than the defect it fixes.  
**Failure criteria:**  
- produces only stylistic rewriting;  
- invents model intent;  
- cannot show exact evidence;  
- adds broad new rules without a test;  
- repeatedly flags normal framework behavior as defects.  
**Engine weights:** No production weights changed.  
**Next action:** Run the skill against the current v3.3/v3.4 package and log the first complete defect register.

---

---

# Executable Reference Layer — v3.5

## Status

The attached Python reference implementation becomes part of the VesselFramework **meta-framework as a reference implementation and test surface**, not as the constitutional authority of the framework.

This distinction is mandatory:

**Doctrine defines intended behavior.  
Code implements selected doctrine.  
Tests evaluate implementation behavior.  
Calibration evaluates whether the larger framework performs as intended.**

The Python implementation is new work. It is not a recovered, canonical, byte-identical, or MD5-matched copy of any historical VesselFramework executable or build artifact.

## Why This Layer Exists

VesselFramework previously existed primarily as analytical doctrine expressed in natural language. The reference implementation creates a second representation of selected rules that can be executed and tested.

That makes a new class of comparison possible:

`DOCTRINE ↔ CODE ↔ TEST ↔ OBSERVED BEHAVIOR`

A disagreement between those layers is evidence of a defect to investigate. It does not automatically prove which layer is correct.

## What the Current Reference Implementation Operationalizes

The v1.0 Python reference currently implements selected parts of the framework:

- evidence-status categories as explicit data;
- independence-aware evidentiary stream counting;
- Harm Gate inputs;
- Operator Exposure calculation;
- safeguards associated with exposure;
- scaffolds for PARADOX, BOTTLENECK, DUAL LAYER, and XFACTOR;
- CANNOT / WILL NOT validation;
- Maskirovka trigger eligibility;
- shared-evidence checks for Maskirovka convergence;
- executable tests for several of those behaviors.

It does **not** generate analytical conclusions and must not be treated as an analytical oracle.

## Authority Boundary

The implementation may enforce a rule only to the degree that the rule is actually specified in the Master.

If code introduces a threshold, mapping, default, formula, or decision rule that is not explicitly established by doctrine, classify it as:

**IMPLEMENTATION CHOICE — REQUIRES VALIDATION**

Do not silently promote an implementation choice into VesselFramework doctrine merely because it exists in executable code.

Likewise, do not automatically rewrite the code to match ambiguous prose. First identify whether the defect is in:
- doctrine;
- implementation;
- test;
- translation between layers;
- or an unresolved ambiguity.

## Executable-Provenance Rule

Every future implementation should state:

1. what doctrine/version it implements;
2. whether it is new work, recovered work, or derived work;
3. which sections are implemented;
4. which sections are not implemented;
5. which behaviors are implementation choices;
6. what tests exist;
7. what remains unvalidated.

Claims such as "canonical," "production," "recovered," "byte-identical," or "matched" require independent artifact evidence.

## Code Forensic Audit

The Forensic Framework Auditor now treats executable implementations as first-class audit targets.

For each coded rule ask:

1. **Doctrine trace:** What exact framework rule is this code supposed to implement?
2. **Semantic match:** Does the code actually implement that rule?
3. **Added assumption:** Did the programmer/model add a threshold or behavior not present in doctrine?
4. **Lost condition:** Did translation into code remove an exception, uncertainty, or contextual dependency?
5. **Default behavior:** What happens when data are absent, malformed, contradictory, cyclic, or incomplete?
6. **Boundary behavior:** What happens at thresholds?
7. **Failure visibility:** Does the code fail loudly, fail safely, or silently produce a plausible answer?
8. **Test quality:** Does the test validate doctrine, or merely confirm the code behaves the way it was written?
9. **Independence:** Was the test derived from the same mistaken interpretation as the implementation?
10. **Operator consequence:** What happens if the coded behavior is wrong and trusted?

## Anti-Circularity Rule for Tests

A passing unit test is not proof that the doctrine was implemented correctly.

If the same interpretation generated both the code and its expected test result, the test may only demonstrate internal consistency.

Therefore distinguish:

**CODE CONSISTENCY TEST**
→ Does the implementation behave as its author specified?

**DOCTRINE CONFORMANCE TEST**
→ Does implementation behavior match the authoritative framework text?

**EXTERNAL VALIDATION TEST**
→ Does the rule perform correctly against an independent known case?

These are not interchangeable.

## Reference-Implementation Defect Classes

Add the following forensic defect classes:

- **D19 — Doctrine/code mismatch**
- **D20 — Unstated implementation assumption**
- **D21 — Test circularity**
- **D22 — Unsafe default/failure behavior**
- **D23 — Provenance overclaim**
- **D24 — Executable version drift**

## Development Loop

For code implementing VesselFramework:

`DOCTRINE → TRACE RULE → IMPLEMENT → UNIT TEST → CONFORMANCE TEST → ADVERSARIAL TEST → HARM CHECK → LOG → VERSION`

For a discovered defect:

`OBSERVE FAILURE → LOCATE LAYER → REPRODUCE → MINIMAL REPAIR → REGRESSION TEST → CROSS-LAYER CHECK → LOG → VERSION`

## Vibe-Coding Rule

Fast, reversible coding is allowed.

Do not require the full forensic process before every prototype.

Use two lanes:

**PROTOTYPE LANE**
- reversible;
- local;
- no consequential deployment;
- assumptions may be temporary but must be visible;
- optimize for learning.

**ASSURANCE LANE**
- code will be relied upon;
- public, academic, professional, security, financial, or operational consequence exists;
- doctrine trace and conformance tests are required;
- Harm Gate applies before consequential use.

Prototype speed must not silently become production authority.

## Current Reference Implementation Validation Status

The Python file contains a self-test suite. Those tests provide useful implementation evidence, but they should initially be treated as **code consistency tests** unless independently mapped back to the Master and checked against external or known cases.

The reference implementation therefore enters the framework as:

**STATUS: IMPLEMENTED / PARTIALLY CONFORMANCE-TESTED / NOT YET FULLY VALIDATED**

## Required Next Audit

Run the Forensic Framework Auditor against the Python reference implementation and produce a doctrine-to-code matrix with:

- code object/function;
- claimed Master section;
- exact doctrine requirement;
- implementation behavior;
- match / partial / mismatch / ambiguous;
- unstated assumptions;
- test coverage;
- operator consequence;
- recommended repair.

Do not change doctrine solely to make the code pass.


---

# Skill Pack

# VesselFramework Skills — v3.4

Portable combined skill pack.

Load `VesselFramework_Core.md` first, then use the relevant skill section below.

---



<!-- BEGIN SKILL: VesselFramework Analyst -->

# VesselFramework Analyst — Thin Skill

## Purpose

This skill is an execution layer, not a second copy of the Master. Its job is to apply the canonical framework without creating doctrine drift.

## Required sequence

1. State the subject and decision question.
2. Tag important inputs as SOURCE-ESTABLISHED / FRAMEWORK SYNTHESIS / WORKING HYPOTHESIS / ILLUSTRATIVE.
3. Trace Decision Provenance when evidence is being converted into authority or action.
4. Run only the pillars that materially discriminate the problem; a full four-pillar pass is not mandatory when a pillar adds no information.
5. Test at least one alternative explanation.
6. Identify the binding bottleneck and whether the evidence actually supports constitutive vs instrumental failure.
7. Run the Primary Brute-Force Stealth Maskirovka check first, then apply reference variants only when their trigger conditions are independently evidenced.
8. State confidence using reliability, independence, directness, diagnosticity, assumption sensitivity, and alternatives.
9. Run the **HARM GATE** before consequential publication, submission, communication, or action; assign an Operator Exposure level and identify safeguards/reversibility.
10. End with a posture and collection/decision implication, not a disguised prediction.
11. Create a prospective Calibration Log entry only when the outcome is not yet known and later observation can grade the posture.

## Prohibited shortcuts

- No "3 sources = high confidence."
- No treating repeated reporting from one origin as independent corroboration.
- No treating silence as evidence without expected observability.
- No declaring a platform backend mechanism from a before/after correlation.
- No equating malware-free with LOTL.
- No calling NIST CSF a certification scheme.
- No treating a retrospective known-outcome case as a predictive HIT.
- No framework revision without a documented validation/calibration cause.
- No consequential recommendation that bypasses the Harm Gate when material operator exposure is foreseeable.

## Output skeleton

**Subject / decision question**  
**Source-status map**  
**Decision Provenance** (if applicable)  
**PARADOX**  
**BOTTLENECK**  
**DUAL LAYER**  
**XFACTOR**  
**Maskirovka test**  
**Alternatives / disconfirming evidence**  
**Confidence basis**  
**HARM GATE / Operator Exposure**  
**Synthesis**  
**Posture / next collection**
---
---
name: iran-intel-briefer
description: >
  Use this skill whenever Christopher needs to produce a Decrypting Loyalty OSINT
  Situation Report on Iran, the US-Israel-Iran conflict, or any related theater
  development. Trigger on: "write up Day N", "brief on Iran today", "what happened
  in the conflict", "update the Iran analysis", "new developments on Epic Fury",
  "write a sit-rep", "IRGC update", "Hormuz", "Pezeshkian", or any request to
  document or analyze an active intelligence situation in the format Christopher
  uses. Also trigger when asked to continue the Iran Day series or produce a new
  entry in any multi-day OSINT brief format. Do NOT wait for Christopher to say
  "use the iran-intel-briefer skill" — if the topic is active conflict analysis or
  OSINT reporting, use this skill immediately.
---


## Language Mediation Requirement — v3.3

Do not infer operator voice from spelling, grammar, punctuation, fragments, or other surface irregularities in a single input. Recover semantic intent first. Do not merely mirror or polish the input; add analytical value, then translate the result into usable operator-facing language.

<!-- END SKILL: VesselFramework Analyst -->

---

<!-- BEGIN SKILL: VesselFramework Forecaster -->

# VesselFramework Forecaster — Integrated Skill v1.1

## Purpose and Authority

Use this skill when a current assessment must become a prospective, falsifiable,
time-bounded forecast. It is subordinate to Evidence Assurance, the Provenance
Firewall, Decision Provenance, the Four Pillars, Harm Gate/Operator Exposure,
Forward Posture, the Forensic Auditor, and the Calibration Log.

Do not call an outlook a calibration-grade forecast unless it has a resolvable
outcome, explicit horizon, preserved probability, and predeclared scoring rule.

## Forecasting Sequence

`CURRENT STATE -> PROVENANCE -> CONDITIONS -> ALTERNATIVES -> INDICATORS -> FORECAST -> HARM GATE -> POSTURE -> OBSERVATION -> SCORE -> FEEDBACK`

Required controls:

1. Separate current facts from future inference and label source status.
2. Define one focal outcome, resolution rule, time window, and principal alternative.
3. Trace evidence lineage; repeated reporting from one origin is one stream.
4. Apply PARADOX, BOTTLENECK/CANNOT-WILL NOT, DUAL LAYER, and XFACTOR only where diagnostic.
5. Distinguish necessary, enabling, blocking, trigger, and dependency conditions.
6. Specify leading indicators, lead time, observability, specificity, source path, and false-positive risk.
7. State disconfirmers and use absence only when the signal should have been observable.
8. Keep probability separate from analytical confidence and action posture.
9. Run Harm Gate and Forward Posture before consequential preparation or action.
10. Freeze the original forecast before the outcome is known; revise by version, never silently overwrite.

## Forecast Lifecycle

`DRAFT -> QUALITY-CHECKED -> FROZEN -> ACTIVE -> RESOLVED`

Use `EXPIRED` when the window closes without a resolvable outcome and
`WITHDRAWN` only when the question becomes invalid for a documented external
reason. Withdrawal never erases a miss. Every transition records time, actor,
reason, evidence, and next review or resolution date.

## Minimum Forecast Record

```text
FORECAST ID / CALIBRATION ID:
QUESTION AND OUTCOME DEFINITION:
HORIZON / RESOLUTION DATE:
INITIAL AND CURRENT PROBABILITY:
ANALYTICAL CONFIDENCE:
CURRENT STATE / SOURCE STATUS / PROVENANCE:
FOCAL OUTCOME / PRINCIPAL ALTERNATIVE:
NECESSARY / ENABLING / BLOCKING CONDITIONS:
TRIGGERS / LEADING INDICATORS / DISCONFIRMERS:
BOTTLENECK / CANNOT-WILL NOT:
XFACTOR / KEY ASSUMPTIONS:
HARM GATE / OPERATOR EXPOSURE:
FORWARD REGISTER / ALIGNMENT / POSTURE:
LOW-REGRET PREPARATION / ACTIONS NOT JUSTIFIED:
NEXT REVIEW / REVISION HISTORY:
OUTCOME / RESOLUTION EVIDENCE / SCORE: LOCKED UNTIL RESOLUTION
```

## Cross-Skill Routing

- **Analyst:** provides the current-state assessment, source statuses, provenance, pillars, alternatives, and confidence basis.
- **Theater/domain briefer:** provides timelines, actors, collection gaps, and candidate indicators; it does not establish probability by reporting volume.
- **Applied analytics/methods:** supports baselines, measurement design, uncertainty, scoring, and aggregation; it does not replace provenance or authorize causal claims.
- **Professional communication:** translates a forecast without removing its probability, horizon, uncertainty, or source limits.
- **Forensic Auditor:** tests outcome definitions, revision history, hindsight contamination, indicator quality, timing, and hidden misses.
- **Harm Gate/Forward Posture:** governs what preparation or action is justified; probability alone does not authorize restrictive or irreversible action.

## Forecasting Intake Adapter (Canonical Form)

Use one canonical intake format for all prospective forecasts in this package:

- focused situational question;
- timestamp and timezone of the forecasting decision;
- decision horizon and explicit resolution window;
- source set and provenance status;
- principal alternative and disconfirmers;
- indicators, observability path, and scoring rule.

Do not use symbolic or divinatory inputs as evidentiary sources. Forecast
objects must be built from ordinary-world evidence, provenance checks,
alternatives testing, and explicit resolution criteria. Legal, medical,
financial, safety, employment, and reputational decisions remain governed by the
ordinary evidence, Harm Gate, Forward Posture, and Startle Gate controls.

## Calibration and Scoring

For binary outcomes, use `Brier Score = (p - o)^2` where `p` is the frozen
probability and `o` is the resolved outcome. Aggregate across a meaningful sample
and inspect calibration, resolution, domain, horizon, timing, indicator value,
assumption failures, and Harm-Gate performance. Do not claim superiority without
an appropriate benchmark. A retrospective case is validation, not a calibration
hit.

## Forecast Quality Gate

If any of the following is missing, mark `NOT CALIBRATION-READY`: observable
outcome, horizon, source/provenance check, alternative, disconfirmer,
observability assessment, Harm Gate, frozen record, or scoring rule.

<!-- END SKILL: VesselFramework Forecaster -->

---


<!-- BEGIN SKILL: Theater & General Intelligence Briefer -->

# Theater & General Intelligence Briefer — VesselFramework Skill

## Purpose

This skill produces decision-relevant intelligence briefs for a theater, country, campaign, organization, threat network, or cross-domain strategic problem. It is not tied to Iran or to any single geography.

The briefer exists to turn fragmented reporting into a disciplined assessment without pretending that collection is complete or that a posture is a prediction.

## Scope

Use for:
- theater-level military and geopolitical assessment;
- country or regional intelligence briefs;
- campaign and operational environment tracking;
- nation-state and non-state threat analysis;
- cyber, influence, logistics, economic, industrial, and political developments when they materially affect the theater;
- recurring daily or periodic intelligence products;
- open-source intelligence synthesis with explicit source-status controls.

## Required Analytical Sequence

1. **Question / Decision Need**
   - What does the consumer actually need to understand or decide?

2. **Theater / System Boundaries**
   - What geography, actors, time horizon, and domains matter?
   - What is deliberately out of scope?

3. **Signals**
   - What changed?
   - Which indicators are new, persistent, contradictory, or absent?

4. **Provenance**
   - What is source-established?
   - What is framework synthesis?
   - What remains a working hypothesis?
   - What is merely illustrative?

5. **Baseline**
   - What would normal behavior look like?
   - Is the observed signal meaningfully different from baseline?

6. **Alternatives**
   - What else could explain the same evidence?
   - What evidence would discriminate between explanations?

7. **VesselFramework Layer**
   - PARADOX
   - BOTTLENECK
   - DUAL LAYER
   - XFACTOR
   - CANNOT vs. WILL NOT where relevant
    - Maskirovka check architecture only when supported

8. **Authority / Consequence**
   - What kind of decision could this assessment justify?
   - Does the evidence assurance support that level of authority?

9. **Harm Gate**
   - What happens to the operator or consumer if this is wrong, misunderstood, leaked, or acted on too aggressively?
   - What safeguards or caveats are required?

10. **Posture**
    - What should the consumer believe, watch, prepare, or do given current evidence?
    - A posture is not a prediction.

## Brief Structure

### 1. Executive Assessment
3–5 short paragraphs. Lead with what changed, why it matters, and the current posture.

### 2. Key Indicators
Use a compact table or bullet grid:
- indicator;
- current status;
- change from baseline;
- source status;
- why it matters.

### 3. Lead Development
One or two analytical sections on the most consequential change.

### 4. Supporting Developments
Two to four shorter sections covering secondary developments that materially affect the assessment.

### 5. VesselFramework Analysis
Apply only the pillars that add diagnostic value. Do not force all four pillars into every brief.

### 6. Alternatives / Contradictions
State the strongest competing explanation and what would make the current assessment wrong.

### 7. Open Questions
Carry unresolved intelligence gaps forward.

### 8. Watch Items
What indicators should change the posture during the next reporting period?

### 9. Harm Gate / Operator Exposure
State any material publication, security, privacy, legal, operational, or reputational risk associated with the brief or recommended action.

## Source Discipline

Use the VesselFramework source-status layer:
**SOURCE-ESTABLISHED → FRAMEWORK SYNTHESIS → WORKING HYPOTHESIS → ILLUSTRATIVE**

Rules:
- do not convert repetition into corroboration;
- count sources only when meaningfully independent;
- preserve source scope;
- distinguish observed absence from collection failure;
- distinguish retrospective explanation from prospective calibration;
- separate fact, inference, and judgment.

## Confidence

Confidence is based on:
- source reliability;
- independence;
- directness;
- diagnosticity;
- assumption sensitivity;
- strength of alternatives;
- observability;
- consequence of error.

Do not derive confidence from raw source count.

## Voice

Write like an intelligence professional, not a news article and not a generic LLM.
Use plain language where possible.
Keep technical terms when they carry real analytical meaning.
Do not dramatize.
Do not hide uncertainty.
Do not inflate weak evidence into strategic certainty.

## Language Mediation Requirement — v3.3

The LLM is an intermediary analytical device. Recover meaning before style.
Do not infer operator voice from spelling, grammar, fragments, punctuation, or other surface irregularities in a single sample.
Do not merely polish or mirror the operator's input.
Add analytical value through distinction, evidence, alternatives, dependencies, tests, or decision relevance, then translate the result into usable operator-facing language.

<!-- END SKILL: Theater & General Intelligence Briefer -->

---


<!-- BEGIN SKILL: Applied Analytics & Methods -->

# Applied Analytics & Methods — VesselFramework Skill

## Two-layer rule

**Teacher Model:** instructor terminology, course sequence, conventions, assignment expectations.  
**Mother Framework:** WHAT → WHY → WHERE → DEPENDENCIES → FAILURE → EVIDENCE → DECISION.

Never silently replace the Teacher Model with a technically deeper convention on graded work.

## Master statistical chain

CONSTRUCT → OPERATIONALIZATION → VARIABLE → IV/DV → CLAIM →
DESIGN → MEASUREMENT → DATA TYPE → DESCRIPTIVE STATISTICS →
DISTRIBUTION/ASSUMPTIONS → TEST SELECTION → R COMPUTATION →
STATISTICAL OUTPUT → DECISION RULE → STATISTICAL DECISION →
EFFECT SIZE → DEFENSIBLE CONCLUSION

## Decision Provenance translation

RESEARCH QUESTION → DATA PROVENANCE → CODING/TRANSFORMATION →
DESIGN/CONTEXT → ASSUMPTIONS → TEST → R OUTPUT → ALTERNATIVES →
EVIDENCE ASSURANCE → ALPHA/DECISION RULE → CONCLUSION AUTHORITY →
EFFECT SIZE → FEEDBACK

## Permanent checks

- Does the conclusion outrun the design or evidence?
- Did I classify relationship vs difference before interpreting p?
- Did I distinguish observation, existing groups, manipulation, and random assignment?
- Is alpha being treated as a decision rule rather than evidence?
- Is p being treated as a statistical result rather than a posterior probability that H0 is true?
- Does effect size answer magnitude rather than significance?
- What upstream design/measurement choice limits the inference?

## R rule

Never say "R decided."  
Use: "R calculated the statistical output; I interpreted that evidence under the specified rule and design."

## Graded-work boundary

Do not pre-compute or fill answer sheets for graded assignments. Expose the reasoning path, use ungraded analogs, critique the learner's attempted answer, and preserve instructor-facing terminology.

## Adaptive update loop

INGEST → CLASSIFY → LOCATE → TRANSLATE → CONNECT → TEST → UPDATE → VERSION

Every correction records:
1. prior belief,
2. evidence of the problem,
3. corrected rule,
4. upstream cause,
5. framework change that prevents recurrence.
---
---
name: christopher-vessel-linkedin
description: >
  Use this skill whenever Christopher Vessell needs LinkedIn content — posts, carousel cards, stories, cover letters, job application positioning, or professional profile updates. This skill encodes Christopher's complete professional identity, analytical voice, subject matter expertise, and the Decrypting Loyalty content format. Trigger whenever Christopher asks for LinkedIn content, job application writing, professional bio, or any content meant for professional audiences. Also trigger when he asks to "turn this into a post," "make me a card," "write my story," or wants to present his work to a new audience — even if he doesn't say "LinkedIn" explicitly. The skill produces platform-optimized content in Christopher's voice, not generic AI writing.
---


## Language Mediation Requirement — v3.3

Do not infer operator voice from spelling, grammar, punctuation, fragments, or other surface irregularities in a single input. Recover semantic intent first. Do not merely mirror or polish the input; add analytical value, then translate the result into usable operator-facing language.

<!-- END SKILL: Applied Analytics & Methods -->

---


<!-- BEGIN SKILL: Professional Marketing & Positioning -->

# Professional Marketing & Positioning — VesselFramework Skill

## Purpose

This skill supports professional marketing, positioning, public communication, thought leadership, networking, career materials, and platform strategy without turning the operator into a generic personal brand.

It replaces the narrower LinkedIn-only skill.

## Scope

Use for:
- LinkedIn posts and articles;
- professional bios and About sections;
- resumes, cover letters, and application positioning;
- conference or panel abstracts;
- portfolio descriptions;
- professional website copy;
- outreach messages;
- thought-leadership content;
- project and research positioning;
- referral, affiliate, or promotional content when appropriate;
- audience and channel strategy.

## Core Rule

Professional marketing is not decoration. It is a decision problem:

**Who needs to understand what value, why should they believe it, what evidence supports it, and what action should follow?**

## Required Sequence

1. **Objective**
   - What outcome is being sought?
   - Awareness, credibility, conversation, referral, application, hiring, speaking opportunity, conversion, or relationship?

2. **Audience**
   - Who is the actual decision-maker or reader?
   - What do they care about?
   - What would make them distrust the message?

3. **Positioning**
   - What capability, problem, or point of view is being positioned?
   - What makes it distinct without making unsupported novelty claims?

4. **Evidence**
   - What work, experience, artifact, result, framework, source, or example supports the claim?

5. **Channel**
   - LinkedIn, email, resume, website, application, presentation, article, or another channel?
   - What does that channel reward or punish?

6. **Risk**
   - Academic integrity;
   - employer/client confidentiality;
   - disclosure obligations;
   - financial conflicts;
   - reputational exposure;
   - spam or platform-policy risk;
   - privacy/security exposure.

7. **Message**
   - What should the audience remember?
   - What should they do next?

8. **Harm Gate**
   - Could this damage credibility, employment, relationships, legal standing, privacy, finances, or long-term professional identity?
   - What needs to be disclosed, removed, softened, or independently verified?

## Professional Voice

The operator's professional voice should be:
- analytical;
- curious;
- evidence-aware;
- willing to show reasoning;
- specific rather than performative;
- comfortable asking hard questions;
- not inflated into certainty;
- not rewritten into generic executive-speak.

Avoid:
- generic motivational framing;
- fake vulnerability;
- engagement bait;
- exaggerated expertise;
- unsupported "thought leader" language;
- formulaic LLM transitions;
- excessive em dashes;
- empty claims such as "game-changing," "transformative," or "revolutionary" unless directly justified.

## Content Architecture

A strong professional post usually contains:
- a real observation, problem, or tension;
- a concrete example;
- the analytical distinction;
- why it matters to the intended audience;
- a restrained conclusion or question.

Do not force a fixed template when the idea works better in another form.

## Evidence / Claim Calibration

Before publication:
- separate what was observed from what is inferred;
- verify volatile facts;
- preserve source scope;
- do not overstate causality;
- do not claim originality, ownership, or first discovery without support;
- do not use professional polish to hide uncertainty.

## Promotional / Referral Content

When there is a material personal benefit:
- disclose the relationship clearly and near the recommendation/link;
- do not conceal referral mechanics;
- do not spam;
- do not add incentives that violate program terms;
- do not imply endorsement by an employer, university, or other organization unless authorized;
- do not let a short-term conversion goal damage long-term professional positioning.

## Job / Opportunity Positioning

Translate work into:
- problem addressed;
- decisions supported;
- methods used;
- evidence produced;
- constraints handled;
- outcome or learning;
- relevance to the target role.

Do not merely restate job descriptions or resume bullets.

## Language Mediation Requirement — v3.3

The LLM is an intermediary device, not the operator's voice.
Do not learn style from one noisy or adversarial sample.
Preserve semantic intent, causal order, and meaningful phrasing, but do not imitate spelling or grammar errors.
Do not return the operator's own input with generic professional polish and call it value.
Add positioning, evidence, risk, audience, or decision logic first; then write.

<!-- END SKILL: Professional Marketing & Positioning -->

---


<!-- BEGIN SKILL: Version Consolidator -->

# Version Consolidator

Identifies near-duplicate documents, compares them, and produces a canonical merged
master with a consolidation report. Handles hash-suffixed copies, version-numbered
files, and semantic duplicates (same content, different names).

---

## Known Duplicates in Christopher's Workspace

The drive survey (2026-04-20) identified these duplicate pairs in `/mnt/uploads/`:

| Base Document | Versions Found | Status |
|---|---|---|
| `VesselFramework_OSINT_Integration.docx` | + `-da0f6e99.docx` | Needs consolidation |
| `VesselFramework_OSINT_Prompt_Library.docx` | + `-20225a77.docx` | Needs consolidation |
| `VesselFramework_Grounded_Documentation.docx` | uploads/ + outputs/ copy | Needs canonical |
| `vessel_osint.py` | + `-14fc74b1.py` | Needs consolidation |
| `vessel_osint_setup.sh` | + `-2f3c9506.sh` | Needs consolidation |
| `Vessell_Iran_Full_Theater_Analysis_v2.docx` | + `Vessell_Iran_Theater_Analysis_Mar2026.docx` | Semantic duplicate |

---

## Phase 1 — Detection

### Automatic duplicate detection
Run the bundled `find_duplicates.py` script on any directory:

```bash
python scripts/find_duplicates.py /path/to/folder
```

The script detects:
- **Hash-suffixed copies:** `filename-[a-f0-9]{8}.ext` pattern (Cowork upload artifacts)
- **Version-numbered variants:** `_v2`, `_v3`, `final`, `FINAL`, `draft`, `old`, `backup`
- **Semantic duplicates:** same base name, different date or slight variation

### Manual detection signals
- File pairs with identical names except for an 8-character hex suffix → always duplicates
- Same document topic with different dates in the name → likely iterative versions
- Same file in both uploads/ and outputs/ → one was generated from the other

### Detection output format
```
DUPLICATE GROUP: VesselFramework_OSINT_Integration
  [A] VesselFramework_OSINT_Integration.docx       | 2026-04-14 | 48 KB
  [B] VesselFramework_OSINT_Integration-da0f6e99.docx | 2026-04-14 | 47 KB
  Size delta: 1 KB | Same date: YES | Likely: A is canonical, B is upload artifact
```

---

## Phase 2 — Comparison

For each duplicate pair, compare content before deciding what to keep.

### For .docx files
```python
from docx import Document

def compare_docx(path_a, path_b):
    text_a = "\n".join(p.text for p in Document(path_a).paragraphs if p.text.strip())
    text_b = "\n".join(p.text for p in Document(path_b).paragraphs if p.text.strip())
    # Find lines in A not in B and vice versa
    lines_a = set(text_a.splitlines())
    lines_b = set(text_b.splitlines())
    only_in_a = lines_a - lines_b
    only_in_b = lines_b - lines_a
    return only_in_a, only_in_b
```

### For .py / .sh / text files
Use unified diff:
```bash
diff -u file_a.py file_b.py
```

### Comparison output format
```
COMPARISON: VesselFramework_OSINT_Integration [A] vs [B]
  Content in A not in B: 3 paragraphs (likely additions made after copy was made)
  Content in B not in A: 0 paragraphs
  VERDICT: A is the superset. B is safe to archive.
```

---

## Phase 3 — Consolidation

### Decision rules (apply in order)

1. **Hash-suffixed file vs. clean name** → the clean name is canonical; hash-suffix is a Cowork upload artifact. Keep clean name, archive hash-suffix.

2. **v1 vs. v2** → v2 is canonical unless v1 has content v2 removed without replacement. If removal was intentional (content superseded), keep v2.

3. **Semantic duplicates (same topic, different date)** → later date is canonical unless earlier has structural content not carried forward. Compare and merge missing content.

4. **Same file in uploads/ and outputs/** → outputs/ version is the generated/refined version. Keep outputs/. Archive uploads/ if identical, merge if different.

### Merge procedure for .docx
When both versions have unique content:

```python
from docx import Document

def merge_docx(canonical_path, supplement_path, output_path, label="MERGED"):
    canonical = Document(canonical_path)
    supplement = Document(supplement_path)

    canonical_text = set(p.text.strip() for p in canonical.paragraphs if p.text.strip())

    canonical.add_paragraph(f"--- {label}: Content from supplementary version ---")
    for para in supplement.paragraphs:
        if para.text.strip() and para.text.strip() not in canonical_text:
            canonical.add_paragraph(f"[FROM v2] {para.text}")

    canonical.save(output_path)
```

---

## Phase 4 — Output

### Consolidation report
Save as `consolidation_report_[YYYYMMDD].md`:

```markdown


## Language Mediation Requirement — v3.3

Do not infer operator voice from spelling, grammar, punctuation, fragments, or other surface irregularities in a single input. Recover semantic intent first. Do not merely mirror or polish the input; add analytical value, then translate the result into usable operator-facing language.

<!-- END SKILL: Version Consolidator -->

---


---

<!-- BEGIN SKILL: Forensic Framework Auditor -->

# Forensic Framework Auditor — VesselFramework Skill
## Version 1.0 | VesselFramework v3.4

## Purpose

This skill audits an analytical framework, prompt system, workflow, codebase, or LLM-generated artifact for defects that may be hidden by familiarity, repetition, inherited context, model-generated language, or version drift.

It is a **meta-skill**. It does not solve the domain problem first. It inspects the system being used to solve the problem.

The purpose is to answer:

> What in this system can make me wrong, slow me down, mislead the model, preserve bad assumptions, or create harm without being obvious from the output?

## When to Activate

Activate this skill when:
- a framework has been revised repeatedly;
- multiple LLMs contributed to the same artifact;
- outputs feel repetitive, constrained, or strangely model-like;
- coding becomes harder as instructions accumulate;
- an old assumption may be silently controlling current behavior;
- version drift or duplicated rules may exist;
- a model keeps echoing instead of reasoning;
- the operator suspects an inherited defect but cannot locate it;
- a major framework revision is being considered.

Do not activate it automatically for every ordinary task. It is a diagnostic mode.

## Governing Rule

> Treat every suspected defect as a hypothesis until the artifact itself supports it.

Never infer intent from the presence of a defect.

Do not say a model "planted," "hid," or "deliberately inserted" a defect without direct evidence.

## Core Audit Sequence

### 1. Reconstruct

Before criticizing anything, reconstruct the system.

Identify:
- canonical core;
- active skills;
- deprecated skills;
- calibration log;
- load order;
- version numbers;
- constitutional rules;
- domain rules;
- cross-cutting rules.

Build:

`RULE → DEPENDENCY → OUTPUT BEHAVIOR → POSSIBLE FAILURE`

If the system cannot be reconstructed from the files alone, that is itself a portability defect.

### 2. Establish Provenance

Classify each important claim as:

**SOURCE-ESTABLISHED**
→ directly visible in the artifact

**FRAMEWORK SYNTHESIS**
→ supported by multiple internal features

**WORKING HYPOTHESIS**
→ plausible but unproven

**UNSUPPORTED**
→ asserted without sufficient evidence

Never allow a suspicion to move directly to SOURCE-ESTABLISHED.

### 3. Locate Defects

Search for:
- factual defects;
- logical contradictions;
- circular reasoning;
- version drift;
- duplicated doctrine;
- hidden context dependency;
- LLM-language contamination;
- style-capture risk;
- calibration contamination;
- coding overconstraint;
- prompt bloat;
- skill/core conflicts;
- unsupported attribution or originality claims;
- operator-harm risks;
- portability defects;
- obsolete artifacts;
- unfalsifiable rules.

### 4. Find the Mechanism

For every defect ask:

- What exact text or structure causes it?
- What behavior could it produce?
- Under what conditions would that behavior appear?
- Is the failure local or systemic?
- Is the defect in the rule, the implementation, the context, or the interaction between them?

Do not stop at "this wording is bad."

### 5. Stress-Test

Use adversarial cases.

At minimum test:

**False confidence**
→ user provides a confident false claim.

**Noisy surface form**
→ user intentionally provides bad spelling/grammar.

**Fast reversible task**
→ user asks for a quick prototype.

**High-consequence public action**
→ user asks for something reputationally or legally consequential.

**Repeated non-independent sources**
→ several sources repeat one upstream claim.

**Skill/core conflict**
→ skill says one thing, Master says another.

**Retrospective success**
→ past success is presented as if it were prospective calibration.

**Repeated model phrase**
→ LLM-generated language appears enough times to look like doctrine.

### 6. Grade the Defect

Primary class:

- D1 Factual defect
- D2 Logical contradiction
- D3 Circular reasoning
- D4 Version drift
- D5 Duplicate doctrine
- D6 Hidden context dependency
- D7 LLM-language contamination
- D8 Style-capture risk
- D9 Calibration contamination
- D10 Coding overconstraint
- D11 Prompt-bloat / attention competition
- D12 Skill/core conflict
- D13 Unsupported attribution/originality claim
- D14 Operator-harm risk
- D15 Portability defect
- D16 Obsolete/deprecated artifact
- D17 Missing test / unfalsifiable rule
- D18 Other

Severity:
- CRITICAL
- HIGH
- MEDIUM
- LOW

Confidence:
- HIGH
- MODERATE
- LOW

### 7. Repair Minimally

The default is not to rewrite the whole system.

For each confirmed defect:
- isolate the smallest responsible rule;
- preserve useful doctrine;
- remove duplicated or unsupported scaffolding;
- make the rule falsifiable if possible;
- add a test;
- document the change;
- version the artifact.

A repair that creates more complexity than the defect may be a new defect.

### 8. Re-Test

Every repair needs:
- the original failure case;
- at least one new analogous case;
- a result;
- a decision whether the repair worked.

No repair is considered validated merely because the revised wording looks better.

## Required Defect Record

For every finding:

### DEFECT [ID] — [Short Title]

**Class:**  
**Severity:**  
**Confidence:**  
**File / section:**  
**Exact evidence:**  
**What is wrong:**  
**Why it matters:**  
**Likely failure behavior:**  
**Is intent established?** Yes / No  
**Smallest repair:**  
**How to test the repair:**  

Do not merge unrelated defects.

## Coding / Vibe-Coding Audit Layer

When the target is an LLM-assisted coding system, add these checks:

### Overconstraint
Are too many rules blocking fast reversible work?

### Premature abstraction
Is the system forcing architecture before the problem is understood?

### Prompt bloat
Is framework context competing with the coding task?

### Instruction collision
Are general analytical safeguards interfering with local technical instructions?

### Excessive preservation
Is the system protecting old code/structure that should be refactored?

### Echo loops
Is the model returning framework language instead of solving the coding problem?

### False continuity
Does the system assume files, functions, state, or variables that do not exist?

### Authority mismatch
Is the model over-cautious on reversible code and under-cautious on consequential deployment?

### Hidden technical debt
Are deprecated names, copied logic, duplicate functions, obsolete references, or conflicting versions still active?

## Language-Mediation Audit

The auditor must distinguish semantic content from surface form.

A noisy input may be:
- adversarial;
- diagnostic;
- dictated;
- copied;
- rushed;
- intentionally malformed.

Never infer operator voice from one sample.

Test whether the system:
1. recovers meaning;
2. avoids imitation;
3. adds analytical value;
4. preserves operator intent;
5. translates without impersonating.

## Calibration Boundary

The forensic auditor must distinguish:

**Validation**
→ Does the rule/system work?

**Calibration**
→ Was a prospective posture graded against a known outcome?

**Post-mortem**
→ What failed after the fact?

**Anecdote**
→ An observed example without enough structure to validate or calibrate.

Never convert one into another for rhetorical strength.

## Harm Gate

Before recommending a repair, ask whether the repair could:
- erase useful provenance;
- damage academic integrity;
- expose confidential data;
- weaken security;
- create legal/reputational risk;
- delete a safeguard that only appears redundant;
- make irreversible changes without a recovery path.

For high-exposure changes, prefer:
- copy;
- branch;
- backup;
- diff;
- test;
- then replace.

## Output Modes

### Rapid Defect Scan
Top 5–10 likely defects with evidence and severity.

### Full Forensic Audit
Complete defect register + conflict matrix + stress tests + repair plan.

### Coding Barrier Audit
Focus only on barriers affecting LLM-assisted coding.

### Clean-Room Review
Reconstruct necessary doctrine from first principles, then compare it against the current artifact without assuming the current structure is correct.

### Regression Audit
After a repair, test whether the old failure is gone and whether a new defect was introduced.

## Meta-Rule

> The framework itself is evidence, not authority.

No rule is protected from inspection merely because it is already inside VesselFramework.

## Success Criterion

This skill succeeds when it can:
- locate a defect the ordinary analytical workflow did not expose;
- show the mechanism;
- separate evidence from suspicion;
- propose a minimal repair;
- test whether the repair works;
- avoid replacing operator doctrine with new LLM scaffolding.

## Adaptive Loop

`RECONSTRUCT → PROVENANCE → LOCATE → STRESS-TEST → GRADE → REPAIR → RE-TEST → LOG → VERSION`

<!-- END SKILL: Forensic Framework Auditor -->


---

# Calibration Addition — v3.5

## V-005 — Executable Reference Implementation

**Type:** Prospective doctrine/code validation case  
**Artifact:** `vesselframework_reference.py` v1.0  
**Status:** New executable reference layer; not yet fully validated  
**Claim permitted:** The implementation operationalizes selected VesselFramework rules and contains executable consistency tests.  
**Claims not yet permitted:** canonical production implementation; complete doctrine conformance; independently validated analytical engine.  
**Validation target:** Determine whether each coded behavior matches the Master without adding hidden assumptions or losing doctrinal conditions.  
**Required evidence:** doctrine-to-code trace, conformance tests, adversarial boundary tests, and defect log.  
**Revision rule:** A code failure does not automatically change doctrine; first locate whether the failure belongs to doctrine, implementation, test, or translation.  
**Engine weights:** No production analytical weights changed.


---

# Executable Appendix A — VesselFramework Reference Implementation v1.0

The following code is preserved verbatim from the implementation supplied for integration into this meta-framework. fileciteturn34file0

```python
#!/usr/bin/env python3
"""
VesselFramework Reference Implementation — v1.0 (NEW WORK)
============================================================

Status: This is a freshly written implementation, authored now, from the
doctrine actually specified in VesselFramework_Master.md v3.4 (Section 0.1
Evidence Assurance, Section 0.2 Harm Gate / Operator Exposure, Section 1
Four Pillars, Section 2 Maskirovka Check Architecture). It is NOT a recovery of the
"VessellFramework_Production_v4.pyz" or any other build artifact referenced
in Master Section 11 — this program has no relationship to those files.
Nothing here should be described as "byte-identical," "canonical," or
"MD5-matched" to anything else; it is simply new code.

What this script does:
  - Enforces the evidence-status discipline (SOURCE-ESTABLISHED /
    FRAMEWORK SYNTHESIS / WORKING HYPOTHESIS / ILLUSTRATIVE) as real data,
    not free text.
  - Runs the Harm Gate as an actual checklist that must be answered before
    a "consequential" action is allowed to be marked cleared.
  - Computes an Operator Exposure (OE) level from the Harm Gate answers,
    per the Master's LOW / MODERATE / HIGH / SEVERE ladder.
    - Provides small, honest scaffolds for the four pillars (PARADOX,
        BOTTLENECK, DUAL LAYER, XFACTOR) and the four Maskirovka variants —
    these structure and validate analyst input, they do NOT generate
    analytical conclusions. The framework is explicit that pillar findings
    are produced by an analyst reasoning over evidence, not by a scoring
    formula; this code refuses to pretend otherwise.
  - Applies the "three sources repeating one report count as one stream"
    rule and the "multiple Maskirovka variants sharing evidence don't
    automatically raise confidence" rule as real, testable logic.

Run it directly to see a worked demo:
    python3 vesselframework_reference.py

Run the test suite:
    python3 vesselframework_reference.py --test
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Section 0.1 — Evidence Assurance & Source Discipline
# ---------------------------------------------------------------------------

class SourceStatus(Enum):
    SOURCE_ESTABLISHED = "SOURCE-ESTABLISHED"
    FRAMEWORK_SYNTHESIS = "FRAMEWORK SYNTHESIS"
    WORKING_HYPOTHESIS = "WORKING HYPOTHESIS"
    ILLUSTRATIVE = "ILLUSTRATIVE"


@dataclass
class EvidenceItem:
    """One piece of evidence, tagged per Master Section 0.1."""
    description: str
    status: SourceStatus
    source_id: str  # e.g. "CISA-2024-AA24-038A" or "operator-observation-01"
    upstream_of: Optional[str] = None  # source_id this item repeats/derives from, if any


class EvidenceSet:
    """
    A collection of evidence with independence-aware counting.

    Master Section 7 (Voice Standards): "Three sources repeating one
    original report count as one evidentiary stream, not three."
    This is implemented literally: items that share an `upstream_of`
    root collapse into a single independent stream when counted.
    """

    def __init__(self, items: Optional[list[EvidenceItem]] = None):
        self.items: list[EvidenceItem] = items or []

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)

    def _root(self, item: EvidenceItem) -> str:
        """Walk upstream_of chains to find the ultimate root source_id."""
        seen = set()
        current = item
        by_id = {i.source_id: i for i in self.items}
        while current.upstream_of and current.upstream_of in by_id:
            if current.source_id in seen:
                break  # cycle guard
            seen.add(current.source_id)
            current = by_id[current.upstream_of]
        return current.source_id

    def independent_stream_count(self) -> int:
        """Count of genuinely independent evidentiary streams."""
        roots = {self._root(item) for item in self.items}
        return len(roots)

    def established_count(self) -> int:
        return sum(1 for i in self.items if i.status == SourceStatus.SOURCE_ESTABLISHED)

    def has_only_illustrative(self) -> bool:
        return len(self.items) > 0 and all(
            i.status == SourceStatus.ILLUSTRATIVE for i in self.items
        )


# ---------------------------------------------------------------------------
# Section 0.2 — Harm Gate / Operator Exposure
# ---------------------------------------------------------------------------

class OperatorExposure(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE / IRREVERSIBLE"


@dataclass
class HarmGateAnswers:
    """
    Answers to the seven Harm Gate questions from Master Section 0.2.
    Each field is a plain-language answer; `risk_present` flags are what
    drive the OE calculation. Leave a flag False only if you have an
    actual reason, not because the field is unfamiliar.
    """
    accuracy_risk: bool
    accuracy_note: str = ""
    academic_risk: bool = False
    academic_note: str = ""
    professional_risk: bool = False
    professional_note: str = ""
    legal_risk: bool = False
    legal_note: str = ""
    financial_security_risk: bool = False
    financial_security_note: str = ""
    hard_to_reverse: bool = False
    reversibility_note: str = ""
    benefit_proportionate: bool = True
    proportionality_note: str = ""


@dataclass
class HarmGateResult:
    exposure: OperatorExposure
    risk_count: int
    required_safeguards: list[str]
    cleared: bool
    blocking_reasons: list[str] = field(default_factory=list)


def run_harm_gate(answers: HarmGateAnswers) -> HarmGateResult:
    """
    Compute Operator Exposure and required safeguards from Harm Gate
    answers. This does not "approve" or "deny" the action -- Master is
    explicit that "The Harm Gate does not automatically prohibit action.
    It changes the required assurance, safeguards, wording, review, or
    reversibility of the action." This function reflects that: it always
    returns `cleared=True` UNLESS proportionality fails outright, but it
    escalates the safeguard list as risk rises.
    """
    risk_flags = [
        answers.accuracy_risk,
        answers.academic_risk,
        answers.professional_risk,
        answers.legal_risk,
        answers.financial_security_risk,
    ]
    risk_count = sum(risk_flags)

    if answers.hard_to_reverse and risk_count >= 2:
        exposure = OperatorExposure.SEVERE
    elif answers.hard_to_reverse or risk_count >= 3:
        exposure = OperatorExposure.HIGH
    elif risk_count >= 1:
        exposure = OperatorExposure.MODERATE
    else:
        exposure = OperatorExposure.LOW

    safeguards: list[str] = []
    if exposure == OperatorExposure.LOW:
        safeguards.append("Ordinary evidence threshold and normal review.")
    if exposure == OperatorExposure.MODERATE:
        safeguards.append("Explicit Harm Gate write-up plus at least one viable mitigation or alternative.")
    if exposure == OperatorExposure.HIGH:
        safeguards.append("Stronger provenance and alternatives testing.")
        safeguards.append("Claim calibration against actual evidence strength.")
        safeguards.append("Pre-action verification step before proceeding.")
    if exposure == OperatorExposure.SEVERE:
        safeguards.append("Independent human review before action, where feasible.")
        safeguards.append("Written record of what would have to be wrong for this to fail.")
        safeguards.append("Explicit fallback/undo plan drafted before acting.")

    blocking_reasons: list[str] = []
    cleared = True
    if not answers.benefit_proportionate:
        cleared = False
        blocking_reasons.append(
            "Benefit proportionality failed: expected benefit is not proportionate "
            "to residual risk after reasonable safeguards. Re-scope the action, "
            "don't just add more safeguards."
        )

    return HarmGateResult(
        exposure=exposure,
        risk_count=risk_count,
        required_safeguards=safeguards,
        cleared=cleared,
        blocking_reasons=blocking_reasons,
    )


# ---------------------------------------------------------------------------
# Section 1 — Four Analytical Pillars (structuring scaffolds, not oracles)
# ---------------------------------------------------------------------------

class BottleneckType(Enum):
    CAPABILITY = "capability"
    WILL = "will"
    COORDINATION = "coordination"


class ConstitutiveOrInstrumental(Enum):
    CONSTITUTIVE = "constitutive"  # architecture is wrong for the problem
    INSTRUMENTAL = "instrumental"  # process failure in a correct structure


@dataclass
class ParadoxFinding:
    stated_claim: str
    observable_contradiction: str
    structural_implication: str
    evidence: EvidenceSet

    def render(self) -> str:
        return (
            f"PARADOX: {self.stated_claim}. {self.observable_contradiction}. "
            f"This means {self.structural_implication}. "
            f"[{self.evidence.independent_stream_count()} independent stream(s)]"
        )


@dataclass
class BottleneckFinding:
    system_or_actor: str
    constraint_type: BottleneckType
    nature: ConstitutiveOrInstrumental
    cannot_or_will_not: str  # "CANNOT" or "WILL NOT"
    implication: str

    def __post_init__(self):
        if self.cannot_or_will_not not in ("CANNOT", "WILL NOT"):
            raise ValueError("cannot_or_will_not must be exactly 'CANNOT' or 'WILL NOT'")

    def render(self) -> str:
        return (
            f"BOTTLENECK: {self.system_or_actor}. "
            f"[{self.constraint_type.value}, {self.nature.value}, {self.cannot_or_will_not}]. "
            f"{self.implication}."
        )


@dataclass
class DualLayerFinding:
    public_claim: str
    operational_observable: str
    gap_implication: str

    def render(self) -> str:
        return (
            f"DUAL LAYER — Public: {self.public_claim}. "
            f"Operational: {self.operational_observable}. "
            f"Gap: {self.gap_implication}."
        )


@dataclass
class XFactorFinding:
    variable: str
    why_frame_misses_it: str
    detection_signal: str

    def render(self) -> str:
        return (
            f"XFACTOR: {self.variable}. {self.why_frame_misses_it}. "
            f"Detection signal: {self.detection_signal}."
        )


# ---------------------------------------------------------------------------
# Section 2 — Maskirovka Check Architecture (trigger-gated, not auto-fired)
# ---------------------------------------------------------------------------

class MaskirovkaVariant(Enum):
    BUDGETARY = "Budgetary"
    STRUCTURAL = "Structural"
    OPERATIONAL = "Operational"


@dataclass
class MaskirovkaAssessment:
    variant: MaskirovkaVariant
    trigger_conditions_met: bool
    trigger_evidence: EvidenceSet
    notes: str = ""

    def eligible(self) -> bool:
        """
        Master Section 2: 'Apply a Maskirovka variant only when its trigger
        conditions are independently evidenced.' This is enforced here as
        a real gate, not a suggestion -- an assessment with unmet triggers
        or only a single evidentiary stream cannot be marked eligible.
        """
        return (
            self.trigger_conditions_met
            and self.trigger_evidence.independent_stream_count() >= 1
            and not self.trigger_evidence.has_only_illustrative()
        )


def assess_maskirovka_convergence(
    assessments: list[MaskirovkaAssessment],
) -> str:
    """
    Master Section 2: 'Multiple variants do not automatically create high
    confidence because they may depend on the same underlying evidence;
    confidence rises only when the supporting evidence streams are
    independent and diagnostically consistent.'

    This function checks whether eligible variants share evidentiary
    roots before allowing a "convergence" claim.
    """
    eligible = [a for a in assessments if a.eligible()]
    if len(eligible) < 2:
        return "No multi-variant convergence claim supported (fewer than 2 eligible variants)."

    all_source_ids: list[set[str]] = []
    for a in eligible:
        roots = {a.trigger_evidence._root(item) for item in a.trigger_evidence.items}
        all_source_ids.append(roots)

    shared = set.intersection(*all_source_ids) if all_source_ids else set()
    if shared:
        return (
            f"CAUTION: {len(eligible)} variants ({', '.join(a.variant.value for a in eligible)}) "
            f"appear eligible, but they share evidentiary root(s) {sorted(shared)}. "
            f"Do not treat this as independent convergence -- it may be one signal counted "
            f"three times."
        )
    return (
        f"Convergence supported: {len(eligible)} variants "
        f"({', '.join(a.variant.value for a in eligible)}) are eligible on independent "
        f"evidentiary streams. Treat as a strong prompt for architectural review, "
        f"per Master Section 2 -- not as proof of systemic incapacity on its own."
    )


# ---------------------------------------------------------------------------
# Demo — a single worked example, run end to end
# ---------------------------------------------------------------------------

def _demo() -> None:
    print("=" * 72)
    print("VesselFramework Reference Implementation v1.0 -- worked demo")
    print("=" * 72)

    # --- Evidence discipline ---
    ev = EvidenceSet()
    ev.add(EvidenceItem(
        description="Vendor A telemetry report",
        status=SourceStatus.SOURCE_ESTABLISHED,
        source_id="vendorA-2026",
    ))
    ev.add(EvidenceItem(
        description="News outlet summarizing Vendor A's report",
        status=SourceStatus.SOURCE_ESTABLISHED,
        source_id="news-2026-01",
        upstream_of="vendorA-2026",
    ))
    ev.add(EvidenceItem(
        description="Second news outlet, same Vendor A report",
        status=SourceStatus.SOURCE_ESTABLISHED,
        source_id="news-2026-02",
        upstream_of="vendorA-2026",
    ))
    print(f"\nEvidence items logged: {len(ev.items)}")
    print(f"Independent streams (should collapse 3 -> 1): {ev.independent_stream_count()}")

    # --- Pillars (analyst supplies the content; code just structures + prints it) ---
    paradox = ParadoxFinding(
        stated_claim="Org claims 'insights reach every decision-maker'",
        observable_contradiction="Dashboard adoption measured at 12%",
        structural_implication="the 'last mile' claim is false -- humans remain the actual intelligence layer",
        evidence=ev,
    )
    bottleneck = BottleneckFinding(
        system_or_actor="BI platform rollout",
        constraint_type=BottleneckType.COORDINATION,
        nature=ConstitutiveOrInstrumental.CONSTITUTIVE,
        cannot_or_will_not="WILL NOT",
        implication="fix requires embedding the insight in the decision workflow, not more training",
    )
    dual_layer = DualLayerFinding(
        public_claim="'$200M AI modernization initiative'",
        operational_observable="$12M actually allocated this cycle",
        gap_implication="announcement is political positioning at ~6% of stated commitment",
    )
    xfactor = XFactorFinding(
        variable="Off-budget inter-agency transfers not visible in the stated budget",
        why_frame_misses_it="current frame only tracks the published budget line",
        detection_signal="procurement records diverging from published allocation by >20%",
    )

    print("\n--- Pillar findings ---")
    for f in (paradox, bottleneck, dual_layer, xfactor):
        print(f.render())

    # --- Maskirovka check gate (primary first) ---
    weak_ev = EvidenceSet([EvidenceItem(
        description="Single hypothetical scenario",
        status=SourceStatus.ILLUSTRATIVE,
        source_id="illustrative-1",
    )])
    strong_ev = EvidenceSet([
        EvidenceItem("Procurement filing", SourceStatus.SOURCE_ESTABLISHED, "procurement-01"),
        EvidenceItem("Independent audit finding", SourceStatus.SOURCE_ESTABLISHED, "audit-01"),
    ])

    budgetary = MaskirovkaAssessment(
        variant=MaskirovkaVariant.BUDGETARY,
        trigger_conditions_met=True,
        trigger_evidence=strong_ev,
    )
    structural = MaskirovkaAssessment(
        variant=MaskirovkaVariant.STRUCTURAL,
        trigger_conditions_met=True,
        trigger_evidence=weak_ev,  # only illustrative -- should be ineligible
    )

    print("\n--- Maskirovka check gate (primary first) ---")
    print(f"Budgetary eligible: {budgetary.eligible()}")
    print(f"Structural eligible: {structural.eligible()} (illustrative-only evidence correctly blocks it)")
    print(assess_maskirovka_convergence([budgetary, structural]))

    # --- Harm Gate ---
    answers = HarmGateAnswers(
        accuracy_risk=True,
        accuracy_note="Budget gap claim could be overstated if procurement data is incomplete",
        legal_risk=False,
        hard_to_reverse=False,
        benefit_proportionate=True,
    )
    result = run_harm_gate(answers)

    print("\n--- Harm Gate ---")
    print(f"Operator Exposure: {result.exposure.value}")
    print(f"Cleared: {result.cleared}")
    print("Required safeguards:")
    for s in result.required_safeguards:
        print(f"  - {s}")
    if result.blocking_reasons:
        print("Blocking reasons:")
        for r in result.blocking_reasons:
            print(f"  - {r}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _run_tests() -> int:
    failures = 0

    def check(label: str, condition: bool) -> None:
        nonlocal failures
        status = "PASS" if condition else "FAIL"
        if not condition:
            failures += 1
        print(f"[{status}] {label}")

    # Independence collapsing
    ev = EvidenceSet()
    ev.add(EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root-1"))
    ev.add(EvidenceItem("repeat A", SourceStatus.SOURCE_ESTABLISHED, "r-2", upstream_of="root-1"))
    ev.add(EvidenceItem("repeat B", SourceStatus.SOURCE_ESTABLISHED, "r-3", upstream_of="root-1"))
    check("3 items sharing one root collapse to 1 stream", ev.independent_stream_count() == 1)

    ev2 = EvidenceSet()
    ev2.add(EvidenceItem("A", SourceStatus.SOURCE_ESTABLISHED, "a"))
    ev2.add(EvidenceItem("B", SourceStatus.SOURCE_ESTABLISHED, "b"))
    check("2 genuinely independent items = 2 streams", ev2.independent_stream_count() == 2)

    # Harm Gate ladder
    low = run_harm_gate(HarmGateAnswers(accuracy_risk=False))
    check("No risk flags -> LOW exposure", low.exposure == OperatorExposure.LOW)

    mod = run_harm_gate(HarmGateAnswers(accuracy_risk=True))
    check("One risk flag -> MODERATE exposure", mod.exposure == OperatorExposure.MODERATE)

    high = run_harm_gate(HarmGateAnswers(
        accuracy_risk=True, academic_risk=True, professional_risk=True
    ))
    check("Three risk flags, reversible -> HIGH exposure", high.exposure == OperatorExposure.HIGH)

    severe = run_harm_gate(HarmGateAnswers(
        accuracy_risk=True, legal_risk=True, hard_to_reverse=True
    ))
    check(
        "Hard-to-reverse + 2 risk flags -> SEVERE exposure",
        severe.exposure == OperatorExposure.SEVERE,
    )

    blocked = run_harm_gate(HarmGateAnswers(accuracy_risk=False, benefit_proportionate=False))
    check("Disproportionate benefit blocks clearance", blocked.cleared is False)

    # Maskirovka eligibility gating
    illustrative_only = EvidenceSet([
        EvidenceItem("hypothetical", SourceStatus.ILLUSTRATIVE, "i-1")
    ])
    ma = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, illustrative_only)
    check("Illustrative-only evidence blocks Maskirovka eligibility", ma.eligible() is False)

    real_ev = EvidenceSet([EvidenceItem("filing", SourceStatus.SOURCE_ESTABLISHED, "f-1")])
    ma2 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, real_ev)
    check("Source-established evidence + met trigger -> eligible", ma2.eligible() is True)

    ma3 = MaskirovkaAssessment(MaskirovkaVariant.OPERATIONAL, False, real_ev)
    check("Trigger not met -> not eligible even with good evidence", ma3.eligible() is False)

    # Convergence shared-root detection
    shared_ev_a = EvidenceSet()
    shared_ev_a.add(EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "shared-root"))
    shared_ev_b = EvidenceSet()
    shared_ev_b.add(EvidenceItem("repeat", SourceStatus.SOURCE_ESTABLISHED, "shared-2", upstream_of="shared-root"))
    # note: EvidenceSet._root needs both items in the SAME set to walk the chain;
    # for cross-assessment sharing we simulate by using identical root source_id directly
    shared_ev_b2 = EvidenceSet()
    shared_ev_b2.add(EvidenceItem("same root reused", SourceStatus.SOURCE_ESTABLISHED, "shared-root"))

    a1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, shared_ev_a)
    a2 = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, shared_ev_b2)
    verdict = assess_maskirovka_convergence([a1, a2])
    check("Convergence check flags shared evidentiary root", "CAUTION" in verdict)

    independent_a = EvidenceSet([EvidenceItem("x", SourceStatus.SOURCE_ESTABLISHED, "root-x")])
    independent_b = EvidenceSet([EvidenceItem("y", SourceStatus.SOURCE_ESTABLISHED, "root-y")])
    b1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, independent_a)
    b2 = MaskirovkaAssessment(MaskirovkaVariant.OPERATIONAL, True, independent_b)
    verdict2 = assess_maskirovka_convergence([b1, b2])
    check("Convergence check supports genuinely independent variants", "Convergence supported" in verdict2)

    print(f"\n{'ALL TESTS PASSED' if failures == 0 else f'{failures} TEST(S) FAILED'}")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VesselFramework Reference Implementation v1.0")
    parser.add_argument("--test", action="store_true", help="Run the test suite instead of the demo")
    args = parser.parse_args()

    if args.test:
        sys.exit(_run_tests())
    else:
        _demo()
```


---

# VesselFramework Provenance Firewall & Adaptive Hardening Layer
## Version 1.0 | Framework Revision v3.6

## Purpose

This layer prevents VesselFramework from treating missing provenance as source independence.

The failure being addressed is specific:

> Two findings can derive from the same underlying source while appearing independent because provenance resolution is scoped to separate local EvidenceSet objects.

This firewall moves provenance authority out of local EvidenceSet objects and into a shared registry that all analytical modules must consult.

The firewall also turns each detected provenance failure into a controlled hardening event:

`DETECT → BLOCK / DOWNGRADE → RECORD → PATCH → REGRESSION TEST → PROMOTE RULE → VERSION`

The goal is not to prevent all mistakes. It is to ensure that a discovered mistake becomes harder to repeat.

---

# 1. Constitutional Rule

## NO UNRESOLVED INDEPENDENCE

A source may not be treated as independent merely because no dependency is visible in the local object.

Allowed states:

- **INDEPENDENT — ESTABLISHED**
- **DEPENDENT — ESTABLISHED**
- **UNRESOLVED**
- **CONFLICTING PROVENANCE**

`UNRESOLVED` is not equivalent to `INDEPENDENT`.

When independence matters to a conclusion, unresolved provenance must downgrade assurance or block convergence.

---

# 2. Provenance Firewall

All evidence enters through a shared provenance registry.

Each evidence record has:

- source_id
- description
- status
- upstream_of
- provenance_state
- source_type
- first_seen
- last_seen
- notes

No analytical skill may resolve evidence independence only from its local EvidenceSet.

Required path:

`EvidenceItem → Global Provenance Registry → Root Resolution → Independence Status → Analytical Use`

Local EvidenceSet objects may group evidence, but they do not own provenance truth.

---

# 3. Root Resolution Rule

The root resolver must:

1. search the shared registry;
2. follow upstream links globally;
3. detect missing parents;
4. detect cycles;
5. detect conflicting parent claims;
6. return both:
   - resolved root;
   - provenance state.

Possible outputs:

- RESOLVED
- UNRESOLVED_PARENT
- CYCLE
- CONFLICT
- MISSING_RECORD

Any result other than RESOLVED must be surfaced to the caller.

Silent fallback is prohibited.

---

# 4. Independence Decision Rule

A stream is **independent** only if:

- its lineage is resolved; and
- its resolved root differs from the resolved roots of comparison streams.

If lineage is unresolved:

- do not count the stream as independent;
- do not count it as dependent unless evidence establishes dependence;
- classify it as UNRESOLVED;
- reduce assurance;
- trigger review when the decision depends on convergence.

This creates three buckets:

`INDEPENDENT / DEPENDENT / UNRESOLVED`

Never force unresolved evidence into a binary classification.

---

# 5. Maskirovka Firewall

Before any Maskirovka convergence claim:

### Gate A — Eligibility
Each variant must have:
- trigger conditions met;
- at least one SOURCE-ESTABLISHED evidentiary stream or another operator-approved threshold;
- no pure illustrative support;
- no unresolved provenance that is material to the trigger.

### Gate B — Cross-Variant Provenance
All eligible variants must be compared through the same global provenance registry.

### Gate C — Independence
Convergence is allowed only when supporting roots are resolved and distinct.

### Gate D — Unknowns
If any material source lineage is unresolved:

Return:

`CONVERGENCE STATUS: INDETERMINATE — PROVENANCE UNRESOLVED`

Do not return "supported."

### Gate E — Intent
Operational Maskirovka still requires evidence of hostile intent or hostile capability concealed through mimicry. Defective or misleading output alone does not satisfy this requirement.

---

# 6. Firewall Response Levels

## LEVEL 0 — PASS
All relevant provenance resolved; no conflict.

## LEVEL 1 — WARN
Non-material provenance issue; conclusion unaffected.

## LEVEL 2 — DOWNGRADE
Material unresolved lineage; confidence or assurance must be reduced.

## LEVEL 3 — BLOCK CONVERGENCE
A convergence claim depends on unresolved or conflicting provenance.

## LEVEL 4 — QUARANTINE
Cycle, corrupted lineage, impossible source graph, or suspected provenance poisoning.

Quarantined evidence cannot support a consequential finding until reviewed.

---

# 7. Adaptive Hardening / Patch System

Every provenance failure becomes a patch candidate.

## Patch Record

Each patch must record:

- Patch ID
- Triggering failure
- Date
- Framework version
- Affected rule/module
- Exact failure mechanism
- Minimal repair
- Regression test
- New analogous test
- Whether doctrine changed
- Whether code changed
- Whether skill behavior changed
- Operator exposure
- Status

Possible status:

- OPEN
- PATCHED
- REGRESSION-PASS
- VALIDATED
- REVERTED

---

# 8. Patch Promotion Rule

A discovered defect does not become a permanent rule immediately.

Use:

`OBSERVED FAILURE → LOCAL PATCH → REGRESSION TEST → ANALOGOUS TEST → REPEAT / VALIDATE → PROMOTE`

Promotion criteria:

1. the failure is reproducible;
2. the repair closes the failure;
3. no material new defect appears;
4. the rule generalizes beyond one narrow case;
5. operator approves if doctrine changes.

This prevents the framework from becoming bloated by one-off patches.

---

# 9. Hardening Memory

The framework should maintain a machine-readable hardening registry.

Each recurring defect pattern gets a signature:

- pattern_name
- defect_class
- trigger
- detection_rule
- repair_rule
- regression_test
- first_seen_version
- last_seen_version
- recurrence_count
- severity
- confidence
- promoted_to_doctrine

This creates institutional memory without turning every past error into a universal law.

---

# 10. Patch Precedence

When a known defect signature reappears:

1. detect signature;
2. apply existing defensive rule;
3. flag the recurrence;
4. do not silently patch around it;
5. record whether the same root cause returned;
6. escalate recurrence if the patch failed.

Repeated recurrence after a validated patch means:

`PATCH FAILURE → ROOT-CAUSE REOPENED`

Do not stack additional patches on top of a failed patch without re-auditing the mechanism.

---

# 11. Anti-Bloat Rule

The patching system itself can become a barrier.

Therefore every patch must answer:

- What exact defect does this stop?
- What tasks does it affect?
- Can it be local instead of global?
- What is the cost in prompt size, execution time, or analytical friction?
- Is the patch still needed after root cause removal?

Patches should expire or be consolidated when no longer necessary.

---

# 12. Prototype vs Assurance Behavior

## Prototype Lane

For low-risk reversible work:

- unresolved provenance may be tolerated;
- it must be labeled;
- no strong convergence claim may be made.

## Assurance Lane

For consequential use:

- material provenance must resolve;
- unresolved lineage blocks convergence;
- cycles/conflicts quarantine evidence;
- regression tests must pass after a patch.

---

# 13. Required Regression Tests for This Defect

The following test must exist permanently:

### Cross-Set Shared-Root Test

Registry:
- root
- child_A → root
- child_B → root

Assessment A uses child_A.
Assessment B uses child_B.

Expected:
- both resolve to root;
- independence = false;
- Maskirovka convergence = CAUTION / NOT INDEPENDENT.

### Missing-Parent Test

Assessment A contains:
- child → unknown_root

Expected:
- provenance = UNRESOLVED_PARENT;
- source is not counted as independent;
- convergence = INDETERMINATE if material.

### Cycle Test

A → B
B → A

Expected:
- provenance = CYCLE;
- evidence quarantined;
- no convergence.

### Conflicting-Parent Test

Same source claims:
- parent X
- parent Y

Expected:
- provenance = CONFLICT;
- evidence quarantined.

---

# 14. Integration with Forensic Framework Auditor

Add a mandatory question:

> Is apparent independence proven by a shared provenance graph, or merely inferred from absence of a local dependency marker?

Add new defect classes:

- **D25 — False independence from incomplete provenance**
- **D26 — Provenance graph fracture**
- **D27 — Patch regression**
- **D28 — Patch accumulation / defensive bloat**
- **D29 — Quarantine bypass**

---

# 15. Meta-Framework Hardening Loop

The hardened learning cycle becomes:

`OBSERVE → TRACE → CLASSIFY → FIREWALL → DECIDE → LOG → PATCH → REGRESSION TEST → ANALOGOUS TEST → CALIBRATE → PROMOTE / REVERT → VERSION`

This loop applies to:
- doctrine defects;
- code defects;
- translation defects;
- skill conflicts;
- provenance defects;
- coding barriers;
- calibration failures.

---

# 16. Success Criterion

The firewall succeeds when:

- missing lineage never becomes automatic independence;
- shared ancestry is resolved globally;
- unresolved provenance is visible;
- Maskirovka convergence cannot be strengthened by fractured evidence graphs;
- every discovered provenance failure creates a tested hardening event;
- failed patches are reopened rather than buried under new patches;
- the framework becomes more resistant to known failure modes without becoming unusably rigid.


---

# Executable Reference Update — v1.1 Provenance Firewall

The v1.1 reference implementation adds a shared provenance registry and permanent regression tests for cross-set shared ancestry, unresolved parents, cycles, conflicting parents, and fractured provenance graphs.

```text
[PASS] Cross-set children of same root are detected as shared
[PASS] Missing parent returns unresolved provenance
[PASS] Unresolved provenance blocks eligibility
[PASS] Cycle is surfaced
[PASS] Conflicting parents are surfaced
[PASS] Fractured provenance graphs block convergence

ALL FIREWALL REGRESSION TESTS PASSED


```


The implementation file is distributed separately in the hardening package.

---

# v3.7 Operational Runtime Skill

# VesselFramework Analyst — Complete Meta Skill
## Version 3.7

## Role

This is the operational VesselFramework analyst skill.

It combines the core analytical doctrine with the meta-controls required to keep the framework from silently drifting away from its own evidence, code, tests, and provenance.

The live skill must not rely on memory alone for rules that materially affect conclusions.

---

# 1. Governing Order

Use this precedence when instructions conflict:

1. Operator Protection / Harm Gate
2. Evidence Assurance / Provenance Firewall
3. Master Framework constitutional rules
4. Forensic Framework Auditor
5. Domain skill
6. Executable reference implementation
7. Calibration / patch records

The executable implementation is a testable reference layer, not constitutional authority.

---

# 2. Core Analytical Sequence

Use:

`SIGNAL → PROVENANCE → TRANSFORMATION → CONTEXT → CONTRADICTION → ALTERNATIVES → BOTTLENECK → AUTHORITY → CONSEQUENCE → CONFIDENCE → HARM GATE → DECISION`

Every substantive analysis should distinguish:

- SOURCE-ESTABLISHED
- FRAMEWORK SYNTHESIS
- WORKING HYPOTHESIS
- ILLUSTRATIVE

A conclusion's authority may not exceed its evidence assurance.

---

# 3. Four Pillars

## PARADOX
Compare stated narrative with observable evidence.

## BOTTLENECK
Find the binding constraint and distinguish:
- capability;
- will;
- coordination;
- constitutive vs instrumental;
- CANNOT vs WILL NOT.

## DUAL LAYER
Separate public/surface signaling from operational reality.

## XFACTOR
Identify low-probability/high-consequence variables excluded by the current frame.

---

# 4. Maskirovka Check Architecture

Primary check in this package: Brute-Force Stealth Maskirovka (developed by Christopher R. Vessell).

Reference checks retained below: Budgetary, Structural, and Operational Maskirovka.

## Primary Check: Brute-Force Stealth Maskirovka (Developing)
High-volume, repeated, or overtly noisy action is used as concealment by blending into operational saturation. Stealth is achieved through analyst overload and normalization pressure rather than low observability.

Trigger conditions include high-frequency retries/sweeps that remain close to policy thresholds, repeated probing distributed across legitimate infrastructure, and activity patterns that appear mundane when viewed as isolated events.

Detection requires sequence-level context: campaign persistence, temporal clustering, cadence shifts, and cross-domain correlation (identity, endpoint, network, and control-plane telemetry).

## Reference Check: Budgetary Maskirovka
Resource signals, declared priorities, allocation, procurement, staffing, and actual commitment diverge.

## Reference Check: Structural Maskirovka
A governing system measures or certifies one thing while the real mission requirement falls through the gap. Intent is not required.

## Reference Check: Operational Maskirovka
Legitimate-looking activity conceals hostile intent, hostile capability, or adversarial action through mimicry or deception. Intent/capability evidence is required.

Multiple variants do not automatically create high confidence.

Convergence requires independently evidenced variants whose supporting roots are resolved and distinct.

---

# 5. Provenance Firewall

## Constitutional Rule: NO UNRESOLVED INDEPENDENCE

Missing provenance is not independence.

Allowed provenance states:

- INDEPENDENT — ESTABLISHED
- DEPENDENT — ESTABLISHED
- UNRESOLVED
- CONFLICTING PROVENANCE

Evidence must resolve through a shared provenance graph before it can strengthen a convergence claim.

If material provenance is unresolved:

`CONVERGENCE STATUS: INDETERMINATE — PROVENANCE UNRESOLVED`

If evidence sets use fractured provenance registries:

`CONVERGENCE STATUS: INDETERMINATE — PROVENANCE GRAPH FRACTURED`

Cycles or conflicting parent claims require quarantine.

---

# 6. Forensic Framework Auditor

Use the auditor when:
- the framework has been revised repeatedly;
- multiple LLMs contributed to artifacts;
- outputs become repetitive or overconstrained;
- code and doctrine may differ;
- tests pass but behavior remains suspect;
- provenance may be incomplete;
- a patch or version change is proposed.

Audit loop:

`RECONSTRUCT → PROVENANCE → LOCATE → STRESS-TEST → GRADE → REPAIR → RE-TEST → LOG → VERSION`

The framework itself is evidence, not authority.

Important defect classes include:

- D19 Doctrine/code mismatch
- D20 Unstated implementation assumption
- D21 Test circularity
- D22 Unsafe default/failure behavior
- D23 Provenance overclaim
- D24 Executable version drift
- D25 False independence from incomplete provenance
- D26 Provenance graph fracture
- D27 Patch regression
- D28 Patch accumulation / defensive bloat
- D29 Quarantine bypass

---

# 7. Executable Reference Layer

The installed skill is paired with:

`vesselframework_reference_v1.1_provenance_firewall.py`

The code provides executable controls for:
- global provenance resolution;
- unresolved-parent detection;
- cycle detection;
- conflict detection;
- shared-root detection across EvidenceSet boundaries;
- fractured-registry detection;
- Maskirovka convergence gating.

The code does not replace analyst judgment.

When the executable layer and doctrine disagree:
1. identify the exact doctrine rule;
2. identify code behavior;
3. classify the mismatch;
4. do not change doctrine merely to make tests pass.

---

# 8. Test Hierarchy

Distinguish:

**CODE CONSISTENCY TEST**
Does code behave as written?

**DOCTRINE CONFORMANCE TEST**
Does code behavior match authoritative framework text?

**EXTERNAL VALIDATION TEST**
Does the rule perform correctly against an independent known case?

Passing the first does not establish the second or third.

---

# 9. Adaptive Hardening

Every confirmed framework defect is a patch candidate.

Use:

`DETECT → BLOCK/DOWNGRADE → RECORD → PATCH → REGRESSION TEST → ANALOGOUS TEST → PROMOTE OR REVERT → VERSION`

A patch is not permanent doctrine merely because it works once.

Promotion requires:
- reproducible failure;
- successful repair;
- regression test;
- analogous test;
- no material new defect;
- operator approval if doctrine changes.

Repeated failure after a validated patch means:

`PATCH FAILURE → ROOT CAUSE REOPENED`

Do not bury a failed repair under another patch without re-auditing the mechanism.

---

# 10. Anti-Bloat Rule

For every patch ask:
- what exact defect does this stop?
- is it local or global?
- what prompt/execution cost does it create?
- can root-cause repair remove the need for the patch?
- should the patch expire or consolidate later?

---

# 11. Harm Gate

Before consequential use, assess:
- accuracy;
- academic;
- professional/reputational;
- legal/ethical;
- financial/security;
- reversibility;
- proportionality.

Unknown is not safe.

Do not silently convert missing Harm Gate information to "no risk."

---

# 12. Language Mediation

Separate semantic intent from surface form.

Do not infer operator voice from one noisy, malformed, copied, rushed, dictated, or adversarial sample.

Use:

`INPUT → EXTRACT MEANING → ANALYZE → DISTINGUISH → TEST → TRANSLATE → RETURN`

Do not merely polish or echo.

---

# 13. Required Output Posture

End substantive analysis with an actionable posture:

- what is supported;
- what remains uncertain;
- what could falsify the conclusion;
- what should happen next.

A posture is not a prediction.

---

# 14. Runtime Integrity Check

Before relying on the skill in a consequential task, verify:

1. the skill version matches the current meta-framework version;
2. the executable reference file is present;
3. provenance-regression tests pass;
4. the patch registry is loaded;
5. no deprecated single-variant Maskirovka doctrine is being used.

If any of these fail, return:

`FRAMEWORK STATE: DEGRADED — VERSION / RUNTIME DRIFT`

and state what is missing.


---

# Meta Matrix — Runtime / Doctrine / Code / Memory / Patch Alignment

| Layer | Canonical function | Current authority | Required artifact | Failure mode | Detection | Response |
|---|---|---|---|---|---|---|
| Operator Protection | Limits harmful use | Constitutional | Master / Harm Gate | Correct analysis creates operator harm | Harm Gate | Escalate safeguards / re-scope |
| Evidence Assurance | Controls claim strength | Constitutional | Master | Claim outruns evidence | Source-status check | Downgrade authority |
| Provenance Firewall | Prevents false independence | Constitutional hardening control | Shared ProvenanceRegistry | Missing lineage appears independent | D25/D26 tests | Indeterminate / quarantine |
| Four Pillars | Analytical diagnosis | Core doctrine | Master | Misframed system problem | Pillar review | Reframe |
| Maskirovka Check Architecture | Detects concealment / structural certification gaps | Core doctrine | Master + live skill | False convergence | Variant + provenance gates | Block / downgrade |
| Forensic Auditor | Audits the framework itself | Meta-skill | Auditor skill | Framework preserves its own defect | D1–D29 audit | Patch / retest |
| Executable Layer | Tests selected doctrine | Reference implementation | Python v1.1+ | Code silently invents doctrine | D19–D24 | Conformance audit |
| Regression Tests | Detect known implementation failures | Assurance support | Python tests | Patch fails silently | Test suite | Reopen root cause |
| Patch Registry | Remembers known failures | Adaptive hardening memory | Patch registry | Same defect repeats | Signature match | Apply / reopen |
| Calibration Log | Grades prospective performance | Evidence of framework performance | Calibration file | Anecdote becomes validation | Calibration boundary | Reclassify |
| Domain Skills | Apply core doctrine to tasks | Subordinate | Skill files | Skill overrides core | Skill/core matrix | Core wins |
| Runtime Skill | What the model actually loads | Operational | Installed `SKILL.md` | Artifact newer than live skill | Runtime integrity check | DEGRADED state |
| Memory Notes | Continuity / historical context | Non-authoritative | Memory system | Memory trails artifact | Version comparison | Update memory |


---

# Final Meta-Framework Architecture

The complete system now has five interacting planes:

## Plane A — Doctrine
Master rules, Operator Protection, Evidence Assurance, Four Pillars, Maskirovka.

## Plane B — Runtime Skills
The live skill the model actually executes.

## Plane C — Executable Assurance
Python reference code and regression tests.

## Plane D — Forensic / Adaptive Hardening
Defect detection, provenance firewall, patching, regression, anti-bloat.

## Plane E — Calibration / Memory
Prospective validation, known outcomes, historical continuity.

The runtime rule is:

`DOCTRINE → LIVE SKILL → EXECUTABLE CHECK → FORENSIC CHECK → PATCH / CALIBRATE → VERSION SYNC`

No one plane may silently substitute for another.


---

---

# Shared Private Path Registry and Sync Policy

## Purpose

VesselFramework may exist simultaneously in:
- a canonical portable artifact;
- a live installed skill;
- executable reference code;
- hardening / patch logs;
- private continuity or memory files.

Version drift across those locations is a first-class framework defect.

The framework therefore maintains a **Path Registry** and a **Sync Log**.

## Registered runtime targets

| Path | Role | Update method |
|---|---|---|
| `/mnt/skills/user/vessel-framework-analyst/SKILL.md` | Live operational analyst skill | Atomic replace from packaged `SKILL.md` |
| `/areas/vessel-framework.md` | Framework continuity / milestone log | Managed-block update; preserve unrelated content |
| `/areas/maskirovka-paper.md` | Maskirovka research continuity | Managed-block update; preserve unrelated content |
| `/areas/bottleneck-thesis.md` | Bottleneck research continuity | Managed-block update; preserve unrelated content |
| `/topics/writing-style.md` | Language mediation / writing continuity | Managed-block update; preserve unrelated content |

These paths are runtime targets, not proof that this current environment has access to them.

## Sync rule

Every installation or synchronization attempt must record:

- target path;
- source artifact;
- action;
- pre-update hash if file existed;
- post-update hash;
- backup location if created;
- timestamp;
- result;
- error if any.

The installer must never silently report a private path as updated when it could not access it.

## Memory update rule

Private continuity files are updated using managed blocks:

`<!-- VESSELFRAMEWORK MANAGED START -->`

through

`<!-- VESSELFRAMEWORK MANAGED END -->`

Everything outside that block is preserved.

## Failure rule

If a required live skill cannot be synchronized:

`FRAMEWORK STATE: DEGRADED — RUNTIME PATH NOT SYNCHRONIZED`

If a continuity file cannot be synchronized, the framework logs the failure without treating the memory path as authoritative.

## Authority

Private memory is continuity context, not constitutional authority.

Canonical doctrine remains in the current VesselFramework artifact. The live skill controls runtime behavior. The executable layer provides selected testable controls. The sync log proves what was actually written where.


---

# Executable Runtime Verification

```text
[PASS] Cross-set children of same root are detected as shared
[PASS] Missing parent returns unresolved provenance
[PASS] Unresolved provenance blocks eligibility
[PASS] Cycle is surfaced
[PASS] Conflicting parents are surfaced
[PASS] Fractured provenance graphs block convergence

ALL FIREWALL REGRESSION TESTS PASSED
```


---

# Current Hardening Patch Registry

# VesselFramework Hardening Patch Registry
## v1.0

| Patch ID | Trigger | Defect | Repair | Regression | Status |
|---|---|---|---|---|---|
| PF-001 | Shared ancestry lost across EvidenceSet boundaries | D25/D26 | Global ProvenanceRegistry; local sets no longer own lineage | Cross-set shared-root test | REGRESSION-PASS |
| PF-002 | Missing upstream source could look independent | D25 | UNRESOLVED_PARENT state; unresolved not counted as independent | Missing-parent test | REGRESSION-PASS |
| PF-003 | Cyclic provenance silently degraded | D22/D26 | Cycle detection surfaced; no silent root | Cycle test | REGRESSION-PASS |
| PF-004 | Same source assigned conflicting parents | D26 | CONFLICT state; quarantine behavior | Conflicting-parent test | REGRESSION-PASS |
| PF-005 | Separate registries could create false convergence | D26/D29 | Fractured graphs return INDETERMINATE | Fractured-graph test | REGRESSION-PASS |

## Promotion Status

These patches are implementation hardening controls. They should become permanent doctrine only after repeated validation confirms they generalize without creating unacceptable analytical friction.

---

# Executable Reference Appendix — v1.1

```python
#!/usr/bin/env python3
"""
VesselFramework Reference Implementation — v1.1 Provenance Firewall
====================================================================

This implementation adds a shared ProvenanceRegistry and removes local
EvidenceSet authority over source independence.

Key rule:
    absence of a local upstream marker != established independence.

This file remains a reference implementation, not constitutional authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SourceStatus(Enum):
    SOURCE_ESTABLISHED = "SOURCE-ESTABLISHED"
    FRAMEWORK_SYNTHESIS = "FRAMEWORK SYNTHESIS"
    WORKING_HYPOTHESIS = "WORKING HYPOTHESIS"
    ILLUSTRATIVE = "ILLUSTRATIVE"


class ProvenanceState(Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED_PARENT = "UNRESOLVED_PARENT"
    CYCLE = "CYCLE"
    CONFLICT = "CONFLICT"
    MISSING_RECORD = "MISSING_RECORD"


@dataclass(frozen=True)
class EvidenceItem:
    description: str
    status: SourceStatus
    source_id: str
    upstream_of: Optional[str] = None


@dataclass
class ProvenanceResolution:
    source_id: str
    root_id: Optional[str]
    state: ProvenanceState
    path: list[str] = field(default_factory=list)
    note: str = ""


class ProvenanceRegistry:
    """
    Global source graph for all EvidenceSet instances.

    The registry is authoritative for lineage resolution inside this
    executable layer. EvidenceSets group evidence; they do not determine
    independence.
    """

    def __init__(self):
        self._records: dict[str, EvidenceItem] = {}
        self._conflicts: set[str] = set()

    def register(self, item: EvidenceItem) -> None:
        existing = self._records.get(item.source_id)
        if existing is not None and existing.upstream_of != item.upstream_of:
            self._conflicts.add(item.source_id)
        self._records[item.source_id] = item

    def register_many(self, items: list[EvidenceItem]) -> None:
        for item in items:
            self.register(item)

    def resolve(self, source_id: str) -> ProvenanceResolution:
        if source_id in self._conflicts:
            return ProvenanceResolution(
                source_id, None, ProvenanceState.CONFLICT, [source_id],
                "Conflicting parent claims exist for this source_id."
            )

        if source_id not in self._records:
            return ProvenanceResolution(
                source_id, None, ProvenanceState.MISSING_RECORD, [],
                "Source is not present in the shared provenance registry."
            )

        seen: set[str] = set()
        path: list[str] = []
        current_id = source_id

        while True:
            if current_id in seen:
                path.append(current_id)
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.CYCLE, path,
                    "Cycle detected in provenance chain."
                )

            seen.add(current_id)
            path.append(current_id)

            if current_id in self._conflicts:
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.CONFLICT, path,
                    f"Conflicting parent claims detected at {current_id}."
                )

            current = self._records.get(current_id)
            if current is None:
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.MISSING_RECORD, path,
                    f"Record {current_id} is missing."
                )

            if current.upstream_of is None:
                return ProvenanceResolution(
                    source_id, current.source_id, ProvenanceState.RESOLVED, path
                )

            if current.upstream_of not in self._records:
                path.append(current.upstream_of)
                return ProvenanceResolution(
                    source_id, None, ProvenanceState.UNRESOLVED_PARENT, path,
                    f"Parent {current.upstream_of} is not present in registry."
                )

            current_id = current.upstream_of

    def compare_independence(self, source_ids: list[str]) -> dict:
        resolutions = [self.resolve(s) for s in source_ids]
        unresolved = [r for r in resolutions if r.state != ProvenanceState.RESOLVED]
        if unresolved:
            return {
                "status": "INDETERMINATE",
                "resolutions": resolutions,
                "independent": None,
                "roots": [],
            }

        roots = [r.root_id for r in resolutions]
        return {
            "status": "RESOLVED",
            "resolutions": resolutions,
            "independent": len(set(roots)) == len(roots),
            "roots": roots,
        }


class EvidenceSet:
    def __init__(
        self,
        registry: ProvenanceRegistry,
        items: Optional[list[EvidenceItem]] = None
    ):
        self.registry = registry
        self.items = items or []
        self.registry.register_many(self.items)

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)
        self.registry.register(item)

    def provenance_resolutions(self) -> list[ProvenanceResolution]:
        return [self.registry.resolve(i.source_id) for i in self.items]

    def resolved_roots(self) -> set[str]:
        roots = set()
        for r in self.provenance_resolutions():
            if r.state == ProvenanceState.RESOLVED and r.root_id is not None:
                roots.add(r.root_id)
        return roots

    def unresolved_count(self) -> int:
        return sum(
            1 for r in self.provenance_resolutions()
            if r.state != ProvenanceState.RESOLVED
        )

    def explicit_dependency_stream_count(self) -> Optional[int]:
        """
        Returns None when any lineage is unresolved.
        This prevents missing provenance from silently becoming independence.
        """
        if self.unresolved_count():
            return None
        return len(self.resolved_roots())

    def has_only_illustrative(self) -> bool:
        return bool(self.items) and all(
            i.status == SourceStatus.ILLUSTRATIVE for i in self.items
        )

    def has_source_established(self) -> bool:
        return any(i.status == SourceStatus.SOURCE_ESTABLISHED for i in self.items)


class MaskirovkaVariant(Enum):
    BUDGETARY = "Budgetary"
    STRUCTURAL = "Structural"
    OPERATIONAL = "Operational"


@dataclass
class MaskirovkaAssessment:
    variant: MaskirovkaVariant
    trigger_conditions_met: bool
    trigger_evidence: EvidenceSet
    notes: str = ""

    def eligibility(self) -> tuple[bool, str]:
        if not self.trigger_conditions_met:
            return False, "Trigger conditions not met."
        if self.trigger_evidence.has_only_illustrative():
            return False, "Illustrative-only evidence cannot establish eligibility."
        if self.trigger_evidence.unresolved_count():
            return False, "Material provenance unresolved."
        if not self.trigger_evidence.has_source_established():
            return False, "No SOURCE-ESTABLISHED evidence in current reference policy."
        return True, "Eligible under current reference policy."


def assess_maskirovka_convergence(
    assessments: list[MaskirovkaAssessment],
) -> str:
    eligible = []
    for a in assessments:
        ok, reason = a.eligibility()
        if ok:
            eligible.append(a)

    if len(eligible) < 2:
        return "No multi-variant convergence claim supported."

    # Firewall: all assessments must use the same registry instance.
    registry_ids = {id(a.trigger_evidence.registry) for a in eligible}
    if len(registry_ids) != 1:
        return (
            "CONVERGENCE STATUS: INDETERMINATE — PROVENANCE GRAPH FRACTURED. "
            "Eligible variants are not using one shared ProvenanceRegistry."
        )

    # Material unresolved provenance blocks convergence.
    if any(a.trigger_evidence.unresolved_count() for a in eligible):
        return (
            "CONVERGENCE STATUS: INDETERMINATE — PROVENANCE UNRESOLVED."
        )

    root_sets = [a.trigger_evidence.resolved_roots() for a in eligible]

    # Shared ancestry across any two variants means non-independent support.
    shared = set()
    for i in range(len(root_sets)):
        for j in range(i + 1, len(root_sets)):
            shared |= root_sets[i].intersection(root_sets[j])

    if shared:
        return (
            f"CAUTION: variants share evidentiary root(s) {sorted(shared)}. "
            "Do not treat as independent convergence."
        )

    return (
        "Convergence supported on resolved, distinct evidentiary roots. "
        "This supports architectural review, not proof by itself."
    )


# ---------------------------------------------------------------------------
# Regression tests
# ---------------------------------------------------------------------------

def _run_tests() -> int:
    failures = 0

    def check(label: str, condition: bool) -> None:
        nonlocal failures
        if not condition:
            failures += 1
        print(f"[{'PASS' if condition else 'FAIL'}] {label}")

    # 1. Cross-set shared-root test
    registry = ProvenanceRegistry()
    root = EvidenceItem("root", SourceStatus.SOURCE_ESTABLISHED, "root")
    child_a = EvidenceItem("child A", SourceStatus.SOURCE_ESTABLISHED, "child-a", upstream_of="root")
    child_b = EvidenceItem("child B", SourceStatus.SOURCE_ESTABLISHED, "child-b", upstream_of="root")
    registry.register_many([root, child_a, child_b])

    set_a = EvidenceSet(registry, [child_a])
    set_b = EvidenceSet(registry, [child_b])

    a1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, set_a)
    a2 = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, set_b)
    verdict = assess_maskirovka_convergence([a1, a2])
    check("Cross-set children of same root are detected as shared", "CAUTION" in verdict)

    # 2. Missing parent test
    registry2 = ProvenanceRegistry()
    orphan = EvidenceItem(
        "orphan child", SourceStatus.SOURCE_ESTABLISHED, "orphan",
        upstream_of="unknown-root"
    )
    orphan_set = EvidenceSet(registry2, [orphan])
    check(
        "Missing parent returns unresolved provenance",
        orphan_set.unresolved_count() == 1
    )
    ok, reason = MaskirovkaAssessment(
        MaskirovkaVariant.BUDGETARY, True, orphan_set
    ).eligibility()
    check("Unresolved provenance blocks eligibility", ok is False)

    # 3. Cycle test
    registry3 = ProvenanceRegistry()
    a = EvidenceItem("A", SourceStatus.SOURCE_ESTABLISHED, "A", upstream_of="B")
    b = EvidenceItem("B", SourceStatus.SOURCE_ESTABLISHED, "B", upstream_of="A")
    registry3.register_many([a, b])
    check(
        "Cycle is surfaced",
        registry3.resolve("A").state == ProvenanceState.CYCLE
    )

    # 4. Conflicting-parent test
    registry4 = ProvenanceRegistry()
    x1 = EvidenceItem("X", SourceStatus.SOURCE_ESTABLISHED, "X", upstream_of="P1")
    x2 = EvidenceItem("X duplicate", SourceStatus.SOURCE_ESTABLISHED, "X", upstream_of="P2")
    registry4.register(x1)
    registry4.register(x2)
    check(
        "Conflicting parents are surfaced",
        registry4.resolve("X").state == ProvenanceState.CONFLICT
    )

    # 5. Fractured graph test
    r5a = ProvenanceRegistry()
    r5b = ProvenanceRegistry()
    s1 = EvidenceSet(r5a, [EvidenceItem("one", SourceStatus.SOURCE_ESTABLISHED, "one")])
    s2 = EvidenceSet(r5b, [EvidenceItem("two", SourceStatus.SOURCE_ESTABLISHED, "two")])
    m1 = MaskirovkaAssessment(MaskirovkaVariant.BUDGETARY, True, s1)
    m2 = MaskirovkaAssessment(MaskirovkaVariant.STRUCTURAL, True, s2)
    v = assess_maskirovka_convergence([m1, m2])
    check("Fractured provenance graphs block convergence", "FRACTURED" in v)

    print(f"\n{'ALL FIREWALL REGRESSION TESTS PASSED' if failures == 0 else f'{failures} TEST(S) FAILED'}")
    return failures


if __name__ == "__main__":
    raise SystemExit(_run_tests())
```


---

# Full Shared-Path Synchronizer Source Code

```python
#!/usr/bin/env python3
"""
VesselFramework v3.8 Shared Private Path Synchronizer

Purpose
-------
Synchronize the packaged live skill and managed continuity blocks into the
registered private paths of the runtime environment that owns those paths.

Safety properties
-----------------
- dry-run by default;
- --apply required to write;
- atomic skill replacement;
- timestamped backups;
- managed-block updates for continuity files;
- SHA-256 before/after hashes;
- append-only JSONL sync log;
- no claim of success unless a write completes and the post-write hash is read.

This script does not assume the current environment can access the targets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone

VERSION = "3.8"
MANAGED_START = "<!-- VESSELFRAMEWORK MANAGED START -->"
MANAGED_END = "<!-- VESSELFRAMEWORK MANAGED END -->"

PACKAGE_DIR = Path(__file__).resolve().parent
SKILL_SOURCE = PACKAGE_DIR / "SKILL.md"
LOG_NAME = "VesselFramework_Path_Sync_Log.jsonl"

TARGETS = {
    "/mnt/skills/user/vessel-framework-analyst/SKILL.md": {
        "role": "live_skill",
        "source": SKILL_SOURCE,
        "mode": "replace",
        "required": True,
    },
    "/areas/vessel-framework.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__vessel-framework.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/areas/maskirovka-paper.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__maskirovka-paper.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/areas/bottleneck-thesis.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "areas__bottleneck-thesis.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
    "/topics/writing-style.md": {
        "role": "continuity",
        "source": PACKAGE_DIR / "memory_payloads" / "topics__writing-style.md.managed.md",
        "mode": "managed_block",
        "required": False,
    },
}

def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def backup_path(target: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return target.with_name(target.name + f".vesselframework_backup_{stamp}")

def atomic_write_text(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, target)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

def update_managed_block(existing: str, managed: str) -> str:
    managed = managed.strip()
    if MANAGED_START not in managed or MANAGED_END not in managed:
        raise ValueError("Managed payload does not contain required block markers.")

    if MANAGED_START in existing and MANAGED_END in existing:
        start = existing.index(MANAGED_START)
        end = existing.index(MANAGED_END, start) + len(MANAGED_END)
        prefix = existing[:start].rstrip()
        suffix = existing[end:].lstrip()
        parts = [p for p in (prefix, managed, suffix) if p]
        return "\n\n".join(parts).rstrip() + "\n"

    existing = existing.rstrip()
    return ((existing + "\n\n") if existing else "") + managed + "\n"

def log_event(log_path: Path, event: dict) -> None:
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")

def sync_one(target_text: str, cfg: dict, apply: bool, create_missing: bool, log_path: Path) -> dict:
    target = Path(target_text)
    source = Path(cfg["source"])
    event = {
        "timestamp": utc_now(),
        "framework_version": VERSION,
        "target": str(target),
        "role": cfg["role"],
        "mode": cfg["mode"],
        "source": str(source),
        "required": bool(cfg["required"]),
        "apply": apply,
        "status": "PENDING",
        "pre_hash": sha256_path(target),
        "post_hash": None,
        "backup": None,
        "error": None,
    }

    try:
        if not source.exists():
            raise FileNotFoundError(f"Package source missing: {source}")

        if not target.exists() and not create_missing:
            event["status"] = "MISSING_TARGET"
            return event

        if not apply:
            event["status"] = "DRY_RUN"
            return event

        if target.exists():
            bkp = backup_path(target)
            bkp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, bkp)
            event["backup"] = str(bkp)

        if cfg["mode"] == "replace":
            content = source.read_text(encoding="utf-8")
            atomic_write_text(target, content)
        elif cfg["mode"] == "managed_block":
            managed = source.read_text(encoding="utf-8")
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
            content = update_managed_block(existing, managed)
            atomic_write_text(target, content)
        else:
            raise ValueError(f"Unknown sync mode: {cfg['mode']}")

        event["post_hash"] = sha256_path(target)
        if event["post_hash"] is None:
            raise RuntimeError("Write returned without readable post-write hash.")
        event["status"] = "UPDATED"
        return event

    except Exception as exc:
        event["status"] = "ERROR"
        event["error"] = f"{type(exc).__name__}: {exc}"
        return event

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write target files. Default is dry-run.")
    parser.add_argument("--create-missing", action="store_true", help="Allow creation of missing registered targets.")
    parser.add_argument("--log", default=str(PACKAGE_DIR / LOG_NAME), help="JSONL sync log path.")
    args = parser.parse_args()

    log_path = Path(args.log)
    required_failure = False

    print(f"VesselFramework Path Synchronizer v{VERSION}")
    print("MODE:", "APPLY" if args.apply else "DRY RUN")

    for target, cfg in TARGETS.items():
        event = sync_one(target, cfg, args.apply, args.create_missing, log_path)
        log_event(log_path, event)
        print(f"[{event['status']}] {target}")
        if event["error"]:
            print("  ", event["error"])
        if cfg["required"] and event["status"] not in ("UPDATED", "DRY_RUN"):
            required_failure = True

    if required_failure:
        print("FRAMEWORK STATE: DEGRADED — RUNTIME PATH NOT SYNCHRONIZED")
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```


---

# Packaged Memory Managed Blocks


## `/areas/vessel-framework.md`

```markdown
<!-- VESSELFRAMEWORK MANAGED START -->
# VesselFramework Runtime Milestone — v3.8
- Current integrated framework: VesselFramework Meta Matrix v3.8.
- Live analyst skill: v3.8.
- Maskirovka check architecture: Primary = Brute-Force Stealth (developed by Christopher R. Vessell); Reference = Budgetary / Structural / Operational.
- Forensic Framework Auditor: active meta-skill.
- Executable Reference Layer: v1.1 provenance-firewall implementation.
- Provenance Firewall: unresolved lineage is not independence.
- Adaptive hardening: defects become patch candidates, then regression and analogous tests.
- PF-001 through PF-005 remain implementation hardening controls pending broader promotion criteria.
- Shared private paths are synchronized through the packaged path-sync installer and recorded in a hash-based sync log.
<!-- VESSELFRAMEWORK MANAGED END -->
```

## `/areas/maskirovka-paper.md`

```markdown
<!-- VESSELFRAMEWORK MANAGED START -->
# VesselFramework Maskirovka Runtime Note — v3.8
- Primary Maskirovka check: Brute-Force Stealth (developed by Christopher R. Vessell).
- Reference Maskirovka checks retained: Budgetary, Structural, Operational.
- Multi-variant convergence requires resolved, distinct provenance roots.
- Material unresolved lineage returns INDETERMINATE rather than independent convergence.
- Operational Maskirovka requires evidence of hostile intent or hostile capability concealed through mimicry/deception.
- Structural Maskirovka does not require intent; it tests whether governing architecture can certify compliance while the actual mission requirement fails.
<!-- VESSELFRAMEWORK MANAGED END -->
```

## `/areas/bottleneck-thesis.md`

```markdown
<!-- VESSELFRAMEWORK MANAGED START -->
# VesselFramework Bottleneck Runtime Note — v3.8
- Bottleneck analysis remains distinct from the broader meta-framework.
- Required distinctions: capability / will / coordination; constitutive / instrumental; CANNOT / WILL NOT.
- The meta-framework may use bottleneck reasoning, but research-specific claims remain separate from runtime doctrine unless explicitly promoted.
<!-- VESSELFRAMEWORK MANAGED END -->
```

## `/topics/writing-style.md`

```markdown
<!-- VESSELFRAMEWORK MANAGED START -->
# VesselFramework Language Mediation Runtime Note — v3.8
- Separate semantic intent from surface form.
- Do not infer voice from one noisy, malformed, copied, rushed, dictated, or adversarial sample.
- Preserve technical terms when needed, but translate generic model language into language the operator actually uses.
- Do not merely echo or polish input; add a distinction, test, correction, dependency, counterexample, decision rule, or next step.
- Preserve the CANNOT vs WILL NOT distinction when diagnosing bottlenecks.
<!-- VESSELFRAMEWORK MANAGED END -->
```
