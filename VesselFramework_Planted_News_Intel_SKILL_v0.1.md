---
name: vessel-framework-planted-news-intel
description: >
  Hostile-spread analysis for VessellFramework: tier-weighted corroboration
  with independence discount, synchronized-burst detection, text-clone-army
  analysis, single-origin laundering tracing, and orphaned-claim detection —
  a deterministic answer to "is this story manufactured?", every indicator
  carrying its evidence.
---

# VesselFramework Planted-News Intel Skill
## Version 0.1 — Hostile-Spread Doctrine

## 1. Purpose

A planted story and a real story look identical in a single screenshot.
They differ in *spread*: who carries the claim, when, in whose words, and
what sits at the root. This skill turns those differences into
deterministic indicators:

`INTAKE -> CORROBORATE -> TIME-CLUSTER -> TEXT-CLUSTER -> ROOT-TRACE -> VERDICT -> REPORT`

The package implementation (`vessell.verify.analyze_planted_news`) performs
no network calls and no model inference. It judges only the sightings it is
given. Verification informs; the analyst decides.

## 2. Operating Contract

The agent must:
- intake every sighting with source, tier, publish time, wording excerpt,
  evidentiary root, and whether it is an official record — thin sightings
  produce thin verdicts, honestly labeled `UNVERIFIABLE`;
- run the base corroboration check first (`verify_claim`): tier-weighted
  roots, independence discount, official-record rule;
- then hunt hostile indicators; never invert the order (a burst means
  nothing until corroboration is scored);
- let an official record win: USGS event page, primary-source document,
  employer's own listing — distribution is not manufacture;
- never assert `LIKELY_PLANTED` on a single indicator; the bar is an
  established denial or two independent hostile indicators;
- ship every verdict with its indicator codes *and* human-readable
  signal lines, plus the embedded corroboration record.

## 3. Indicator Catalog

| Code | Fires when | Reads as |
|---|---|---|
| `official-record` | an authoritative record affirms | authentic anchor (verdict: `AUTHENTIC`) |
| `established-denial` | an established-tier source denies, no official affirmation | manufactured (verdict: `LIKELY_PLANTED`) |
| `synchronized-burst` | >= 4 low-tier outlets publish near-identical text inside a 90-minute window | coordinated push |
| `text-clone-army` | >= 5 distinct sources carry near-identical wording | not independent reporting |
| `single-origin-laundering` | every sighting traces to one non-established root | laundering chain, not corroboration |
| `no-primary-source` | claim circulates with no official record and no established outlet | orphaned claim |

Verdict ladder: official record -> `AUTHENTIC`; established denial ->
`LIKELY_PLANTED`; 2+ hostile indicators -> `LIKELY_PLANTED`; 1 ->
`SUSPECT` (verify against a primary source); clean corroboration ->
`AUTHENTIC`; otherwise `UNVERIFIABLE` — "do not assert" is a verdict too.

## 4. Package Mapping

| Skill concept | VessellFramework implementation |
|---|---|
| Claim + sightings | `ClaimCheck`, `SourceSighting` (tier, published_at, text, root, denies, is_official_record) |
| Corroboration scoring | `verify_claim()` — reuses `SOURCE_TIER_WEIGHTS`, one root counts once |
| Burst detection | `_detect_synchronized_burst()` — sliding 90-min window over low-tier publish times + text clustering |
| Clone analysis | `_cluster_near_duplicate_texts()` — difflib >= 0.92 |
| Root tracing | `effective_root()` — shared wire/origin collapses to one ancestor |
| Full analysis | `analyze_planted_news()` -> `PlantedNewsReport` with `to_dict()` audit record |

## 5. Worked Examples

**Authentic — Sept 29 2026 Wauna M4.2.** USGS official event page
(reviewed by a seismologist, 7,155 felt reports) + PNSN + KOMO + Kitsap
Sun. `official-record` fires; verdict `AUTHENTIC`. The quake was real;
suspicion was the error, and the module says so.

**Likely planted — manufactured bridge-closure scare.** Five low-tier
outlets, byte-identical text, published inside 25 minutes, no official
record, no established outlet. `synchronized-burst` + `no-primary-source`
+ `text-clone-army` fire: 3 hostile indicators -> `LIKELY_PLANTED`.

**Laundering chain.** Three sites cite each other back to one rumor root,
no primary anywhere. `single-origin-laundering` + `no-primary-source` ->
`LIKELY_PLANTED`. Ten sites running one wire copy are one root, not ten —
the independence discount is the whole game.

## 6. Guardrails

- Satire, parody, and opinion are out of scope: the module judges
  *factual* claims and their spread, not tone or viewpoint.
- A burst with an official record behind it is *distribution*
  (everyone reports the quake at once), not manufacture. Corroboration
  runs first for exactly this reason.
- Timestamps must be observed or source-stated, never inferred. Without
  publish times, burst detection stays silent — the verdict degrades
  honestly instead of guessing.
- Low-tier does not mean wrong: a lone local blog can be right. The
  indicators punish *coordination without provenance*, not obscurity.
- This skill produces analytic judgments for the operator's own
  sense-making. It is not a content-moderation verdict about real people
  and must not be wired to one without human review.

## 7. Validation and Promotion

Promote a collection adapter only after:
1. fixture-based tests pass without network access (`tests/test_verify.py`);
2. the USGS-style official-record fixture returns `AUTHENTIC`;
3. the synchronized-burst fixture returns `LIKELY_PLANTED` with all three
   indicators present;
4. ten same-wire sightings collapse to one root (independence discount);
5. single-sighting and empty intakes return `SINGLE_SOURCE` /
   `UNVERIFIABLE`, never a false planted verdict;
6. every verdict reproduces byte-identically from its stored sightings.
