---
name: meditation-video
description: Produce calm spoken-word audio and video for relaxation and sleep — a warm narration over a single still image — entirely offline with open-source tools (Kokoro TTS + ffmpeg, no API key or GPU). Two content modes: guided meditations (mindfulness, breathing, body scan, relaxation, sleep meditation) and sleep essays (long-form narrated deep-dives on obscure topics, written to fall asleep to). Use whenever someone wants to create or narrate anything meant to calm, relax, soothe, or help someone fall asleep: a guided meditation, relaxation or breathing audio, a calming/relaxing audio or video, a sleep/mindfulness track, a bedtime or sleep audio essay, ambient "talk over a calm picture" content, or turning a meditation script or written essay into narrated audio or an MP4. Handles the whole pipeline: writing or refining the words with the right pacing, generating natural narration with Kokoro text-to-speech, stitching in pauses, choosing a backdrop image, and rendering a shareable MP4 with ffmpeg. Trigger on "guided meditation," "meditation video," "relaxation/calming/relaxing/soothing audio or video," "breathing exercise audio," "sleep meditation," "sleep essay," "audio essay to fall asleep to," "bedtime narration," or "narrate this script/essay."
---

# Meditation Video

Make calm, narrated spoken-word videos: a warm voice over a single still image, rendered as a portable MP4. Everything runs locally with open-source tools — Kokoro for the voice, ffmpeg for the video. No API keys, no GPU, no per-minute cost.

## Two content modes

The audio→video machinery (generate narration → stitch in pauses → render over an image) is shared. What differs is the words and the pacing. Pick the mode from what the person wants, and read the matching craft reference before writing:

- **Guided meditation** — mindfulness, breathing, body scan, relaxation, sleep meditation. Short cues separated by long, deliberate silence. The defining belief: **the silence is the content** — the words are scaffolding around the spaces where the listener actually meditates, so a good one is mostly quiet (speech fills only ~a third of the runtime). Craft guide: `references/meditation-script-craft.md`.
- **Sleep essay** — a long-form (15+ minute) narrated deep-dive on an obscure, "lore"-rich topic, written as flowing prose to fall asleep to. The opposite pacing: **continuous narration** with only small natural pauses. Requires researching the topic first and delivering the essay as a Markdown artifact. Craft guide: `references/sleep-essay-craft.md`.

The pipeline steps below are written for a meditation; the **"Sleep essays"** section near the end covers the one place the flow differs (how the essay becomes a segments file). Everything else — setup, generation, image, render, delivery — is identical.

## When to run this vs. just talking

If the person only wants *the script* (the words), you can write that directly — see `references/meditation-script-craft.md` for how — and skip the audio/video machinery. Run the full pipeline when they want a produced artifact: narrated audio or a video.

Gather a few specifics first (don't over-ask — most have a quick answer):

- **Length** — 5 minutes is the common default. Drives how much silence to budget.
- **Theme/style** — mindfulness/breath, body scan, sleep, loving-kindness, anxiety relief. Sets the script.
- **Voice** — female or male, and any accent. Default `af_heart` (American female) is the warmest. Full roster in `references/kokoro-and-ffmpeg.md`.
- **Backdrop** — a vibe for the still image (misty lake, night sky, candle). You can pick a sensible one if they don't care.
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

Read `references/meditation-script-craft.md` before writing — it covers the arc, the two pause lengths (≈3s short, 7–30s long) and when to use each, the audience calibration, and the two easy-to-miss rules: **start almost immediately** (tiny `lead_in`) and **end with an explicit spoken close**, not trailing silence, so the listener knows when to get up. `speed: 0.9` slows the voice slightly, which reads as calmer.

### 2. Generate the narration segments

```bash
python3 assets/generate_segments.py meditation.json --workdir work
```

One WAV per line, into `work/`. It's resumable — already-rendered lines are skipped — so if it's interrupted, just run it again. Generation is CPU-only at several times real-time.

### 3. Stitch in the silence

```bash
python3 assets/build_audio.py meditation.json --workdir work --out meditation.wav
```

Concatenates the segments with exact digital silence from each `pause` value, plus the lead-in and tail. It prints the total duration and the speech-to-silence ratio — glance at that ratio; if silence is well under ~55% the meditation is probably too talky. **This WAV is the audio-only deliverable** if that's all they wanted.

### 4. Choose and fetch a backdrop image

```bash
bash assets/fetch_image.sh image.jpg "https://images.unsplash.com/photo-<id>?w=1920&h=1080&fit=crop&q=80"
```

Pick a deliberately calm, low-contrast, slow scene — the image sets the mood before a word is spoken. Free sources that need no key: Unsplash CDN direct URLs and `https://picsum.photos/1920/1080`. Aim for 1920×1080.

### 5. Render the video

```bash
python3 assets/render_video.py image.jpg meditation.wav --out meditation.mp4
```

Produces an H.264/AAC MP4 with gentle fade-in/out and an audio fade that lands in the trailing silence (never over a word). It deliberately renders at a low frame rate because the image is static — that keeps a 5-minute encode down to a few seconds. See `references/kokoro-and-ffmpeg.md` for every flag and why it's there.

### 6. Verify and deliver

Confirm the output before handing it over: check the duration matches expectations and that it actually plays.

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height \
  -of default=noprint_wrappers=1 meditation.mp4
```

Then present the file to the person. Offer the obvious next tweaks — different voice, more or less silence, a different backdrop — since each is a one-line change and re-render.

## Iterating

Every dial is in the JSON or a CLI flag, so changes are cheap. Re-rendering reuses the already-generated segments unless their text changed:

- **Different voice or pace** → edit `voice` / `speed`, delete `work/`, regenerate.
- **Adjust a single pause** → edit that `pause`, skip generation, just re-run `build_audio.py` and `render_video.py` (the silence is added at build time, so no regeneration needed).
- **Different image** → re-fetch and re-run `render_video.py` only.
- **Hit a target length** → tweak the longer pauses (the open-awareness rest is the easiest place to add or remove time) and rebuild.

## Sleep essays

A sleep essay rides the same machinery but differs in mode: continuous narration instead of silence, and a research-and-write step up front. **Read `references/sleep-essay-craft.md` first** — it covers topic selection (the "lore" criterion), the pitch workflow, research strategy, the already-covered topics to avoid, and how to write flowing prose for the ear.

The flow:

1. **Research, then write** the essay (15+ minutes read aloud, ~4,000–6,000+ words of flowing prose) and save it as a Markdown file. **Present this Markdown as an artifact** — it's a primary deliverable the person also reads on screen, not just the video's soundtrack.
2. **Convert the essay to a segments file** — this is the one extra step versus a meditation. Instead of hand-authoring the JSON, run:

   ```bash
   python3 assets/essay_to_segments.py essay.md --out essay.json \
       --voice af_heart --speed 0.9 --sentence-pause 0.5 --paragraph-pause 1.4 --tail 4
   ```

   It strips Markdown, splits the prose into one segment per sentence (keeping generation chunked and resumable), inserts small pauses, and prints the word count and estimated read time so you can confirm the 15-minute floor.
3. **Run the shared pipeline** on `essay.json`: `generate_segments.py` → `build_audio.py` → fetch image → `render_video.py`. Two deliberate differences at render time:
   - **No wake-up ending and a longer dissolve** — a sleep essay must not tell the listener to return to their day; let it trail off. Pass `--audio-fade-out 4` (or more) to `render_video.py`.
   - **A dark, dim backdrop** (night sky, dark water) so a phone left playing doesn't light the room.

   Note that generation is the long pole here — tens of minutes of audio is minutes of CPU compute — but the generator is resumable, so just re-run it until all segments exist.

## References

- `references/meditation-script-craft.md` — guided-meditation words and silence: structure, pacing, audience, sources.
- `references/sleep-essay-craft.md` — sleep-essay craft: the "lore" criterion, topic domains and examples, the pitch/research workflow, topics already covered, and writing prose for the ear.
- `references/kokoro-and-ffmpeg.md` — the technical layer: Kokoro ONNX setup, the full voice roster, gotchas (including the `segments.py` name clash), and every ffmpeg flag explained.
