#!/usr/bin/env python3
"""Select shots and render the casual-essay slideshow in one ffmpeg pass.

Shot selection is anchors + greedy fill (hand-fitting 30 gaps is miserable and
you will get it wrong):

* anchors are pinned to the segment whose sentence they illustrate — every
  diagram, plus any photo whose subject is named right there;
* candidates are a deliberately over-dense pool, each cued to the segment
  where it is relevant; a greedy selector fills every gap so no shot runs
  under --min-shot or over --max-shot, rejecting a candidate whose plate
  equals the previous shot's.

All cue times come from the real WAV durations via seg_times.py — never from a
clock — so every picture change lands on a sentence boundary.

The render is a single pass: N looped image inputs -> per-input constant-size
`crop` (3x faster than zoompan and pixel-sharp; see
references/kokoro-and-ffmpeg.md) -> an `xfade` chain whose dissolves straddle
each boundary -> mux the narration. Full-bleed plates get a slow pan/tilt/drift
capped at --max-rate px/s with alternating direction; any plate that is
effectively frame-sized is held perfectly static so text never crawls.

Usage:
    python3 render_slideshow.py essay.json shots.json --workdir work \
        --audio essay.wav --out master.mp4 [--select-only] [--dry-run]

shots.json:
    {"anchors":    [{"plate": "plates/dia_map.png", "segment": 12}, ...],
     "candidates": [{"plate": "plates/scroll.png", "segment": 30}, ...]}
(an entry may add "static": true to force stillness on an oversized plate)

Always run --select-only first and READ the unused-plates list: the selector
optimises spacing, not meaning, and it will happily drop your most important
image. Expect the render to take ~1.15x realtime — start it before writing
the credits.
"""
import argparse
import json
import math
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seg_times import segment_start_times  # noqa: E402

FRAME_W, FRAME_H = 1920, 1080
STATIC_W, STATIC_H = 1930, 1090  # gate on plate size, not just a flag


def select_shots(anchors, candidates, starts, total, min_shot, max_shot):
    """Greedy fill between pinned anchors. Returns the ordered shot list."""
    def timed(entries):
        out = []
        for e in entries:
            if not 0 <= e["segment"] < len(starts):
                raise SystemExit(f"shot {e['plate']}: segment {e['segment']} "
                                 f"out of range (0..{len(starts) - 1})")
            out.append(dict(e, time=starts[e["segment"]]))
        return sorted(out, key=lambda s: s["time"])

    fixed = timed(anchors)
    pool = timed(candidates)

    # The opening shot is forced to t=0 (video time, before the lead-in ends).
    if fixed and fixed[0]["segment"] == 0:
        opening = fixed.pop(0)
    elif pool:
        opening = min(pool, key=lambda s: s["segment"])
        pool.remove(opening)
        if opening["segment"] != 0:
            print(f"WARNING: no shot cued to segment 0; opening on "
                  f"{opening['plate']} (segment {opening['segment']}) at 0:00")
    else:
        raise SystemExit("no anchors or candidates to open the video with")
    opening["time"] = 0.0
    shots = [opening]

    boundaries = [(a, a["time"]) for a in fixed] + [(None, total)]
    for anchor, b_time in boundaries:
        while b_time - shots[-1]["time"] > max_shot:
            cur = shots[-1]
            lo, hi = cur["time"] + min_shot, cur["time"] + max_shot
            viable = [c for c in pool
                      if lo <= c["time"] <= hi
                      and b_time - c["time"] >= min_shot
                      and c["plate"] != cur["plate"]]
            if not viable:  # relax the lower bound before giving up
                viable = [c for c in pool
                          if cur["time"] < c["time"] <= hi
                          and b_time - c["time"] >= min_shot
                          and c["plate"] != cur["plate"]]
            if not viable:
                print(f"WARNING: no candidate fits after {cur['time']:.0f}s; "
                      f"shot runs {b_time - cur['time']:.0f}s "
                      f"(max {max_shot:.0f}) — add candidates near there")
                break
            pick = max(viable, key=lambda s: s["time"])
            pool.remove(pick)
            shots.append(pick)
        if anchor is not None:
            gap = anchor["time"] - shots[-1]["time"]
            if gap < min_shot:
                print(f"WARNING: anchor {anchor['plate']} at "
                      f"{anchor['time']:.0f}s follows the previous shot by "
                      f"only {gap:.0f}s (min {min_shot:.0f})")
            if anchor["plate"] == shots[-1]["plate"]:
                print(f"WARNING: {anchor['plate']} repeats back-to-back")
            shots.append(anchor)
    return shots


def motion_exprs(w, h, length, max_rate, direction):
    """Rate-capped pan/tilt/drift expressions for one full-bleed plate."""
    slack_x, slack_y = w - FRAME_W, h - FRAME_H
    mag = math.hypot(slack_x, slack_y)
    scale = min(1.0, (max_rate * length) / mag) if mag else 0.0
    span_x, span_y = slack_x * scale, slack_y * scale

    def axis(slack, span):
        start = (slack - span) / 2  # centred on the leftover slack
        if span < 1:
            return f"{slack / 2:.1f}"
        if direction < 0:
            start = start + span
            span = -span
        return f"{start:.1f}+{span / length:.4f}*t"

    return axis(slack_x, span_x), axis(slack_y, span_y)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="segments JSON (from essay_to_segments.py)")
    ap.add_argument("shots", help="shots JSON with anchors + candidates")
    ap.add_argument("--workdir", default="work", help="dir with seg_NNN.wav")
    ap.add_argument("--audio", default="essay.wav", help="stitched narration")
    ap.add_argument("--out", default="master.mp4")
    ap.add_argument("--resolved", default="shots.resolved.json")
    ap.add_argument("--select-only", action="store_true",
                    help="emit the resolved shot list + plate diff, no render")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the ffmpeg command without running it")
    ap.add_argument("--min-shot", type=float, default=30)
    ap.add_argument("--max-shot", type=float, default=60)
    ap.add_argument("--xfade", type=float, default=1.6)
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--crf", type=int, default=21)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--max-rate", type=float, default=32,
                    help="travel cap in px/s; uncapped wide pans look like hunting")
    ap.add_argument("--fade-in", type=float, default=2)
    ap.add_argument("--video-fade-out", type=float, default=3)
    ap.add_argument("--audio-fade-out", type=float, default=3)
    args = ap.parse_args()

    spec, starts, total = segment_start_times(args.spec, args.workdir)
    with open(args.shots) as fh:
        shot_spec = json.load(fh)

    shots = select_shots(shot_spec.get("anchors", []),
                         shot_spec.get("candidates", []),
                         starts, total, args.min_shot, args.max_shot)

    # Durations + static gate + alternating motion direction.
    moving = 0
    for k, s in enumerate(shots):
        nxt = shots[k + 1]["time"] if k + 1 < len(shots) else total
        s["duration"] = nxt - s["time"]
        w, h = Image.open(s["plate"]).size
        s["width"], s["height"] = w, h
        s["static"] = bool(s.get("static")) or (w <= STATIC_W and h <= STATIC_H)
        if not s["static"]:
            s["direction"] = 1 if moving % 2 == 0 else -1
            moving += 1

    with open(args.resolved, "w") as fh:
        json.dump([{k: s[k] for k in
                    ("plate", "segment", "time", "duration", "static")}
                   for s in shots], fh, indent=2)

    # GOTCHA: the selector optimises spacing, not meaning — it has dropped the
    # most important plates of a film before. Diff used against available and
    # EYEBALL this list before rendering.
    available = {s["plate"] for s in
                 shot_spec.get("anchors", []) + shot_spec.get("candidates", [])}
    used = {s["plate"] for s in shots}
    print(f"{len(shots)} shots over {total:.0f}s -> {args.resolved}")
    for s in shots:
        mark = "static" if s["static"] else "moving"
        print(f"  {s['time']:7.1f}s  {s['duration']:5.1f}s  {mark:6}  {s['plate']}")
    unused = sorted(available - used)
    if unused:
        print(f"\nUNUSED PLATES ({len(unused)}) — eyeball this list; is anything "
              f"here more important than what made the cut?")
        for p in unused:
            print(f"  - {p}")
    if args.select_only:
        return

    # Sanity: computed total vs the stitched narration.
    import soundfile as sf
    info = sf.info(args.audio)
    audio_dur = info.frames / info.samplerate
    if abs(audio_dur - total) > 0.1:
        print(f"WARNING: audio is {audio_dur:.2f}s but segment math says "
              f"{total:.2f}s — wrong workdir or stale WAVs?")

    X = args.xfade
    if shots[1]["time"] < X:
        raise SystemExit(f"first cut at {shots[1]['time']:.1f}s is inside the "
                         f"opening crossfade ({X}s); move or drop that shot")

    cmd = ["ffmpeg", "-y"]
    lines = []
    for k, s in enumerate(shots):
        length = s["duration"] + (X / 2 if k == len(shots) - 1 else X)
        cmd += ["-loop", "1", "-framerate", str(args.fps),
                "-t", f"{length:.3f}", "-i", s["plate"]]
        if s["static"]:
            filt = f"scale={FRAME_W}:{FRAME_H},setsar=1"
        else:
            ex, ey = motion_exprs(s["width"], s["height"], length,
                                  args.max_rate, s["direction"])
            filt = f"crop={FRAME_W}:{FRAME_H}:x='{ex}':y='{ey}',setsar=1"
        lines.append(f"[{k}:v]{filt}[v{k}]")

    cur = "[v0]"
    for k in range(1, len(shots)):
        offset = shots[k]["time"] - X / 2  # dissolve straddles the boundary
        nxt = f"[x{k}]"
        lines.append(f"{cur}[v{k}]xfade=transition=fade:duration={X}"
                     f":offset={offset:.3f}{nxt}")
        cur = nxt
    lines.append(
        f"{cur}format=yuv420p,fade=t=in:st=0:d={args.fade_in},"
        f"fade=t=out:st={total - args.video_fade_out:.3f}"
        f":d={args.video_fade_out}[vout]")
    lines.append(
        f"[{len(shots)}:a]afade=t=out:st={total - args.audio_fade_out:.3f}"
        f":d={args.audio_fade_out}[aout]")

    script = os.path.join(args.workdir, "slideshow_filter.txt")
    with open(script, "w") as fh:
        fh.write(";\n".join(lines) + "\n")

    cmd += ["-i", args.audio, "-filter_complex_script", script,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
            "-r", str(args.fps), "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "-t", f"{total:.3f}", args.out]

    print(" ".join(cmd))
    if args.dry_run:
        return

    # GOTCHA: a second ffmpeg writing the same path interleaves two encoders
    # into one plausible-looking, unplayable file. And kill renders with
    # `pkill -x ffmpeg` — never -f (see references/kokoro-and-ffmpeg.md).
    check = subprocess.run(["pgrep", "-x", "ffmpeg"], capture_output=True)
    if check.returncode == 0:
        raise SystemExit("another ffmpeg is already running (pgrep -x ffmpeg); "
                         "kill it with `pkill -x ffmpeg` before rendering")

    print(f"rendering {total:.0f}s at ~1.15x realtime — "
          f"expect ~{total * 1.15 / 60:.0f} min")
    subprocess.run(cmd, check=True)

    # ffprobe will NOT catch corruption; only a full decode does.
    verify = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", args.out, "-f", "null", "-"],
        capture_output=True, text=True)
    if verify.returncode != 0 or verify.stderr.strip():
        raise SystemExit(f"FULL-DECODE CHECK FAILED for {args.out}:\n"
                         f"{verify.stderr.strip()}")
    size = os.path.getsize(args.out) / 1e6
    print(f"wrote {args.out}: {total:.0f}s, {size:.0f} MB, full decode clean"
          + ("" if size <= 30 else
             " — over the 30 MB delivery cap; compress before sending "
             "(references/casual-essay.md)"))


if __name__ == "__main__":
    main()
