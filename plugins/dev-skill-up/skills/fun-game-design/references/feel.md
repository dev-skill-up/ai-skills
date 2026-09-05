# Game feel: principles, the perceive loop, and the checks

This file covers everything between "the state changed" and "the player enjoyed watching the state change". It carries **no genre-specific magnitudes** — every duration, distance, angle and scale comes from the reference table you measured (`measurement.md` §1). It carries only the perceptual constants in SKILL.md, which belong to the human viewer rather than to any game.

## 1. The principles, in default/check form

SKILL.md lists the ten legibility constants. These are the rest, in the same form. The middle line is the point: it names the code you are about to write.

**Squash and stretch.** Mass deforms under acceleration and impact. *Default:* scale stays 1.0 the whole way, or one uniform scale pop with no volume conservation. *Check:* on the contact sheet, at least one frame shows non-uniform scale (x ≠ y) in the acceleration and impact phases.

**Anticipation.** A short counter-motion or hold precedes a big action. *Default:* the action starts at the instant the state changes, from rest, at full speed. *Check:* the first frames of a big-moment animation move *away* from the target (or hold and dim), then reverse.

**Staging.** One thing at a time draws the eye. *Default:* the reward tween plays while the board reflows behind it, three particles systems fire, and a counter ticks. *Check:* during the reward window, the number of simultaneously changing regions is ≤ what the spec declared; ask the vision judge "where does the eye go" and see if the answer matches intent.

**Follow-through and overlapping action.** Appendages, trailing elements, and secondary objects stop after the primary does, and different parts start at different times. *Default:* every property of every element shares one start time, one duration and one easing. *Check:* per-element start times differ by at least a frame; frames after the primary's end still show change.

**Secondary action.** Something that isn't the main motion reacts: the thing being acted upon flinches, dust puffs, a neighbor jiggles, a counter rolls. *Default:* the actor animates and the world is inert. *Check:* the reference table's "what reacts on impact" column has entries; your contact sheet has the same number of reacting elements or you wrote down why not.

**Timing.** Different weights get different durations; the same duration for everything reads as a UI, not a world. *Default:* one shared `DURATION` constant. *Check:* the durations in the spec differ across families in the same direction as the reference table's.

**Exaggeration.** Push past the physically plausible until it reads at the size it will actually be viewed at. *Default:* the physically plausible value, or the value that keeps a nearby approximation valid. *Check:* compare your measured travel/rotation/scale against the reference table; being systematically under it across every family is the timidity signature, and is a finding.

**Appeal.** The moment is worth watching on its own, muted, out of context. *Check:* the vision judge's "would a player notice this" question. This one is allowed to be subjective — that is why the pass exists.

**Completion is an event, not a state.** When a goal, a level, a set, or a chain finishes, something fires: a sequence, a distinct sound, a summary, a change of frame. *Default:* the goal's `complete` flag flips to true and the UI re-renders with a checkmark. *Check:* grep the code for the place where completion is detected and confirm an event is emitted there and consumed by the feel layer; on the contact sheet, the completion frames are visibly different from an ordinary update.

**Interrupt gracefully.** A new action during an animation resolves the old one instantly to its end state and starts the new one. *Default:* the two tweens fight over the same properties, or input is locked out. *Check:* the interrupt scenario below.

**Reduced motion conveys the same information.** See the constant in SKILL.md; the trap is deleting the animation and with it the meaning (which item merged into which, which cell was selected).

## 2. Sound

Sound is not a later task. It is roughly half of perceived impact and it is the cheapest escalation channel you have.

- Every animation family gets a sound; sounds in a family are variations of one motif (pitch, filter, layering), not unrelated samples.
- Pitch or layer count rises with tier so the player can **hear** which tier they hit without looking.
- The biggest moment in the game has its own cue that appears nowhere else.
- Under a capped intensity dial: soft attacks, no harsh highs, no sudden loudness — but still a full escalation ladder, built out of timbre and layering rather than volume and attack.
- Everything must survive being muted: a player with sound off should still read the tier from the visuals.

## 3. The perceive loop for feel

Record → sample → check deterministically → compare to the reference → judge → drift-check. Run it on every change to feel. **A feel change inspected only in source is not checked.**

### 3.1 Drive a deterministic scenario

Headless browser or equivalent, fixed viewport, fixed seed, **real speed** (not a fast-forwarded clock — you are measuring what a human eye would see). Drive it through a test hook that dispatches exact actions and reports state, not through synthetic UI clicks that add their own latency.

One scenario per animation family, plus two mandatory extras:

- an **interrupt** scenario: a second action dispatched ~80 ms into each animation;
- a **reduced-motion** scenario.

Log wall-clock timestamps of **each dispatched action** and of each animation's start and end. The dispatched-action timestamp is the one the onset check uses; using the animation's own start callback makes the check tautological and it will pass forever.

### 3.2 Record video

Verify frame timing on the first run — count frames in a known-duration clip. If the recorder's timing is unstable, fall back to a fixed-rate screencast. Unstable frame timing silently invalidates every duration measurement downstream.

### 3.3 Extract stills two ways

- **Event-aligned:** for each logged animation — at its start, at fixed offsets through its budget, and ~200 ms after its declared end (this is what catches missing settle).
- **Change-driven:** every frame where something visibly changed (frame-difference threshold). This catches motion the spec never declared, which is where the accidental jank lives.

Assemble labeled **contact sheets** with timestamps burned in, plus a slowed clip for ambiguous cases.

### 3.4 Deterministic checks — each with a negative fixture

**Every check has a fixture; every fixture has a check. A check that passes its own negative fixture is a failing test** and must be fixed before its result means anything. Build the fixtures as deliberately broken variants of the real animation, behind a flag.

| Check | Passes when | Negative fixture it must fail on |
|---|---|---|
| Onset | first differing frame ≤ 100 ms after the **dispatched input** timestamp | onset delayed past the constant |
| Duration | within the reference budget ± one frame | duration doubled / halved |
| Settle | final frame equals a still rendered directly from final state | element left at 1.02× / offset by a few px |
| Continuity | the moving element is present in every intermediate frame | element hidden for the middle of the tween |
| Easing | endpoint velocities near zero on the bounding-box track | linear tween |
| Arc | path curvature nonzero for flights | straight-line lerp |
| Follow-through | frames after declared end differ, then converge | motion stops dead at t = 1 |
| Escalation | measured magnitude monotonic across tiers | all tiers play the same effect |
| Interrupt | both actions applied in state; frame at +1 shows the first animation's end state | input blocked until tween completes |
| Reduced motion | ≤ 2 px displacement per frame, no particles, within fade budget | full animation leaks through the flag |
| Blocked input | total blocked time is zero | a modal or lock during the reward |

### 3.5 Compare to the reference table

Line up your measured output against `measurement.md` §1's table: durations, travel, rotation, scale, **number of discrete things that happen** in the moment, what reacts on impact, what the completion sequence contains, and the ratio of biggest moment to routine moment. **List every deviation. Each one is either justified in writing or fixed.** Being uniformly smaller and shorter than the reference across all families is not a series of small deviations — it is the timidity failure and it gets fixed, not justified.

### 3.6 Vision judgment

Give a vision-capable model: the contact sheet, the animation's spec **including its "what the reader should see" line**, and the principle checklist. It scores 1–5 with **timestamped** reasons and answers:

- Does the motion read as squash / anticipation / overshoot / settle where the spec says it should?
- Is the eye led to the reward?
- Does any frame pair look linear or mechanical?
- Is there follow-through?
- **Would a player notice this?** (the appeal question — subjective on purpose)
- Does anything obscure the play area, or leave residue behind?
- Under a capped intensity dial: does anything read as sudden, bright, or loud?

The judge gets no access to the deterministic check results, and no access to the conversation in which the animation was written.

### 3.7 Drift check

- Deterministic checks pass but the judge scores ≤ 2 → **the check is wrong.** Find what the frames show that the metric didn't encode, add or adjust the check, re-run, log it.
- The judge scores ≥ 4 where a check failed → same conclusion, opposite direction: the check is measuring something that doesn't matter, or is measuring it wrong.
- A **second, independent judge** (fresh context; no access to the first judge's scores or to the check results) is the outer anchor. Where both judges agree against a check, the check changes. Where the judges disagree *with each other* in a pattern, the **rubric** is underspecified — clarify it and log the clarification.
- **Never tune the judge prompt to agree with the code.** That is the one move that destroys the whole loop, and it is the move you will reach for first, because it is the fastest way to a green run.

## 4. Where the timidity shows up in code

When you audit an existing "flat" animation, these are the shapes to grep for. Each one is a magnitude decision that was made to protect something other than appeal:

- a single shared duration constant used by every family;
- `easeInOut` (or a raw lerp) as the only easing in the file;
- a rotation, offset or scale clamped just below where a nearby approximation breaks, usually with a comment explaining the clamp;
- a fill or gauge computed linearly in units when the container's geometry is not linear;
- `crispEdges`, integer rounding, or pixel snapping applied to animated elements;
- render paths that rebuild and replace child nodes on each update, making tweening impossible;
- a completion condition that sets a flag with no event emitted;
- an input handler that sets a `busy` flag for the tween's duration;
- exactly one animated property per element.

Every one of these is covered by SKILL.md step 8: **appeal outranks the approximation.** Replace the approximation and record it.
