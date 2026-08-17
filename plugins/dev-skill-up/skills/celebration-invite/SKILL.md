---
name: celebration-invite
description: 'Turn a restaurant reservation — usually a screenshot, sometimes just a sentence — into a calendar event with a real street address plus a print-quality 5x7in invitation (PDF master and 1500x2100 PNG at 300 dpi), themed to the venue''s cuisine and built from CC0 artwork. Use whenever someone wants an invitation, an invite, a party invite, a save-the-date, or an RSVP card made; wants a birthday dinner, anniversary, graduation, or celebration dinner put on the calendar; pastes an OpenTable/Yelp/Resy/Tock reservation confirmation; or says "make an event and an invitation for X''s birthday", "create an invite for this dinner", or "add this reservation to my calendar and make me something to send people".'
---

# Celebration Invite

A reservation goes in; two things come out:

1. **A calendar event** with a real, routable street address in its `location` field.
2. **A 5x7in invitation** — a PDF print master plus a 1500x2100 PNG at 300 dpi. The PDF is for printing; the PNG is what people actually forward.

Produce both, always, unless the person asked for only one.

**This skill runs unattended.** Nobody is watching to answer a question or press a confirm button. So: never block on a question, never stage an event for later confirmation, and put every assumption you made into the final response — that is the only place the person learns what you decided, and one wrong assumption should cost one correction, not a re-read of the whole card.

## 1. Extract the reservation

From a screenshot, pull **venue name, date, time, party size**, and any address fragment. Confirmations from OpenTable, Yelp, Resy and Tock typically show a partial address — `680 Main St, Pleasanton` — with a city but no ZIP.

**Verify the weekday in code, not from memory.** If the screenshot says "Wednesday Aug 19", compute the real day for that date:

```bash
python3 -c "import datetime; print(datetime.date(2026, 8, 19).strftime('%A'))"
```

A mismatch means the year is wrong or you misread the date. Resolve it before anything else — everything downstream inherits the error.

## 2. Resolve the full address by web search — always

Never write an address you did not confirm. Search the venue name plus the street and city, then fetch the venue's own site or a local business directory and confirm **street, city, state, ZIP, and phone**. Screenshots routinely omit the ZIP, and a venue name alone is often ambiguous — several unrelated restaurants share a name across different states.

If the screenshot gives no city at all and the search returns more than one plausible venue: **pick the best-supported match, build everything from it, and name the choice in your response.** Do not stop to ask, and do not invent an address you could not confirm.

While the venue page is open, also grab:

- **Cuisine or concept.** This drives the entire visual theme (§5) and is the difference between a made card and a generated one.
- **Hours for that specific weekday.** If the reservation time falls outside them, flag it — that usually means the screenshot was misread.

## 3. Create the calendar event

Backend, in priority order:

1. **Any connected calendar MCP server.** Discover it at runtime rather than assuming a provider — look for tools that create calendar events, list calendars, or compose events, and use whatever is connected.
2. **No calendar connected → write an `.ics` file** and deliver it with the invitation. A standard VEVENT with `UID`, `DTSTAMP`, `DTSTART;TZID=`, `DTEND`, `SUMMARY`, `LOCATION`, `DESCRIPTION` imports cleanly into every major calendar app. Say plainly in your response that no calendar was connected and the `.ics` is the substitute.

Event content:

- **Title** — `<Name>'s Birthday Dinner 🎂`, or the appropriate occasion.
- **Start** — the reservation time. **Duration: 2 hours** unless told otherwise; restaurant reservations are almost never one hour.
- **Timezone** — set it explicitly from the venue's actual location (a Pleasanton, CA restaurant is `America/Los_Angeles`). Never let it default: the person may not be in the venue's timezone.
- **`location`** — `<Venue>, <street>, <city>, <ST> <ZIP>`, the full string, so maps apps can route to it.
- **`description`** — party size, the address again on its own line, and the venue phone. People open the event on their phone when they are lost or running late.

**Create the event directly. Do not stage it.** Some calendar tools offer a "compose" or "stage" mode that drops the event into a confirmation widget instead of committing it (Fastmail's `compose_event` is one). Do not use it — a staged event nobody confirms is a silently missed dinner. Use the direct create/commit tool. If the only available tool stages, commit it by whatever follow-up the provider offers and say clearly in your response that the event may need confirmation.

Everywhere else the reservation is ambiguous, take the most reasonable reading and proceed. Sensible defaults: **2-hour duration**, the **venue's timezone**, **no age number** on the card (you rarely know it), and the occasion inferred from how the request was phrased.

## 4. Source CC0 artwork

Use the Openverse API — no key, and it filters by licence server-side:

```
https://api.openverse.org/v1/images/?q=<terms>&license=cc0&extension=png&page_size=6
```

Join query terms with `+`; read `title`, `source`, `url` from `results`. Because `license=cc0` filters at the API level, **every result is already cleared** — do not hand-audit licences afterwards, and do not fall back to unfiltered image search.

Search for transparent, sticker-style art: `"<subject> png sticker"` and `"<subject> png sticker vintage"` return clean cut-out illustrations rather than photographs. **Vintage botanical and engraving-style results compose far better on a card than modern clip art.**

### The checkerboard trap — this WILL bite you

Rawpixel, the highest-quality CC0 source Openverse indexes, serves URLs ending in `.png` that return **JPEG with a transparency checkerboard baked into the pixels**. Check the actual bytes with `file`; never trust the extension.

Strip it programmatically — the pattern is pure `#ffffff` and `#eeeeee` squares. A naive "make white transparent" destroys the artwork's own white areas (book pages, cake panels), so `scripts/clean_sticker.py` uses connected-component analysis instead: build a mask of neutral pixels (R≈G≈B) at or above ~234, label components, kill every component touching the border, also kill enclosed components whose pixels are ≥20% pure-255 **and** ≥20% ~238 (that two-tone signature is checkerboard trapped inside the artwork; genuine solid-white interiors carry only one tone and survive), dilate the kill mask one pixel to eat antialiased seams, then crop to `getbbox()`.

```bash
python3 scripts/clean_sticker.py img/toucan.png img/hibiscus.png img/cake.png
python3 scripts/clean_sticker.py img/palm.png --fade 0.60      # corner sprigs
python3 scripts/clean_sticker.py img/panel.png --auto-key      # solid colour panel
```

`--fade 0.60` writes `<stem>_fade.png` — from `palm.png` you get `palm_clean.png` and `palm_fade.png`, so reference `palm_fade.png` as the corner asset.

Some stickers sit on a solid coloured rectangle (a peach or pastel panel) rather than a checkerboard. `--auto-key` samples the most common non-neutral colour and keys it out within a tolerance of ~20–28; `--key R,G,B --tol 26` sets it by hand. `--auto-key` can latch onto a dominant colour that belongs to the artwork (the green of a leaf, say) — the connected-component pass usually spares it anyway, but that is precisely what the contact sheet is for.

**Always build a contact sheet and look at it before composing:**

```bash
montage img/*_clean.png -tile 3x2 -geometry +5+5 -background '#fbf5ea' contact.jpg
```

Then actually read `contact.jpg`. Background removal fails in ways that are obvious to the eye and invisible to a pixel count.

## 5. Design the card

**Theme the card to the venue's cuisine or concept, not to a generic birthday template.** A literature-themed Mediterranean restaurant gets an open book, parchment and Art Nouveau ornament; a South American restaurant gets a toucan engraving, hibiscus and palm fronds. This single choice is what makes the output feel made rather than generated.

When producing a set of invitations for the same family or friend group, **keep the layout and typography identical and vary only palette and motifs**, so they read as siblings.

### Fonts

Verify with `fc-list` before relying on any of these:

- **TeX Gyre Chorus** — chancery script. The honoree's name and short flourish lines. It is the whole reason the card looks calligraphic rather than word-processed.
- **TeX Gyre Pagella** — body serif.
- **Poppins** — letterspaced uppercase for eyebrows, labels, and the address line.
- **Noto Color Emoji** — declare it in the font stack so emoji render in colour.

```bash
fc-list : family | tr ',' '\n' | grep -iE "gyre chorus|gyre pagella|poppins|color emoji" | sort -u
```

If one is missing, install it (`apt-get install fonts-texgyre` covers Chorus and Pagella) or substitute a near equivalent in the stack — a geometric sans such as Montserrat stands in for Poppins. Never leave a missing script font to fall back silently; the card stops looking calligraphic and no numeric check reports it.

### Layout that works

5in × 7in, roughly this vertical rhythm — `assets/template.html` implements it with `{{TOKEN}}` placeholders:

```
eyebrow          YOU ARE INVITED           (Poppins, .30em letterspacing)
hero image       themed line art, ~1.0–1.6in
flourish         "Once upon a time…"       (Chorus)
NAME             large Chorus, 37–46pt, accent colour
subtitle         BIRTHDAY DINNER           (Poppins caps)
divider art      floral / botanical, ~1.0–2.4in
─────────────────────────────────────────
venue name       larger, accent colour, with a themed emoji
address line     STREET · NEIGHBOURHOOD, ST (Poppins, ~7.2pt)
date / time / party size, one emoji + one line each
─────────────────────────────────────────
cake             with the honoree's initial overlaid on the cake's blank panel
closing line     two lines of Chorus + a couple of emoji
footer           PLEASE ARRIVE A LITTLE EARLY · 🎉
```

A double-rule frame inset ~0.22in plus four corner sprigs (rotated and mirrored copies of one botanical asset) reads as a real card. **The initial on the cake costs three lines of CSS and is the thing people notice.**

### Filling the template

```python
import re

t = open("assets/template.html").read()
vals = {
    "INK": "#33352b", "ACCENT": "#a8321c", "SECONDARY": "#1f5f4b",
    "GOLD": "#c99a3f", "MUTED": "#8a6a2b", "PAPER": "#fbf5ea",
    "HERO_WIDTH": "1.02in", "NAME_SIZE": "37pt", "DIVIDER_WIDTH": "1.02in",
    "CORNER_ASSET": "palm_fade.png",
    "HERO_ASSET": "toucan_clean.png",
    "DIVIDER_ASSET": "hibiscus_clean.png",
    "FLOURISH": "Come feast with us&hellip;",
    "NAME": "Zoya", "OCCASION": "Birthday Dinner", "INITIAL": "Z",
    "VENUE_EMOJI": "\U0001F334", "VENUE": "Oyo",
    "STREET": "680 Main Street", "NEIGHBOURHOOD": "Downtown Pleasanton, CA",
    "DATE_LONG": "Monday, August&nbsp;24",
    "TIME_WORDS": "6:00 in the evening",
    "PARTY_SIZE_WORDS": "A table for six",
    "CLOSING_LINE_1": "South American plates, candles,",
    "CLOSING_LINE_2": "and a toast to Zoya ✨\U0001F382",
    "FOOTER": "Please arrive a little early &middot; \U0001F389",
}
for k, v in vals.items():
    t = t.replace("{{%s}}" % k, v)

# fail loudly on anything left unfilled in the body
left = set(re.findall(r"\{\{[A-Z_0-9]+\}\}", t.split("</style>")[1]))
assert not left, f"unfilled tokens: {left}"
open("invite.html", "w").write(t)
```

`PAPER` must match `--base` of the background (below), or a hairline of the wrong colour shows at the page edge.

## 6. Render

Read **`references/rendering.md` before rendering** — it is one screen and it holds the bug that matters most.

The short version: **never put a CSS gradient in the card.** Chromium encodes gradients as PDF ShadingType 1/3 with a FunctionType 4 (PostScript calculator) function; with an alpha stop, that function stores premultiplied colour and divides to un-premultiply, and viewers whose interpreters handle the near-zero-alpha branch differently render wildly wrong colours. A cream card comes out **hot magenta** — perfect in your renderer, broken on the recipient's phone. Bake the background as a raster PNG instead, and bake image opacity into the alpha channel rather than using CSS `opacity` (which emits transparency groups). The target is a PDF containing nothing but images, text, and solid-colour borders.

Full build sequence:

```bash
# 1. background, tuned to the venue's palette
python3 scripts/make_background.py --out img/bg.png \
        --base '#fbf5ea' --pool '#eee4ce' --highlight '#fffdf6'

# 2. clean the downloaded CC0 stickers (§4), then LOOK at the contact sheet

# 3. fill the template (python above), then render
chromium --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
         --print-to-pdf=out.pdf invite.html
pdftoppm -png -r 300 -singlefile out.pdf invitation     # the 1500x2100 deliverable
```

Playwright's Chromium at `/opt/pw-browsers/chromium-*/chrome-linux/chrome` is fine — **never run `playwright install`**.

## 7. Verify — every single time

**Look at the rendered PNG with your own eyes before delivering.** Read the image; not a pixel histogram, not a colour sample. Sampling your own render only proves your renderer agrees with itself — it cannot catch a bug where a different viewer reads the same file differently. Blank pages, overlapping text and clipped elements all pass numeric checks and are instantly obvious visually.

Then the programmatic checks:

```bash
pdfinfo out.pdf | grep Pages                      # must be 1
qpdf --qdf --object-streams=disable out.pdf /tmp/q.pdf
grep -a -c "ShadingType" /tmp/q.pdf               # must be 0
grep -a -c "FunctionType 4" /tmp/q.pdf            # must be 0
pdftoppm  -png -r 150 -singlefile out.pdf check_splash
pdftocairo -png -r 150 -singlefile out.pdf check_cairo
```

Compare the two rasterizers in numpy, and judge by **eroding** the difference mask rather than by counting differing pixels — a card full of line art and hairline rules legitimately differs on ~3% of pixels, all of it one pixel wide, while a misinterpreted shading leaves a solid blob that survives erosion. **Overflow to page 2 is the most common failure**; measure the overflow instead of guessing at it (`pdftoppm -f 2 -l 2`, find the non-background rows) and reclaim the space by shrinking the hero, dropping the name font size, tightening margins, or dropping the bottom ornament outright. Dropping one decorative element beats cramping everything. Both procedures, with the numpy snippets, are in `references/rendering.md`.

## 8. Deliver

Send the **PNG and the PDF together** with a one-line caption. Then, in the response, state:

- **The event that was created** — or the `.ics`, if no calendar was connected — with the full address and the confirmed timezone.
- **The venue's hours that day**, if you checked them. It reassures the person that the reservation time is real.
- **Anything you dropped or assumed**, one line each. If you cut the bottom ornament to fit one page, say so. If you chose between two venues of the same name, say which and why.

Do not narrate the rendering pipeline unless something went wrong.

## 9. Dependencies

Verify rather than assume; install what is missing.

```bash
for c in pdftoppm pdftocairo pdfinfo qpdf convert montage identify fc-list; do
  printf "%-12s %s\n" "$c" "$(command -v $c || echo MISSING)"; done
python3 -c "import PIL, numpy, scipy; print('python imaging ok')"
ls /opt/pw-browsers/chromium-*/chrome-linux/chrome
```

`apt-get update && apt-get install -y poppler-utils qpdf imagemagick fonts-texgyre` covers the CLI side (`apt-get update` first — a stale index 404s); `pip install pillow numpy scipy` covers Python. Chromium comes from Playwright's copy; **never run `playwright install`**.

## Files

- `references/rendering.md` — the no-gradients rule and the verification checklist. One screen. Read it before rendering.
- `scripts/make_background.py` — bakes the card background as a raster PNG (base colour, radial pool, highlight, edge darkening, paper grain). Exists so the CSS never needs a gradient.
- `scripts/clean_sticker.py` — strips rawpixel checkerboards and solid panels from CC0 stickers by connected-component analysis; `--fade` bakes opacity into alpha.
- `assets/template.html` — the 5x7in card with `{{TOKEN}}` placeholders, correct `@page` sizing, the double-rule frame, corner sprigs, and the monogram-on-cake detail.
