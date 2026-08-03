# Removing AI tells from essay prose

Run this procedure on every researched essay — sleep or casual — after the draft is finished and before any audio is generated. It is a multi-pass procedure with measurements, not a "polish" prompt. Everything here comes from one real production run; the numbers are measured.

## The lesson to lead with

**Each pass removed a tell and the tell came back wearing different clothes.**

- Pass 1 killed the lexical tells (`delve`, `underscore`, `tapestry`). Cheap, and worth the least.
- Pass 2 cut paragraph-final zingers "from 31 to 6" — except the metric only counted multi-sentence paragraphs and missed standalone one-line paragraphs, which are the same tic with a spotlight on it. True figure: **31 of 53 paragraphs, 58%**.
- Pass 3 found that the kicker had not died at all. It had **swapped its full stop for a comma**: 43 sentences ran `[long clause], and [short flat coda]`, 20 of them paragraph-final. "…and he bought a body." "…and he said so." "…and it has gone almost unread." Same shrug, twenty times, on a metronome.

So: **run at least four passes, each hunting different ground, and re-measure after every one.** Tell each reviewer explicitly what earlier passes already fixed, or it will hand back the same list.

## Pass structure

1. **Lexical + mechanical.** Word blocklist, em dashes, curly quotes, negative parallelism (`not just X but Y`), participial tails (`, ...ing [significance]`). Grep-able. Do it fast, don't linger.
2. **Rhythm and cadence.** Kicker paragraphs, the comma-coda, sentence-length variance, repeated syntactic frames. This is where most of the tell lives.
3. **Structure and register.** Repeating analytical units, outline-shaped order, information density, name density, narrator infallibility, tonal monotony.
4. **Verify.** Re-run every metric; check you did not over-correct.

Run passes 2 and 3 as **adversarial subagent reviews** with a brief that says *assume the text is still machine-written and find what survived*. Ask for 25–40 concrete items with quote / problem / replacement, and ask flat out: **"if a skilled reader saw this cold, what would tip them off first?"** The best single finding of the whole source project came from that question.

## Metrics, with targets (per ~3,000 words)

Run `assets/tell_metrics.py essay.md` after every pass. Before → after from the source run:

| Metric | Before | After | Target |
|---|---|---|---|
| `[clause], and [≤10w coda]` | 43 | 17 | < 20 |
| …of those, paragraph-final | 20 | 5 | < 6 |
| Kicker paragraphs (incl. one-liners) | 58% | 24% | < 25% |
| Sentence-length stdev | 10.7 | 11.4 | **> 9** |
| Em dashes | 16 | 8 | 4–8 |
| Sentence-initial "The" | 30 | 17 | < 20 |
| Non-restrictive `, which` | 13 | 8 | < 9 |
| `a [profession] named [Name]` | 9 | 3 | ≤ 3 |
| `In YEAR, NAME VERBed` | 5 | 1 | ≤ 2 |
| Named individuals | 28 | ~20 | < 1 per 150 words |
| Sentences carrying no fact ("slack") | 2 | 6 | ≥ 4 |
| First person | 2 | 25 | **0** |
| AI vocabulary hits | — | 0 | 0 |

The script measures everything grep-able in that table (plus sentence openers, which expose repeated frames). Named individuals and slack sentences are judgment calls — count them in the pass-3 review, don't pretend a regex can.

## The structural tells worth naming explicitly

- **The repeating analytical unit.** "Term → scholar A reads it X → scholar B reads it Y → unresolved" ran **8 times**, and the same two scholars were staged as a matched pair **5 times**. Fix: introduce the recurring cast *once*, then either assert one reading flatly or refer to them generically. Keep 3 disputes, the ones with the best evidence and the highest stakes.
- **Outline order.** Discovery → language → method → content → object → provenance → conservation → conclusion is a filing cabinet, not a train of thought. Add 2–3 deliberate disruptions: move a description to the scene where someone is physically holding the thing; let a fact that invalidates earlier facts barge in early and get abandoned, then picked back up where it lands; move context to where it is needed rather than where it tidies up.
- **Zero slack.** 2 of 169 sentences carried no fact. Real speech has clauses that exist only to reach the next one. Add 3–4.
- **Name density.** 28 named people in 2,950 words, nearly all mentioned once with a credential appositive and a date. Nobody talking remembers that many.
- **The narrator never fails.** Add genuine friction — but never first-person friction; first person is banned outright (see the over-correction section). The friction lives in the structure instead: a gloss that lands two paragraphs after the term needed it, an abandoned thread picked back up late, a stated fact corrected in the open a sentence later, a section that visibly loses patience with its own subject and moves on.
- **Narrating what the essay is not.** "Everybody knows that crash… It is as good as people say, and this is not that story." Appealing to what "everybody knows", or naming an adjacent famous topic just to wave it off, is throat-clearing borrowed from someone else's essay. **Excise it, do not replace it** — no subtler rewording. What remains should be only what is actually in the essay.
- **The unattributed rumor.** "I have heard", "it is said", "some say", "legend has it". Either the claim is established — then state it flatly — or it is a persistent rumor worth engaging, in which case point at where it actually lives ("the New York Times described it as X") and correct it, and do even that only when the correction is load-bearing. Usually the right move is to not mention the false version at all.
- **The narrator's guess.** "Nobody writes down why two and not three; my guess is cost, because…" — remove the guess, keep the fact. If research produced a real, interesting reason, state the reason; if not, move on. Speculation staged as insight is filler with a confident voice.
- **Tonal monotony.** The deepest tell: one attitude applied to everything at identical strength. A death, a joke, a paywalled paper and a cat's head in a wreath all delivered at the same wry, level pitch. A human loses the register somewhere.
- **The composed ending.** Four fragments in descending length with the strangest item last is a drumroll. Consider moving that material to where a person would naturally mention it, and ending on something genuinely unresolved instead.

## Warn about over-correction

Adding friction, the source run pushed first-person from 2 to 25 instances — which is just a different tic, and one the house style now bans outright. **First person is excised entirely: the `tell_metrics.py` first-person count must read 0.** Friction comes from structure (late glosses, abandoned threads, open corrections), never from a narrator persona. **Re-measure what you added, not only what you removed.** The same watch applies to "And"-initial sentences, fragments, and self-correction.

## Narration-specific

Spoken text fails differently. Include in the passes:

- no initials in names (`L. B. van der Meer` becomes "ell-bee-van-der-meer");
- round numbers unless precision is the point;
- attribution before the claim, not after;
- name the noun instead of "this" or "these";
- long lists of foreign words are unlistenable — cut to three and say so;
- gloss some terms and not others, and gloss one late.

## Factual verification

Run an **independent fact-check subagent** over any researched script, briefed to verify load-bearing claims against sources rather than to admire the prose. On the source run it caught five outright errors that had survived a careful write, including a study whose finding was reported backwards and a claim off by an order of magnitude.
