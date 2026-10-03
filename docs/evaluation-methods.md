# Evidence and evaluation methods

## Scope and standing

This map connects the local rebuild's assessed gaps to executable checks,
public data, and methods for subsequent empirical validation. Bibliographic
metadata and scope documents do not need to become executable to be useful:
their proper test is accuracy, traceability, and agreement with the software.
Implementation tests, real-data scoring, independent computational replication,
and independent field validation are different levels of evidence.

The initial Llama importance/support/confidence scores were ordinal judgments
about an earlier GitHub snapshot, not estimates of efficacy. Do not increase
them merely because a dataset or a method has been added. Reassess affected
claims against the new code and results while retaining the historical scores.

## Methods by framework aspect

| Aspect / assessed gap | Appropriate method and measures | Available data / current execution | Evidence still required |
|---|---|---|---|
| Harm Gate / unknown exposure | Truth-table and missing-field/type regression tests; explicit review outcome; distinguish intake clearance from authority | Shared evaluator used by both runners and packaged pipeline. Tests cover all 128 complete boolean combinations, each missing field, invalid values, and report/CLI review status | Independent assessment of whether the gate reduces harm under realistic decisions; proportional safeguards must be observed, not inferred from a cleared flag |
| Provenance, independence, correction propagation | Lineage invariants, cycle/conflict/missing-parent tests, repeated-root discounting, stale/disavowed claim rejection; timestamped audit of source-to-output derivation | Existing provenance/lifecycle regressions; official source files, retained hashes and retrieval metadata. W3C PROV provides an external vocabulary and constraint reference | Source-content truth and independence require external corroboration; matching a checksum proves file identity, not claim truth. No W3C conformance certification claimed |
| Case/report output format | Validate real serializer outputs, reject missing/mismatched payloads, read back JSON and Markdown against the same evaluated result | New verification-record contracts and paired-output checks; illustrative case remains explicitly illustrative | No report-format test establishes analyst findings or control efficacy |
| Forecasting / no outcome scoring | Proper interval score, empirical interval coverage, point error, paired persistence comparison, explicit forecast/observation/date/horizon joins | Executable CDC state ensemble incident-death scorer; retained data/checksums; separately implemented base-R cross-check | Prospective forecasts produced by the framework, frozen pre-outcome records, release-vintage observations, preregistered thresholds, temporal holdout, and block/cluster uncertainty |
| Llama weighting / ordinal score reliability | Repeated blinded runs, model/prompt/version hashes, rank stability, human-label agreement, ablation against unweighted baseline; report runtime and accuracy separately | Existing weight tests and prior two-worker scoring assessment; current scores are not calibrated probabilities | Independent labels, reserved holdout and uncertainty; no efficacy conclusion from model self-rating |
| Claim verification / planted-news heuristics | Labeled evidence retrieval and verdict evaluation: confusion matrix, per-class precision/recall, abstention, false-positive costs; time/source-grouped split | Existing deterministic heuristic tests; FEVER data terms verified, published download blocked | Licensed labeled holdout and a verified label mapping. A provenance corroboration verdict is not automatically a FEVER entailment verdict |
| Ghost-job filtering | Posting-level longitudinal ground truth, independent employer adjudication, time/company-grouped holdout, precision/recall and error cost | Existing heuristic fixtures; BLS openings/hires and OPM accessions are public context | No public aggregate series labels a particular advertisement as fraudulent. Do not label an openings/hires difference as a ghost-job count |
| Cyber vulnerability intelligence | CVE/date/source extraction, as-of selection, severity versus likelihood separation, positive-set recall; verify deployment applicability with authorized scanner evidence | Full KEV, 25 NVD enrichments, current EPSS; regression excludes future KEV dates | Historical EPSS and dated outcome telemetry. KEV absence is not a negative exploitation label; CVSS is not a probability |
| SOC, scanner ingestion, remediation | NIST SP 800-53A examine/interview/test; replay known events, approval/authorization/rollback tests; false alarms, detection latency, verified post-remediation state | Existing scanner/SOC/remediation tests; no scans or changes to external systems made in this evaluation | Authorized operational telemetry with baseline/comparator, control deployment and verification timestamps; controlled rollout needed for causal risk-reduction claims |
| Security-control selection / organizational efficacy | SP 800-55 measures tied to objective, population and period; baseline versus intervention; record confounders, failures and unintended effects | DoD award/subaward samples provide funding/sector provenance, not effectiveness labels | Public technical reports with methods, comparators, outcome measures and matching contract identifiers; no automatic award-to-report causal join |
| Four pillars, analytical briefing and alternatives | Blinded case assessment, fixed rubric, multiple independent raters, disagreement adjudication; compare framework versus ordinary analysis | Existing doctrine and case fixtures; WWC study-review data can test evidence-appraisal practice, not analytical-domain transfer | Representative task set, blinded reviewers, inter-rater reliability, time/error outcomes and independent external replication |
| Evil Twin / recognition and Startle Gate | False acceptance/rejection, challenge replay and timeout tests in an authorized environment; assess verification burden | Existing recognition and single-file tests | Realistic labeled challenges and independent evaluators; do not equate fixture success with identification accuracy |
| Cyber-range learning | Education-style comparative study, baseline equivalence, attrition, pre/post and delayed retention; blinded scoring | WWC standards and study-review records for method selection; IPEDS directory for institution context | Consenting participants, protocol/ethics review as applicable, a comparison group, meaningful skill outcomes; existing unrelated studies do not validate this framework |
| Schemas, citation metadata and canonical scope | Required-field/type/range contracts, serializer-schema agreement, accurate citation/version and canonical/noncanonical classification | New positive and required-field-negative tests for forecast, evidence-product, skill and verification records | Schema validity is not real-world validity. Scope/citation files should retain their documentary role |
| Synchronization / integrity | Expected-versus-read-back content hash, corrupt-write negative test, exact canonical/mirror comparison, manifest drift verification | Installer now checks expected content; packaged skill bytes tested; paired reports verified | Proof applies only to inspected local files. Remote GitHub, private mounts and other machines remain unverified unless independently read back |

## Domain datasets must not be pooled indiscriminately

- **CDC:** join on exact location, target date, target type, issue date and
  horizon; count exact duplicates, nonfuture targets and missing observations.
  Current retrospective scoring is exploratory and uses revised archive data.
- **NOAA/NWS:** preserve station/location, units, quality flags, issue time,
  valid time and accumulation window. Daily NOAA observations are not archived
  NWS forecasts; match future forecasts or historical vintages before scoring.
- **BLS/OPM/USAJOBS:** preserve series definitions, seasonality, units, period,
  publication date and revisions. Job openings are a stock and hires a flow;
  subtraction or a ratio does not identify fake listings. OPM monthly
  accessions cannot be joined to USAJOBS postings without appropriate keys.
- **DoD prime/subawards:** preserve generated award identifiers, prime linkage,
  UEI, NAICS/PSC and action periods. The downloaded top-ten samples are
  nonrepresentative discovery samples, not complete sector estimates.
- **Education:** WWC review/findings records are not independent study counts:
  one review can contain multiple outcomes and contrasts. Review standards
  version, design, attrition, baseline equivalence and effect-size definitions
  before synthesis. IPEDS HD2023 is a directory, not student outcome data.
- **State:** advisories/country reports establish what the agency published.
  Advisory levels are policy judgments, not calibrated event probabilities.
  Travel advisories are not DoD award or hiring outcomes.

Combine these sources through a **common evidence catalog**, not a single
unlabeled training table. A usable entry records source URL/version, retrieval
time, hash, license/access conditions, units, keys, geography, date/vintage,
outcome-label definition, method, exclusions and limitations. Keep lineage for
every derived feature; unresolved cross-domain joins remain unresolved.

## Primary method references

1. [NIST SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final):
   assessment procedures and examine/interview/test. This does not attribute
   VessellFramework's analytical doctrine to NIST.
2. [NIST SP 800-55 Volume 1](https://csrc.nist.gov/pubs/sp/800/55/v1/final):
   information-security measurement and measure selection.
3. [W3C PROV-O](https://www.w3.org/TR/prov-o/) and
   [PROV constraints](https://www.w3.org/TR/prov-constraints/): provenance
   entities, activities, agents, derivation and validity.
4. [Bracher et al., 2021](https://doi.org/10.1371/journal.pcbi.1008618):
   evaluating epidemic interval forecasts. The current implementation uses a
   single 95% interval score, not the full weighted interval score.
5. [R scoringutils](https://CRAN.R-project.org/package=scoringutils): independent
   scoring tooling. The executed cross-check used base R, not this package.
6. [WWC handbooks and protocols](https://ies.ed.gov/ncee/wwc/Handbooks):
   study-design review and evidence synthesis; adapt the design logic without
   implying that education intervention effects transfer to cybersecurity.
7. [NIST Phish Scale User Guide](https://www.nist.gov/publications/nist-phish-scale-user-guide):
   contextual difficulty in awareness assessments, not a generic deception
   classifier or proof of training effectiveness.
8. [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework):
   measurement and risk-management guidance; not certification of a model.
9. [FIRST CVSS 4.0](https://www.first.org/cvss/v4.0/specification-document)
   and [EPSS FAQ](https://www.first.org/epss/faq): severity and exploitation
   likelihood are distinct from environmental impact.
10. [DTIC technical reports](https://discover.dtic.mil/technical-reports/) and
    [distribution restrictions](https://discover.dtic.mil/marking-documents/):
    use only public-release reports; contract awards alone do not establish
    controlled-study design or efficacy.
11. [CISA SSVC](https://www.cisa.gov/resources-tools/resources/stakeholder-specific-vulnerability-categorization-ssvc)
    and [CMU SEI SSVC v2](https://www.sei.cmu.edu/library/prioritizing-vulnerability-response-a-stakeholder-specific-vulnerability-categorization-version-20/):
    stakeholder-specific prioritization. Exploitation, impact, automatability
    and mission/public-well-being context must be supplied; KEV alone cannot
    fill the decision tree. A prioritization method is not evidence of a
    successful patch or a measured reduction in incidents.
12. [CISA AA24-038A incident advisory](https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-038a)
    with its linked public STIX report: source-attributed incident observations
    and defensive recommendations, not a representative labeled negative set
    or organization-level patch-outcome table.
13. [UNB CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html):
    labeled laboratory intrusion-detection traffic. Review capture and label
    quality; split by day/session/scenario rather than random correlated
    flows. This is not production incident telemetry or a patch-efficacy trial.
14. [CMU CERT insider-threat test datasets](https://www.sei.cmu.edu/library/insider-threat-test-dataset/):
    explicitly synthetic, with answer keys. Review repository terms before
    downloading; synthetic detection performance is not field effectiveness.
15. [Stanford HELM](https://crfm.stanford.edu/helm/): Holistic Evaluation of
    Language Models, not a vulnerability-patching framework. Use multi-metric
    task evaluation, not a single self-assigned support score.
16. [R irr](https://CRAN.R-project.org/package=irr): agreement and inter-rater
    reliability methods for independently labeled cases. Choice of coefficient
    depends on scale, number of raters and missingness; agreement is not truth.

Free university courses, Khan Academy and official YouTube lecture sources are
mapped separately in [free method courses](free-method-courses.md). Their role
is teaching how to perform an evaluation, not supplying outcome labels.

## Executable public-data quality checks

Run the standard-library audit on the downloaded batch, keeping generated
reports outside the input directory:

```sh
python -m vessell.data_evidence --data-dir /path/to/public_evaluation_data \
  --output-dir /path/to/data_audit
```

It checks NOAA station/date uniqueness, observed calendar gaps, missing values
and quality flags; BLS series/period uniqueness, monthly-versus-annual records
and retained source warnings; and WWC review-level design/rating counts without
treating repeated findings as independent studies. Conflicting review metadata
is exposed and excluded from those distributions.

The existing initial download manifest is checked before parsing. Supplemental
file hashes are captured as a local baseline, not asserted as remote
authentication. On later runs, pass the prior generated JSON with
`--previous-catalog /path/to/data_audit/evaluation.json` to reject source drift.
Output JSON and Markdown use the shared exact read-back synchronization check.
Do not overwrite source data with reports. PDF and OPM Parquet entries state
their limited framing/header validation rather than claiming full semantic
inspection. This audit does not fit a model, infer causal effects, or supply
missing operational outcome labels.

To combine an earlier weight assessment with these results while preserving
its scores and original snapshot, run:

```sh
python -m vessell.evidence_assessment --assessment /path/to/assessment.json \
  --data-audit /path/to/data_audit/evaluation.json \
  --forecast-evaluation /path/to/forecast/evaluation.json \
  --project-root /path/to/rebuild --output-dir /path/to/combined_assessment
```

Both input reports must have synchronized Markdown counterparts. The generated
extension hashes linked implementation/test files, lists every historical
artifact's linkage status, and explicitly leaves unreviewed gaps unresolved.
It does not rerun Llama or silently inflate historical importance/support scores.

## What cannot honestly be closed with downloaded data

No independent external field validation of VessellFramework has been
established. Public observational records cannot supply missing randomization,
deployment, consent, outcome adjudication or a prospective framework prediction.
Use external studies as method/evidence references, evaluate applicability, and
retain uncertainty. Do not silently turn a documented limitation into a success
claim or fabricate outcome labels.
