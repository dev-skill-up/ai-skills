# The measurement toolkit

This is the external comparator. Your own eye is not one: it is the same eye that chose the timid number, so a perceive loop without an outside reference is a mirror that converges on "acceptable to me", and "acceptable to me" was the problem.

Sections: §1 reference measurement (replaces carried magnitudes) · §2 the design-decisions artifact · §3 bots, traces, metrics, verdicts · §4 judged traces · §5 games with no repeatable loop · §6 judge hygiene, calibration, and the human anchor.

## 1. Reference measurement — the procedure that replaces carried magnitudes

**If you are about to type a duration, angle, scale, distance, count or cost and you have not measured a reference, stop and measure.**

1. **Pick one shipped, commercially proven game in the target genre** — two if the genre is broad (e.g. "roguelike" spanning deckbuilders and action roguelites). This is a reference for **structure and timing only**: never for art, names, copy, characters, or assets. Nothing is copied. Record which game and which version/build you measured.
2. **Capture the relevant moments** as video or frame sequences: the core action, its feedback, a mid-tier reward, a top-tier reward, a completion event, a failure, and the single biggest moment the game has.
3. **Step them frame by frame** and tabulate, for each phase of each moment:
   - duration of the phase;
   - how far the principal element **moves**, **rotates**, and **scales**;
   - what happens on impact — **what reacts, and for how long**;
   - what happens at completion — the whole sequence, in order;
   - how many discrete "things happen" in the moment (count them);
   - how long input is unavailable (usually zero — write down the zero, it is a finding about your own build later);
   - how big/loud the biggest moment is **relative to** the routine one (a ratio, not an absolute).
4. **Write the table into `design-decisions.md` as the project's budget.** Every magnitude in the feel spec either matches the table or records why it deviates.
5. **Repeat for loop pacing** where a loop exists: actions between rewards; time to first reward; time to first new element; how quickly the game recovers a player from a full board or an empty resource; how often something new appears.

This is the only place genre-specific numbers enter this skill, and they enter measured. Ratios travel better than absolutes — prefer "the top-tier reward is ~3× the routine one in scale and ~2× in duration" over a raw millisecond count when adapting across platforms or art styles.

## 2. The design-decisions artifact

One file (`assets/design-decisions.template.md` is the shape), living with the project, containing: components and their emotional targets; the three dials per component; boundary rules; the signed metric table; the reference table; the feel spec per animation family; the list of approximations broken and kept; the genre primer (§4); and a log of every drift-check decision and threshold change.

It is not documentation written after the fact. Steps 1–6 of the procedure produce it, and steps 7–8 append to it. If it does not exist, the design decisions were not made — they were defaulted.

## 3. Bots, traces, metrics, verdicts

Where the game has a repeatable loop with a legal action set, the loop is played by **bots against the real game core**. This forces the core to be **headless and deterministic**: same seed + same actions = same state, and the legal action set is exposed at every state. If that is expensive to build, build it anyway — it is the difference between measuring the loop and guessing about it, and it pays for itself the first time you tune a screen.

### 3.1 The personas

Bots are **human styles, not optimal agents**. The point is coverage of how people actually play, not a solver. Instantiate each per game:

| Persona | Policy | Represents |
|---|---|---|
| **optimizer** | lookahead toward the next goal; keeps headroom; banks strategically | the player who thinks |
| **impulsive** | acts whenever it can; takes the first legal progress move; never banks | the player who doesn't think and shouldn't have to |
| **optimizer-with-slips** | optimizer with error rate ε drawn from the mistake catalog; every mistake **annotated in the trace** (what it did, what it should have done) | the player who thinks and slips |
| **goal-tunneler** | only acts toward the currently visible goal; ignores system health | the player who reads the objective and nothing else |
| **hoarder** | never converts past what a goal needs; banks everything | the player afraid to waste |
| **distracted** | random legal action with mild preferences; ignores a completable goal some fraction of the time | the player half-watching TV |
| **quitter** | any persona, plus: quits/skips after N consecutive actions with no progress | anyone who found the exit |

Rules:

- Run **every persona on every screen with ≥ 30 seeds**.
- Bots must be fast — thousands of actions per second. If they aren't, the core isn't headless enough.
- **Bot parameters are frozen per release. Screens are tuned to the bots; bots are never tuned to screens.** The moment you adjust ε to make a screen pass, the instrument is gone.
- A **CI invariant** checks the skill ordering: optimizer ≤ optimizer-with-slips ≤ impulsive in median actions-to-complete; distracted ≥ impulsive. A violation means a bot is broken, not that the screen is interesting.
- A **replay test** records a real-build session's actions and replays them through the headless core, comparing state hashes. This is what proves the bots play the same game the player does. Without it, every number below is about a simulation of your game.

### 3.2 Trace format

One record per action (schema: `assets/trace-record.schema.json`):

- timestamp, persona, seed, action, result summary;
- visible goals, and which are completable now;
- resources; progression step;
- an **events** list marking big changes: goal complete, progression step, high-tier outcome, combo/bonus, area unlocked, story beat, choice made, reveal, skip/quit — **and first-seen item / first-reached tier / newly unlocked system**, because if the events list contains only rewards, the novelty interval cannot be computed and a loop that pays constantly while teaching nothing will score well;
- an **ASCII snapshot** every N actions and at every big change, so a reader can *see* the state without replaying;
- an **annotation** field, filled only by mistake-making personas.

### 3.3 Mistake catalog

Genre-neutral shapes; instantiate per game:

- destroyed / consumed something a goal needed;
- over-committed a resource, causing a stall;
- spent effort on something no goal needs;
- banked something and forgot it;
- spent early (included deliberately to verify it is harmless — if it isn't, that is a finding about the design, not about the bot);
- missed a bonus that was available.

For each annotated mistake, the scorer measures **recovery cost** (actions until prior progress is regained) and records **foreseeability** (was the consequence visible in the state at the time). Expensive **and** unforeseeable is the punishing case.

### 3.4 Metrics

Sign every one of these from the dial tables in SKILL.md before reading any of them.

- **Completion** and **actions-to-complete**, per persona.
- **Skill gradient** — measured in **speed** under a tension failure dial (the optimizer finishes faster), in **size** under a safe one (the optimizer gets richer outcomes; completion is universal). Measuring the wrong one makes a well-tuned cozy screen look broken.
- **Flat flag** — raised when optimizer and impulsive are statistically indistinguishable on the axis the dial says matters. Skill buys nothing here.
- **Reward interval** — mean, p90, max.
- **Novelty interval** — same statistics over first-seen/first-reached events.
- **Escalation** — big events per 100 actions across the screen; must rise (and under a capped intensity dial, must also stop rising).
- **Decision index** — at each state, the optimizer's value gap between best and second-best move. Always large means one obvious move; always near zero means the choice doesn't matter. The measure of interesting decisions is **the fraction of states with close-but-different top moves**, plus **persona divergence at the same state** (different styles pick differently and both get somewhere).
- **Anticipation fraction** — share of time with a visible payoff one step away.
- **Stall** — longest run of actions with no progress.
- **Dead end** — states with no progress-making move. **Zero tolerance.**
- **Board-full / resource-out** count and exit time.
- **Recovery cost** and **foreseeability**, from the annotated mistakes.
- **Quit / skip rate** at moderate patience — the primary outcome where no compulsion layer exists.
- **Variance across seeds** — coefficient of variation of actions-to-complete for the optimizer. High means chance decides, not the player.

### 3.5 Verdicts and routing

One verdict per screen, naming the metric that produced it and the seeds to look at:

| Verdict | Route to |
|---|---|
| `pass` | — |
| `flat` | deepen what skill buys (add a lever the optimizer can pull that the impulsive bot won't) |
| `too_hard` | goals or layout |
| `too_slow` | cut costs, or add a mid-screen big change |
| `punishing` | add headroom, or reorder so the expensive mistake becomes foreseeable |
| `dead_end` | goals or layout — always, immediately |
| `chance_bound` | reduce generator variance |
| `no_decisions` | add tradeoffs; make an always-right move situational |

### 3.6 Protections on the scorer

- **Thresholds move stricter only**, unless a logged judge disagreement justifies loosening. CI diffs the metrics doc and **fails an unlogged loosening**. Otherwise the thresholds drift to wherever the current build happens to sit.
- A **fixture set of known-bad screens** — a dead end, a flat screen, a too-slow screen, a punishing screen, a chance-bound screen, a no-decision screen — each with the verdict it must receive, run in CI. **A metric change that stops flagging a fixture fails the build.**

### 3.7 What bots cannot tell you

Bots score the loop. They do not score the reveal, the story, the art, or the feel. **A screen can pass every loop verdict and still be flat because the reward is ugly or the beat is dull.** The feel pipeline (`feel.md` §3) and the judged traces (§4) gate those. Never report "all screens pass" as "the game is fun".

## 4. Judged traces

For each screen, sample traces **stratified**: worst stall, best optimizer run, highest-recovery-cost mistake run, median impulsive run, one random.

Render each as a readable log — snapshots, events, annotations, one narrative line per big change — and hand it to a judge along with:

- the **design intent** for that screen (its targets and dials, from `design-decisions.md`);
- a **genre primer** — a document you write once per project describing what a good session in this genre feels like moment to moment, what a lapsed player expects in the first ten minutes, the standard complaints, and what "satisfying" means here.

The judge writes: **fun 1–5** and **frustration 1–5** with timestamped reasons; where it would have quit; whether the annotated mistakes look human and the punishment proportionate; and whether the design intent came through.

**Judges never see the deterministic scores first.** Drift-check as in `feel.md` §3.7, with a second independent judge who gets only the design intent and a one-paragraph description of the game.

## 5. When there is no repeatable loop

Pure narrative games, walking sims, and one-shot experiences have no legal action set to enumerate. **Skip §3 and say so** rather than forcing bots onto it. What replaces it:

- **Beat-level pacing measurement** instead of loop metrics: time between meaningful changes of frame, novelty interval over first-seen locations/characters/mechanics, anticipation fraction over visible pending payoffs.
- **Path coverage** instead of personas: enumerate the reachable branches and confirm each is reachable and non-dead-ended.
- **The judged-artifact protocol (§6)** carries the weight: blind judges reading the beat sequence against the design intent and the genre primer.
- The feel pipeline is unchanged and matters more, not less.

## 6. Judge hygiene, calibration, and the human anchor

- **Blind critic.** The judge sees only the rubric, the artifact, and the minimum context needed for the artifact to make sense. Never the drafting conversation, never the author's intent beyond what the rubric requires, and never the fact that the draft is its own.
- **Every criterion, by name.** For each rubric criterion, the critique either produces a required change quoting the lines it applies to, or states how adherence was measured, with citations into the artifact. A criterion neither fixed nor measured is a **critique defect** — the critique is re-run, not accepted.
- **Score by minimum**, iterate to a cap (art and animation ~4; specs and prose ~3). **At the cap, escalate one level** — to the spec, the rubric, or the design decision the artifact depends on — and that gets its own critique before the retry. **Nothing is silently accepted at the cap.**
- **Appeal rubrics are calibrated against a hold-out.** Generate a spread of candidate outputs spanning the parameter space, some deliberately bad. Split in half. Iterate the rubric on the first half until it agrees with two independent judges on the top and bottom quartiles. **Never iterate against the second half**, and require every rubric change to leave hold-out agreement no worse (CI-checked). Write the independent judges' briefs **before the rubric exists** and commit their hashes; the briefs never change to fit the rubric.
- **Comparative before absolute.** Rank variants against each other first; derive absolute thresholds from the ranked winners. Absolute numbers pulled from nowhere are provisional and get marked so.
- **Model judges share a blind spot.** Two readings by the same model family are not independent samples of human taste. The drift check catches disagreement between them; it cannot catch an agreed miscalibration. The **reference measurement (§1) is the one element in the loop that is not the model's taste** — which is why it is not optional.
- **The human anchor.** Published validation of LLM agents as game testers covers **difficulty** (agent performance correlates with human difficulty data, roughly 0.6–0.9 across the games studied) and **explicitly does not cover enjoyment**. So: get a human anchor wherever one can be had — even a handful of human ratings, or the genre's real complaint corpus (store reviews, forum threads) distilled into the genre primer. **Without one, say plainly that the "fun" scores are predictions of what a human would say, not measurements.** Report them that way in the summary; do not launder a prediction into a measurement by putting a number on it.
