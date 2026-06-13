#!/usr/bin/env python3
"""Stitch rendered segments into one narration WAV with calibrated silence.

The silence between lines is the heart of a guided meditation, and TTS models
will not hold a reliable pause on their own — they rush or fill it. So we
generate each spoken line separately and insert exact, digital silence between
them here. This gives precise, repeatable timing straight from the script's
`pause` values.

Usage:
    python3 build_audio.py SCRIPT.json [--workdir work] [--out meditation.wav] [--sr 24000]
"""
import argparse
import json
import os

import numpy as np
import soundfile as sf


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("script")
    ap.add_argument("--workdir", default="work")
    ap.add_argument("--out", default="meditation.wav")
    ap.add_argument("--sr", type=int, default=24000, help="Kokoro outputs 24000 Hz")
    args = ap.parse_args()

    with open(args.script) as fh:
        spec = json.load(fh)
    sr = args.sr
    lead_in = float(spec.get("lead_in", 0.5))
    tail = float(spec.get("tail", 0.8))
    segs = spec["segments"]

    def silence(seconds: float) -> np.ndarray:
        return np.zeros(int(max(0.0, seconds) * sr), dtype=np.float32)

    parts = [silence(lead_in)]
    for i, s in enumerate(segs):
        wav = os.path.join(args.workdir, f"seg_{i:03d}.wav")
        audio, file_sr = sf.read(wav, dtype="float32")
        if audio.ndim > 1:  # collapse to mono
            audio = audio.mean(axis=1)
        if file_sr != sr:
            raise SystemExit(f"{wav} is {file_sr} Hz, expected {sr}; pass --sr {file_sr}")
        parts.append(audio)
        parts.append(silence(float(s.get("pause", 3))))
    parts.append(silence(tail))

    full = np.concatenate(parts)
    sf.write(args.out, full, sr)
    dur = len(full) / sr
    spoken = sum(
        len(sf.read(os.path.join(args.workdir, f"seg_{i:03d}.wav"))[0]) / sr
        for i in range(len(segs))
    )
    print(f"wrote {args.out}: {dur:.1f}s = {int(dur // 60)}:{int(dur % 60):02d}  "
          f"({spoken:.0f}s speech, {dur - spoken:.0f}s silence — "
          f"{100 * (dur - spoken) / dur:.0f}% silence)")


if __name__ == "__main__":
    main()
