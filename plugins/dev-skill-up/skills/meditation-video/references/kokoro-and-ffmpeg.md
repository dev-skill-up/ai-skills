# The technical layer: Kokoro TTS + ffmpeg

Everything here runs offline on CPU. This doc explains the choices baked into the scripts and the gotchas worth knowing before you debug something.

## Why the ONNX build of Kokoro

[Kokoro](https://github.com/hexgrad/kokoro) is an 82M-parameter open-weights TTS model. Its quality is excellent for the size and it runs comfortably on CPU — no GPU needed — which makes it the right pick for a constrained sandbox.

The default `kokoro` package on PyPI depends on **PyTorch**, whose wheel is ~400MB and is slow to unpack. In a tight environment (limited RAM, or short per-command time limits) installing torch can be impractical or impossible.

[`kokoro-onnx`](https://github.com/thewh1teagle/kokoro-onnx) sidesteps this entirely: it runs the *same Kokoro v1.0 weights*, exported to ONNX, through `onnxruntime`. The dependency is a few MB and installs in seconds. The voice is identical to the torch build — you are not trading quality for convenience.

`setup.sh` installs `kokoro-onnx onnxruntime soundfile` and downloads two files from the kokoro-onnx model release:

- `kokoro-v1.0.onnx` — the acoustic model, ~310MB (the fp32 build; a smaller int8 quant exists if you need it).
- `voices-v1.0.bin` — the voice embeddings, ~27MB.

Output audio is **24000 Hz mono**.

## Voices

There are **54 voices**. The name encodes language and gender: first letter = language, second letter = `f`emale / `m`ale.

Languages: `a` American English, `b` British English, `e` Spanish, `f` French, `h` Hindi, `i` Italian, `j` Japanese, `p` Brazilian Portuguese, `z` Mandarin Chinese.

For English meditations you'll almost always want an American or British voice:

- **American female (`af_`)**: af_heart, af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- **American male (`am_`)**: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa
- **British female (`bf_`)**: bf_alice, bf_emma, bf_isabella, bf_lily
- **British male (`bm_`)**: bm_daniel, bm_fable, bm_george, bm_lewis

`af_heart` is the warmest, most natural default and is what the example uses. `af_bella` and `af_nicole` are also strong for this calm register. If unsure, generate one line with two or three candidates and let the person pick — auditioning is cheap.

Other languages exist too (ef_dora, ff_siwis, hf_alpha/beta, if_sara, jf_alpha, zf_xiaoxiao, etc.). To use them, set both `voice` and a matching `lang` in the script JSON (e.g. `"lang": "es"` for Spanish). Set `lang` to `en-us` for `af_`/`am_` and `en-gb` for `bf_`/`bm_`.

Get the live list any time:

```python
from kokoro_onnx import Kokoro
print(sorted(Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin").get_voices()))
```

## Generating audio

The API is one call:

```python
audio, sr = kokoro.create(text, voice="af_heart", speed=0.9, lang="en-us")
```

- **`speed`** below 1.0 slows delivery. `0.9` is a good calm meditation pace; `0.85` is noticeably slow.
- Generate **one line at a time** and save each to its own WAV (`generate_segments.py`). This is what makes generation resumable and lets you insert exact silence between lines.

### Do not make the model "pause"

TTS models don't hold silence reliably — they rush it or fill it with a breath/artifact. Never try to encode long pauses by putting blank lines, dots, or "[pause]" into the text. Generate the spoken lines only, then concatenate them with real digital silence (`build_audio.py` writes `numpy` zeros between segments). Your timing becomes exact and repeatable.

## Gotchas

- **The `segments.py` name clash (this one bites).** Kokoro's phonemizer dependency imports a third-party package literally named `segments`. If your working directory contains a file called `segments.py`, Python imports *yours* instead and the whole thing dies with `AttributeError: module 'segments' has no attribute 'Profile'`. Never name a local file `segments.py`. (This is why the script data is JSON, not a Python module.)
- **espeak-ng / apt.** Kokoro phonemizes via a bundled backend, so you generally do **not** need a system `espeak-ng`, which is good because installing it needs root (`apt`) that a sandbox often lacks. If you ever do hit a missing-espeak error, the `espeakng-loader` pip package provides the binary without apt.
- **onnxruntime CPU warnings.** On some VMs you'll see `cpuid_info ... Unknown CPU vendor` on stderr. It's harmless noise; filter it (`grep -vE 'cpuid|cpuinfo'`) so it doesn't clutter logs.
- **Background installs may not survive.** In sandboxes where each shell command runs in a fresh process group, a backgrounded `pip install &` can be torn down when the command returns. Run installs in the foreground. If a big download is the bottleneck, `pip`'s cache and `wget -c` both resume, so re-running makes progress.

## The ffmpeg still-video render

`render_video.py` builds this command (durations computed from the WAV):

```
ffmpeg -y -loop 1 -framerate 10 -i image.jpg -i narration.wav \
  -c:v libx264 -preset ultrafast -tune stillimage -pix_fmt yuv420p -r 10 \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,fade=t=in:st=0:d=2,fade=t=out:st=<dur-2>:d=2" \
  -af "afade=t=out:st=<dur-0.6>:d=0.6" \
  -c:a aac -b:a 192k -movflags +faststart -shortest out.mp4
```

Why each piece:

- **`-loop 1` + `-framerate 10` / `-r 10`** — loop the single image into a video stream at a low frame rate. The image never moves, so high fps only multiplies encode time. *This is the key to fast renders:* at 25fps a 5-minute video is ~7500 frames and can blow past a short command time limit; at 10fps it's ~3000 and encodes in a few seconds. Low fps does not hurt a static image; the only thing it touches is the smoothness of the fades, and 10fps is plenty for slow 2-second fades.
- **`-preset ultrafast -tune stillimage`** — fastest x264 preset, tuned for a held frame. Combined with low fps, even a long meditation renders almost instantly.
- **`-pix_fmt yuv420p`** and **even dimensions** (`scale=trunc(iw/2)*2:trunc(ih/2)*2`) — both required for broad playback (browsers, QuickTime, phones). Odd width/height makes some players refuse the file.
- **Video fades** — `fade=in` over 2s at the start, `fade=out` over 2s at the end, for a calm open and close.
- **Audio fade** — a short `afade=out` (0.6s) placed in the *trailing silence*, computed as `duration − 0.6`. Keep it short and late so it never fades out over spoken words. If the script ends with an explicit spoken close (as it should), the last words finish before this fade begins.
- **`-movflags +faststart`** — relocates the moov atom to the front so the file streams/plays immediately instead of needing a full download first.
- **`-shortest`** — stop when the audio ends (the looped image would otherwise run forever).

### Render performance

If a render ever times out, the lever is **frame rate first** (drop `--fps`), then preset. Don't reach for higher fps on a still image — there's no motion to smooth.

## Pipeline data flow

```
meditation.json ──> generate_segments.py ──> work/seg_000.wav, seg_001.wav, ...
                                                     │
meditation.json ──> build_audio.py ─────────────────┴──> meditation.wav  (audio deliverable)
                                                                 │
image.jpg ──────> render_video.py ───────────────────────────────┴──> meditation.mp4
```
