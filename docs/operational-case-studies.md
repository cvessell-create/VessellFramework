# Operational case-study release (3.9.0)

This is executable local software, not a demo-only distribution. Existing
validator, pipeline, tool and authorization interfaces remain available.
Examples remain examples. Removing the project-wide demo framing does not
remove authorization, provenance, review requirements or evidence limitations.
The pipeline now requires an explicit `--input` and validates its contract.

## Run the reconstructed claim-correction comparison

```sh
python -m pip install .
vessell-study --spec case_studies/claim_correction/spec.json \
  --output-dir outputs/claim-correction-study
vessell-study --verify-only --output-dir outputs/claim-correction-study/framework
```

Use a new output directory for every run. Existing runs are never overwritten.
Both arms run in separate Python processes to isolate lifecycle registries.
Every snapshot is a real JSON file. SQLite stores file receipts and the full
hash-chained lifecycle event records. A fresh process reopens the database and
checks every consumer's ID, digest and event ordering. Paired JSON/Markdown
reports are verified before success is returned. Exit statuses: 0 accepted,
1 comparison acceptance failed, 2 input, execution or integrity failure.

The first scenario reconstructs an unverified constraint and five dependent
consumers: goal, scheduled search, morning edition, evening edition and memory.
These are **managed local files**, not external accounts, scheduled services,
application portals or an actual memory system. The second scenario is a
constructed official-record positive control with two consumers, checking
that the gate does not simply block everything.

The `snapshot-only` baseline stores the initial claim, allows consequential
use without corroboration and does not update downstream snapshots after
withdrawal. It is a specified counterfactual comparator, not a measurement
of the original assistant or a competing product. Both arms use exactly the
same frozen input population. The framework arm uses existing intake, gate,
supersession, dependency delivery and confirmation APIs. It confirms a
correction **only after writing and reading back the actual file**. New
corrections remain UNVERIFIED; propagation does not establish their truth.

Reports count unverified uses allowed, corroborated uses blocked, corrections
read back and original snapshots remaining. Counts are deterministic for the
frozen specification; UUIDs, event execution times and hashes can differ.
No field-effectiveness percentages or statistical significance are inferred.
Narrative dates travel separately from actual lifecycle execution timestamps.
Noon UTC in the frozen specification is a normalized reconstruction value,
not a verified time from original operational logs.

## Source-document findings applied before publication

The supplied *From AI to SI Claim Provenance and Correction Propagation* DOCX
was retained locally. Its SHA-256 is pinned in the deidentified specification;
the original, personal details and external configuration files are not
published. Paragraph numbers refer to the extracted document body, not pages.

| Source requirement / finding | Executable response | Evidence boundary |
|---|---|---|
| 19-23: unverified intake becomes a consequential constraint | Provenance snapshot and consequential gate; positive control | Local gate behavior, not corroboration of the historical report |
| 24, 29-30: downstream systems lack enforcement | Managed JSON adapter with registered dependencies | No external connector or CAPTCHA bypass |
| 80-81: supersession and verified propagation | Original retained in receipts/events; write/read-back before acknowledgment | Tests are not a machine-checked causal-broadcast proof |
| 82: claim decay and revalidation | Existing stale-claim fail-closed lifecycle tests remain applicable | This comparison has no long-duration field follow-up |
| 76, 101: repository described as private | Release points to the public local-rebuild repository | Historical document not silently rewritten |
| 29, 76, 102: AI-to-SI executive-order terminology | The cited official White House fact sheet was retrieved and supports the terminology summary | Terminology is not evidence of this software's intelligence or efficacy; the order's full legal text was not reviewed |
| 74, 81, 86: formal/SI or operational proof language | Explicit local-software evidence level in every study report | No formal certification, external efficacy or independent field proof |

Required primary records for a historical replay remain absent: original
configurations, memory exports, scheduled-job logs, receipts and actual outcome
labels. The reconstruction does not fill those missing records with fiction.

The terminology source is the [White House fact sheet dated September 29,
2026](https://www.whitehouse.gov/fact-sheets/2026/09/fact-sheet-president-donald-j-trump-inaugurates-the-era-of-super-intelligence/).
The release does not convert its policy terminology into a capability claim.

## Durable state and scope

The comparison persists receipts and events and supports post-restart
verification. The library's live lifecycle registries remain process-local.
This release is **not** a crash-resumable production workflow controller, a
transaction across arbitrary files and databases, or a distributed broadcast
service. Files and receipts can be damaged between operations; failed runs
remain for diagnosis and return failure rather than success. No automatic
repair of drift, concurrent consumer writers or arbitrary file formats is
supported. Local hashes detect alteration relative to receipts; they are not
an externally signed attestation or protection against rewriting all evidence.

Runtime reference code and schemas are now included in installed wheels and
source distributions, generated from canonical repository sources at build
time. CI runs the case study again from outside the checkout after non-editable
wheel installation. The historical manifest filename is retained for
compatibility; it tracks current source contents, not the runtime version.

Independent replication with a separate evaluator, prospective labeled
outcomes, authorized real-system connectors, crash/concurrency recovery and
sector-specific field studies remain subsequent gates. Public-data audits,
CDC retrospective scoring, the replay lab and Linux containment remain
separate evidence streams; their results are not new framework field outcomes.

## Release measurements

Executable source evaluated at commit
`6b4447d030911485a144d0e5e86c8973cb3259fa`; subsequent release changes only
document the measurements and update the source-integrity manifest.
The frozen specification SHA-256 is
`c4c274bf47fbc54ba088037ba29ccea30e440487c6eb34b5ee654a0335d2903e`.
The case-study implementation SHA-256 is
`28eb28f7a1ec294583665a0ef08a4887a1635ee8c7cb846134b1a395ddef655d`.

| Local outcome | Snapshot-only baseline | Framework |
|---|---:|---:|
| Unverified consequential uses allowed (five-consumer scenario) | 5 | 0 |
| Corroborated positive-control uses allowed | 2 | 2 |
| Corrected consumer files verified by read-back | 0 / 7 | 7 / 7 |
| Original snapshots remaining after withdrawal | 7 | 0 |
| Newly issued unverified corrections pass consequential gate | 0 | 0 |

All 342 regression tests passed on macOS and inside the offline Linux
container (zero Linux skips/failures/errors). Focused lint and strict type
checks passed. All ten containment assertions and all 271 source-manifest
entries passed in the evaluated image. Existing public-data replay and
ATT&CK/EPSS audits also passed without modifying the frozen inputs.

A fresh environment installed the non-editable wheel and completed the same
comparison from outside the checkout, then reopened and verified seven
framework receipts. A separate base-R script recalculated SHA-256 with the
system hashing tool and read all fourteen baseline/framework snapshot IDs:
all matched the exported SQLite receipts; seven original snapshots remained
in the baseline and none in the framework arm. This is cross-language
computational replication by the same evaluation workflow, **not independent
third-party or field validation**. No significance or population efficacy
estimate is reported from these seven managed consumers.
