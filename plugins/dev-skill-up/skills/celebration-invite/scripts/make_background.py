#!/usr/bin/env python3
"""Render the card background as a RASTER image.

Why this script exists: Chromium encodes CSS gradients into the PDF as
ShadingType 1/3 driven by a FunctionType 4 (PostScript calculator) function. With
an alpha stop, that function stores premultiplied colour and DIVIDES to
un-premultiply. Viewers whose PostScript interpreters treat the near-zero-alpha
branch differently render wildly wrong colours — a cream card comes out hot
magenta. It looks perfect locally and broken on the recipient's phone.

A baked PNG cannot be misinterpreted. Never put a gradient in the CSS.

Usage:
    python3 make_background.py --out img/bg.png
    python3 make_background.py --out img/bg.png \
        --base '#fbf5ea' --pool '#eee4ce' --highlight '#fffdf6'
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter


def hex2rgb(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def build(width, height, base, pool, highlight,
          pool_strength=1.0, highlight_strength=0.55, edge_strength=0.16,
          grain=1.6, blur=0.6, seed=7):
    W, H = width, height
    x, y = np.meshgrid(np.arange(W, dtype=np.float32),
                       np.arange(H, dtype=np.float32))
    nx, ny = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)

    # soft pool of deeper colour at the bottom centre
    d_bot = np.sqrt(((x - W / 2) / (W * 0.57)) ** 2 + ((y - H) / (H * 0.55)) ** 2)
    w_bot = np.clip(1 - d_bot, 0, 1) ** 1.4 * pool_strength
    # gentle highlight near the top centre
    d_top = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2
                    + ((y - H * 0.08) / (H * 0.62)) ** 2)
    w_top = np.clip(1 - d_top, 0, 1) ** 1.6 * highlight_strength
    # faint darkening toward the edges
    edge = np.clip((np.abs(nx) ** 3 + np.abs(ny) ** 3) * 0.55, 0, 1) * edge_strength

    img = base[None, None, :] * np.ones((H, W, 1), np.float32)
    img = img * (1 - w_bot[..., None]) + pool[None, None, :] * w_bot[..., None]
    img = img * (1 - w_top[..., None]) + highlight[None, None, :] * w_top[..., None]
    img = img * (1 - edge[..., None]) + pool[None, None, :] * edge[..., None]

    if grain:                                   # paper texture
        rng = np.random.default_rng(seed)
        img = img + rng.normal(0, grain, (H, W, 1)).astype(np.float32)

    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True)
    p.add_argument("--width", type=int, default=1500)    # 5in @ 300dpi
    p.add_argument("--height", type=int, default=2100)   # 7in @ 300dpi
    p.add_argument("--base", default="#fdf6e8")
    p.add_argument("--pool", default="#f6e7d2")
    p.add_argument("--highlight", default="#fffdf7")
    p.add_argument("--grain", type=float, default=1.6)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()

    im = build(a.width, a.height, hex2rgb(a.base), hex2rgb(a.pool),
               hex2rgb(a.highlight), grain=a.grain, seed=a.seed)
    im.save(a.out)

    arr = np.asarray(im).astype(int).reshape(-1, 3)
    warm = (arr[:, 0] >= arr[:, 1]).mean() * 100
    print(f"{a.out}  {im.size}  range {arr.min(0)}..{arr.max(0)}  "
          f"R>=G in {warm:.1f}% of pixels")


if __name__ == "__main__":
    main()
