#!/usr/bin/env python3
"""Build 1920x1080-ready plates for the casual-essay slideshow.

Two honest styles — never letterbox bars, never a blurred-copy fill:

* full-bleed: the image is scaled to COVER the frame with ~12% margin, so the
  renderer can crop a moving 1920x1080 window out of it (a tall image tilts, a
  wide one pans, one with slack both ways drifts). Nothing is lost — whatever
  is off-frame arrives later in the shot.
* split panel: when an image cannot fill the frame honestly (over ~1.25x
  upscale, or so tall a 16:9 crop shows a sliver), the picture sits at full
  height in a right-hand column with a caption panel on the left, in the same
  palette as the diagrams. Give the caption a real fact so the screen is doing
  work rather than apologising — a label-length fact (a name, a date, an
  attribution), never sentences. The narration owns the prose; a paragraph on
  screen just competes with the voice.

Sizes matter downstream: split panels (and diagrams) land at exactly 1920x1080,
which is what makes render_slideshow.py's static gate hold them perfectly
still; full-bleed plates land oversized, which is what gives the crop window
its slack.

Usage:
    python3 make_plates.py plates_spec.json --outdir plates

plates_spec.json is a list:
    [
      {"src": "images_raw/scroll.jpg", "out": "scroll.png"},
      {"src": "images_raw/portrait.jpg", "out": "portrait.png",
       "mode": "split", "title": "Not her",
       "caption": "No freely licensed photograph of ... exists; this is ...",
       "accent": "#c8963c"}
    ]
`mode` is auto (default) / full / split / static. A frame-sized source (a
diagram already rendered at 1920x1080) passes through untouched in auto mode —
inflating it to a pannable plate would make its text crawl. Writes each plate
plus plates/plates.json recording {plate, mode, static, width, height}.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

FRAME_W, FRAME_H = 1920, 1080
GROUND = "#14110e"     # dark warm ground, shared with the diagrams
INK = "#ece5d8"        # warm off-white
ACCENT = "#c8963c"     # default; better: draw one from the subject itself

SERIF_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/dejavu/DejaVuSerif.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
]


def load_font(size):
    for p in SERIF_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    print("WARNING: no serif TTF found; falling back to PIL's bitmap font")
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def full_bleed(img, margin, max_upscale, forced):
    w, h = img.size
    s = margin * max(FRAME_W / w, FRAME_H / h)
    if s > max_upscale and not forced:
        return None  # caller falls through to split
    if s > max_upscale:
        print(f"  WARNING: forced full-bleed needs {s:.2f}x upscale "
              f"(> {max_upscale}); it will look soft")
    return img.resize((max(FRAME_W, round(w * s)), max(FRAME_H, round(h * s))),
                      Image.LANCZOS)


def split_panel(img, title, caption, accent, max_upscale):
    w, h = img.size
    s = min(FRAME_H / h, max_upscale)
    pic = img.resize((round(w * s), round(h * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (FRAME_W, FRAME_H), GROUND)
    canvas.paste(pic, (FRAME_W - pic.width, (FRAME_H - pic.height) // 2))

    draw = ImageDraw.Draw(canvas)
    panel_x, panel_w = 84, FRAME_W - pic.width - 84 - 60
    if panel_w < 380:
        print(f"  WARNING: caption panel only {panel_w}px wide; "
              f"consider full-bleed or a tighter crop of the source")
    y = 140
    title_font, cap_font = load_font(64), load_font(36)
    for line in wrap(draw, title or "", title_font, panel_w):
        draw.text((panel_x, y), line, font=title_font, fill=INK)
        y += 78
    draw.rectangle([panel_x, y + 14, panel_x + panel_w, y + 17],
                   fill=accent or ACCENT)
    y += 56
    for line in wrap(draw, caption or "", cap_font, panel_w):
        draw.text((panel_x, y), line, font=cap_font, fill=INK)
        y += 50
    if y > FRAME_H - 80:
        print("  WARNING: caption overflows the frame; shorten it")
    return canvas


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="plates spec JSON (list of {src, out, ...})")
    ap.add_argument("--outdir", default="plates")
    ap.add_argument("--margin", type=float, default=1.12,
                    help="cover-scale overshoot that gives the pan its slack")
    ap.add_argument("--max-upscale", type=float, default=1.25,
                    help="beyond this an image can't fill the frame honestly")
    ap.add_argument("--min-aspect", type=float, default=0.6,
                    help="w/h below this = a 16:9 crop shows a sliver -> split")
    args = ap.parse_args()

    with open(args.spec) as fh:
        items = json.load(fh)
    os.makedirs(args.outdir, exist_ok=True)

    manifest = []
    for item in items:
        img = Image.open(item["src"]).convert("RGB")
        mode = item.get("mode", "auto")
        out = os.path.join(args.outdir, item["out"])
        w, h = img.size

        if mode == "static" or (mode == "auto" and (w, h) == (FRAME_W, FRAME_H)):
            plate = img if (w, h) == (FRAME_W, FRAME_H) else \
                img.resize((FRAME_W, FRAME_H), Image.LANCZOS)
            plate.save(out)
            manifest.append({"plate": item["out"], "mode": "static",
                             "static": True, "width": FRAME_W,
                             "height": FRAME_H})
            print(f"{out}: static {FRAME_W}x{FRAME_H} (passed through)")
            continue

        plate = None
        if mode in ("auto", "full"):
            if mode == "auto" and w / h < args.min_aspect:
                print(f"{item['src']}: aspect {w / h:.2f} too tall -> split")
            else:
                plate = full_bleed(img, args.margin, args.max_upscale,
                                   forced=(mode == "full"))
                if plate is None:
                    print(f"{item['src']}: needs > {args.max_upscale}x upscale "
                          f"-> split")
        final_mode = "full" if plate is not None else "split"
        if plate is None:
            if not item.get("caption"):
                print(f"  WARNING: {item['out']} became a split panel with no "
                      f"caption — give it a real fact to carry")
            elif len(item["caption"].split()) > 18:
                print(f"  WARNING: {item['out']} caption is "
                      f"{len(item['caption'].split())} words — that is prose, "
                      f"not a label. The screen carries names, dates, and "
                      f"sources; the narration carries the sentences.")
            plate = split_panel(img, item.get("title", ""),
                                item.get("caption", ""), item.get("accent"),
                                args.max_upscale)

        plate.save(out)
        static = final_mode == "split"
        manifest.append({"plate": item["out"], "mode": final_mode,
                         "static": static, "width": plate.width,
                         "height": plate.height})
        print(f"{out}: {final_mode} {plate.width}x{plate.height}"
              f"{' (static)' if static else ''}")

    with open(os.path.join(args.outdir, "plates.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"{len(manifest)} plates -> {args.outdir}/ (+ plates.json)")


if __name__ == "__main__":
    main()
