---
name: security-control-selection-placement-analyst
description: >
  Use when the operator must compare, select, place, tailor, or justify cybersecurity
  controls against a concrete attack path, asset, trust boundary, or mission requirement.
  The skill evaluates where a control acts, what attack steps it can influence, what
  dependencies it requires, how it can fail, what residual paths remain, and what evidence
  demonstrates effectiveness. It is designed for comparisons such as perimeter vs endpoint,
  network vs host controls, preventive vs detective controls, segmentation vs identity,
  and competing defense-in-depth investments.
---

# Security Control Selection & Placement Analyst
## Version 0.1 — Research Candidate

## Status
**Skill status:** RESEARCH CANDIDATE / PILOT REQUIRED  
**Authority:** Domain skill; subordinate to VesselFramework doctrine, Evidence Assurance,
Provenance Firewall, Operator Protection/Harm Gate, and Forensic Framework Auditor.  
**Runtime state:** File creation does not establish installation or synchronization.

# 1. Purpose

Select the control that most directly reduces a defined risk at the correct enforcement point.

This skill rejects generic questions such as "Which technology is best?" unless they are
converted into a decision involving:

`ASSET -> THREAT -> ATTACK PATH -> TRUST BOUNDARY -> CONTROL POINT ->
CONTROL -> DEPENDENCIES -> FAILURE MODE -> RESIDUAL PATH -> EVIDENCE -> DECISION`

The skill is useful when several controls are individually valid but act at different parts
of the attack path.

# 2. Research Basis

## NIST Risk Management Framework / SP 800-53
Adopt:
- select, tailor, and document controls commensurate with risk;
- allocate controls to system components;
- tailor controls to mission, environment, threats, vulnerabilities, and constraints;
- distinguish selecting a control from assessing whether it operates effectively.

## NIST CSF 2.0
Adopt:
- control decisions exist inside a broader risk-management system;
- outcomes span Govern, Identify, Protect, Detect, Respond, and Recover;
- control selection should be related to desired cybersecurity outcomes rather than
  technology presence alone.

## MITRE ATT&CK
Adopt:
- map defenses to adversary techniques/attack steps;
- network segmentation reduces attack surface and lateral movement;
- network traffic filtering can be enforced by network appliances or endpoint software;
- software-installation restrictions and allowlisting constrain unauthorized execution;
- different mitigations address different adversary behaviors.

## CYBR-5000 course material
Adopt:
- technical, managerial, operational, and physical control categories;
- preventive, detective, corrective, compensating, deterrent, and directive control types;
- attack surfaces and threat vectors;
- device placement, security zones, DMZs, segmentation, firewall functions, VPNs,
  remote access, fail-open/fail-closed, SD-WAN, SASE, and endpoint/network distinctions.

## VesselFramework
Adopt:
- evidence-status separation;
- provenance firewall;
- bottleneck analysis;
- CANNOT vs WILL NOT;
- formal/configured state vs operational state;
- alternatives and disconfirmers;
- Harm Gate;
- control-assurance chain.

# 3. Trigger Conditions

Use when asked:
- Which security control is more effective?
- Should protection be at the perimeter, endpoint, identity layer, application, or data layer?
- Where should a firewall/IPS/EDR/allowlist/DLP/segmentation control be placed?
- Which control most directly stops this attack path?
- Which control should be prioritized under budget, architecture, or operational constraints?
- Is an existing control actually effective or merely present?
- What compensating control is appropriate when the preferred control cannot be deployed?
- How should controls be layered without redundant spending?

Do not use for:
- simple definitions;
- product shopping;
- vulnerability exploitation instructions;
- incident response where the primary question is containment/eradication rather than control design;
- a purely compliance-driven checklist with no control-selection decision.

# 4. Intake Contract

Record:

```text
CONTROL DECISION INTAKE
Decision question:
Protected asset / mission:
Security objective:
Threat actor / threat event:
Known attack vector:
Attack path:
Trust boundaries crossed:
Current controls:
Candidate controls:
Required availability:
Required confidentiality/integrity:
Environment:
  on-prem / cloud / hybrid / remote / OT / mobile
Constraints:
  budget / staffing / legacy / latency / safety / regulation / usability
Evidence available:
Decision deadline:
Consequence of wrong selection:
```

If the asset, attack path, or required outcome is undefined, the comparison is not yet
decision-grade.

# 5. Attack-Path Model

Build the path:

`ENTRY -> ACCESS -> EXECUTION -> PRIVILEGE -> MOVEMENT -> ACTION ON OBJECTIVE`

Not every case uses every step.

For each step record:
- attacker action;
- required condition;
- observable evidence;
- current control;
- candidate control;
- bypass path;
- residual risk.

The "best" control is not necessarily the one nearest the Internet or nearest the endpoint.
It is the one that most effectively constrains the attack step that dominates the risk.

# 6. Control-Placement Model

Classify enforcement location:

1. **Perimeter / north-south network**
   - firewalls
   - network IPS
   - secure web gateways
   - ingress/egress filtering

2. **Internal network / east-west**
   - segmentation
   - internal firewalls
   - microsegmentation
   - NAC / 802.1X

3. **Identity / access**
   - MFA
   - PAM
   - conditional access
   - ZTNA

4. **Endpoint / host**
   - EDR
   - host firewall
   - application allowlisting
   - exploit protection
   - device control

5. **Application / workload**
   - WAF
   - sandboxing
   - workload isolation
   - API controls

6. **Data**
   - encryption
   - DLP
   - rights management
   - database controls

7. **Human / process**
   - awareness
   - approval workflow
   - separation of duties
   - incident reporting

Placement classification does not establish superiority.

# 7. Control-Function Model

Classify what the control does:

- prevent;
- deter;
- detect;
- delay;
- contain;
- correct/recover;
- compensate;
- direct/govern.

A preventive control should not be compared to a detective control as though they perform
the same mission.

# 8. Attack-Path Coverage Test

For every candidate control answer:

1. Which attack step can it affect?
2. Does it act before, during, or after compromise?
3. Does the attack have to cross its enforcement point?
4. Can legitimate credentials or permitted traffic bypass its logic?
5. Does encrypted traffic reduce its visibility?
6. Does the control survive remote/cloud/mobile operation?
7. Does it constrain lateral movement?
8. Does it constrain execution?
9. Does it constrain privilege or identity abuse?
10. What attack path remains after the control succeeds?

Output:

`CONTROL -> COVERED STEPS -> UNCOVERED STEPS -> BYPASS CONDITIONS -> RESIDUAL PATH`

# 9. Control-Assurance Chain

Never treat deployment as proof of effectiveness.

Use:

`SELECTED
 -> DEPLOYED
 -> ENABLED
 -> CORRECTLY CONFIGURED
 -> RECEIVES REQUIRED TELEMETRY/INPUT
 -> ENFORCES INTENDED POLICY
 -> RESISTS EXPECTED BYPASS
 -> PRODUCES EXPECTED SECURITY EFFECT
 -> IMPROVES RISK OUTCOME`

Evidence at one stage cannot prove all later stages.

Examples:
- Firewall installed != effective segmentation.
- EDR agent present != telemetry healthy.
- Application allowlist configured != correct authorized-software policy.
- MFA enabled != phishing-resistant authentication.
- IDS alerting != containment.

# 10. Dependency Analysis

For each candidate control identify dependencies:

```text
CONTROL
  -> identity dependency
  -> policy dependency
  -> configuration dependency
  -> network dependency
  -> endpoint dependency
  -> telemetry dependency
  -> administrative dependency
  -> vendor/cloud dependency
  -> user/process dependency
```

Then ask:

**Which dependency becomes the binding constraint?**

A technically strong control with an unmanageable policy burden may be less effective in
practice than a narrower control that can be maintained correctly.

# 11. Failure-Mode Analysis

For each control define:

- fail-open behavior;
- fail-closed behavior;
- silent failure;
- degradation mode;
- false positive cost;
- false negative cost;
- operational availability effect;
- detection of failure;
- rollback/recovery.

Do not assume "fail closed" is always superior. Compare the security consequence of
unauthorized access against the mission consequence of denied service.

# 12. Adversarial Bypass Test

Reverse the design.

Ask:
- If the control works exactly as designed, how can the attacker route around it?
- Can the attacker use an approved protocol?
- Can the attacker use valid credentials?
- Can the attacker shift from north-south to east-west movement?
- Can they abuse an allowed application?
- Can they execute using an already approved interpreter/tool?
- Can they target an unmanaged device?
- Can they use a third party or cloud path?
- Can they exploit the control's management plane?

A candidate control is downgraded if bypass removes it from the dominant attack path.

# 13. Comparative Control Matrix

Compare candidates using:

| Criterion | Meaning |
|---|---|
| Attack-path relevance | Does it touch the dominant attack step? |
| Prevention strength | Can it stop rather than only observe? |
| Coverage | How much of the environment/path is covered? |
| Persistence | Does protection remain across remote/cloud/mobile states? |
| Bypass resistance | How easily can attack behavior move around it? |
| Lateral-movement control | Does it constrain east-west movement? |
| Execution control | Does it constrain unauthorized code/actions? |
| Visibility | What useful evidence does it produce? |
| Operational burden | Staffing, tuning, maintenance, exceptions |
| Availability effect | Failure and false-positive consequence |
| Integration | Dependencies on identity, network, endpoint, cloud |
| Verifiability | Can effectiveness be tested? |
| Cost | Acquisition + lifecycle cost |
| Residual risk | What meaningful path remains? |

Weights may be used only when their rationale is explicit.

# 14. Decision Rules

## Rule 1 — Attack-Path Proximity
Prefer controls that directly constrain the dominant attack step over controls that merely
exist earlier or later in the architecture.

## Rule 2 — Persistent Enforcement
When users/assets regularly operate outside a fixed network boundary, increase the value of
controls that persist with identity, endpoint, workload, or data.

## Rule 3 — Choke-Point Efficiency
When many attack paths must cross a single reliable boundary, increase the value of a
central network enforcement point.

## Rule 4 — Internal Threat / Lateral Movement
Perimeter controls lose comparative value when the dominant threat originates inside the
boundary or uses legitimate remote access. Evaluate endpoint, identity, and internal
segmentation controls.

## Rule 5 — Execution Risk
When success requires unauthorized code execution, evaluate allowlisting/application
control and endpoint enforcement directly.

## Rule 6 — Availability-Critical Systems
A theoretically strong blocking control may be inappropriate if false positives or failure
can create unacceptable operational harm. Evaluate monitoring, staged enforcement,
compensating controls, or highly tested allowlists.

## Rule 7 — Defense in Depth
If the decision allows multiple controls, do not force a false winner. Select complementary
controls at different attack-path stages.

## Rule 8 — Forced Choice
If the assignment or decision explicitly requires one control, state the assumptions that
make the choice rational and identify what residual risk the rejected control would have
covered.

# 15. Perimeter-vs-Endpoint Decision Pattern

Use this specialized branch only when required.

### Perimeter strengths
- centralized choke point;
- attack-surface reduction;
- ingress/egress control;
- network segmentation;
- broad asset coverage;
- visibility of boundary traffic;
- protection for hosts that cannot run agents.

### Perimeter limitations
- traffic that does not cross the boundary may be invisible;
- legitimate/compromised credentials can traverse allowed paths;
- remote/cloud/mobile architecture weakens a static perimeter;
- encrypted/approved traffic can reduce inspection value;
- post-entry execution may occur beyond the control point.

### Endpoint strengths
- enforcement where code/actions occur;
- persists across multiple network locations;
- can restrict unauthorized execution;
- can observe host/process context unavailable to network appliances;
- remains relevant after perimeter crossing.

### Endpoint limitations
- agent health and management burden;
- policy drift;
- application exceptions;
- performance/compatibility effects;
- unmanaged/unsupported devices;
- sophisticated abuse of approved tools may remain possible.

### Forced-choice discriminator
Ask:

`WHERE MUST THE ADVERSARY SUCCEED TO ACHIEVE THE OBJECTIVE?`

Then choose the control whose verified enforcement point most directly constrains that step.

# 16. Evidence and Provenance

Tag material claims:
- SOURCE-ESTABLISHED
- FRAMEWORK SYNTHESIS
- WORKING HYPOTHESIS
- ILLUSTRATIVE

For external standards:
- record publication/version/date;
- preserve exact control/mitigation scope;
- do not convert guidance into proof of comparative superiority;
- distinguish control capability from empirical effectiveness.

Repeated MITRE mappings or vendor claims do not by themselves establish effectiveness in
the operator's environment.

# 17. Testing Effectiveness

Design tests that correspond to the claim.

Examples:

### Firewall / segmentation
- attempt unauthorized inter-segment connection;
- verify deny rule and log;
- confirm allowed required flows remain available;
- test alternate path;
- review configuration drift.

### Network IPS
- replay safe test signature / approved test traffic;
- verify detection/block;
- confirm encrypted and alternate protocol coverage assumptions;
- test failover behavior.

### Application allowlisting
- attempt approved application;
- attempt unauthorized executable/script;
- test signed but unauthorized software;
- test approved interpreter abuse scenarios;
- verify exception workflow and logging.

### EDR
- verify agent health;
- generate benign test telemetry;
- confirm alert delivery;
- test isolation workflow;
- identify coverage gaps.

A test demonstrates only the condition tested.

# 18. Policy / Investment Output

When the comparison supports a budget or policy decision, return:

```text
DECISION
Preferred control:
Decision assumptions:
Dominant attack path:
Why this enforcement point matters:
What the control prevents:
What it does not prevent:
Operational dependencies:
Failure mode:
Residual risk:
Rejected alternative and what it would cover:
Compensating control, if allowed:
Verification test:
Success measure:
Review trigger:
```

# 19. Harm Gate

Apply stronger review when control selection can:
- interrupt healthcare/safety/industrial operations;
- isolate critical systems;
- block business-critical software;
- create material privacy effects;
- impose large financial cost;
- affect legal/regulatory obligations.

High impact does not prove high threat probability.

Prefer staged, reversible deployment when evidence is incomplete and availability costs are
significant.

# 20. Adversarial Test Suite

T1 — Internet exploit against public service: network controls should receive strong weight.  
T2 — Malware delivered through permitted email/web path: endpoint/application control must
be considered.  
T3 — Stolen VPN credential: perimeter-only answer should fail if identity/endpoint path
dominates.  
T4 — Internal compromised host: evaluate segmentation/endpoint over external perimeter.  
T5 — Unmanaged medical/OT device: endpoint-agent assumption must be rejected if unsupported.  
T6 — Remote workforce: static-boundary assumptions must be challenged.  
T7 — Application allowlist blocks business-critical tool: availability/operations must alter
the recommendation.  
T8 — Firewall present but rule permits attack path: presence must not equal effectiveness.  
T9 — EDR installed but agent offline: deployment must not equal operation.  
T10 — Two controls cover distinct attack steps: skill should recommend defense in depth
unless forced to choose one.  
T11 — Duplicate vendor evidence: no false corroboration.  
T12 — Alternate attack path bypasses preferred control: recommendation must be downgraded or
revised.

# 21. Calibration Plan

Pilot across at least:
1. perimeter vs endpoint;
2. segmentation vs identity;
3. EDR vs network IPS;
4. preventive vs detective control;
5. IT vs availability-critical healthcare/OT case.

Measure:
- whether the skill identifies the dominant attack step;
- whether recommendations change appropriately with architecture;
- whether false "best control" claims decrease;
- whether residual paths are surfaced;
- whether test plans actually validate the claimed control effect.

# 22. Source Register

External grounding:
- NIST Risk Management Framework, Select step.
- NIST SP 800-53 Rev. 5 and SP 800-53B control selection/tailoring concepts.
- NIST Cybersecurity Framework 2.0.
- MITRE ATT&CK Enterprise mitigations, including Network Segmentation (M1030),
  Filter Network Traffic (M1037), Network Intrusion Prevention (M1031), and
  Limit Software Installation (M1033).
- MITRE ATT&CK ICS network segmentation/filtering material where relevant to
  operational environments.

Course grounding:
- CYBR-5000 Chapter 1: control categories and control types.
- CYBR-5000 Chapter 2: CIA, AAA, gap analysis, zero trust, deception/disruption.
- CYBR-5000 Chapter 5: threat actors and motivations.
- CYBR-5000 Chapter 6-1: vectors, attack surfaces, vulnerable/unsupported software,
  unsecure networks, open ports, credentials, supply-chain and human vectors.
- CYBR-5000 Chapter 11: enterprise infrastructure, placement, zones, attack surface,
  connectivity, failure modes, appliances, port security, segmentation, firewalls,
  remote access, VPN, tunneling, SD-WAN, and SASE.

Internal grounding:
- VesselFramework evidence-status and provenance controls.
- Bottleneck / CANNOT-WILL NOT reasoning.
- control-assurance separation.
- alternatives and adversarial-path testing.
- Harm Gate and runtime-state truth rules.

# 23. Final Rule

**Do not ask which security product is strongest in the abstract. Identify the mission,
attack path, and enforcement point; then select the control whose verified operation most
directly constrains the risk while leaving the least consequential residual path.**
