#!/usr/bin/env python3
"""Render each line of a meditation script to its own WAV using Kokoro (ONNX).

Resumable by design: a segment whose WAV already exists is skipped, so if the
process is interrupted (or killed by a sandbox time limit) you just run it again
and it picks up where it left off. Generation is CPU-only and runs at several
times real-time.

Usage:
    python3 generate_segments.py SCRIPT.json [--workdir work] \
        [--model kokoro-v1.0.onnx] [--voices voices-v1.0.bin]

SCRIPT.json shape (see meditation.example.json):
    {
      "voice": "af_heart", "speed": 0.9, "lang": "en-us",
      "lead_in": 0.5, "tail": 0.8,
      "segments": [ {"text": "...", "pause": 3}, ... ]
    }

GOTCHA: do not name any file in your working directory `segments.py`. Kokoro's
phonemizer dependency imports a third-party package literally named `segments`,
and a local `segments.py` will shadow it and crash with a confusing
`module 'segments' has no attribute 'Profile'`. (That's why the script-data file
here is JSON, not a Python module.)
"""
import argparse
import json
import os


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("script", help="meditation script JSON file")
    ap.add_argument("--workdir", default="work", help="where seg_NNN.wav files go")
    ap.add_argument("--model", default="kokoro-v1.0.onnx")
    ap.add_argument("--voices", default="voices-v1.0.bin")
    args = ap.parse_args()

    with open(args.script) as fh:
        spec = json.load(fh)
    voice = spec.get("voice", "af_heart")
    speed = float(spec.get("speed", 0.9))
    lang = spec.get("lang", "en-us")
    segs = spec["segments"]
    os.makedirs(args.workdir, exist_ok=True)

    import soundfile as sf

    def path(i: int) -> str:
        return os.path.join(args.workdir, f"seg_{i:03d}.wav")

    todo = [(i, s) for i, s in enumerate(segs) if not os.path.exists(path(i))]
    print(f"{len(segs) - len(todo)}/{len(segs)} already rendered; {len(todo)} to generate")

    if todo:
        from kokoro_onnx import Kokoro  # imported lazily so --help is instant

        k = Kokoro(args.model, args.voices)
        for i, s in todo:
            audio, sr = k.create(s["text"], voice=voice, speed=speed, lang=lang)
            sf.write(path(i), audio, sr)
            preview = s["text"][:55].replace("\n", " ")
            print(f"  seg {i:03d} ({len(audio) / sr:5.1f}s): {preview}")

    done = sum(os.path.exists(path(i)) for i in range(len(segs)))
    print(f"done: {done}/{len(segs)} segments on disk in {args.workdir}/")


if __name__ == "__main__":
    main()
