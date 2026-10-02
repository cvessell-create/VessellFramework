# Claim provenance and correction lifecycle

VessellFramework treats claims as records with provenance, uncertainty, and
an explicit lifecycle. The supported API is in `vessell.provenance` and is
re-exported from both `vessell` and the compatibility namespace `vessel`.

## Operating rules

- Intake records the assertion, subject, source, source tier, and observation
  time. New claims default to `UNVERIFIED`; AI-generated content cannot be
  designated as an official record.
- Corroboration requires an official record or two distinct provenance roots.
  Repeated reports from one root count once.
- `gate_for_use(claim, "low")` permits provisional use only with the status
  attached. Consequential use requires corroboration or an explicit,
  named, reasoned waiver. Waivers are consumed by the next consequential
  gate decision.
- Disavowal does not erase the original. It records the reason and actor,
  marks the original `DISAVOWED`, and creates a linked superseding claim.
- Operational consumers register as dependents. Corrections are delivered
  and confirmed in causal order; a dependent cannot confirm a correction it
  has not received or skip an earlier correction in the same lineage.
- A claim with an expired `valid_until` value is stale. Stale claims cannot
  pass the consequential-use gate until revalidated.
- Attribution of an artifact, path, package, or warning to a person or project
  is a separate claim from describing its contents. Do not infer ownership,
  authorship, or association from a name embedded in an artifact alone. Keep
  the artifact separate unless provenance supports the link; record and
  propagate an explicit correction when the subject disclaims it. Do not
  present unsupported personal, academic, professional, or career-impacting
  conclusions as findings.
- Negative existential claims use the search-path gate in `vessell.verify`:
  at least two independent dataset roots must support the absence, and any
  path that finds the target contradicts the negative claim. Record an
  explicit `SearchOutcome` for every attempt: only
  `NOT_FOUND_IN_CHECKED_SOURCE` counts toward absence; `BLOCKED` and `ERROR`
  remain visible but do not count. `dataset_root` identifies shared provider
  or index infrastructure so aliases over one backend are counted once. It
  is caller-supplied provenance, not an authenticity guarantee.

## Example

```python
from vessell import (
    ClaimKind,
    SourceStatus,
    disavow,
    gate_for_use,
    intake_claim,
    register_dependent,
)

claim = intake_claim(
    text="The role is unavailable to the subject.",
    subject="candidate",
    source="unverified intake note",
    source_tier=SourceStatus.WORKING_HYPOTHESIS,
    kind=ClaimKind.REPORT,
    uncertainty="Unverified single-source report.",
)

allowed, reason = gate_for_use(claim, "consequential")
assert not allowed
print(reason)

register_dependent(
    claim.id,
    artifact="job-search configuration",
    location="eligibility filters",
    via="intake note -> project goals -> job-search configuration",
)

correction = disavow(
    claim,
    disavowed_by="analyst",
    reason="The intake statement was not independently verified.",
    corrected_text="Eligibility has not been established.",
)
```

Use `deliver_correction` to deliver the correction to registered dependents
and `confirm_dependent_update` only after each dependent has applied it.
`propagate_correction(claim_id)` without a correction ID is a read-only
enumeration of registered dependents.

## Audit limits

Lifecycle state and the SHA-256 event chain are process-local. The hash chain
detects edits, removal, and reordering while the event data remains available;
it is not a digital signature, a proof that a claim is true, or evidence that
a remote dependent received an update. Applications that require durable
records must persist exported claim/event records in their controlled
storage and retain independently verifiable backups.
