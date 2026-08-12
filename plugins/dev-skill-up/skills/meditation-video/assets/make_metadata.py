#!/usr/bin/env python3
"""Generate youtube-description.txt + youtube-tags.txt from the shot list.

A finished video is not a deliverable on its own: every essay run must emit
these two files and send them WITH the MP4. Generate them — never write them
by hand, or they drift from the video after the next re-render. Chapters come
from the same seg_times.py the shot list uses, so chapter marks and picture
changes always agree. Full spec: references/publishing-metadata.md.

Hard limits enforced here: description 5,000 chars (sources spill to
pinned-comment.txt when over), tags 500 chars (trimmed from the end, dropped
tags printed).

The description talks about the video's SUBJECT only. It never mentions the
pipeline or tools, never describes the essay's own methodology, never states
licence positions or grants reuse permission, and never inventories what the
video doesn't contain. Credits are credit for material used — nothing more.

Usage:
    python3 make_metadata.py meta.json --spec essay.json --workdir work \
        [--shots shots.resolved.json --credits credits.json] [--outdir .]

For a sleep essay there is no shot list: omit --shots/--credits (or point at
files that don't exist) and put the backdrop's credit in meta.json as an
"image_credits" line.

meta.json:
    {"title": "...",                      # warns if over 60 chars
     "hook": "2-4 short paragraphs...",   # open on the video's opening image
     "chapters": [{"segment": 0, "title": "A cat's head in a wreath"}, ...],
     "sources": ["Author, 'Title', Journal 12 (1999)", ...],
     "substitutions": ["the card at 1:11 shows Seti I instead and says so"],
     "image_credits": ["Backdrop - Jane Doe, Unsplash"],  # shot-less runs
     "tags": ["most specific first", ...]}

credits.json maps each plate (path or basename) to
    {"subject": "...", "author": "...", "collection": "...",
     "original": false}
Entries with "original": true (diagrams, caption panels) get NO credit line —
there is nobody to credit, so the description says nothing about them.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seg_times import segment_start_times, fmt_ts  # noqa: E402

DESC_LIMIT = 5000
TAG_LIMIT = 500


def strip_markdown(s):
    """Manifests written as Markdown leak literal ** into the description."""
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s or "")
    return re.sub(r"(\*\*|__|\*|_|`)", "", s).strip()


def credit_line(c):
    """Subject - Author, Collection — empty fields dropped, never a dangling
    comma. No licence tag: credits credit, they don't state or grant
    licences (the licence records stay in the manifest for verification)."""
    subject = strip_markdown(c.get("subject", ""))
    tail = ", ".join(x for x in (strip_markdown(c.get("author", "")),
                                 strip_markdown(c.get("collection", ""))) if x)
    line = subject or "(unlabelled image)"
    if tail:
        line += " - " + tail
    return line


def build_chapters(chapters, starts, total):
    if len(chapters) < 3:
        raise SystemExit("need at least 3 chapters or YouTube ignores the list")
    if chapters[0]["segment"] != 0:
        raise SystemExit("first chapter must be segment 0 — chapters must "
                         "start at 0:00")
    times = [0.0] + [starts[c["segment"]] for c in chapters[1:]]
    lines = []
    for i, (t, c) in enumerate(zip(times, chapters)):
        end = times[i + 1] if i + 1 < len(times) else total
        if end - t < 10:
            raise SystemExit(f"chapter '{c['title']}' runs {end - t:.0f}s; "
                             f"each needs 10s or YouTube ignores the list")
        if end - t > 120:
            print(f"note: chapter '{c['title']}' runs {end - t:.0f}s "
                  f"(aim for one every 60-90s)")
        lines.append(f"{fmt_ts(t)} {c['title']}")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("meta", help="meta JSON (hook, chapters, sources, tags...)")
    ap.add_argument("--spec", default="essay.json")
    ap.add_argument("--workdir", default="work")
    ap.add_argument("--shots", default="shots.resolved.json")
    ap.add_argument("--credits", default="credits.json")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    with open(args.meta) as fh:
        meta = json.load(fh)
    # A sleep essay has no shot list — run without one and take credits from
    # meta.json's "image_credits" lines instead.
    shots, credits = [], {}
    if os.path.exists(args.shots):
        with open(args.shots) as fh:
            shots = json.load(fh)
        with open(args.credits) as fh:
            credits = json.load(fh)
    _, starts, total = segment_start_times(args.spec, args.workdir)

    title = meta.get("title", "")
    if len(title) > 60:
        print(f"WARNING: title is {len(title)} chars; YouTube truncates ~60")

    chapter_lines = build_chapters(meta["chapters"], starts, total)

    # Credits: one line per unique third-party plate, in shot order (de-dup by
    # plate, not by shot — a reused image gets one credit). Original plates
    # (diagrams, caption panels) get no line: nobody to credit, say nothing.
    seen, credit_lines, missing = set(), [], []
    for s in shots:
        plate = s["plate"]
        if plate in seen:
            continue
        seen.add(plate)
        c = credits.get(plate) or credits.get(os.path.basename(plate))
        if c is None:
            missing.append(plate)
        elif not c.get("original"):
            credit_lines.append(credit_line(c))
    if missing:
        print(f"WARNING: no credit entry for {len(missing)} plate(s): "
              + ", ".join(missing))
    credit_lines += [strip_markdown(x) for x in meta.get("image_credits", [])]
    credit_lines += [strip_markdown(x) for x in meta.get("substitutions", [])]

    sources = [strip_markdown(s) for s in meta.get("sources", [])]
    src_block = ["SOURCES"] + sources

    def assemble(sources_in_desc):
        parts = [meta["hook"].strip(), "", "CHAPTERS"] + chapter_lines + [""]
        if sources_in_desc:
            parts += src_block + [""]
        else:
            parts += ["SOURCES", "Full source list in the pinned comment.", ""]
        # Only when there is something to credit — never an empty header, and
        # never a note explaining that everything is original.
        if credit_lines:
            parts += ["IMAGE CREDITS"] + credit_lines
        return "\n".join(parts).strip() + "\n"

    desc = assemble(sources_in_desc=True)
    pinned = None
    if len(desc) > DESC_LIMIT:
        print(f"description {len(desc)} chars > {DESC_LIMIT}: moving sources "
              f"to pinned-comment.txt")
        pinned = "\n".join(src_block) + "\n"
        desc = assemble(sources_in_desc=False)
    if len(desc) > DESC_LIMIT:
        raise SystemExit(
            f"description still {len(desc)} chars > {DESC_LIMIT}. Sizes: "
            f"hook {len(meta['hook'])}, chapters "
            f"{sum(len(l) for l in chapter_lines)}, credits "
            f"{sum(len(l) for l in credit_lines)}. Tighten the hook or the "
            f"credit subjects.")

    # Tags: most specific first; trim from the end until the joined string
    # fits — YouTube silently drops the overflow otherwise.
    tags = list(meta.get("tags", []))
    dropped = []
    while tags and len(", ".join(tags)) > TAG_LIMIT:
        dropped.append(tags.pop())
    if dropped:
        print(f"tags over {TAG_LIMIT} chars; dropped from the end: "
              + ", ".join(reversed(dropped)))
    tag_str = ", ".join(tags) + "\n"

    os.makedirs(args.outdir, exist_ok=True)
    desc_path = os.path.join(args.outdir, "youtube-description.txt")
    tags_path = os.path.join(args.outdir, "youtube-tags.txt")
    with open(desc_path, "w") as fh:
        fh.write(desc)
    with open(tags_path, "w") as fh:
        fh.write(tag_str)
    if pinned:
        with open(os.path.join(args.outdir, "pinned-comment.txt"), "w") as fh:
            fh.write(pinned)
        print(f"wrote pinned-comment.txt ({len(pinned)} chars)")
    print(f"wrote {desc_path} ({len(desc)}/{DESC_LIMIT} chars), "
          f"{tags_path} ({len(tag_str.strip())}/{TAG_LIMIT} chars, "
          f"{len(tags)} tags)")
    print("deliver BOTH files in the same SendUserFile call as the video")


if __name__ == "__main__":
    main()
