# VesselFramework v3.8.1 — Stale-State Correction

Date: 2026-09-06

## Corrections
- Removed the inference that package contents prove live/private runtime synchronization.
- Runtime synchronization now requires successful apply + post-write verification.
- Added an internal-method boundary for proprietary/original analytical methods.
- Added a translation rule: internal framework findings may be expressed externally using accepted domain terminology.
- Clarified that framework confidentiality cannot be used to evade academic-integrity or source/tool disclosure requirements.
- Added disclosure accuracy rule: disclose only external tools/sources actually consulted.
- No claim is made that this package has modified any private runtime path.

## Current state
- Package specification: v3.8.1
- Runtime/private-path state: UNVERIFIED/NOT APPLIED unless independently verified after installation.

## Verification and State Lifecycle

The framework uses the following runtime state sequence:

```text
UNVERIFIED/NOT APPLIED
		-> DRY RUN
		-> APPLY ATTEMPTED
		-> VERIFIED
```

An error, inaccessible target, failed write, or failed post-write hash returns
the affected target to `UNVERIFIED/NOT APPLIED` or marks the overall runtime
state `DEGRADED`. A package may not be described as installed merely because
the dry run completed or the source files are present.

### Required verification evidence

An installation claim requires all of the following where applicable:

- the resolved target root or target path;
- the source artifact used;
- a successful write result;
- the pre-write hash when a target already existed;
- the post-write hash read from the target;
- the timestamp and result recorded in the sync log;
- the backup location when an existing target was replaced.

The SHA-256 package manifest verifies the contents of this package. It does
not, by itself, verify a private runtime path. The path synchronizer and its
post-write log provide that separate runtime evidence.

### Failure and rollback rules

The synchronizer must preserve an existing target before replacement. If the
write or post-write verification fails, the operation must be reported as an
error and the previous target must remain available through its backup. No
partial or unverified result may be reported as successful installation.

### Authority boundaries

- **Package contents** define the intended framework state.
- **The synchronizer** attempts to change the configured runtime state.
- **The sync log** records what was actually attempted and written.
- **The SHA-256 manifest** verifies package-file integrity.
- **This correction record** defines the claims that may legitimately be made
	about installation and disclosure.

No one artifact substitutes for the others.

### Operator verification checklist

Before relying on the runtime copy:

```text
[ ] Confirm the owner-controlled target root.
[ ] Run the package hash verifier.
[ ] Run the synchronizer in dry-run mode.
[ ] Review missing, inaccessible, or required targets.
[ ] Apply synchronization only after the dry run is acceptable.
[ ] Confirm post-write hashes in the sync log.
[ ] Retain backups and record the verified runtime state.
```
