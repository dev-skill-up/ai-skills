---
name: meditation-video
description: 'Produce narrated spoken-word audio and video — a warm voice over one or many still images — entirely offline with open-source tools (Kokoro TTS + ffmpeg, no API key or GPU). Three content modes: guided meditations (mindfulness, breathing, body scan, sleep meditation), sleep essays (long-form narrated deep-dives on obscure topics, written to fall asleep to), and casual essays (awake ~20-minute documentaries over researched, licence-verified images and original diagrams, with YouTube description/chapters/tags). Use whenever someone wants to create or narrate anything calming or sleep-related — or a documentary, video essay, explainer, or narrated slideshow on a researched topic. Trigger on "guided meditation," "meditation video," "relaxing/calming/soothing audio or video," "breathing exercise," "sleep meditation," "sleep essay," "audio essay to fall asleep to," "bedtime narration," "narrate this script/essay," "documentary," "video essay," or "explainer video."'
---

# Meditation Video

Make narrated spoken-word videos: a warm voice over still imagery, rendered as a portable MP4. Everything runs locally with open-source tools — Kokoro for the voice, ffmpeg for the video. No API keys, no GPU, no per-minute cost.

## Three content modes

The audio→video machinery (generate narration → stitch in pauses → render over imagery) is shared. What differs is the words, the pacing, and the pictures. Pick the mode from what the person wants, and read the matching craft reference before writing:

- **Guided meditation** — mindfulness, breathing, body scan, relaxation, sleep meditation. Short cues separated by long, deliberate silence. The defining belief: **the silence is the content** — the words are scaffolding around the spaces where the listener actually meditates, so a good one is mostly quiet (speech fills only ~a third of the runtime). Craft guide: `references/meditation-script-craft.md`.
- **Sleep essay** — a long-form (15+ minute) narrated deep-dive on an obscure, "lore"-rich topic, written as flowing prose to fall asleep to. The opposite pacing: **continuous narration** with only small natural pauses, over a single dark backdrop. Requires researching the topic first and delivering the essay as a Markdown artifact. Craft guide: `references/sleep-essay-craft.md`.
- **Casual essay** — a narrated documentary for someone who is **awake**: "something to put on while eating or doing the dishes." Same continuous narration, but at normal speaking speed, over **many images and original diagrams** — a new picture every 30–60 seconds, cut on sentence boundaries. Wry, argumentative, allowed real tension. Craft guide: `references/casual-essay.md`.

The pipeline steps below are written for a meditation; the **"Sleep essays"** and **"Casual essays"** sections near the end cover where each flow differs. Setup, generation, and audio assembly are identical everywhere.

## When to run this vs. just talking

If the person only wants *the script* (the words), you can write that directly — see the matching craft reference — and skip the audio/video machinery. Run the full pipeline when they want a produced artifact: narrated audio or a video.

Settle a few specifics from the request itself — **do not stop to ask the user questions; this skill runs completely autonomously**. Take what the request already says and fall back to the defaults below:

- **Length** — 5 minutes is the meditation default; essays run 15–25+.
- **Theme/style** — mindfulness/breath, body scan, sleep, loving-kindness, anxiety relief — or, for essays, the topic and the register.
- **Voice** — female or male, and any accent. Default `af_heart` (American female) is the warmest. Full roster in `references/kokoro-and-ffmpeg.md`.
- **Backdrop** — a vibe for the still image (misty lake, night sky, candle). For a casual essay there is no licence question to ask: **tier A (no obligation) is the only allowable tier, always** — see `references/image-sourcing.md`.
- **Audio-only or video** — some people just want the MP3/WAV.

## The pipeline

The assets in `assets/` do each stage. They're CLI scripts; run them with the Bash tool. All of them are safe to re-run.

### 0. Set up Kokoro (once per environment)

```bash
bash assets/setup.sh .       # installs kokoro-onnx + onnxruntime, downloads model + voices
```

This uses the **ONNX build of Kokoro on purpose** — it runs the same Kokoro v1.0 weights through onnxruntime instead of PyTorch, avoiding a ~400MB torch install and any GPU requirement. The model download is ~310MB and is resumable. Details and rationale: `references/kokoro-and-ffmpeg.md`.

### 1. Write the script as JSON

A meditation script here is a list of `{ "text": ..., "pause": <seconds> }` objects plus a little metadata. Copy `assets/meditation.example.json` (a full, tested 5-minute mindfulness script) and adapt it, or write a fresh one. The data format:

```json
{
  "voice": "af_heart", "speed": 0.9, "lang": "en-us",
  "lead_in": 0.5, "tail": 0.8,
  "segments": [ { "text": "Find a position that feels comfortable.", "pause": 3 } ]
}
```

Read `references/meditation-script-craft.md` before writing — it covers the arc, the two pause lengths (≈3s short, 7–30s long) and when to use each, the audience calibration, and the two easy-to-miss rules: **start almost immediately** (tiny `lead_in`) and **end with an explicit spoken close**, not trailing silence, so the listener knows when to get up. `speed: 0.9` slows the voice slightly, which reads as calmer. A segment may also carry its own `"speed"`, overriding the top-level one — that's how a meditation section spliced into a sleep essay keeps its own pace.

### 2. Generate the narration segments

```bash
python3 assets/generate_segments.py meditation.json --workdir work
```

One WAV per line, into `work/`. It's resumable — already-rendered lines are skipped — so if it's interrupted, just run it again. Generation is CPU-only at several times real-time.

For essay-derived scripts this command also enforces the de-AI gate: it demands `--passes passes.json`, the verdicts of the final clean ai-tells cycle, and refuses to generate otherwise (see the essay sections below). **Never edit the script to loosen that check** — if it blocks, the loop isn't done.

### 3. Stitch in the silence

```bash
python3 assets/build_audio.py meditation.json --workdir work --out meditation.wav
```

Concatenates the segments with exact digital silence from each `pause` value, plus the lead-in and tail. It prints the total duration and the speech-to-silence ratio — glance at that ratio; if silence is well under ~55% the meditation is probably too talky. **This WAV is the audio-only deliverable** if that's all they wanted.

### 4. Choose and fetch a backdrop image

```bash
bash assets/fetch_image.sh image.jpg "https://images.unsplash.com/photo-<id>?w=1920&h=1080&fit=crop&q=80"
```

Pick a deliberately calm, low-contrast, slow scene — the image sets the mood before a word is spoken. For this single-backdrop case, Unsplash CDN direct URLs and `https://picsum.photos/1920/1080` are fine. Aim for 1920×1080. (A casual essay sources ~30 topical images instead — that whole discipline, licence tiers included, lives in `references/image-sourcing.md`.)

### 5. Render the video

```bash
python3 assets/render_video.py image.jpg meditation.wav --out meditation.mp4
```

Produces an H.264/AAC MP4 with gentle fade-in/out and an audio fade that lands in the trailing silence (never over a word). It deliberately renders at a low frame rate because the image is static — that keeps a 5-minute encode down to a few seconds. See `references/kokoro-and-ffmpeg.md` for every flag and why it's there. (Casual essays use `assets/render_slideshow.py` instead — a multi-image dissolve chain with slow pans.)

### 6. Verify and deliver

Confirm the output before handing it over: check the duration matches expectations and that it actually plays. `ffprobe` catches the basics; a **full decode** is the only thing that catches real corruption:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height \
  -of default=noprint_wrappers=1 meditation.mp4
ffmpeg -v error -i meditation.mp4 -f null -   # silence means clean
```

Then present the file to the person. **For either essay mode, the video alone is not the deliverable**: also emit `youtube-description.txt` and `youtube-tags.txt` (see step 7) and send them in the same delivery (the same `SendUserFile` call) as the MP4. Offer the obvious next tweaks — different voice, more or less silence, a different backdrop — since each is a one-line change and re-render.

### 7. Publishing metadata (required for essays)

Any sleep-essay or casual-essay run must produce **`youtube-description.txt`** (hook, chapters generated from real narration timings, sources, image credits — under 5,000 characters) and **`youtube-tags.txt`** (under 500 characters, most specific first). Generate them with `assets/make_metadata.py` — never by hand, or they drift from the video on the next re-render. A casual essay feeds it the shot list and credits manifest; a sleep essay has neither and runs it without them, with the backdrop credit in `meta.json`. The description is about the video's **subject only** — no pipeline or tool info, no describing the essay's own methodology, no licence statements or reuse grants, no "no stock footage / no music" inventory; credits credit what was used, nothing more. The full spec is `references/publishing-metadata.md`. This step was forgotten once and had to be asked for; treat it as part of rendering, not an extra.

## Iterating

Every dial is in the JSON or a CLI flag, so changes are cheap. Re-rendering reuses the already-generated segments unless their text changed:

- **Different voice or pace** → edit `voice` / `speed`, delete `work/`, regenerate.
- **Adjust a single pause** → edit that `pause`, skip generation, just re-run `build_audio.py` and `render_video.py` (the silence is added at build time, so no regeneration needed).
- **Different image** → re-fetch and re-run `render_video.py` only.
- **Hit a target length** → tweak the longer pauses (the open-awareness rest is the easiest place to add or remove time) and rebuild.

## Sleep essays

A sleep essay rides the same machinery but differs in mode: continuous narration instead of silence, and a research-and-write step up front. **Read `references/essay.md` first** (the shared topic workflow, research strategy, kill criterion, and house rules), then `references/sleep-essay-craft.md` (the "lore" criterion, topic domains, already-covered topics, and how to write flowing prose for the ear).

The flow:

1. **Research, then write** the essay (15+ minutes read aloud, ~4,000–6,000+ words of flowing prose) and save it as a Markdown file. **Present this Markdown as an artifact** — it's a primary deliverable the person also reads on screen, not just the video's soundtrack.
2. **De-AI the prose and fact-check it.** A researched essay written in one pass reads machine-written in ways you cannot see from inside. Run the convergence loop in `references/ai-tells.md` — every pass re-run from the top after any fix, with its metrics script and the independent fact-check it describes, until one full cycle returns zero findings. When that clean cycle exists, write its structured verdicts to `passes.json` (format in `references/ai-tells.md`) — audio generation is mechanically gated on that file: `generate_segments.py` checks that all nine passes are present and clean, and refuses to run without it. **Do not edit the scripts to get around the gate, and do not write a verdict for a pass that didn't run** — a blocked gate means more cycles, nothing else.
3. **Convert the essay to a segments file** — this is the one extra step versus a meditation. Instead of hand-authoring the JSON, run:

   ```bash
   python3 assets/essay_to_segments.py essay.md --out essay.json \
       --voice af_heart --speed 0.7 --sentence-pause 0.5 --paragraph-pause 1.4 --tail 4
   ```

   `--speed 0.7` is the sleep-essay setting. The script strips Markdown, splits the prose into one segment per sentence (keeping generation chunked and resumable), inserts small pauses, and prints the word count and estimated read time so you can confirm the 15-minute floor. It also stamps the JSON `"passes_required": true` — the marker `generate_segments.py` uses to enforce the audio gate.

   **If the video includes a relaxation/meditation section** (e.g. a body relaxation before the essay), that section is a meditation, not essay prose: keep it out of the essay Markdown, write it per `references/meditation-script-craft.md` with **real silences** (`pause` values, not filler) and **its own per-segment `"speed"`**, and splice its segments into the JSON — see `references/sleep-essay-craft.md`.
4. **Run the shared pipeline** on `essay.json`: `generate_segments.py essay.json --passes passes.json` → `build_audio.py` → fetch image → `render_video.py`. Deliberate differences at render time:
   - **No wake-up ending and a longer dissolve** — a sleep essay must not tell the listener to return to their day; let it trail off. Pass `--audio-fade-out 4` (or more) to `render_video.py`.
   - **A dark, dim backdrop** (night sky, dark water) so a phone left playing doesn't light the room. Fetch it from Unsplash via `assets/fetch_image.sh` — never generate one — and **randomize the pick** among several fitting candidates (`shuf`), like the topic draw.

   Note that generation is the long pole here — tens of minutes of audio is minutes of CPU compute — but the generator is resumable, so just re-run it until all segments exist.
5. **Verify with `ffprobe`** (plus a full decode, step 6 above) that the MP4 plays and the duration comfortably clears 15 minutes.
6. **Emit the publishing metadata** (step 7 above) and deliver the Markdown essay, the MP4, and the metadata files together in one `SendUserFile` call so all of them are downloadable from the session.

## Casual essays

A casual essay is the **awake** documentary: same Kokoro + ffmpeg pipeline, three differences — normal speaking speed, many images instead of one, and original diagrams. **Read `references/essay.md` first** (the shared topic workflow, research strategy, kill criterion, and house rules), then `references/casual-essay.md`; it carries the measured numbers (length calibration, shot cadence, render cost) and the gotchas that silently produce wrong-looking-right results. The flow, briefly:

1. **Research and write 2,900–3,600 words** for a 20–25 minute video (`references/casual-essay.md`). Image licensing is fixed and never asked about: **tier A (no obligation) only** (`references/image-sourcing.md`).
2. **De-AI and fact-check** the script (`references/ai-tells.md`) before generating audio, and write the clean cycle's verdicts to `passes.json` — the gate `generate_segments.py` enforces.
3. **Segments at speed 1.0**: `essay_to_segments.py --speed 1.0 --sentence-pause 0.6 --paragraph-pause 2.2 --lead-in 0.5 --tail 4`, then bump the title segment's pause to ~2.8. Generate with `generate_segments.py essay.json --passes passes.json` and build audio as usual.
4. **Source ~30 images and build ~7 diagrams**, verify every licence (`references/image-sourcing.md`), make plates with `assets/make_plates.py`.
5. **Plan shots and render** with `assets/render_slideshow.py` — anchors + greedy fill, cues timed off the real WAVs, one ffmpeg pass at ~1.15× realtime, so **start the render before you write the credits**. Eyeball the used-vs-unused plate diff before rendering.
6. **Generate metadata** with `assets/make_metadata.py`, verify with a full decode, compress under the 30 MB delivery cap, and deliver MP4 + description + tags together.

## References

- `references/meditation-script-craft.md` — guided-meditation words and silence: structure, pacing, audience, sources.
- `references/essay.md` — craft shared by both essay types: the topic workflow (seed with web searches → pitch 50 → randomized draw from the bottom half → research → write → render, restart on discard), research strategy, the "no story, no essay" kill criterion, the six hard house rules, and the pre-audio de-AI/fact-check requirement.
- `references/sleep-essay-craft.md` — sleep-essay craft: the "lore" criterion, topic domains and examples, topics already covered, writing prose for the ear, the 0.7 narration speed, the randomized Unsplash backdrop, and how to splice in a relaxation/meditation section (real silences, own speed).
- `references/casual-essay.md` — the awake documentary: register, measured length calibration, shot cadence and selection, plate styles, diagram craft, render settings and costs, delivery under the size cap.
- `references/image-sourcing.md` — sourcing 30 topical images honestly: tier A (no obligation) as the only allowable tier — never ask — plus tier-A techniques, verified sources, Commons API resolution, SHA-1 provenance checks, and what to do when no honest image exists.
- `references/ai-tells.md` — removing machine-written tells from essay prose: the convergence loop and its hard audio gate (enforced by `generate_segments.py` via the `passes.json` report), the destructive excision and cut passes, the adversarial/cold review passes, `assets/tell_metrics.py` with measured targets, the structural tells, over-correction, narration-specific rules, and the fact-check pass.
- `references/publishing-metadata.md` — the required description/chapters/tags deliverables: structure, hard limits, what never goes in a description (pipeline info, methodology self-description, licence statements), credits-are-just-credits rules, and generating it all with `make_metadata.py` so it never drifts.
- `references/kokoro-and-ffmpeg.md` — the technical layer: Kokoro ONNX setup, the full voice roster, the still render and the slideshow render (crop-vs-zoompan, xfade math, render costs), process-kill and verification gotchas, cairosvg gotchas.
