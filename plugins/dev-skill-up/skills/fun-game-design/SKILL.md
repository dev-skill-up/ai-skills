---
name: fun-game-design
description: Design, build, tune, or evaluate a game so that it is actually fun, and verify the fun by measurement instead of taste. Use whenever the work is a game — building or extending one, adding or tuning a mechanic, balancing, pacing, level or screen design, onboarding, progression, economy, reward moments — or when someone says "make this fun", "add juice", "the game feel is off", "this animation feels weak/flat/unsatisfying", "playtest this", "balance this", "is this screen boring", "why isn't this fun", or wants a game to feel cozy. Covers per-component emotional targets, the failure/scarcity/intensity dials, acquiring animation and pacing magnitudes by measuring a shipped reference, bot playtests with traces and signed metrics, and blind-judge protocols. Do not use for non-game UI animation, app polish, or general frontend motion work.
---

# Fun Game Design

You know the principles of fun and you will not apply them unless forced, because in implement-the-feature mode appeal is never the objective, because the code you sample from is the median code in the wild, and because magnitudes without a comparator default to timid. This skill forces four things in order: commit, per component, to emotional targets and to three dials — failure, scarcity, intensity — and write the boundary between components that differ; sign every metric from those dials; acquire every magnitude by measuring a shipped reference in the genre rather than typing a plausible number; and perceive your own output against that reference with deterministic checks, negative fixtures, and blind judges whose disagreements fix the checks rather than the judges. Legibility — acknowledge input in ~100 ms, never linear, overshoot and settle, follow through, acknowledge decisions, no dead ends, something new regularly — is common to every genre. Everything else has a sign, and the sign comes from the dials.

## The objective flip

The deliverable is not "the feature works" — it is **worth watching and worth playing**, with correctness as a constraint on that, not as the goal. A passing test suite, a compiling tween, and a state machine that reaches the right state are the floor; if you stop there you will ship the flat version and be able to recite, afterward, every principle you failed to apply.

## Scope and degradation

- **No vision capability?** The reference table (step 5) and the deterministic checks (step 7) still run. Say plainly, in the PR or the summary: *a feel change inspected only in source is not checked.*
- **No repeatable loop** (pure narrative game, walking sim)? Skip bot playtesting entirely and say so — do not force bots onto it. Steps 1–8 minus the bots still apply, and `references/measurement.md` §5 covers what replaces them.
- **Tiny change to an existing game?** You still do step 4 (sign the metrics you will move) and step 5 (measure before typing a number). You may inherit steps 1–3 from an existing `design-decisions.md` — read it, don't re-derive it.

## The procedure

Do all of this, in order, **before writing gameplay or animation code**, and write the results into `design-decisions.md` (copy `assets/design-decisions.template.md`). Nothing here is optional and every step exists because you will skip it otherwise.

**1. Name the emotional targets, per component.** Decompose the game — typically core loop, meta/progression, narrative delivery, feel/juice, onboarding; adjust per game. Give each 2–3 targets from the pluralist vocabulary: **hard fun** (fiero, triumph over adversity), **easy fun** (curiosity, discovery), **serious fun** (relaxation, rhythm, altered state), **people fun** (amusement, social), plus **mastery** (exercising skill you already have). One sentence per component: *"the board is easy fun and serious fun with light hard fun available."* A component with no named target cannot be evaluated, so it will be evaluated by vibes.

**2. Set three dials, per component.** These are the axes whose sign flips between action fun and cozy fun.

| Dial | "Tension" end | "Safe" end |
|---|---|---|
| **Failure** | Failure is the payload: frequent, internal, recoverable; fiero on recovery | Failure is a hazard: rare, never surprising, always recoverable; mistakes cost little |
| **Scarcity** | Resources / space / time are the tension; triage is the skill | Abundance; nothing runs out; pressure exists only where the player put it |
| **Intensity** | Rising curve; shake, flash, bass, hit-stop are legal | Capped; nothing sudden, loud or bright. Exaggeration is still legal — it is not intensity |

**Cozy** is the named preset with all three at the safe end. Other presets (arcade, puzzle, tactical, roguelike) are fine but must be **expressed in the three dials**, not named and left vague. Time pressure is a form of scarcity. Extrinsic reward chains push toward the tension end whether you intend it or not — name them when you add them.

**3. If components differ, write the boundary rule.** Mixed designs — tense loop with cozy meta, safe hub with dangerous expedition — are where most designs fail. The only coexistence model that works is **consent + pacing control**: pressure lives in a named component, the player enters that component by choice, and **nothing in it fires while the player is elsewhere** — no timers ticking in the hub, no notifications, no forced events, no expiring rewards. Write one sentence per boundary. If you cannot write it, the design is incoherent; change the design now, not after it is built.

**4. Sign every metric from the dials.** Copy the sign tables below into `design-decisions.md` and fill the column your dials select, producing this project's metric table: for each metric, its direction — floor, ceiling, both, or neutral — *given this component's dials*. A metric without a sign is not a metric, it is a number you will rationalize later.

**5. Acquire magnitudes by measuring a reference.** Before writing **any** duration, distance, angle, scale, count, or cost, run the reference-measurement procedure in `references/measurement.md` §1: pick one shipped, commercially proven game in the target genre, capture its key moments, step them frame by frame, and tabulate the phases, durations, travel, rotation, scale, impact reactions, completion sequences, and the ratio of biggest moment to routine moment. Write that table into `design-decisions.md` as the project's **budget**. It is a reference for structure and timing only — never for art, names, copy, or assets, and nothing is copied. **If you are about to type a duration, angle, or scale and you have not measured a reference, stop and measure.**

**6. Write the feel spec with observable predictions.** For every animation family and every reward moment: trigger, principles used, keyframe table, duration budget (from step 5), interrupt behavior, reduced-motion variant, and — this is the load-bearing line — **what a reader should see on a contact sheet**: *"frame 2: source squashed to 0.85; frame 5: result at 1.3×; frame 8: settled at 1.0 with residual wobble."* That prediction is what the perceive loop tests. A spec without it is unfalsifiable.

**7. Build with the perceive loop on.** Every change to feel or to the loop goes through `references/feel.md` §3 (render → sample → deterministic checks with negative fixtures → compare to the reference table → blind vision judge → drift check) and, where a repeatable loop exists, `references/measurement.md` §3 (bots → traces → signed metrics → verdict → judged traces). **Never ship a feel change that was only inspected in source.**

**8. Use your permission to break simplifications for appeal.** Wherever a magnitude is being limited to keep an approximation valid, **appeal outranks the approximation — replace the approximation.** The cap is not a constraint you inherited; it is a decision you are now overruling. Common shapes, all of which you would otherwise preserve:
- a small-angle approximation capping a rotation → solve the real geometry;
- a linear-in-units fill that assumes a straight-sided container → solve area-correct;
- a layout that assumes nothing overlaps → allow overlap, add z-ordering;
- a rebuild-and-replace-children render path → reuse nodes so they can be tweened;
- `crispEdges` / integer snapping / pixel quantization on anything animated → remove it;
- a straight lerp kept because the curve math is annoying → write the curve.

Record each one you broke, and each one you kept, with a reason.

## Named bad defaults

These apply at every dial setting. Each is stated as **principle / the default you will write instead / the check**. The middle line is the important one: it names what you are about to type.

### Legibility constants — the only numbers this skill carries

- **Acknowledge every input within ~100 ms** (~6 frames at 60 fps); the acknowledgment may be tiny. *Default:* the input updates state and the render catches up whenever the next state change happens. *Check:* first differing frame within 100 ms **of the dispatched input timestamp** — never of the animation's own start callback, which makes the check tautological.
- **Never linear.** Everything eases. Pops and rewards overshoot and settle (back-out); motion toward a target eases out; UI eases in-out. *Default:* one `easeInOut` for everything, or a raw lerp. *Check:* from the bounding-box track, velocity at start and end near zero — a linear tween has constant velocity.
- **Overshoot then settle; follow through.** After the primary motion stops, something small keeps moving for a few frames. This is most of the difference between "done" and "satisfying". *Default:* motion stops dead at t = 1. *Check:* frames after the declared end differ from the final frame, then converge to it.
- **Arcs, not lines.** Anything flying to a target travels on a curve. *Default:* `x += dx * t; y += dy * t`. *Check:* path curvature from the track is nonzero.
- **Anticipation on the big moments only.** A short wind-up — small counter-motion, a dim, a held beat — before a reward or reveal. *Default:* none anywhere, or (once told) on everything, which makes the loop feel sluggish.
- **One focus at a time (staging).** When the reward plays, everything else holds or dims. *Default:* the reward plays while the board keeps updating behind it and the eye lands nowhere.
- **Escalate legibly.** Bigger outcomes get bigger feedback, monotonic in the outcome's magnitude, and audible — the player should be able to *hear* which tier they hit. *Default:* every outcome plays the same effect. *Check:* measured pop scale / particle count / pitch is monotonic across tiers.
- **Never block input; any tap skips the animation, not the state change.** *Default:* input disabled until the tween finishes. *Check:* dispatch a second action mid-animation — both actions applied in state, and the frame at +1 shows the first animation's end state.
- **Reduced motion is a real mode.** All tweens become ≤ ~120 ms fades; no shake, no particles; everything the motion *conveyed* (selection, progress, source→target) still conveyed statically. *Check:* no element displaces > 2 px between frames, no particles, all changes complete within the fade budget.
- **Sound is half of it.** Every animation family has a sound; sounds within a family are variations on one motif; the biggest moment has its own cue. *Default:* no sound, or one click for everything.

### Fairness

- **No dead ends, ever.** A state whose legal action set contains no progress-making move is external failure and is a defect in every genre, at every dial setting. *Check:* bots flag any such state; zero tolerance.
- **Failure is attributable.** When the player fails, the visible state must have made it foreseeable. *Default:* the cost is computed from hidden state. *Check:* for each annotated bot mistake, record *was this foreseeable from visible state* — expensive **and** unforeseeable is the punishing case.
- **Recovery is proportionate.** The cost to return to prior progress after a slip is bounded, and the bound comes from the failure dial.

### Decisions

- **Acknowledge every decision.** A choice with no visible downstream consequence is not a choice. *Default:* a cosmetic option set once and never referenced again. *Check:* for each player-facing choice, name the later moment that reflects it; a choice with no named moment is cut or wired up.
- **A screen has decisions only when the top moves are close but different.** One obvious move is no decision; a choice that doesn't matter is no decision either. *Check:* the decision index in `references/measurement.md` §3.

### Learning and novelty

- **Something new, regularly.** Track first-seen items, first-reached tiers, newly unlocked systems as first-class events and measure the **novelty interval** alongside the reward interval. *Default:* the events list contains only rewards, so a loop that pays constantly and teaches nothing scores well.
- **Introduce gently, use hard.** A new element arrives with a task needing only its simplest form; later tasks demand its depth.
- **Teach by construction, not by text.** The first screen is a good screen a veteran would enjoy; it teaches because of how it is built. *Check:* if a naive bot or a naive judge can't find the core mechanic on the first screen, fix the screen — not the tutorial copy.

### Anticipation and reveal

- **Legible starting state.** The player can predict the finished state from the unfinished one — the mess reads as fixable, the boss has a health bar.
- **Every step visibly changes the frame; the biggest change lands last; lighting lands late** (it retroactively improves everything before it); **the signature piece is the reveal.**
- **Measure anticipation** as the fraction of time with a visible pending payoff. Decide deliberately how much **near-miss** you want rather than accruing it by accident — its evidence base is gambling, and its behavior in skill-based, non-monetized play is unstudied.

### Narrative delivery

- **Story arrives at rest points, never mid-loop.** Short beats, tap-to-advance, back to play within seconds. *Default:* dialogue triggers on the action it is about, interrupting the action it is about.
- **Skip-safe.** Every skippable beat is recoverable in a journal, and the story must make sense read that way. *Check:* a fresh reader given only the journal reconstructs the plot.
- **The loop is fun with the arcs off.** *Check:* bots play with narrative disabled and no metric depends on it.

## Sign tables

Copy these into `design-decisions.md` and keep only the column each component's dials select. Metric definitions are in `references/measurement.md` §3.

### Loop metrics by dial

| Metric | Failure: tension | Failure: safe | Scarcity: tension | Scarcity: safe | Intensity: rising | Intensity: capped |
|---|---|---|---|---|---|---|
| Stall (longest run with no progress) | ceiling, tight | ceiling, loose; neutral if visibly building | ceiling | neutral | — | — |
| Dead end | zero | zero | zero | zero | — | — |
| Recovery cost per mistake | high allowed **if foreseeable** | low, always | — | — | — | — |
| Board-full / resource-out events | expected; measure exit time | rare; each one is a finding | expected | defect | — | — |
| Skill gradient | measured in **speed** (the optimizer finishes faster) | measured in **size** (the optimizer gets richer outcomes; completion is universal) | — | — | — | — |
| Completion by the unskilled persona | may be < 100 % | ≥ ~95 % without skipping | — | — | — | — |
| Escalation (big events per 100 actions across the screen) | floor: must rise | floor: must rise | — | — | floor | **floor and ceiling** |
| Variance across seeds | moderate allowed | low — chance must not decide | — | — | — | — |
| Reward interval | tight cadence | steady drip; spikes not required | — | — | — | — |
| Novelty interval | floor | floor | — | — | — | — |
| Voluntary quit / skip rate | ceiling | ceiling (**primary outcome**) | ceiling | ceiling | ceiling | ceiling |

### Feel properties by intensity dial

| Property | Rising | Capped |
|---|---|---|
| Screen shake, hit-stop, flash | legal, scaled to magnitude | ≤ 2–4 px on the single biggest moment, or none |
| Exaggeration (squash, overshoot, tilt past "realistic") | legal | **legal** — exaggeration is not intensity |
| Sound attack | sharp allowed | soft attacks, no harsh highs |
| Escalation | can grow without bound | grows to a ceiling and stops |
| Particles | count scales with magnitude | few, slow, drifting |
| Camera | may move | fixed; the state delta is the reward |

### Pressure sources by scarcity dial — the consent test

List every pressure source in the design (timers, limited resources, filling space, expiring goals, cooldowns, streaks, energy). For each, record: **who controls when it applies** (player / game), **whether the player can opt out without penalty**, and **whether it can reach into another component**.

- At the **safe** end, every source must be player-controlled or trivially small — a cooldown of seconds that gives an animation room, never one that ends a session.
- At the **tension** end, game-controlled sources are legal but must still be foreseeable from visible state.
- A source that fires while the player is in another component violates the boundary rule from step 3, at either end.

## Retention is not the target

Retention is produced by compulsion as readily as by fun. The honest operationalization is: **fun is what a person gives time and attention to, unforced** — so in any design without a compulsion layer, **voluntary quit / skip rate is the primary outcome metric**, and retention benchmarks borrowed from compulsion-driven games do not apply. When asked to add a mechanic whose job is to bring players back on a schedule (daily timers, streaks, energy, expiring rewards, login bonuses), name it as a compulsion mechanic, give it the sign of the scarcity dial, and — if the component is at the safe end — decline it or reframe it as opt-in with no penalty for ignoring it. Say which you did and why.

## Where the depth is

- `references/theory.md` — the frameworks and when each applies: pluralist aesthetics, flow's full component set, Juul on failure, Meier on interesting decisions, Cook on loops vs. arcs, the coziness literature, the sign flip. Two-minute read; consult it when a design decision needs a frame.
- `references/feel.md` — the animation principles in default/check form, the perceive loop for feel, the negative-fixture catalog, the vision-judge rubric, sound, and reduced motion.
- `references/measurement.md` — reference measurement, the bot personas, trace format, the mistake catalog, the metric definitions and verdicts, scorer protections, judged traces, judge hygiene and calibration, and the human anchor.
- `assets/design-decisions.template.md` — the file you fill in during the procedure.
- `assets/trace-record.schema.json` — the JSON Schema for one bot trace record.
- `evals/` — the test cases this skill is graded against; read `evals/rubric.md` if you are changing the skill itself.
