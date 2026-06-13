# Writing a sleep essay

A **sleep essay** is a long-form audio essay on an obscure, research-level topic, written to be listened to while falling asleep. The point is not to teach efficiently — it's to be a calm, knowledgeable voice carrying the listener through a genuinely deep subject until they drift off. The same audio→video pipeline as the guided meditation produces the final artifact; this doc covers how to produce the *words*.

The deliverable is twofold: the essay itself **as a Markdown artifact** (the thing the listener can also read on screen), and the rendered video. Always produce the essay as an artifact/file, not just inline chat text.

## What makes a topic work: lore

The single criterion is **lore** — not mere obscurity, but layered depth that rewards a long, slow exploration. A topic has lore when it offers some mix of:

- a compelling **discovery narrative** — how did anyone figure this out? the detective work, the wrong turns, the lucky break;
- real **technical or scientific substance** — something with mechanism, math, or method underneath it, not just a curiosity;
- ongoing **scholarly controversy** — competing interpretations, a debate that isn't settled;
- a resonant **concluding insight** — the essay should land somewhere, reframing what came before.

Obscurity without depth is not enough. "Here's a weird thing that exists" is a dead end; "here's a weird thing, and the story of how it was understood is a 30-minute rabbit hole with an argument at the bottom" is a sleep essay.

Recent breakthroughs (roughly **2015–2025**) are especially prized, particularly ones that *reframe* older knowledge — a new dating method overturning a chronology, a re-reading of an inscription, a mechanism finally explained.

## Topic domains

The reliable veins, in rough order of strength:

- **The Ancient Near East** — the consistent sweet spot. Inscriptions, scripts, calendars, metallurgy, scribal practice, archaeology.
- **Mathematics** and the **history of science** — old methods reconstructed, lost techniques, the genealogy of an idea.
- **Religious studies** — textual history, ritual calculation, manuscript traditions.
- **Technology history** and deep computer-science topics — algorithms with a story, engineering knowledge that was lost or compartmentalized.

History need not be the Ancient Near East — other times and places can be fascinating — but it does need genuine lore.

### Example pitches (the right register)

These convey the scholarly angle and a recent development in 2–3 sentences, intriguing without needing full verification up front:

- **Quorum quenching** in bacterial communities — not the now-familiar quorum *sensing*, but the active disruption of bacterial communication by other organisms producing enzyme inhibitors. An arms race conducted in chemistry.
- Deep-sea bacteria that appear to use **quantum coherence** in photosynthesis under near-zero light.
- **Tyrian purple** and the recent finding that murex were harvested on specific lunar cycles because dye concentration tracks the mollusk's reproductive timing.
- Medieval Islamic **prayer-time calculation** by shadow-stick measurements that varied by exact latitude and season — requiring spherical trigonometry.
- **Chronostatic ions** in glass: ions temporarily frozen in place during formation, producing materials with memory effects.
- **Mycelial networks** performing analog computation through hydraulic pressure changes.
- The Javanese gamelan **slendro** tuning: intervals that don't map to equal temperament, creating culturally meaningful beat frequencies acoustically invisible to untrained ears.

## The workflow

1. **Pitch a batch.** When asked for ideas, produce a numbered list of **20–30** pitches, each a 2–3 sentence hook in the register above. Pitches can be speculative — verification happens later — but each must promise lore, not just oddity. Spread them across the domains.
2. **Selection.** The person picks one (or asks for another batch).
3. **Research the chosen topic** before writing (see below).
4. **Write the full essay** as a Markdown artifact.
5. **Render to video** via the pipeline (see "Feeding the pipeline").

### Don't repeat covered topics

Already done — do not pitch or re-write these without being asked:

> the Copper Scroll · the Deir ʿAlla inscription · the Umm el-Marra alphabet · the Tel Dan inscription · Babylonian proto-calculus (the Jupiter trapezoid method) · the Elephantine papyri · the medieval Hebrew calendar · the Proto-Sinaitic alphabet · the Hallstatt Plateau radiocarbon problem · the Jerusalem Givati moat · the Caremark corporate-law doctrine · line-of-sight algorithms in roguelikes · Timsort / Powersort · Greek fire

Keep this list current as new essays are finished.

## Research strategy

Search **before** writing, both for inspiration and to verify specifics. The patterns that work:

- **Many targeted queries beat one broad one.** Fire several narrow searches rather than a single general one.
- **Combine scholar names + technical terms + discovery years.** This is the most reliable way to surface actual academic sources rather than popularizations. E.g. a site name plus an excavator's surname plus "2019"; a method's technical name plus the mathematician who reconstructed it.
- **Go general → specific progressively.** Start wide to find the names and terms, then re-search with those to reach the primary scholarship.
- Verify the load-bearing claims — the surprising reversal, the specific date, the mechanism — at this stage. The pitch could be a speculative hook; the essay should not be.

## Essay craft

- **Length: 15+ minutes read aloud**, which in practice means roughly **4,000–6,000+ words**. At a calm narration pace (~140 words/min) 4,000 words already runs ~28 minutes, so hitting that word range clears the 15-minute floor with room to spare. Err long; this is for falling asleep, not for efficiency.
- **Flowing narrative prose, not academic structure.** No headers-as-outline, no bullet lists, no "in this essay I will." Write it as one continuous telling that moves from a hook through the substance to a closing insight. It should read aloud as a single calm voice thinking through a subject.
- **Structure the journey, not the document.** Open with a concrete, intriguing entry point (an object, a moment, a puzzle). Move into the discovery narrative and the technical substance. Air the scholarly debate. Close on the resonant insight that recasts the whole thing.
- **Calm, even register.** Long, smooth sentences. Few exclamations. Nothing jarring or suspenseful enough to wake someone — the goal is absorbing, not gripping. Curiosity, not cliffhangers.
- **Write for the ear.** Spell out symbols and numbers as words where a reader would stumble; prefer commas and periods to dashes and parentheticals; avoid constructions that only parse on the page (tables, footnotes, "see above").

## Feeding the pipeline

A sleep essay is **continuous narration** — the opposite of a meditation's silence-heavy pacing. So the conversion to the pipeline's segment format uses small, natural pauses, not long meditative gaps.

1. Write the essay to a Markdown file (this is also the artifact you present).
2. Convert it to a segments JSON with the helper:

   ```bash
   python3 assets/essay_to_segments.py essay.md --out essay.json \
       --voice af_heart --speed 0.9 --sentence-pause 0.5 --paragraph-pause 1.4 --tail 4
   ```

   It strips Markdown, splits the prose into one segment per sentence (so generation stays chunked and resumable), and inserts a short beat after each sentence and a slightly longer one between paragraphs. It prints the word count and an estimated read time so you can check the 15-minute floor.

3. Run the normal pipeline on `essay.json`: `generate_segments.py` → `build_audio.py` → choose image → `render_video.py`.

Differences from a meditation render, worth setting deliberately:

- **Voice/pace:** a warm, even voice at `speed` ~0.9. `af_heart` works; a lower male voice (e.g. `am_onyx`) suits some listeners for sleep.
- **No wake-up ending.** A meditation ends by telling the listener to return to their day; a sleep essay must *not*. Let it simply conclude and trail off. Use a longer audio fade-out so it dissolves rather than stops: `render_video.py ... --audio-fade-out 4`.
- **Image:** a dark, dim, low-stimulation backdrop (night sky, dark water, candlelight) so a phone screen left on doesn't light up the room.
- **Generation is the long pole.** Tens of minutes of audio is a lot of TTS; on CPU it's several minutes of compute. The generator is resumable, so just run it repeatedly until every segment is on disk.
