# Removing AI tells from essay prose

Run this procedure on every researched essay — sleep or casual — after the draft is finished and before any audio is generated. It is a **convergence loop with a hard gate**, not a pipeline and not a "polish" prompt: the passes run until a full cycle of every pass returns zero findings, and nothing proceeds to audio before that. Everything here comes from real production runs; the numbers are measured.

## The lesson to lead with

**A pipeline has a last edit that nothing reviews.** In the run that forced this file onto a loop, every defect that survived to the finished film was created or preserved *after* the pass that would have caught it:

- The reviewers saw a draft where "It is one of the great pieces of aviation folklore and it is as good as people say" was intact and fine. A compression pass that ran after them cut the folklore clause, leaving "It is as good as people say" pointing at a fatal accident. No pass ran after it. It shipped 51 seconds into the film.
- The rhythm reviewer flagged "Not one by one, obviously" and supplied "though not one ridge at a time" — the same negation relocated into a subordinate clause, where the sentence-anchored blocklist pattern cannot see it. No pass ran after it.
- The fact-checker killed an unsourced pool temperature; the repair replaced it with an unsourced causal assertion ("it does not need to") that is *less* falsifiable than the number was. No pass ran after it.

Three different passes, three fixes, three new defects, zero re-checks. A pipeline cannot catch this, and no amount of better pass content will change that — the fix has to be the schedule. An earlier run taught the companion lesson: **each pass removes a tell and the tell comes back wearing different clothes** — one pass cut paragraph-final zingers, and the next found the kicker had merely swapped its full stop for a comma and come back 43 times. Both lessons have the same answer: after any fix, everything runs again.

## The loop

Run every pass, in the cycle order below. **If any pass returns a finding, fix it — and then run every pass again from the top.** The procedure is complete only when one full cycle returns zero findings from every pass. A pass that has not been run in the final clean cycle has not been run.

**This is a hard gate, not advice. Nothing proceeds to audio until one complete cycle is clean.**

### Cycle order — destructive edits first, cheap checks next, expensive reviews last

1. **Bulk destructive operations.** First-person excision (pass A), the cut pass (pass B), reaching the word count, hitting the metric targets. Every bulk edit happens *before* the reviews of its cycle, never after — the targets are what tempt late rewriting, so get to spec first, then review. The worst line in the source run was written during a final compression pass that ran after every review and was seen by nothing but a regex.
2. **Mechanical checks.** The greppable pass (1 below) and `assets/tell_metrics.py`. If this stage finds anything, fix it and restart the cycle — there is no point paying for an adversarial review of text you already know is wrong. The expensive passes only ever see mechanically clean text, which also keeps convergence cheap in the tail: a late cycle costs a script run, not a fleet of subagents.
3. **Reviews**, each a separate subagent: rhythm (2), structure (3a), register (3b), comprehension (4), the cold read (5), and the fact-check (6). Tell each reviewer what earlier cycles already fixed, or it hands back the same list. Any finding → fix → back to the top.

### Loop mechanics

A naive "repeat until zero" oscillates, burns unbounded subagent calls, or exits falsely. These rules make it converge:

- **Structured verdicts.** Every pass returns `{pass, findings: [...], count_by_category}` — with an explicit zero for every category the pass owns. A reviewer that returns "looks good" has not run. A pass that owns fourteen named tells reports fourteen counts, zeros included, so a zero that was looked for is distinguishable from a category that was skipped.
- **Fix findings one at a time where they interact.** If two findings touch the same paragraph, fix one and restart the cycle. Batched fixes to the same passage are how the fix for one tell writes the next one.
- **The touch counter — the termination rule.** Track how many cycles have modified each sentence. A sentence modified in three cycles gets **deleted**, not rewritten a fourth time. Deletion always terminates; rewriting does not. It is also the correct editorial answer: a sentence that three different passes keep objecting to is not a sentence with a wording problem.
- **Deletion bias after cycle 2.** From cycle 3 on, prefer deletion to any other fix. Most tells below already prescribe cutting; once the draft is close, cutting is the default remedy.
- **Escape hatch.** If the loop has not converged after ~5 cycles, stop patching. Non-convergence means the section is structurally wrong, not underpolished — rewrite it from the research. The alternative is an infinite loop that produces increasingly damaged prose.

### Excise, don't reword — the general policy

The default fix for any tell is **deletion, not rewording**. Deleting a clause is safe; rewriting one produces a subtler version of the same sentence — rewording is what laundered "Not one by one, obviously" past the blocklist as "though not one ridge at a time", and what broke the referent in the opening. Deletion has never introduced a new tell. Where a fix genuinely must add words (a gloss the comprehension pass demanded, a fact a repair needs), the addition is new unreviewed text — which is exactly why the cycle restarts.

## The passes

### A. First-person excision (destructive)

**This pass is the reason the loop exists. Do not optimise it away, and do not trim its re-check.**

First person is banned outright: the `tell_metrics.py` first-person count must read 0. Getting a draft to zero is mass rewriting — dozens of sentences, all touched — and it is the single most dangerous operation in the whole skill; in the source run it is exactly what broke the opening.

- **Excise, do not reword.** Deleting a clause is safe; rewriting one produces a subtler version of the same sentence and can orphan the pronoun in the sentence after it.
- Where a first-person sentence carried a real fact, keep the fact in third person and cut everything else. Where it carried only a stance, cut the sentence.
- This pass ends by re-entering the loop at the top. Not "then continue" — **then run every pass again, including the adversarial reviews, against the post-excision text.** A mass-excised draft that no reviewer has seen is the precise failure this file exists to prevent.

### B. The cut pass (destructive; deletion only)

The old procedure had no way to remove anything — every pass substituted or added. This pass only deletes. One question per sentence: **does this carry information the listener does not already have?** If no, delete it. No rewriting in this pass. After each deletion, read the sentences on either side — deletion orphans pronouns.

That one question catches all of these, every one of which shipped: "You cannot melt it." (both melting points were given one sentence earlier) · "Nothing lit up." · "It found nothing." · "They were sure." · "That crack was findable." · "Most stable, least likely to dissolve, most common." (verbatim restatement of the quote above it) · "If you go looking at these documents yourself, that number is sitting there waiting for you." · "and the bore is the whole story" · "it does not need to"

### 1. Lexical + mechanical

Word blocklist, em dashes, curly quotes, negative parallelism (`not just X but Y`), participial tails (`, ...ing [significance]`). Grep-able — this is the `tell_metrics.py` stage. Do it fast, don't linger.

### 2. Rhythm and cadence (adversarial subagent)

Kicker paragraphs, the flat coda in all four punctuation mutations, sentence-length variance, repeated syntactic frames. Brief: *assume the text is still machine-written and find what survived.* Ask for 25–40 concrete items with quote / problem / remedy — where the preferred remedy is a cut, and any replacement text the reviewer proposes is a candidate for the next cycle to review, not an instruction. Ask flat out: **"if a skilled reader saw this cold, what would tip them off first?"** The best single finding of the whole source project came from that question.

### 3a. Structure (adversarial subagent)

Repeating analytical units, outline-shaped order, information density, name density, transition truth (see the false transition below), tonal monotony. Named-individual density is counted here, not by regex.

### 3b. Register (adversarial subagent, split from structure)

Every tell where the essay talks about itself or grades its own material: metanarration, the narrated transition, the flourish, the unearned judgment, performed failure, narrating what the essay is not, the composed ending. One question, applied sentence by sentence, mechanical enough to be reliable: **is the subject of this sentence the topic, or the telling of the topic?**

This pass exists because the old structure brief named six tells while fourteen were documented under it — a reviewer briefed from that line hunts six. In the failed run, essay-about-itself sentences ran to ~16% of the script and had no owner. 3b owns them, and reports a count for every named tell in its list, zeros included.

### 4. Comprehension — the cold listener (subagent)

Brief: *you know nothing about this subject; read linearly and flag every term, name, or concept you are expected to already understand at the point it appears.* "Heat it past eight hundred and eighty degrees and it rearranges into a cube, which is beta" — beta *what*? The writer knows; nobody listening does. Each flag gets one of two fixes: explain the term at first use, or cut it if it is not earning its place. Renaming it or hand-waving past it is not a fix. Do not reuse the adversarial reviewers here — they have read the essay too many times to notice what it never said.

### 5. The cold read (subagent with no context)

A subagent with no context at all — no research, no draft history, no idea what the film is about — receives the text and answers two questions: **what does each sentence literally say?** and **is there anything here you would not want said about the events this covers?** A cold reader catches a broken referent instantly — "It is as good as people say", pointing at a fatal accident — where the author cannot, because the author knows what was meant. At minimum run it on the first 500 words, where the register is set and where the most rewriting has happened.

### 6. Fact-check (subagent — the pass holding the sources)

An independent fact-check over any researched script, briefed to verify load-bearing claims against sources rather than to admire the prose. On the first source run it caught five outright errors that had survived a careful write, including a study whose finding was reported backwards and a claim off by an order of magnitude. Two obligations beyond that brief:

- **It checks the repairs.** The fact-check is a loop member like everything else, so it re-runs after every fix — and that matters most for its own fixes: a repair to a factual defect is exactly where the next factual defect gets written, because the repair is composed under the constraint "put something here that is not the thing that was wrong." That is how an unsourced pool temperature became "it does not need to" — an unsourced causal assertion less falsifiable than the number it replaced.
- **It owns manufactured doubt.** The brief covers whether claims are supported *and whether the stance toward a supported claim is warranted*. "Investigators concluded X. I do not entirely buy it." is accurate in both clauses and indefensible as a whole. The fact-checker holds the sources, so the fact-checker judges the stance.

## Metrics, with targets (per ~3,000 words)

Run `assets/tell_metrics.py essay.md` at the mechanical stage of every cycle.

**A number sitting on its boundary is a finding, not a green light.** A quota silently converts "these are defects" into "this many defects are correct": the failed run measured kickers at exactly 25% against a target of `< 25%` and read it as a pass — what it meant was that ten paragraphs end on a flourish and the skill said that was the right number. Where zero is honest, the target is zero. Where it is not, the last column says why a residual is acceptable — and instances near the boundary still get read one by one.

| Metric | Target | Why the residual is acceptable |
|---|---|---|
| Flat coda `[clause][, and / — / ; / :] [≤10w coda]` | < 20 total, reported per punctuation | Ordinary compound sentences end in short clauses; the tell is the frequency and the metronome, not the shape. The failed run shipped the em-dash mutation ("— it does not need to") while the comma count read fine, so every punctuation is counted. |
| …of those, paragraph-final | < 6 | Same shape, but paragraph-final is where the shrug lands hardest. Read every one. |
| Kicker paragraphs (incl. one-liners) | < 25% | Some paragraphs earn a short close. Near the line that is ten paragraphs ending on a flourish — read them all. |
| Sentence-length stdev | > 9 | A floor on variance, not a quota of anything. |
| Em dashes | ≤ 8 | Legitimate punctuation; density is the tell. (The old 4–8 range is gone — a floor is an instruction to add em dashes.) |
| Sentence-initial "The" | < 20 | Normal English syntax; the drumbeat is the tell. |
| Non-restrictive `, which` | < 9 | Same. |
| `a [profession] named [Name]` | ≤ 3 | The frame is fine once; the repetition is the tell. |
| `In YEAR, NAME VERBed` | ≤ 2 | Same. |
| Named individuals | < 1 per 150 words | People belong in a story; a phone book does not. Judgment call — counted in pass 3a, not by regex. |
| First person | **0** | Banned outright. Zero is honest; see pass A. |
| Metanarration (regex floor) | **0** | Banned outright. The regex count is a floor, not a measurement — in the failed run a hand-written pattern list read ~16% of sentences and a reader found more instances in under a minute. Pass 3b supplies the true figure. |
| AI vocabulary hits | **0** | — |

**The slack floor is removed.** The old table required ≥ 4 sentences "carrying no fact", and the structure notes said to add 3–4 — which directly contradicted the cut pass, and conflated two different things. A connective that exists only to reach the next clause is fine, and needs no quota in either direction. A beat that restates the previous sentence shorter for emphasis ("They were sure." "It found nothing.") is the flourish tell, and the cut pass deletes it. Every "slack" instance in the failed run was the second kind, and the old metric scored them as progress.

## The structural tells worth naming explicitly

- **The repeating analytical unit.** "Term → scholar A reads it X → scholar B reads it Y → unresolved" ran **8 times**, and the same two scholars were staged as a matched pair **5 times**. Fix: introduce the recurring cast *once*, then either assert one reading flatly or refer to them generically. Keep 3 disputes, the ones with the best evidence and the highest stakes.
- **Outline order.** Discovery → language → method → content → object → provenance → conservation → conclusion is a filing cabinet, not a train of thought. Add 2–3 deliberate disruptions: move a description to the scene where someone is physically holding the thing; let a fact that invalidates earlier facts barge in early and get abandoned, then picked back up where it lands; move context to where it is needed rather than where it tidies up.
- **Name density.** 28 named people in 2,950 words, nearly all mentioned once with a credential appositive and a date. Nobody talking remembers that many.
- **The narrator never fails.** Add genuine friction — but never first-person friction (first person is banned outright, see the over-correction section) and never *performed* failure. The friction comes from the material itself: a dispute left unresolved, a fact that barges in and complicates what came before, an abandoned thread picked back up late. Performed boredom is not friction — a narrator "looking at the clock" is announcing an editing failure instead of fixing it.
- **Performed failure.** "…which I should have flagged ten minutes ago when I introduced alpha. Sorry." An apology for structure is not friction, it is a draft narrating its own editing failures. If something should have been introduced earlier, **move the introduction** — that is a silent edit, not content. Explain the concept where it is first needed and delete the commentary about when it arrived.
- **The unearned judgment.** "…which is a rotten name." Editorial asides about the material need backing: if the terminology genuinely confuses people in practice, cite where that confusion is documented; otherwise cut the judgment and let the explanation do the work. Same rule as guesses — opinion staged as insight is filler.
- **The flourish.** "Most stable, least likely to dissolve, most common. Three superlatives, none of them good." A fragment drumroll capped by a sentence admiring its own rhetoric. Write what is meant — the phase is stable, insoluble, and common, and that is exactly what makes the defect dangerous — once, plainly. A line that exists for its sound rather than its content gets cut, and prose never comments on its own phrasing.
- **The restated beat.** Real speech has clauses that exist only to reach the next one, and those are fine — no quota in either direction. But a beat that restates the previous sentence shorter, for emphasis ("They were sure." "It found nothing."), is the flourish wearing casual clothes. The cut pass deletes it: it carries no information the listener does not already have.
- **The narrated transition.** "Jump forward nineteen years for a second, because there is a number that belongs here and nowhere else." Announcing a structural move and then defending its placement is tour-guiding. Make the move without comment: "Nineteen years later, they would find…" The disruptions recommended above — facts barging in early, context moved to where it is needed — are done silently. If the placement is right it needs no defense; if it needs a defense, it is in the wrong place.
- **The false transition.** "Because what matters is what the inspections did and did not do" opening a paragraph, when nothing above it supports the "because" — a causal connective that follows from nothing. Glue pretending to be logic. For every paragraph-initial connective (*because*, *so*, *and that is why*, *which is why*), check that the claimed relation actually holds between the two paragraphs; if it does not, the connective is decoration, and the cut applies to the connective. Owned by pass 3a — nothing else checks whether connectives are true.
- **The essay talking about itself.** "A hundred and eleven people died. A hundred and eighty-five did not. That is the only sentence in this episode about that, and it is the reason there is an episode." The first two sentences are the content; the third is the essay defending its own scope, and it goes. No "this episode", "this essay", no commentary on what the essay is or is not covering, no defending restraint or tangents — if a tangent needs a defense, cut the tangent. Pacing commentary is the same tell: "this is the part of any accident story where I start looking at the clock, so I will be quick" promises brevity instead of delivering it — if a section drags, shorten the section. This is the umbrella over the narrated transition, metanarration, and performed failure: the essay is about its subject, never about itself. Pass 3b owns the whole family.
- **Metanarration.** "As to why nobody saw it, the Board's best reconstruction is almost stupidly mundane." Two tics in one sentence: announcing the question instead of answering it, and rating the answer before delivering it. Write "The Board's best reconstruction is…" and give it — if the reconstruction really is mundane, the mundanity will show; telling the listener how to feel about a fact before stating it is the essay grading its own material.
- **Manufactured doubt.** "Investigators looked hard at whether the two got swapped and concluded that they did not. I still find it an uncomfortable coincidence, and nothing in the record resolves it." The record contains a conclusion; report it: investigators concluded the forgings were not swapped. Bookending a closed question with "never gets resolved" and "nothing resolves it" is the narrator overruling the evidence with a mood — a conspiracy theory in documentary clothing. Doubt needs a citable source that actually disputes the conclusion; without one, the conclusion stands as stated. The bloat is part of the same tell: a paragraph of words wrapped around one sentence of fact is the insinuation doing the padding. (Leaving *genuinely* open disputes open is still right — this is about questions the sources closed.) Owned by the fact-check pass, which holds the sources.
- **Narrating what the essay is not.** "Everybody knows that crash… It is as good as people say, and this is not that story." Appealing to what "everybody knows", or naming an adjacent famous topic just to wave it off, is throat-clearing borrowed from someone else's essay. The negation transition is the same tell in motion: "Now go backwards. Not to the crash. To a foundry in Ohio." Go straight to the foundry — nothing the essay is not about gets named on the way. Excise it, do not replace it — the general policy above. What remains should be only what is actually in the essay.
- **Negating an alternative nobody proposed.** "You cannot melt it." "though not one ridge at a time." "Not after a decade of service." Manufactured contrast out of nothing, and it arrives in five grammatical costumes — sentence-initial, subordinate clause, participial tail — which is why no single pattern finds it. (The negation transition above is one costume, scoped to waving off adjacent topics; this shape is broader.) The cut-pass question catches it: the alternative was never live, so the negation carries no information.
- **The unattributed rumor.** "I have heard", "it is said", "some say", "legend has it". Either the claim is established — then state it flatly — or it is a persistent rumor worth engaging, in which case point at where it actually lives ("the New York Times described it as X") and correct it, and do even that only when the correction is load-bearing. Usually the right move is to not mention the false version at all.
- **The narrator's guess.** "Nobody writes down why two and not three; my guess is cost, because…" — remove the guess, keep the fact. If research produced a real, interesting reason, state the reason; if not, move on. Speculation staged as insight is filler with a confident voice.
- **Tonal monotony.** The deepest tell: one attitude applied to everything at identical strength. A death, a joke, a paywalled paper and a cat's head in a wreath all delivered at the same wry, level pitch. A human loses the register somewhere.
- **The composed ending.** Four fragments in descending length with the strangest item last is a drumroll. Consider moving that material to where a person would naturally mention it, and ending on something genuinely unresolved instead. But genuinely unresolved means a question with stakes — "the Board cannot determine whether the disks came from the same heat… the docket has never been released, the reports are still not public" is not a mystery, it is an archive complaint, and it is the weakest closer there is. End on the strongest thing the essay established, or on an open question that matters. If the only mystery is missing paperwork, do not end on it.

## Warn about over-correction

Adding friction, the source run pushed first-person from 2 to 25 instances — which is just a different tic, and one the house style now bans outright (pass A exists to remove it). Friction comes from structure (late glosses, abandoned threads, open corrections), never from a narrator persona. **Re-measure what you added, not only what you removed** — the loop enforces this mechanically, because every addition restarts the cycle and re-runs every pass over it. The same watch applies to "And"-initial sentences, fragments, and self-correction.

## Narration-specific

Spoken text fails differently. Include in the passes:

- no initials in names (`L. B. van der Meer` becomes "ell-bee-van-der-meer");
- round numbers unless precision is the point;
- attribution before the claim, not after;
- name the noun instead of "this" or "these";
- long lists of foreign words are unlistenable — cut to three and say so;
- every concept the essay leans on gets a gloss, placed where the concept is first needed (that is what pass 4 checks). If a pass finds a term introduced too late, move the introduction — never leave the gloss where it is and narrate that it should have come earlier.

## What not to do: the blocklist is not the fix

The natural response to a new defect list is twenty more strings in `AI_VOCAB`. Resist it. That list once went from 0 hits to 18 hits on unchanged text between two versions of this skill — a blocklist is the skill's memory of what went wrong stored as string literals, and it scores every future essay against the last essay's mistakes.

The blocklist is right for phrase-shaped tells and useless for structure-shaped ones. These shipped, and no list will ever catch them: "and the bore is the whole story" · "There is a second detail here that never gets resolved" · "if you want to rewind, this is the place" · "And we have the Board's finding, which is unambiguous". Each is caught by a pass with a question — the cut pass's "does this carry information the listener does not already have?", 3b's "is the subject the topic or the telling of the topic?", the fact-checker's stance check.

A new tell earns exactly one of three responses: **a question given to a pass, a count given to the metrics, or a change to the schedule.** If a proposed fix is none of the three, it is probably already covered and is not the gap.
