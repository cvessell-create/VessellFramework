# Game Development and Analyst Workflow Reconstruction Skill

## Purpose and authority

Use this skill to explain how **Hail to the Analyst** works, retain every
observable component and narrative family, and transfer useful architecture
into VessellFramework without turning the analyst into a game-score system.
Include the paused **Signal Recall** prototype and its simulation/bridge work.
The operator selected preservation of the framework's analytical purpose.

This skill is below the existing governing doctrine in [SKILL.md](SKILL.md).
Authorization, evidence assurance and Harm Gate protections remain mandatory.
Fictional clearance cards, enemy labels, victory ranks and taunts grant no
real-world authority. Do not transplant combat into external operations.

The original source is pinned to
`cvessell-create/hail-to-the-analyst@0a147bf95e231eff68ea3be7f10003752ce3b573`,
with original `index.html` SHA-256
`0703c346480d6f5aa01b4793e1d760738ba3bc1d9030e225034f076f10638d60`.
Original line references below refer to that commit, not the paused edits.
The [component map](docs/game-component-map.json) covers every named original
function plus presentation, content, callbacks, evaluation and paused additions.

**Knowledge boundary:** source proves the current mechanism, not the exact
prompts, editor actions, authoring dates or order in which the author wrote it.
The build sequence below is a reproducible reconstruction, not invented history.
Retain Apache-2.0 attribution and license when moving actual source. Do not
recreate third-party art, recordings or protected characters just because the
game README calls its visual style a homage.

## 1. Reconstruct the complete system before editing

The game is a self-contained browser program:

`HTML shell -> Canvas context -> world data -> input -> 60 Hz updates -> render -> UI feedback`

The original has no package build, external assets, network requests or real
LLM calls. JavaScript runs inside an IIFE with strict mode and shared module
state. Canvas is 960 x 540; walls use 480 ray columns. Overlay HTML handles
title, briefing, pause, death and victory; procedural canvas shapes provide
walls, characters, items and weapons. WebAudio synthesizes sound.

Inventory before modifying:

1. HTML elements, CSS/theme/media rules and ARIA labels.
2. Globals, map symbol grammar, missions, weapon tables and all narrative strings.
3. Every named function and anonymous event callback.
4. Update order and which functions mutate state.
5. Renderer/notification side effects.
6. Inputs and state transitions, including failure, restart and completion.
7. Tests, CI, publishing requirements and license.
8. Paused interface and bridge additions, keeping their status explicit.

Run the read-only source inventory:

```sh
python -m vessell.game_architecture \
  --game-dir ../hail-to-the-analyst \
  --component-map docs/game-component-map.json \
  --output-dir /absolute/path/to/new-source-inventory
```

It verifies the original checksum, maps all 35 named functions, freezes the
15 original/paused source files, and preserves narrative-bearing original
source lines and the complete original/paused source snapshots in local paired
reports. That retains every authored string and HTML narrative, not only
selected paraphrases. Anonymous callbacks are described here;
the lexical function inventory is not a substitute for a semantic call graph.

## 2. Code-by-code original function ledger

| Original function / line | Mechanism and data | Framework transfer |
|---|---|---|
| `setMessage` / 53 | Message text and expiry | Event-grounded notification, not unsupported assertion |
| `tone` / 54 | Oscillator/envelope selection and mute guard | Feedback adapter only; no audio port needed for analytical correctness |
| `title` / 55 | Title state, overlay, character/syndicate premise, deploy callback | Explicit intake surface and role declaration |
| `briefing` / 56 | Mission objective, authored briefing and breach callback | Case question and preconditions before execution |
| `parseMap` / 57 | ASCII rows to cells; spawn entities/items; record doors | Contract-validated source/configuration loader |
| `loadLevel` / 58 | Player defaults, carried resources, world reset, play state | Isolated run initialization; deliberate carryover only |
| `spawnEnemy` / 59 | Type, health, cooldown, phase, alive/seen flags | Typed records and documented hypotheses, not hostile-person labels |
| `solid` / 60 | Bounds/cell/door collision predicate | Closed contracts and gated boundaries |
| `moveEntity` / 61 | Radius and independent axis movement | Validate operation before applying state change |
| `hasLOS` / 62 | Sampled wall visibility along segment | Restrict decisions to observed lineage; not a proof of independence |
| `use` / 63 | Door/key requirements or exit conditions | Provenance AND Harm Gate; no UI bypass |
| `finishLevel` / 64 | Archive completion and next-mission briefing | Stage completion with explicit acceptance criteria |
| `victory` / 65 | Time, kills, hit fraction, intel and rank | Report actual populations; rank is not analytical confidence |
| `die` / 66 | Dead state and restart callback | Explicit failure and new run, not silent success fallback |
| `fire` / 67 | Ammo/cooldown, spread, nearest visible hit, damage | Bounded proposals and execution budget; fictional combat only |
| `killEnemy` / 68 | Alive/death flags, score, particles, drops, boss condition | Terminal task events and receipts, not source truth by repetition |
| `damage` / 69 | Armor absorption, health, feedback and death | Risk/review signals, not treating health as evidence weight |
| `cycleWeapon` / 70 | Active strategy slot and message | Explicit allowed operation/strategy choice |
| `update` / 71 | Timers, inputs, movement, pickups, enemy logic, projectiles, particles | Ordered bounded event queue with validated commands |
| `enemyShoot` / 77 | Different fictional projectile patterns and boss spawning | Stress-case variants, never active real-world deployment |
| `wallColor` / 78 | Material/side/distance shading and procedural stripes | Presentation policy separate from authority |
| `render` / 79 | Raycast walls, sprites, weapon, HUD, damage overlay | Read-only projection of authoritative records |
| `spriteScreen` / 82 | Camera-relative angle, visibility and projected position | Render observations with explicit scope |
| `renderSprites` / 83 | Far-to-near sorting, approximate wall occlusion, item/entity effects | Prioritized display must not discard audit records |
| `drawEnemy` / 84 | Procedural type palette, body shapes, pain/death effects | UI templates; no 3D enemy port to analyst engine |
| `drawPickup` / 85 | Health/armor/ammo/intel/key shapes | Distinct evidence/resource types, not interchangeable scores |
| `drawWeapon` / 86 | Active sprite, bob/kick/muzzle flash | Explicit active tool indicator; no operational weapon system |
| `drawHUD` / 87 | Resources, intel, keys, message and boss bar | Gates, root count, command population and correction receipts |
| `drawMap` / 88 | Overhead grid/player direction | Dependency/coverage view; source roots remain operator-declared |
| `loop` / 89 | Wall-time accumulator, 1/60 updates, rendering | Separate logical sequence from execution timestamps |
| `initAudio` / 90 | User-gesture AudioContext creation | Optional subsystem initialization must not fake readiness |
| `pause` / 92 | Play/pause overlay switch | Explicit pause/resume state transitions |
| `joyMove` / 94 | Touch displacement clamped to normalized radius | Normalize and validate input at adapter boundary |
| `joyEnd` / 94 | Release/cancel resets movement | End input cleanly; no sticky commands |
| `bindHold` / 96 | Pointer capture, pressed state, down/up/cancel handlers | Adapter lifecycle and visible busy/error status |

The ledger names all functions without assuming each should become a Python
engine component. Some are game-only presentation features; applying them means
retaining their design constraints and boundaries, not manufacturing unused
audio/3D code in the analyst package.

## 3. World/content construction

The missions are authored ASCII grids. `P` is spawn; `.` is floor; `X` is exit;
`#`, `M`, `S` and other wall symbols represent different materials.
`D`, `R`, `B` are normal/red/blue doors. Enemy markers `m`, `d`, `t`, `F`
become entities. Item markers `h`, `a`, `b`, `s`, `i`, `r`, `q` become health,
armor, bullets, shells, intel, red and blue keys.

`parseMap` replaces spawned markers with floor and stores entities separately.
`loadLevel` reconstructs world state, resets mission-local keys and preserves
selected resource values for the second mission. Named missions:

- **The Archive:** recover red clearance and reach the extraction switch.
- **Fabrication Plant:** recover blue clearance, reach the production floor,
  defeat the fictional boss and reach the final exit.

Reconstruction process: define a symbol grammar, validate rows and symbols,
spawn once, check connectivity and legitimate key/exit reachability, then
evaluate resource placement. Do not infer that the original did all those
checks: it sets width from the first row and the authored rows have differing
lengths. Padding/bounds behavior deserves a dedicated future game regression;
it is not silently "fixed" during this paused architecture task.

Framework implementation uses a JSON schema, safe consumer names, unique source
IDs, explicit shared roots, declared command budget and fresh run directory.
The workflow fixture has a primary source, its copy and an independent root.
No duplicated source is counted as new independent support.

## 4. Simulation and physics process

Movement uses direction/strafe components, normalized diagonal speed and
axis-by-axis collision with a radius. Doors are impassable until open.
`hasLOS` samples roughly eight points per unit distance; it is **not** the same
DDA procedure as wall rendering despite the README's stronger description.
Enemy behavior is distance/LOS-driven inside `update`, not an explicit
idle/patrol/chase/attack state-machine implementation as the README suggests.

The fixed-step accumulator calls `update(1/60)`, clamps wall delta to .05 and
renders separately. Update order affects results: player timers and movement,
input fire, doors, pickups, enemies, projectiles, particles. Health/ammo/key
changes are authoritative, while bob/shake/flash are presentation.

Framework transfer: preserve command order, stable equal-tick tie handling,
explicit budgets, pre-operation integrity checks and failure state. Logical
ticks are not a claim of real time. Random UUIDs and wall-clock event timestamps
remain in audit evidence but are excluded from the deterministic replay
projection. No seed is advertised when the workflow uses no random choices.

## 5. Combat/resources and measurement

The original weapon table defines Sidearm, Breacher and Redactor with distinct
ammo, cost, delay, damage, pellets and spread. `fire` rejects empty/cooling
shots, chooses the nearest visible candidate inside its angular size and
applies stochastic fictional damage. Enemy types differ in health, movement,
projectile count and speed; the boss uses radial projectiles and can spawn moles.
Items replenish bounded health/armor and ammo, add intel or unlock doors.

Those are useful **resource/control patterns**, not analyst evidence formulas.
Adapt ammo/cooldown to bounded command opportunities, not to missing factual
evidence. Never equate enemy kills, hit accuracy, intel points, speed or victory
with corroboration, ethical clearance, calibration or real efficacy.

The paused experiment showed both scripted policies win 5/5; both hit 100%
with exact LOS observations. Planned mean time was 39.653 seconds versus
41.100; mean score 6,390 versus 6,100. Seed 99 was slower with planning.
This ceiling effect motivated source-quality and correction mechanics.

## 6. Rendering/assets/audio/UI reconstruction

Walls use a DDA grid traversal: initialize reciprocal ray-axis distances,
advance whichever boundary is nearer, stop at a wall and use side-adjusted
distance times the cosine of camera angle to reduce fisheye distortion.
Approximate wall height is `H / distance`. Columns write the depth buffer.
Sprites use camera-relative angles, distance scaling, far-to-near drawing and
a visible-column test against that buffer. This is an approximation, not a
full per-pixel sprite occlusion engine.

Background gradients, material shading, scanlines, vignette, procedural sprite
rectangles, weapon bob and muzzle flash create the retro presentation without
external texture files. HTML/CSS uses a 16:9 shell, portrait overrides, coarse
pointer controls, color variables, semantic buttons and overlay cards.

WebAudio uses oscillator tones and envelope/gain shapes. It initializes from a
user gesture and respects mute. The original catches audio initialization
errors without reporting them; that is a source limitation, **not** a pattern
to copy into core analyst failures. Optional feedback failure must not be
confused with successful analysis.

Framework adaptation: human-readable and machine-readable outputs are
projections of the same payload; `write_reports` verifies synchronization.
Narrative rendering is pure: no gate mutation, source changes or PRNG consumption.
There is no new Python audio or raycasting renderer claimed here.

## 7. Input and interface boundaries

Original keyboard callbacks map WASD/arrows, space/control, E, digits, M and
Escape; mouse down fires; touch uses a left joystick, right drag, and held action
buttons. The source has no desktop mousemove/pointer-lock look handler and no
P-key pause branch, despite README controls advertising them. No historical
implementation success is inferred from those descriptions.

Callbacks only propose operations. The authoritative state decides whether
they are legal. Framework modes are:

- **Operator:** explicit JSON command list with pause/resume support.
- **Agent:** inspect ordered declared sources, propose gated use, then correction
  and completion. This is a transparent scripted agent, not an unclaimed LLM.
- **Verifier:** read persisted reports/consumer receipts without rerunning decisions.

The paused browser uses `textContent`, explicit connection failures, busy
buttons and same-origin requests. The loopback bridge caps request bodies and
sessions and serves named assets only. Static hosting cannot execute Python.
Do not bypass unavailable APIs by substituting success-shaped browser results.

## 8. Narratives: retain all families, do not confuse them with evidence

The story stars **Jack Slade**, an operative confronting **The Fabricators**.
The fictional boss is **The Fabricator**. Mole, Disinfo Drone and Troll are
authored adversary types. The Archive and Fabrication Plant establish the
mission progression. Red/blue clearance, intel caches and three named weapons
tie story beats to mechanisms. Title, briefing, deployment, first completion,
victory rank, death/restart and pause form the presentation arc.

Narrative families include authored taunts triggered on first sighting,
low-health and first-kill lines, resource/door/key notifications, mission
objectives, boss defeat, intel pickup and victory/death feedback. They are
local templates and strings, **not generated by a live LLM**. "Chatter Engine"
branding does not demonstrate independent source analysis.

The paused sequel adds a radio rumor that an east passage is clear; Archive
and Echo share lineage; Survey is independent; a map change withdraws the
briefing; goals/search/briefing/memory must receive corrections.
These remain **synthetic, fictional fixtures**. Their story is reusable as
instructional design, not real safety, hiring, political or personal evidence.

Transfer narrative at three separate levels:

1. **Fiction:** keep character/world/flavor names in the game context.
2. **Method explanation:** describe provenance, access, correction and dependency
   concepts, with actual source/status caveats.
3. **Operational output:** generate only sentences citing a producing logical
   event, with measured population and outcome.

The workflow's narrative distinguishes blocked uses, permitted local decisions,
observed declared roots and verified corrections. It never calls the operator
a fictional combat hero or claims victory proves SI capability.

## 9. Reuse the paused build rather than discard it

| Paused component | Reusable process | Current evidence boundary |
|---|---|---|
| `HailSimulation` | Opt-in reset/observe/step/draw interface, isolated random stream | Exact map/LOS observations, not pixel perception |
| `simulation/policy.js` | BFS routing, LOS combat proposal, reason string | Transparent JavaScript tactics, not autonomous research |
| `simulation/run.cjs` | Headless execution of actual original script, paired seeds, trace hashes | Stubbed DOM means rendering/audio need browser tests |
| `simulation/worker.cjs` | JSON-lines observation/proposal/action protocol | Paused addition must be tested before claims of Python play |
| `vessell/game_bridge.py` | Local gate execution, source-copy mechanics, consumer repair | Fictional engine designated trusted, not real-source authenticity |
| `lab.html` / `lab.js` / `lab.css` | Autonomous playback, explicit backend status, tactical explanation | Browser view is not an independent evaluator |
| `recall.html` / `recall.js` | Human/autoplay correction mission and Python coach | Prototype information puzzle, not a completed FPS campaign |
| `simulation/test.cjs` | Reset, deterministic replay, invalid input and mission tests | Engine tests do not certify perception/learning outcomes |
| `simulation/FINDINGS.md` / results | Convert measured limitations into feature requirements | No causal/field efficacy or significance from five seeds |
| CI / README | Reproducible commands, static/local hosting distinction | Unpublished working-tree content stays labeled paused |

## 10. Apply the architecture to the analyst runtime

Implemented layer: [vessell/workflow.py](vessell/workflow.py), contract
[schemas/workflow.schema.json](schemas/workflow.schema.json), fixture
[case_studies/game_patterns/workflow.json](case_studies/game_patterns/workflow.json).
It reuses existing pipeline, provenance, Harm Gate, correction adapter and
paired-report writers instead of duplicating their semantics.

`validated case -> intake -> REVIEW -> observations -> gated local use -> READY`

`REVIEW or READY -> PAUSED -> resume -> prior state`

`REVIEW or READY -> correction/write/read-back -> CORRECTED -> finish -> COMPLETE`

Commands are bounded and ordered. Duplicate sightings, unknown sources,
invalid transitions, schema errors, drift, output reuse and missing completion
are explicit failures. Permission requires both corroboration and complete,
proportionate Harm Gate input. A permitted "use" records a **local decision**;
it launches no external action. Original intake/final claim, correction,
lifecycle events and per-file receipts persist in the report.

Run twice and compare deterministic replay:

```sh
python -m vessell.workflow --spec case_studies/game_patterns/workflow.json \
  --output-dir /absolute/path/to/run-a
python -m vessell.workflow --spec case_studies/game_patterns/workflow.json \
  --output-dir /absolute/path/to/run-b --compare-to /absolute/path/to/run-a
python -m vessell.workflow --output-dir /absolute/path/to/run-b --verify-only
```

## 11. Process-by-process reconstruction recipe

1. Pin source/license and separate original, working-tree and inferred evidence.
2. Specify purpose, audience, fictional world, analyst task and exclusions.
3. Declare data contracts and symbol/operation grammar.
4. Build loader and state ownership; reject malformed inputs.
5. Implement one authoritative state/update path before presentation.
6. Implement gates/access boundaries and bounded resources.
7. Implement observations and agents as proposals, not unchecked authority.
8. Separate render/narrative/audio adapters from mutation.
9. Add human/touch/agent/API adapters without duplicating logic.
10. Record events, populations, receipts and source identities.
11. Add deterministic replay and failure/negative controls.
12. Evaluate original behavior against a specified comparator.
13. Design new mechanics from measured gaps; label unimplemented ideas.
14. Run source, installed-package and browser checks relevant to each surface.
15. Publish only verified scope; preserve original narratives and evidence
    boundaries, retain attribution and do not upload private data.

This order can build the observed system; it does not claim to be the author's
actual chronological workflow. The analyst package is incrementally rebuilt
through this layer. Existing compatibility APIs, scientific evaluators,
authorized remediation and historical doctrine remain intact rather than
being gratuitously deleted and recreated.

## 12. Acceptance and remaining gaps

Local verification for this adaptation: 373 regression tests passed; focused
lint and strict type checks passed. Two separate source processes and two
non-editable installed-wheel processes produced the same deterministic replay
hash from outside the checkout. Each fixture executed nine commands, blocked
three unsupported uses, permitted one corroborated local decision, and
corrected/read back four consumers. Standalone verification of the saved wheel
run passed without rerunning its decisions.

The pinned source audit confirmed all 35 original named functions and 15
original/paused files. One reused worker validation (seed 42) passed 2,223
Python gate decisions, reached fictional victory and exactly matched the
scripted planner trajectory. That is a component test, not completion or
publication of the paused game. Full-source/narrative snapshots and evaluation
outputs are retained locally, not uploaded automatically.

Required checks: all named-function coverage; source hash identity; contract
rejection; shared-root discount; independent-root progression; incomplete Harm
Gate remains blocked; stable event order/replay; illegal pause/resume and
completion rejected; narrative tied to events; drift rejected; real file repair
and read-back; original retained; JSON/Markdown synchronized; no mutations on
verification; no report success after failed execution.

Do not claim full framework formal verification, field efficacy or complete
replacement of all subsystem architectures. Existing real-world connectors,
crash recovery, concurrent-writer handling, authenticated source provenance,
prospective labels and independent evaluators remain distinct needs.
Game art/audio mechanics are documented rather than needlessly runtime-ported.
The game build/server stays paused until the operator resumes it.
