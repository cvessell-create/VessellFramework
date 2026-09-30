---
name: vessel-framework-news-edition-report
description: >
  Daily news-edition report doctrine for VessellFramework: research, planted-news
  verification, resume-matched job hunting with ghost-job filtering, and
  artifact delivery — every claim scored, every posting hunted, every verdict
  auditable.
---

# VesselFramework News-Edition Report Skill
## Version 0.1 — Report-Building Doctrine

## 1. Purpose

A daily news edition is an intelligence product: researched, verified,
matched to the reader's needs, and delivered on schedule. This skill is the
standing operating procedure for building it:

`RESEARCH -> VERIFY -> MATCH -> GHOST-HUNT -> BUILD -> DELIVER`

It binds two VessellFramework capabilities into the pipeline: planted-news
verification (`vessell.verify.verify_claim` / `analyze_planted_news`) on the
news side, and ghost-job filtering (`vessell.verify.filter_ghost_jobs`) on
the jobs side. The package judges sightings; this skill tells the report
builder which sightings to gather and what to do with the verdicts.

## 2. Operating Contract

The builder must:
- produce the edition every day, including slow-news days — a quiet day
  gets a quiet edition, never a skipped one;
- verify before asserting: no shaky claim enters the report without a
  verification verdict, and no job lead enters without a ghost-hunt pass;
- label instead of asserting: `SINGLE_SOURCE`, `SUSPECT`, and
  `UNVERIFIABLE` are honest report states, not failures;
- drop `LIKELY_PLANTED` claims and `LIKELY_GHOST` postings outright, and
  say what replaced them;
- keep the reader's standing exclusions inviolate (fraud roles, federal /
  clearance / defense / IC-pedigree employers, application-status items);
- deliver the refreshed artifact card in chat with a one-line note.

## 3. Pipeline

### RESEARCH
Cover the standing beats: national/US, world, Washington state,
Olympia/Thurston County. Prefer primary sources. Record for each item:
source, tier, publish time, wording, evidentiary root, and whether an
official record exists. Aggregator-sourced and developing claims are
flagged at intake, not at write-up.

### VERIFY (planted-news intel)
Apply the `vessell.verify` doctrine to every shaky claim:
- Official record affirms -> `VERIFIED`. Done; cite it.
- Count independent roots: one wire across ten outlets = one root.
  Two or more independent established roots -> `CORROBORATED`.
- Single low-tier source -> `SINGLE_SOURCE`: label it, do not assert it.
- Established denial, no official backing -> `LIKELY_PLANTED`: drop it.
- Hostile-spread tells (synchronized low-tier burst, text-clone army,
  single-origin laundering, orphaned circulation) -> `SUSPECT` at one
  indicator, `LIKELY_PLANTED` at two.
- Otherwise -> `UNVERIFIABLE`: the report says so, plainly.

### MATCH (job section as matching tool)
Score each opening against the reader's resume and LinkedIn profile.
Per role, show what lines up and what the gap is. The bar is "could he
qualify," not "perfect match." Standing filters: commercial employers
only; near Olympia WA / Tacoma / Seattle-Bellevue hybrid / WA-eligible
remote / compatible US remote; junior/associate/Analyst I level.
Exclusions are absolute: fraud, financial crime, federal hiring,
clearances, defense contractors, military/IC-pedigree firms.

### GHOST-HUNT
Run every surviving lead through the ghost-job filter doctrine:
- Identical text on 3+ sources, 3+ listing IDs, 60+ days circulation,
  or fresh "posted N days ago" stamps on old text -> `LIKELY_GHOST`:
  drop and replace with a verified opening.
- One or two signals -> `SUSPECT`: keep, flagged.
- Employer's own careers page is the tiebreaker: a live listing there
  outweighs aggregator noise.

### BUILD
Refresh the edition artifact: tight sections, a source link on every
item, caveats on developing/aggregator claims, verification labels where
earned, per-role match rationale in the jobs section. No application-status
items unless the reader asks.

### DELIVER
Reply in chat with a one-line note and the refreshed artifact card.
The edition is not delivered until the card is presented.

## 4. Package Mapping

| Skill concept | VessellFramework implementation |
|---|---|
| Claim intake | `ClaimCheck`, `SourceSighting` (tier, published_at, text, root, denies, is_official_record) |
| Corroboration verdict | `verify_claim()` -> `VerificationResult` |
| Hostile-spread analysis | `analyze_planted_news()` -> `PlantedNewsReport` |
| Posting intake | `JobPosting` (title, employer, location, text, source, listing_id, claimed_posted, first_seen) |
| Ghost verdict + filtering | `detect_ghost_job()` / `filter_ghost_jobs()` -> `GhostJobReport` |
| Audit trail | `to_dict()` on every report; verdicts reproduce from stored sightings |

## 5. Worked Example

Evening edition, Sept 29 2026: a M4.2 earthquake near Wauna surfaced from
aggregators. Verification: USGS official event page (reviewed by a
seismologist, thousands of felt reports) -> `VERIFIED`, reported as fact
with the USGS citation. Same edition: a Uline Operations Manager posting
showed identical $96k–$160k text across Monster, CareerBuilder (two listing
IDs), and Ladders, circulating 60+ days with fresh "posted days ago"
stamps -> `LIKELY_GHOST`: dropped and replaced with a verified-live White
Cap opening. The edition carried no planted news and no ghost jobs.

## 6. Guardrails

- Verification informs; the builder decides. A `SUSPECT` claim with a
  primary source behind it can still run — with the label attached.
- Never manufacture sightings to force a verdict. Thin intake produces
  `UNVERIFIABLE`, honestly.
- The reader's exclusions (fraud, federal/clearance/defense/IC-pedigree,
  application-status items) are not subject to verification overrides.
- Satire, parody, and opinion are out of scope for the intel pass.
- A burst with an official record behind it is distribution (everyone
  reports the quake at once), not manufacture.

## 7. Validation and Promotion

Promote a report adapter only after:
1. the edition builds end-to-end on a slow news day without skipping;
2. a planted fixture (synchronized low-tier burst, no primary) is dropped,
   not published;
3. a ghost fixture (identical text, multi-ID, long circulation) is dropped
   and replaced;
4. every published claim carries either a verification label or a primary
   source citation;
5. the reader's standing exclusions hold for 30 consecutive editions.
