# Shared essay craft

Everything here applies to **both** essay types — the sleep essay (`references/sleep-essay-craft.md`) and the casual essay (`references/casual-essay.md`). Those files hold only what is specific to their mode; this one holds the shared machinery: how a topic is chosen, how it is researched, when it is killed, and the house rules every essay obeys.

## Topic workflow

1. **Pitch a batch.** Produce a numbered list of **50** pitches, each a 2–3 sentence hook in the register the essay type calls for (for a sleep essay, the lore criterion in `sleep-essay-craft.md`). Pitches can be speculative — verification happens later.
2. **Selection.** The person picks one (or asks for another batch).
3. **Research** the chosen topic before writing (below).
4. **Write the full essay** as a Markdown artifact.
5. **Render** via the pipeline (see the type-specific file).

**If a topic is discarded** — research collapsed the story, or it fails for any other reason — do not quietly substitute a favorite: go back to step 1, generate 50 fresh candidates, and choose from them, exactly as at the start.

## Research strategy

Search **before** writing, both for inspiration and to verify specifics. The patterns that work:

- **Many targeted queries beat one broad one.** Fire several narrow searches rather than a single general one.
- **Combine scholar names + technical terms + discovery years.** This is the most reliable way to surface actual academic sources rather than popularizations. E.g. a site name plus an excavator's surname plus "2019"; a method's technical name plus the mathematician who reconstructed it.
- **Go general → specific progressively.** Start wide to find the names and terms, then re-search with those to reach the primary scholarship.
- Verify the load-bearing claims — the surprising reversal, the specific date, the mechanism — at this stage. The pitch could be a speculative hook; the essay should not be.

## No story, no essay

Decide after research, before writing a word: if the central question closes with "the records were never released" — no mechanism, no reversal, nothing resolved and no open question with real stakes — there is no story. Discard the topic and restart the topic workflow above. Generation and render time are too expensive to spend on a topic whose payoff is a shrug (a casual essay's render alone is ~23 minutes, plus image sourcing and diagram passes).

## The house rules

Six hard rules, enforced in the ai-tells passes (`references/ai-tells.md`):

- **No first person, at all.** The `tell_metrics.py` first-person count must read 0. This also kills the hedge register that rides on it — "I have heard", "I don't understand", "I always assumed". Say what is established, flatly. If a persistent rumor genuinely matters, attribute it to where it lives ("the New York Times described it as X") and then correct it — and do even that only when the correction is load-bearing. Most false claims deserve no airtime at all: leaving them out is the improvement.
- **Never narrate what the essay is not.** No "everybody knows the famous version…", no "this is not that story", no naming an adjacent topic just to wave it away — and no negation transitions either ("Not to the crash. To a foundry in Ohio." — go straight to the foundry). Excise these framings; do not reword them. What remains should be what is actually in the essay.
- **No guesses.** "Nobody writes down why two and not three; my guess is cost" — remove. State the fact ("it's two"); if research turned up an interesting reason why, add the reason; if not, move on. Speculation is not depth. Same for second-guessing documented conclusions: if investigators concluded the two forgings were not swapped, that is the fact, in one sentence. Doubt needs a citable source that disputes the conclusion, not an "uncomfortable coincidence" mood.
- **Fix the structure; never narrate the fixing.** "…which should have been flagged ten minutes ago. Sorry." means the introduction is in the wrong place — move it. Editing failures are not content. The same goes for the moves themselves: "Jump forward nineteen years for a second, because there is a number that belongs here and nowhere else" is a transition apologizing for existing — just make it ("Nineteen years later, they would find…"). Editorial asides ("a rotten name") follow the same rule as guesses: if the name confuses people in practice, cite where that is documented; otherwise cut the judgment and just explain the concept.
- **Say it plainly.** "Most stable, least likely to dissolve, most common. Three superlatives, none of them good" — a drumroll admiring its own rhetoric. State the fact once, in a plain sentence. A line that exists for its sound rather than its content gets cut. No metanarration either: "As to why nobody saw it, the Board's best reconstruction is almost stupidly mundane" announces the question and grades the answer before giving it. Write "The Board's best reconstruction is…" — if it is mundane, the mundanity will show.
- **The essay never mentions itself.** "That is the only sentence in this episode about that, and it is the reason there is an episode" — the essay defending its own scope. Cut it; the content stands on its own. No "this episode", no "this essay", no defending restraint or tangents — if a tangent needs a defense, cut the tangent. No pacing commentary either ("this is the part where…, so I will be quick") — if a section drags, shorten it.

## Before any audio

Run the AI-tell removal procedure (`references/ai-tells.md`) on the finished Markdown draft — multi-pass, with the metrics script, plus the independent fact-check pass it describes. Do it before `essay_to_segments.py`: fixing prose after generation wastes all the TTS compute.
