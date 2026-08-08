#!/usr/bin/env python3
"""Render each line of a meditation script to its own WAV using Kokoro (ONNX).

Resumable by design: a segment whose WAV already exists is skipped, so if the
process is interrupted (or killed by a sandbox time limit) you just run it again
and it picks up where it left off. Generation is CPU-only and runs at several
times real-time.

For essay-derived scripts (essay_to_segments.py stamps them with
`"passes_required": true`), this script IS the hard audio gate from
references/ai-tells.md: it refuses to generate until --passes points at a
report holding the structured verdicts of one full convergence-loop cycle in
which every pass returned zero findings. DO NOT edit this script to weaken or
bypass the gate, and do not strip the stamp from the segments JSON — a blocked
gate means the loop is not done, and the only fix is to run the loop until a
cycle comes back clean.

Usage:
    python3 generate_segments.py SCRIPT.json [--workdir work] \
        [--passes passes.json] \
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

# Every pass of the ai-tells convergence loop. The gate demands a verdict for
# each one — a pass that has not run in the final clean cycle has not run.
REQUIRED_PASSES = (
    "first-person-excision",  # A
    "cut",                    # B
    "mechanical",             # 1 — greppable checks + tell_metrics.py
    "rhythm",                 # 2
    "structure",              # 3a
    "register",               # 3b
    "comprehension",          # 4
    "cold-read",              # 5
    "fact-check",             # 6
)


def check_passes(path: str) -> None:
    """Exit unless PATH records one full clean convergence-loop cycle.

    Expected shape — the structured verdicts of references/ai-tells.md, all
    from the same (final) cycle:

        {"cycle": 4, "passes": [
            {"pass": "rhythm", "findings": [],
             "count_by_category": {"kicker": 0, "flat-coda": 0, ...}},
            ...]}
    """
    try:
        with open(path) as fh:
            report = json.load(fh)
    except (OSError, ValueError) as e:
        raise SystemExit(f"audio gate: cannot read passes report {path}: {e}")
    if not isinstance(report, dict):
        raise SystemExit(f"audio gate: {path} must be a JSON object "
                         '{"cycle": N, "passes": [...]}')

    problems = []
    cycle = report.get("cycle")
    if not isinstance(cycle, int) or cycle < 1:
        problems.append('no "cycle" number — every verdict must come from the '
                        "same, final cycle; a clean result carried over from "
                        "an earlier cycle has not run")
    entries = report.get("passes")
    if not isinstance(entries, list):
        entries = []
        problems.append('no "passes" list of per-pass verdicts')

    seen = set()
    for entry in entries:
        name = entry.get("pass") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            problems.append(f"verdict without a 'pass' name: {entry!r:.60}")
            continue
        if name in seen:
            problems.append(f"{name}: duplicate verdict")
        seen.add(name)
        findings = entry.get("findings")
        if findings != []:
            problems.append(f"{name}: findings must be an explicit empty "
                            f"list, got {findings!r:.60} — fix them and "
                            "re-run every pass from the top")
        counts = entry.get("count_by_category")
        if not isinstance(counts, dict) or not counts:
            problems.append(f"{name}: count_by_category must name every "
                            "category the pass owns, zeros included — "
                            '"looks good" is not a verdict')
        elif any(v != 0 for v in counts.values()):
            nonzero = {k: v for k, v in counts.items() if v != 0}
            problems.append(f"{name}: nonzero counts {nonzero}")
    for name in REQUIRED_PASSES:
        if name not in seen:
            problems.append(f"{name}: no verdict")

    if problems:
        detail = "\n".join(f"  - {p}" for p in problems)
        raise SystemExit(
            f"audio gate: {path} is not one clean cycle of every pass:\n"
            f"{detail}\n"
            "Re-enter the convergence loop (references/ai-tells.md) until one "
            "full cycle returns zero findings from every pass, then write a "
            "new report from that cycle's actual verdicts. Do not edit this "
            "script, and do not fabricate a verdict for a pass that did not "
            "run.")
    print(f"audio gate: {path} clean — cycle {cycle}, "
          f"{len(seen)} passes all zero")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("script", help="meditation script JSON file")
    ap.add_argument("--workdir", default="work", help="where seg_NNN.wav files go")
    ap.add_argument("--model", default="kokoro-v1.0.onnx")
    ap.add_argument("--voices", default="voices-v1.0.bin")
    ap.add_argument("--passes", help="JSON report of the final clean ai-tells "
                    "cycle; required for essay-derived scripts")
    args = ap.parse_args()

    with open(args.script) as fh:
        spec = json.load(fh)
    if spec.get("passes_required") and not args.passes:
        raise SystemExit(
            f"audio gate: {args.script} came from essay_to_segments.py, so "
            "audio generation is gated on the ai-tells convergence loop "
            "(references/ai-tells.md). Pass --passes passes.json holding the "
            "structured verdicts of the final clean cycle. If no clean cycle "
            "exists yet, run the loop — do not edit this script or the "
            "segments JSON to get past the gate.")
    if args.passes:
        check_passes(args.passes)
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
