# Rendering and verification

Short on purpose. This is the part that gets skipped under time pressure, and it is the part that shipped broken output.

## Pipeline

```bash
chromium --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
         --print-to-pdf=out.pdf invite.html
pdftoppm -png -r 300 -singlefile out.pdf invitation      # 1500x2100 deliverable
```

`@page { size: 5in 7in; margin: 0 }` and `html,body { width:5in; height:7in }`. Without the `html,body` rule the page renders blank.

## NEVER use CSS gradients

Chromium encodes `radial-gradient` / `linear-gradient` into the PDF as ShadingType 1 or 3 with a FunctionType 4 (PostScript calculator) function. When a gradient has an alpha stop, that function stores premultiplied colour and divides to un-premultiply. Viewers whose PostScript interpreters handle the near-zero-alpha branch differently produce wildly wrong colours — **a cream card renders as hot magenta**. It looks perfect in your renderer and broken on the user's phone.

Instead:

- **Background**: bake it as a raster PNG with `scripts/make_background.py` (1500x2100 — base colour, soft radial pool, gentle highlight, faint edge darkening, ~1.6σ gaussian noise blurred 0.6px for paper grain). Reference it as `background-image:url(bg.png); background-size:5in 7in`.
- **Image opacity**: bake it into the alpha channel with `clean_sticker.py --fade 0.6`, never CSS `opacity` — that creates PDF transparency groups.

Goal: a PDF containing nothing but images, text, and solid-colour borders.

## Verify — every single time

**1. Look at the rendered PNG with your own eyes.** Read the image. Not a pixel histogram, not a colour sample. Sampling your own render only proves your renderer agrees with itself; it cannot catch a bug where a different viewer reads the same file differently. Blank pages, overlapping text, and clipped elements all pass numeric checks and are instantly obvious visually.

**2. Then run the programmatic checks:**

```bash
pdfinfo out.pdf | grep Pages                      # must be 1

qpdf --qdf --object-streams=disable out.pdf /tmp/q.pdf
grep -a -c "ShadingType" /tmp/q.pdf               # must be 0
grep -a -c "FunctionType 4" /tmp/q.pdf            # must be 0

pdftoppm  -png -r 150 -singlefile out.pdf check_splash
pdftocairo -png -r 150 -singlefile out.pdf check_cairo
```

Compare the two rasterizers in numpy. What matters is **not** the raw percentage of differing pixels — a card full of engraved line art and hairline rules measures ~3% differing at threshold 40, all of it one pixel wide, and that is fine. What matters is whether any *solid region* disagrees. Erode the difference mask: antialiasing and half-pixel rule placement vanish after a pixel or two, a misinterpreted shading does not.

```python
import numpy as np; from PIL import Image
from scipy import ndimage
a = np.asarray(Image.open("check_splash.png").convert("RGB"), float)
b = np.asarray(Image.open("check_cairo.png").convert("RGB"), float)
m = np.abs(a - b).max(axis=2) > 40
e = ndimage.binary_erosion(m, iterations=2)
if e.any():
    lab, n = ndimage.label(e)
    print("SUSPECT: largest solid blob",
          int(ndimage.sum(e, lab, range(1, n + 1)).max()), "px")
else:
    print("edge-only differences — clean")
```

A measured good card: 2.96% of pixels over threshold, but after 2px erosion nothing bigger than a single pixel survives. Any blob of a few hundred pixels means something in the PDF is interpretation-dependent — go find it.

Optional hue audit: sample the corners and blank areas and confirm `R > G > B` monotonically for a warm card. Any light-region pixel where blue exceeds green is a red flag.

## Fitting to one page

Overflow to page 2 is the most common failure. Don't guess how much to cut — measure it. Render page 2 alone and find its non-background rows; that is exactly how many inches to reclaim:

```bash
pdftoppm -png -r 100 -f 2 -l 2 out.pdf pg2
```

```python
import numpy as np; from PIL import Image
a = np.asarray(Image.open("pg2-2.png").convert("L"))
rows = np.where(a.min(axis=1) < 200)[0]
print("content rows", rows.min(), rows.max(), "→", (rows.max() + 1) / 100, "in to reclaim")
```

Reclaim it by shrinking the hero image, reducing the name font size, tightening margins, or **dropping the bottom ornament entirely**. Dropping one decorative element beats cramping everything.

## Two more traps

- **String-slicing CSS edits.** Removing a `body { }` block by index once swallowed the adjacent `html,body { width; height }` rule and produced a completely blank card that passed every numeric check. Edit by matching the rule text, then re-render and look.
- **Fonts.** `fc-list | grep -i "gyre chorus"` before relying on it. A missing script font silently falls back to the body serif and the card stops looking calligraphic — a change no numeric check will report.
