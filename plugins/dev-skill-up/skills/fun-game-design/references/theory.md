# Fun theory, compressed

Read this in two minutes. The point is not to learn the frameworks — you already know them — but to know **which one applies to the decision in front of you**, and to notice where two of them disagree in sign. Attributions are here to help you retrieve what you already have.

## 1. Two camps, and which one to operate under

**Monist** (Raph Koster, *A Theory of Fun*): fun is the emotional response to **learning**. The brain rewards pattern recognition; a game is a pattern-delivery system; boredom is the pattern being exhausted, or being too hard to perceive at all. "Not requiring skill from a player should be considered a cardinal sin." A good game "teaches everything it has to offer before the player stops playing." Koster later carved out practice, story, meditation and comfort as "perfectly valid non-fun reasons to use games" — he preserved the theory by shrinking its domain, which is itself the evidence that the domain is smaller than the word "fun".

**Pluralist** (Marc LeBlanc; Nicole Lazzaro; Chris Bateman's critique of Koster): fun is several distinct emotional targets with different production functions.

- **LeBlanc's eight aesthetics:** sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission (pastime).
- **Lazzaro's four keys,** each with its emotion: **hard fun** (fiero — triumph over adversity; frustration is an ingredient, not a defect), **easy fun** (curiosity, discovery, wonder), **serious fun** (relaxation, altered internal state, rhythm and repetition, "everything is ok"), **people fun** (amusement, social). Her empirical claim: best-sellers offer at least three of the four, and players alternate between them *within a session*.
- **Bateman's addition:** a **mastery aesthetic** — enjoying the exercise of skill you already have, distinct from both learning and winning. "Why should players stop doing what they are enjoying just because they aren't learning?"

**Operate as a pluralist; keep monism as a diagnostic.** Every component names 2–3 emotional targets (SKILL.md step 1), and Koster's test — *is there anything left to learn here?* — is one check among several, not the definition.

## 2. Fun cannot be measured directly

A "how fun was it, 1–10" rating is contaminated by context (a lab, a novel unreleased game) and is useful only **comparatively** — build A vs. build B, level 3 vs. level 4 — and only when backed by *why* and by behavior. So: name the specific emotions the component targets, measure those, and use behavioral proxies (*how many times should players fail here? how long should this take?*).

Two results worth carrying:

- **Need satisfaction predicts retention where enjoyment ratings do not.** Self-determination-theory measures (PENS: competence, autonomy, relatedness) predicted sustained play in longitudinal studies where enjoyment ratings lost predictive power in the same regression. The best-validated current player-experience instrument (PXI) likewise separates *functional* consequences (ease of control, clarity of goals, challenge, progress feedback, audiovisual appeal) from *psychosocial* ones (mastery, curiosity, immersion, autonomy, meaning) — and never asks about "fun".
- **Retention is not fun.** Free-to-play uses retention as its fun proxy, but retention is produced by compulsion as readily as by fun (Jonathan Blow's critique). The honest operationalization is Richard Terrell's: *fun is whatever a person willingly gives time and attention to, unforced.* The load-bearing word is **unforced**. Hence: voluntary quit/skip rate is the primary outcome in any design without a compulsion layer, and retention benchmarks from compulsion-driven games do not transfer.

## 3. Flow is more than the challenge–skill diagonal

Design discourse reduces flow to "match challenge to skill". The theory has more components, and each is something you actually build: **clear goals; immediate feedback; uninterrupted concentration** (nothing interrupts mid-loop); **merged action and awareness** (controls disappear); **loss of self-consciousness; time distortion**.

The eight-channel model labels *high skill / low challenge* the **control** channel and treats it as suboptimal. That channel is exactly what a relaxation-seeking player is buying. **When a component's targets are serious fun or mastery, the control channel is the target, not a failure state.**

## 4. Failure (Jesper Juul, *The Art of Failure*)

Action and challenge fun is *built on* failure: "we feel bad when we fail, yet we seek out situations that guarantee failure." Three axes decide whether failure is acceptable:

- **internal vs. external** — the player's fault, or the game's;
- **stable vs. unstable** — skill-based, or chance-based;
- **global vs. specific** — "I am bad at this", or "I missed this one thing I can now close".

Acceptable failure is **internal, stable, specific, and recoverable**. A **dead end** — a state with no progress-making move — is external failure and is a defect in every genre at every dial setting. How *much* failure is desirable is the failure dial; whether failure is *fair* is not a dial.

## 5. Interesting decisions (Sid Meier)

A decision is interesting when it has **tradeoffs**; is **situational** (interacts with current state instead of being always-right); is **personal** (lets a play style express itself); has **persistence** (consequences that last); is **informed** (the player has enough to reason with); and is **acknowledged** — "there's nothing more paranoia-inducing than having made a decision and the game just kind of goes on."

A screen with one obvious move has no decision. A screen where the choice doesn't matter has no decision either. Both show up in the decision index (`measurement.md` §3).

## 6. Loops and arcs (Daniel Cook)

A **loop**: model → action → system → feedback → updated model. Mastery is asymptotic, so loops don't burn out. An **arc** is a one-time payload — story, a reveal, a cutscene. Players consume an arc once and want another, which puts you on a content treadmill.

Story is arcs; the core mechanic is a loop. Consequence: **the loop must be fun with the arcs disabled** — some players skip every beat, and the loop is what survives when the content runs out.

## 7. Coziness (Project Horseshoe 2017; Cook)

Coziness is the fantasy of **safety** (no threat), **abundance** (needs met, no scarcity), and **softness** (low-intensity stimuli, gentle aesthetics).

It is *negated* by: extrinsic reward loops ("almost any form of extrinsic reward generates a pressing transactional short-term need"), danger signals, mandatory responsibilities, unwanted notifications, intense or sudden stimuli ("anything sudden, disproportionately bright or loud"), artificial scarcity, deception, and non-consensual social presence.

Coziness is **not** the absence of challenge. It is compatible with challenge when the challenge is **opted into and framed by rest the player controls** — the canonical example is a bonfire in a brutally hard game: no immediate danger, and the player chooses when to leave. **The reconciling variable between hard fun and cozy fun is consent and pacing control, not difficulty.** That is why SKILL.md step 3 exists.

## 8. The sign flip

A specific subset of the things that produce action fun are, in the cozy literature, the things that destroy cozy fun:

| Ingredient | Action fun | Cozy fun |
|---|---|---|
| Failure | the payload | a hazard |
| Scarcity | the tension of strategy | a negator |
| Rising intensity | the curve | a negator |
| Extrinsic reward chains | the driver | poison |
| Skill demand | Koster's cardinal virtue | not what the mastery player came for |

What does **not** flip: **legibility** — fast acknowledgment, eased motion, follow-through, clear cause and effect, acknowledged decisions, no dead ends, something new regularly. Every genre needs those.

This table is the whole reason the procedure starts with a per-component commitment. Without the dials, no metric has a sign, and you will silently import an action game's metric set into a cozy component (or the reverse) and tune toward the wrong thing while every number improves.

## 9. Game feel and juice (Steve Swink; Disney; the "juice" talks)

**Game feel = real-time control + simulated space + polish**, and polish is where most of the fun-per-effort lives.

The **Disney twelve** transfer to interactive motion almost unchanged: squash & stretch, anticipation, staging, follow-through & overlapping action, slow-in/slow-out, arcs, secondary action, timing, exaggeration, appeal (plus the two about drawing technique).

**Juice** adds: acknowledge every input; escalate feedback with magnitude; and — genre-dependent — screen shake, hit-stop, flash and bass. Those last are **intensity** tools and are governed by the intensity dial. **Exaggeration is not intensity**: a bottle tilting past horizontal or a merged item popping to 1.3× stays legal under softness. Confusing the two is how a cozy game ends up with no personality at all.

## 10. Anticipation, reveal, and the near-miss

Anticipation is a **state**, not just an animation phase: the player can see the payoff coming. In renovation and progression genres this is the *legible mess* principle — the ruined room reads as fixable, so the player can predict the finished room; each step visibly changes the frame; the biggest change lands last; lighting lands late because it retroactively improves everything before it; the signature piece is the reveal. In action genres it is the boss health bar.

Measure it as the **fraction of time the player has a visible pending payoff**.

Caution: the **near-miss** effect ("almost got it") is a strong motivator whose evidence base is gambling. Its behavior in skill-based, non-monetized play is unstudied. Decide deliberately how much near-miss you want; do not accrue it by accident from a generator that happens to produce a lot of one-away states.

## 11. Novelty cadence

Koster's frame implies the fun event is *the player learned something*, which is not the same event as *the player got paid*. Even the coziest games keep introducing things — a new season, a new recipe, a new room. **A loop in which nothing new appears is dead in every genre**, at every dial setting. Novelty interval is a first-class metric alongside reward interval, and it is the one most often missing from an events list.
