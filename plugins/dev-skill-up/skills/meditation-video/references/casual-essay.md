# Writing and producing a casual essay

A **casual essay** is a long-form narrated documentary for someone who is awake — "something to put on while eating or doing the dishes." It rides the same Kokoro + ffmpeg pipeline as the sleep essay. Three things differ: normal speaking speed, many images instead of one, and diagrams.

Everything in this file is field-tested from a real 20-minute production run. The numbers are measured, not estimated. The **GOTCHA** blocks matter more than the prose around them — each one silently produced a wrong result that looked right.

Deliverables for a run: the essay Markdown (as an artifact), the MP4, and the publishing metadata (`youtube-description.txt` + `youtube-tags.txt` — see `references/publishing-metadata.md`), all sent together.

## The words

Topic selection, research strategy, the kill criterion ("no story, no essay"), and the six hard house rules are shared with the sleep essay — **read `references/essay.md` first**. This section covers only what is casual-specific.

### Settings that actually worked

```bash
python3 assets/essay_to_segments.py essay.md --out essay.json \
    --voice af_heart --speed 1.0 \
    --sentence-pause 0.6 --paragraph-pause 2.2 --lead-in 0.5 --tail 4
```

Then edit `essay.json` and bump the **title segment's pause to ~2.8** so the title reads as a title, not the first sentence of a paragraph.

### Length calibration — measured, use this instead of guessing

At `speed 1.0` with those pauses: **2,999 words → 20:25** (1,025 s speech + 200 s silence). That is ~175 wpm of raw speech and ~147 wpm effective. The read-time estimate `essay_to_segments.py` prints assumes the sleep-essay pace (110 wpm at `speed 0.7`) unless you pass `--wpm 147`, so at speed 1.0 it overshoots badly — use this calibration instead.

- For 20–25 minutes, write **2,900–3,600 words**.
- **Prefer widening pauses over padding prose** when you land short. Going from 0.55/1.9 to 0.65/2.4 bought 60 s on a 3,150-word script.
- If you must add length, add *content* (a comparison object, a source's own argument), never filler. A cut-then-repad cycle is normal: one rewrite dropped 400 words and ~200 went back as new material.

### Register

Awake listener. Real narrative tension is fine — this is not a lullaby. Still flowing prose: no headers, no bullets, no lists read aloud. The six hard house rules in `references/essay.md` apply in full.

The voice itself is **per-project: read it out of the user's brief**, and where the brief and anything in this file conflict, the brief wins. The source run's brief was a channel premised on deference to the investigation's report; the register hardcoded here fought it for the whole script and nothing reconciled them. Absent any signal in the brief, the default is wry, grounded in facts, and willing to leave a genuinely open dispute unresolved — one essay has no room for staged back-and-forth, and accuracy beats attitude wherever the two compete.

### Before any audio

Run the AI-tell **convergence loop** in `references/ai-tells.md`. Do not compress it into "run the passes and the script" — that compression is what once produced two subagent calls total, with structure folded into an open question at the end of the rhythm brief, and a dozen shipped defects. Concretely:

- **It is a loop, not a pipeline.** Any finding from any pass → fix it → run every pass again from the top. The procedure is complete only when one full cycle returns zero findings from every pass.
- **The gate is hard — and mechanical.** Audio generation is blocked until a cycle comes back clean: write that cycle's verdicts to `passes.json`, because `generate_segments.py` demands it (`--passes`) for any essay-derived script and verifies all nine passes are present with zero findings. A pass that has not run in that final clean cycle has not run — and has no verdict to record. Never edit the scripts to get past the gate.
- **These reviews are separate subagents, each cycle they run:** rhythm (2), structure (3a), register (3b), comprehension (4), the cold read (5), and the fact-check (6). None may be folded into another's brief.
- **Bulk edits — first-person excision, the cut pass, hitting the word count — happen before the reviews within a cycle, never after.** Late compression to reach a length target is how the worst line in the source run shipped unreviewed.

The loop and the fact-check both matter more at documentary register than at sleep register, because the listener is awake and paying attention.

## Visuals

**Target: a new picture every 30–60 s, cued to a sentence boundary.** For 20 minutes that is ~30 shots. Mix photographs with original diagrams; 7 diagrams in 30 shots felt right. Sourcing and licensing for the photographs is its own discipline — read `references/image-sourcing.md` before sourcing anything: **tier A (no obligation) is the only allowable tier, and there is nothing to ask the user**.

### Time every cue off the real audio, never off a clock

Sum the actual WAV durations plus each segment's pause to get every segment's exact start, then pin shots to segment indices. A picture that changes mid-sentence reads as broken. The helper the tooling shares (`assets/seg_times.py`):

```python
def segment_start_times(spec_path, workdir):
    spec = json.load(open(spec_path)); t = float(spec.get("lead_in", 0.5))
    starts = []
    for i, seg in enumerate(spec["segments"]):
        info = sf.info(os.path.join(workdir, f"seg_{i:03d}.wav"))
        starts.append(t)
        t += info.frames / info.samplerate + float(seg.get("pause", 0))
    return spec, starts, t + float(spec.get("tail", 0.8))
    # lead_in/tail defaults mirror build_audio.py, so the computed total
    # matches the stitched WAV sample-for-sample
```

`assets/render_slideshow.py` (shots) and `assets/make_metadata.py` (chapters) both read times from this same function, so picture changes and chapter marks always agree with the narration.

### Shot selection: anchors + greedy fill

Hand-fitting 30 gaps is miserable and you will get it wrong. Instead:

- Pin the shots that *must* land on a specific sentence — every diagram, plus any photo whose subject is named right there — as **anchors**.
- Supply a deliberately **over-dense candidates pool** (more plates than gaps, each cued to the segment where it's relevant).
- Let a greedy selector fill each gap so no shot is under 30 s or over 60 s. It rejects a candidate whose plate equals the previous shot's.

`assets/render_slideshow.py` implements exactly this: give it `{"anchors": [...], "candidates": [...]}`, run it with `--select-only` first, and it emits the resolved shot list.

> **GOTCHA — the selector will silently drop your most important images.** It optimises spacing, not meaning. On the source run it twice dropped *both* plates of the actual manuscript from a film about that manuscript. **Always diff used plates against available plates and eyeball the list before rendering.** The script prints the unused-plate list loudly; actually read it.

## Plates: no letterbox bars, no blurred fill

Blurring a copy of the image to fill the frame looks cheap. `assets/make_plates.py` builds two honest styles instead:

- **Full-bleed (most images).** Scale to *cover* 1920×1080 with ~12% margin. The renderer crops a moving 1920×1080 window out of it, travelling along whichever axis has slack: a tall image tilts, a wide one pans, one with slack both ways drifts. Nothing is lost — whatever is off-frame arrives later in the shot. Alternate direction so consecutive shots never move the same way.
- **Split panel (a few).** When an image cannot fill the frame honestly — over ~1.25× upscale, or so tall a 16:9 crop shows a sliver — put the picture at full height in a right-hand column and a caption panel on the left, in the same type and palette as the diagrams. Make the caption carry a real fact so the screen is doing work rather than apologising — but a *label-length* fact (a name, a date, an attribution, one line of context), never sentences. The narration owns the prose; see "On-screen text is labels, not prose" below.

Two motion rules the renderer enforces, and why:

- **Cap the travel rate at ~32 px/s.** Without it a 3.9:1 image panned over 33 s moves at 85 px/s and the frame looks like it is hunting. Travel `span = min(slack, MAX_RATE * duration)`, centred on the leftover.
- **Diagrams and split panels must be perfectly static.** Any drift makes text crawl. Gate on plate size, not just a flag: `if static or (w <= 1930 and h <= 1090)`.

## Rendering

One ffmpeg pass: N looped image inputs → per-input `crop` → `xfade` chain → mux narration. Not two passes; one encode of 20 minutes is enough work. `assets/render_slideshow.py` builds and runs the whole thing; the mechanics (why constant-size `crop` beats `zoompan` 3× on encode time, the exact xfade clip-length and offset math, and the kill/verify gotchas) are in `references/kokoro-and-ffmpeg.md` — read that before debugging a render.

Settings that worked: **20 fps** (slideshow, no real motion), `-preset veryfast -crf 21`, `xfade` **1.6 s**, video fade in 2 s / out 3 s, audio fade out 3 s.

**Cost: ~1.15× realtime.** A 20-minute video takes ~23 minutes to render. Budget for it and **start it before you write the credits** — the metadata work fits inside the render window.

## Diagrams

Original SVG rendered with `cairosvg` at 1920×1080 is the highest-value visual in the whole video: always free of licensing questions, always exactly on topic, and it explains things a photograph cannot. Build them from one small helper so they share a palette and type. What worked:

- dark warm ground (`#14110e`), warm off-white text;
- one accent colour drawn from the subject itself;
- serif for content and sans for labels, a rule under every title.

### On-screen text is labels, not prose

The narration owns the sentences. The screen owns what a spoken voice handles badly: names, dates, numbers, spellings, and structure. A viewer cannot read one text while listening to another, so a plate whose body is a paragraph — even a well-written one, even a true one — does nothing except make the frame busy and compete with the voice.

The test is the title card. **"Francis Baily, 1774–1844" over a rule is a complete card.** Adding a sentence summarising what the narration is saying at that moment makes the card worse, not fuller. A real production run shipped exactly that failure: a name-and-dates card padded with a three-line paragraph restating the narration. Cut to the label.

The same test kills fake diagrams: if a "diagram" has no structure to show — no axis, no map, no flow, no comparison, just sentences on the house palette — it is not a diagram, it is a paragraph in costume. Either find the structure the fact actually has (dates want a timeline, a quantity wants a chart, a claim-vs-claim wants two columns of *labels*) or give the shot to a photograph instead.

For any chart, read the `dataviz` skill first. Its interactive guidance does not apply to a video frame, but the transferable rules do: pick the form from the data's job, single hue for magnitude with one emphasis colour, direct labels instead of a legend, recessive grid, never a dual axis.

> **GOTCHA — always render every SVG to PNG and actually look at it.** First pass of 7 diagrams had: labels colliding with a timeline axis, tick marks pointing at the wrong words, city names overlapping on a map, text overflowing a box, a caption buried under a graphic, and multiple spaces collapsed (use the `letter-spacing` attribute, never padded spaces). None of it was visible from the code. A second cairosvg trap — it silently ignores font fallback lists — is in `references/kokoro-and-ffmpeg.md`.

## Delivery

`SendUserFile` caps at **30 MiB**, which a 20-minute 1080p master blows past (133 MB at CRF 21) — expect this every run, not occasionally. Two-pass compress:

```bash
ffmpeg -y -i master.mp4 -c:v libx264 -preset medium -b:v 125k -pass 1 -an -f null /dev/null
ffmpeg -y -i master.mp4 -c:v libx264 -preset medium -b:v 125k -pass 2 \
       -c:a aac -b:a 40k -ac 1 -movflags +faststart delivery.mp4
```

That yielded **24.8 MiB for 20:25**, and it holds up because slideshow content with dark diagram frames compresses extremely well. The 125k was tuned for that runtime; for a different one, pick `b:v ≈ (26 × 8192 ÷ duration_seconds) − 40` kbps — that targets ~26 MiB total (video + 40k audio) with margin under the cap. Before sending:

1. **Verify diagram text is still crisp** on a sampled frame (`ffmpeg -ss <t> -i delivery.mp4 -frames:v 1 check.png` on a diagram shot, then look at it).
2. **Full-decode both master and compressed output** — `ffmpeg -v error -i out.mp4 -f null -`; `ffprobe` will not catch corruption (see the gotcha in `references/kokoro-and-ffmpeg.md`).

Send the compressed file, mention the master exists, offer to split it or write it to disk. Deliver `youtube-description.txt` and `youtube-tags.txt` in the same call — they are required, not optional (`references/publishing-metadata.md`).

## Data flow

```
essay.md ─(ai-tells convergence loop; clean cycle ──> passes.json)─> essay.md (final)
essay.md ──> essay_to_segments.py --speed 1.0 ──> essay.json (title pause → 2.8)
essay.json + passes.json ──> generate_segments.py --passes passes.json
        ──> work/seg_*.wav ──> build_audio.py ──> essay.wav
images_raw/ ──> make_plates.py ──> plates/ + plates manifest
essay.json + work/ + shots.json (anchors+candidates) ──> render_slideshow.py
        ──> shots.resolved.json + master.mp4 ──> compress ──> delivery.mp4
shots.resolved.json + credits.json + meta.json ──> make_metadata.py
        ──> youtube-description.txt + youtube-tags.txt
```
