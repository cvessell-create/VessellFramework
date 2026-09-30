---
name: vessel-framework-ghost-job-filter
description: >
  Deterministic ghost-job detection for VessellFramework: normalize and
  fingerprint posting text, cluster near-duplicate reposts, score repost,
  circulation, and freshness-masking signals, and filter roles kept alive
  without hiring intent out of a candidate set — every drop auditable.
---

# VesselFramework Ghost-Job Filter Skill
## Version 0.1 — Detection and Filtering Doctrine

## 1. Purpose

Job boards are polluted with listings that circulate without hiring intent:
the same text reposted for months across aggregators under fresh listing
IDs and fresh "posted N days ago" stamps. This skill turns that pattern
into a deterministic filter:

`COLLECT -> GROUP-BY-ROLE -> NORMALIZE -> CLUSTER -> SIGNAL -> VERDICT -> FILTER -> REPORT`

The package implementation (`vessell.verify`) performs no network calls and
no model inference. It judges only the sightings it is given, and every
dropped role ships with the report that dropped it.

## 2. Operating Contract

The agent must:
- group sightings by normalized (employer, title, location) before any
  comparison — different roles are never each other's evidence;
- never judge a role on a single sighting; one posting is `NO_SIGNAL`;
- treat identical text as a *clustering* step, not a verdict — the verdict
  comes from the signal battery (repost IDs, circulation, freshness gap);
- drop `LIKELY_GHOST` roles from the candidate set, keep `SUSPECT` roles
  flagged, keep `NO_SIGNAL` roles clean;
- attach the `GhostJobReport` to every filtered role so the decision is
  reproducible from the raw sightings;
- break ties against the employer's own careers page: a live listing on
  the employer's site outweighs aggregator signals.

## 3. Signal Catalog

| Signal | Threshold | What it means |
|---|---|---|
| Multi-source identical text | same text on >= 3 distinct sources | listing is syndicated, not freshly posted |
| Repost IDs | >= 3 distinct listing IDs, same text | the "new" posting is a re-skin |
| Long circulation | identical text seen >= 60 days apart | kept alive, not filled |
| Freshness masking | claimed posted date >= 30 days later than first observation of the same text | repost disguised as new |

Verdict: 3+ signals -> `LIKELY_GHOST`; 1–2 -> `SUSPECT`; 0 -> `NO_SIGNAL`.

## 4. Package Mapping

| Skill concept | VessellFramework implementation |
|---|---|
| Posting sighting | `JobPosting` (title, employer, location, text, source, listing_id, claimed_posted, first_seen) |
| Role grouping | `group_postings_by_role()` — case/punctuation-insensitive role key |
| Text normalization | `_normalize_text()` — lowercase, strip punctuation, collapse whitespace |
| Near-duplicate clustering | difflib ratio >= 0.92 merges aggregator-tweaked reposts |
| Signal battery + verdict | `detect_ghost_job()` -> `GhostJobReport` |
| Candidate filtering | `filter_ghost_jobs()` -> (kept, reports); deterministic report order |

## 5. Worked Example

Uline Operations Manager, Lacey WA: identical $96k–$160k text on Monster,
CareerBuilder (two listing IDs), and Ladders; same text circulating ~68+
days; "posted 4 days ago" stamps on text first seen ~275 days earlier.
Four signals -> `LIKELY_GHOST` -> dropped from the evening edition's job
section and replaced with a verified opening.

## 6. Guardrails

- Aggregator presence alone is not a signal: legitimate jobs are
  syndicated too. The pattern is *identical text + repost IDs +
  circulation + freshness masking*.
- `first_seen` must be an observed date, never inferred. Without real
  dates, circulation and freshness signals do not fire — the verdict
  degrades to `SUSPECT` at most, never `LIKELY_GHOST` on text alone.
- Salary-only or title-only matches are not text matches: cluster on the
  description body.
- A role the employer confirms as open (careers page, recruiter) is kept
  regardless of aggregator noise; record the override in the report note.

## 7. Validation and Promotion

Promote a collection adapter only after:
1. fixture-based tests pass without network access (`tests/test_verify.py`);
2. near-duplicate clustering merges tweaked reposts and splits distinct roles;
3. single-sighting input returns `NO_SIGNAL`, never a false ghost;
4. every `LIKELY_GHOST` verdict reproduces from its stored sightings;
5. `filter_ghost_jobs()` keeps `SUSPECT` roles flagged rather than dropped.
