#!/usr/bin/env python3
"""Convert a prose essay (Markdown or plain text) into a segments JSON for the
sleep-essay path of the meditation-video pipeline.

Unlike a guided meditation (a few cues separated by long silence), a sleep essay
is continuous narration. So this splits the prose into one segment per sentence
and inserts only small, natural pauses — a short beat after each sentence and a
slightly longer one between paragraphs. One sentence per segment keeps TTS
generation chunked and resumable.

Usage:
    python3 essay_to_segments.py ESSAY.md --out essay.json \
        [--voice af_heart] [--speed 0.9] [--lang en-us] \
        [--sentence-pause 0.5] [--paragraph-pause 1.4] \
        [--lead-in 0.5] [--tail 4]

The resulting JSON feeds generate_segments.py / build_audio.py unchanged.
"""
import argparse
import json
import re

# Abbreviations whose trailing period must NOT be treated as a sentence end.
ABBREV = [
    "e.g.", "i.e.", "etc.", "vs.", "cf.", "al.", "ca.", "approx.",
    "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "St.", "Mt.", "Fr.",
    "Fig.", "No.", "Vol.", "pp.", "p.", "ed.", "trans.",
    "B.C.", "A.D.", "B.C.E.", "C.E.", "A.M.", "P.M.",
]


def strip_markdown(text: str) -> str:
    """Reduce Markdown to plain narration text."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)      # fenced code
    text = re.sub(r"`([^`]*)`", r"\1", text)                 # inline code
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)        # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)     # links -> text
    out_lines = []
    for line in text.splitlines():
        s = line.strip()
        s = re.sub(r"^#{1,6}\s*", "", s)        # headings
        s = re.sub(r"^>\s*", "", s)             # blockquotes
        s = re.sub(r"^[-*+]\s+", "", s)         # bullet markers
        s = re.sub(r"^\d+\.\s+", "", s)         # numbered markers
        out_lines.append(s)
    text = "\n".join(out_lines)
    text = re.sub(r"(\*\*|__|\*|_|~~)", "", text)            # emphasis
    return text


def split_sentences(paragraph: str) -> list:
    """Split a single paragraph into sentences, protecting abbreviations."""
    protected = paragraph
    holders = {}
    for i, ab in enumerate(ABBREV):
        ph = f"\x00{i}\x00"
        protected = protected.replace(ab, ph)
        holders[ph] = ab
    # Protect single-capital initials like "J. R. R."
    protected = re.sub(r"\b([A-Z])\.", lambda m: m.group(1) + "\x01", protected)

    # Split after . ! ? when followed by whitespace and an opening quote,
    # capital letter, digit, or a protected-abbreviation placeholder (\x00) —
    # so a sentence that *starts* with an abbreviation still splits from the
    # previous one. Decimals like "0.5" have no following whitespace and are
    # left intact.
    parts = re.split('(?<=[.!?])\\s+(?=["“‘\'A-Z0-9\x00])', protected)

    out = []
    for p in parts:
        p = p.replace("\x01", ".")
        for ph, ab in holders.items():
            p = p.replace(ph, ab)
        p = " ".join(p.split())  # collapse whitespace
        if not p:
            continue
        # Merge a stray very-short fragment into the previous sentence.
        if out and len(p) < 8:
            out[-1] = out[-1] + " " + p
        else:
            out.append(p)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("essay", help="essay Markdown or text file")
    ap.add_argument("--out", default="essay.json")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=0.9)
    ap.add_argument("--lang", default="en-us")
    ap.add_argument("--sentence-pause", type=float, default=0.5)
    ap.add_argument("--paragraph-pause", type=float, default=1.4)
    ap.add_argument("--lead-in", type=float, default=0.5)
    ap.add_argument("--tail", type=float, default=4.0,
                    help="trailing seconds; longer than a meditation so it dissolves")
    ap.add_argument("--wpm", type=float, default=140.0,
                    help="assumed narration rate for the read-time estimate")
    args = ap.parse_args()

    with open(args.essay) as fh:
        raw = fh.read()
    text = strip_markdown(raw)

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    segments = []
    for para in paragraphs:
        sentences = split_sentences(para)
        for si, sentence in enumerate(sentences):
            last = si == len(sentences) - 1
            segments.append({
                "text": sentence,
                "pause": args.paragraph_pause if last else args.sentence_pause,
            })
    if segments:
        segments[-1]["pause"] = 0  # nothing after the final sentence

    spec = {
        "voice": args.voice,
        "speed": args.speed,
        "lang": args.lang,
        "lead_in": args.lead_in,
        "tail": args.tail,
        "segments": segments,
    }
    with open(args.out, "w") as fh:
        json.dump(spec, fh, ensure_ascii=False, indent=2)

    words = sum(len(s["text"].split()) for s in segments)
    minutes = words / args.wpm
    flag = "" if minutes >= 15 else "  <-- under the 15-minute floor; lengthen the essay"
    print(f"{args.out}: {len(segments)} segments, {words} words, "
          f"~{minutes:.0f} min read aloud at {args.wpm:.0f} wpm{flag}")


if __name__ == "__main__":
    main()
