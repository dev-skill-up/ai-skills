#!/usr/bin/env python3
"""Strip baked-in backgrounds from CC0 "sticker" images.

Rawpixel (the best CC0 source Openverse indexes) serves URLs ending in .png that
actually return JPEG with a transparency CHECKERBOARD painted into the pixels.
Others sit on a solid coloured panel. Both must go before the art can be composed
onto a card.

A naive "make white transparent" destroys the artwork's own white areas (book
pages, cake panels). This uses connected-component analysis instead: only regions
that touch the border, or that carry the checkerboard's two-tone signature, are
removed.

Usage:
    python3 clean_sticker.py IMG [IMG ...]
    python3 clean_sticker.py sticker.png --key 253,222,199 --tol 26
    python3 clean_sticker.py sticker.png --auto-key      # detect the panel colour
    python3 clean_sticker.py sticker.png --suffix _cut --outdir cleaned/
"""
import argparse, os, sys
from collections import Counter

import numpy as np
from PIL import Image
from scipy import ndimage

CHECKER_LIGHT = 255          # the two checkerboard tones rawpixel uses
CHECKER_DARK = 238
NEUTRAL_MIN = 234            # a pixel this bright and this grey is background
NEUTRAL_SPREAD = 8           # max |R-G|,|G-B|,|R-B| to count as neutral


def _neutral_bright(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    neutral = ((abs(r - g) < NEUTRAL_SPREAD) & (abs(g - b) < NEUTRAL_SPREAD)
               & (abs(r - b) < NEUTRAL_SPREAD))
    return neutral & (r >= NEUTRAL_MIN)


def detect_panel_colour(arr):
    """Most common strongly non-neutral colour — usually a solid sticker panel."""
    a = arr.astype(np.int16)
    spread = a.max(axis=2) - a.min(axis=2)
    cand = arr[spread > 25]
    if not len(cand):
        return None
    colour, n = Counter(map(tuple, cand[::7])).most_common(1)[0]
    # only trust it if it covers a real area, else it is just artwork
    return colour if n * 7 > 0.04 * arr.shape[0] * arr.shape[1] else None


def clean(path, out, keys=(), tol=22, dilate=1, crop=True, verbose=True):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im)
    a = arr.astype(np.int16)
    r = a[..., 0]

    mask = _neutral_bright(a)
    for k in keys:
        kr, kg, kb = k
        mask |= ((abs(a[..., 0] - kr) < tol) & (abs(a[..., 1] - kg) < tol)
                 & (abs(a[..., 2] - kb) < tol))

    lab, n = ndimage.label(mask)
    if n == 0:
        Image.fromarray(np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)]),
                        "RGBA").save(out)
        return

    border = set(np.unique(np.concatenate(
        [lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]])))
    border.discard(0)
    kill = set(border)

    # Enclosed checkerboard: a region carrying BOTH tones in quantity. Genuine
    # solid-white interiors have only one tone and survive.
    for i in range(1, n + 1):
        if i in kill:
            continue
        sel = lab == i
        if sel.sum() < 400:
            continue
        v = r[sel]
        if (v >= CHECKER_LIGHT - 3).mean() > 0.2 and \
           ((v >= CHECKER_DARK - 6) & (v <= CHECKER_DARK + 6)).mean() > 0.2:
            kill.add(i)

    bg = np.isin(lab, list(kill))
    if dilate:                      # eat antialiased seams
        bg = ndimage.binary_dilation(bg, iterations=dilate)

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    o = Image.fromarray(np.dstack([arr, alpha]), "RGBA")
    if crop:
        box = o.getbbox()
        if box:
            o = o.crop(box)
    o.save(out)
    if verbose:
        opaque = 100.0 * (alpha > 0).mean()
        print(f"{out}  {o.size}  {opaque:.1f}% opaque")
        if opaque < 2:
            print("  WARNING: almost everything was removed — check --key/--tol",
                  file=sys.stderr)


def fade(path, out, factor):
    """Bake opacity into the alpha channel.

    Use this instead of CSS `opacity`, which makes Chromium emit PDF transparency
    groups. Keeping the PDF to plain images + text + solid fills is what makes it
    render identically in every viewer.
    """
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).copy()
    a[..., 3] = (a[..., 3].astype(np.float32) * factor).astype(np.uint8)
    Image.fromarray(a, "RGBA").save(out)
    print(f"{out}  faded to {factor:.0%}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("images", nargs="+")
    p.add_argument("--key", action="append", default=[],
                   help="extra background colour 'R,G,B' (repeatable)")
    p.add_argument("--auto-key", action="store_true",
                   help="detect a solid panel colour and key it out too")
    p.add_argument("--tol", type=int, default=22)
    p.add_argument("--dilate", type=int, default=1)
    p.add_argument("--no-crop", action="store_true")
    p.add_argument("--suffix", default="_clean")
    p.add_argument("--outdir")
    p.add_argument("--fade", type=float,
                   help="also write a *_fade.png at this alpha factor (0-1)")
    args = p.parse_args()

    keys = [tuple(int(v) for v in k.split(",")) for k in args.key]

    for src in args.images:
        arr = np.asarray(Image.open(src).convert("RGB"))
        k = list(keys)
        if args.auto_key:
            found = detect_panel_colour(arr)
            if found:
                k.append(found)
                print(f"{src}: auto-keyed panel {found}")
        stem, _ = os.path.splitext(os.path.basename(src))
        outdir = args.outdir or os.path.dirname(src) or "."
        os.makedirs(outdir, exist_ok=True)
        out = os.path.join(outdir, stem + args.suffix + ".png")
        clean(src, out, keys=k, tol=args.tol, dilate=args.dilate,
              crop=not args.no_crop)
        if args.fade is not None:
            fade(out, os.path.join(outdir, stem + "_fade.png"), args.fade)


if __name__ == "__main__":
    main()
