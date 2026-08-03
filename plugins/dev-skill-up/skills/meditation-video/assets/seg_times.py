"""Exact segment start times, measured from the rendered WAVs.

Every cue in a casual essay — picture changes and chapter marks alike — must be
timed off the real audio, never off a clock or a words-per-minute estimate. This
is the one shared implementation: render_slideshow.py pins shots with it and
make_metadata.py derives chapters with it, so the two always agree.
"""
import json
import os

import soundfile as sf


def segment_start_times(spec_path, workdir):
    """Return (spec, starts, total): the parsed segments JSON, each segment's
    start time in seconds, and the total duration including lead-in and tail.

    Requires every work/seg_NNN.wav to exist (run generate_segments.py first).
    The defaults for lead_in/tail mirror build_audio.py so the computed total
    matches the stitched WAV sample-for-sample.
    """
    with open(spec_path) as fh:
        spec = json.load(fh)
    t = float(spec.get("lead_in", 0.5))
    starts = []
    for i, seg in enumerate(spec["segments"]):
        info = sf.info(os.path.join(workdir, f"seg_{i:03d}.wav"))
        starts.append(t)
        t += info.frames / info.samplerate + float(seg.get("pause", 0))
    return spec, starts, t + float(spec.get("tail", 0.8))


def fmt_ts(seconds):
    """0:00 / 12:34 / 1:02:03 — the format YouTube chapters expect."""
    s = int(round(seconds))
    if s >= 3600:
        return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"
    return f"{s // 60}:{s % 60:02d}"
