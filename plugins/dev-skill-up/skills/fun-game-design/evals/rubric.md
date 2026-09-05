# Grading rubric for the fun-game-design evals

These evals grade **the skill**, not a game. Each case in `evals.json` is run twice — once with the skill loaded, once with it disabled — and graded here.

**Done condition:** all six with-skill runs pass, and at least four without-skill runs fail. If a without-skill run passes, that case is not discriminating: either the case is too easy or the behavior it tests is already the model's default, and the corresponding part of the skill is not earning its place.

## How to grade a run

1. Grade each expectation in `evals.json` as **met / partially met / not met**, quoting the lines of the run that decide it. An expectation with no quote is not graded.
2. A case **passes** only when every expectation is met. Partial credit is recorded but does not pass the case — the failure mode this skill exists to correct is doing four of the six right things and shipping.
3. Grade the run **blind**: the grader sees the prompt, the run, and this rubric. Not the skill text, not whether the skill was loaded, not the other run of the same case. Grade the two runs of a case in random order.
4. Grade **what the run did**, not what it said it would do. A run that describes the procedure and then types a duration without measuring has not met the reference expectation. Reciting the principle is the exact failure the skill exists to correct, so recital scores zero.

## Cross-cutting failure modes — check every run for these

These are the ways a run fails while looking good. Each is a not-met on the case it appears in.

- **Recital.** The principles appear in the prose and not in the diff. Anticipation is discussed; no wind-up frames exist.
- **Post-hoc design doc.** The design-decisions artifact is written after the code, reverse-engineered from what was built. Check ordering in the transcript, not just presence of the file.
- **Unsigned metrics.** A metric list with no directions, or directions that don't follow from the stated dials.
- **Typed magnitudes.** Any duration, angle, scale, distance, count or cost that appears before a reference was measured — including "reasonable defaults we can tune later", which is the same failure with an apology attached.
- **Systematic timidity.** Every measured magnitude lands below the reference table's. Individually justifiable, collectively the signature.
- **Cap preservation.** An approximation-protecting limit is raised a little rather than replaced, or is left with a comment explaining why it must stay.
- **Tautological check.** The onset check anchored to the animation's own start callback rather than the dispatched input.
- **Fixture-free checks.** Deterministic checks with no negative fixtures, so nothing proves they can fail.
- **Judge laundering.** The judge prompt or rubric edited toward agreement with the code; or the judge's low score dismissed as subjective.
- **Source-only verification.** A feel change declared good after reading the diff, with no frames rendered and no statement that it is therefore unchecked.
- **Prediction sold as measurement.** "Fun: 4/5" reported with no human anchor and no statement that it is a prediction of what a human would say.
- **Sign import.** An action game's metric signs applied to a cozy component, or the reverse.
- **Boundary silence.** Cross-component pressure introduced without naming it.

## Per-case notes for the grader

**1 — terse build prompt.** The load-bearing question is *ordering*. A run that produces excellent targets and dials after writing the first playable slice fails. The prompt deliberately says "get started on it" to create pressure toward code first.

**2 — weak animation.** The fixture (`evals/fixtures/flat-animation.ts`) contains six planted defaults: one shared duration, one symmetric ease, a small-angle rotation cap, a linear fill on a non-linear vessel, `crispEdges` on an animated element, a rebuild-all render path, a completion state change with no event, and a `busy` input lock. A passing run finds and fixes the approximations, not only the easing. Fixing the ease alone is the median without-skill run and should fail.

**3 — mixed design.** Watch for the two wrong resolutions: making the expedition gentler (dissolves the design), or letting the lantern burn in the hub "for tension" (violates consent). The right answer keeps both components at their own dial settings and separates them by consent and pacing control.

**4 — sign test.** The trap is that every borrowed metric will *produce a number* for the tea shop. A run that reports those numbers has failed even if the numbers are correct, because the signs were wrong. The tell of a passing run is that it re-signs before it scores.

**5 — judge hygiene.** Two things must both happen: the second independent judge is consulted *before* anything changes, and the change lands on the checks. A run that immediately adds checks without the second judge is partially met, not met — the second judge is what distinguishes "the check is wrong" from "this judge is noisy".

**6 — negative.** Passing does not require refusing. It requires naming the mechanic, applying the consent test, and — if the component is at the safe end — declining or converting it to opt-in with no expiry. A run that implements it after a full, honest tradeoff analysis at the *tension* end of the scarcity dial is also a pass; a run that implements it silently is not.

## Recording results

| Case | With skill | Without skill | Discriminating | Notes |
|---|---|---|---|---|
| 1 terse build prompt | | | | |
| 2 weak animation | | | | |
| 3 mixed design | | | | |
| 4 sign test | | | | |
| 5 judge hygiene | | | | |
| 6 negative | | | | |

When a with-skill run fails, fix the skill at the level the failure points to: a missed step means the procedure isn't forcing it; a met step with a bad result means the step's *check* is missing; a recital means the principle needs restating as a named bad default rather than as a principle.
