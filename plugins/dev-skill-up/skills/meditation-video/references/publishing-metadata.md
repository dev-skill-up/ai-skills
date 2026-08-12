# Publishing metadata: description, chapters, tags

A finished video is not a deliverable on its own. Any casual-essay or sleep-essay run must also emit **`youtube-description.txt`** and **`youtube-tags.txt`** alongside the MP4, and deliver them in the same `SendUserFile` call. This is a pipeline step, not a footnote — it was forgotten on the run this skill update comes from and had to be asked for.

Generate the whole thing with `assets/make_metadata.py` from a small `meta.json` (hook text, chapter picks, sources, tags) plus, for a casual essay, `shots.resolved.json` and the credits manifest. **Writing it by hand guarantees it drifts from the video after the next re-render.** For a sleep essay there is no shot list — `make_metadata.py` runs without one; put the backdrop's credit in `meta.json` as an `image_credits` line.

## The description

The description is for a **viewer deciding whether to watch**. It talks about the video's *subject* — never about the video, the pipeline, or the writing process. Things that must never appear:

- **Pipeline and tooling.** No "narrated with Kokoro TTS", no "assembled with ffmpeg", no voice names, speed settings, or "entirely offline". Nobody watching needs to regenerate the video.
- **Methodology self-description.** No sentences describing how the essay handles its material ("where the scholarship is unsettled the essay says so…"). The essay just *does* it; the description doesn't brag about it.
- **Licence grants or licence positions.** The description never tells viewers what they may reuse, never states that images "carry no attribution or share-alike obligation", never declares anything "free to reuse". We credit; we don't issue licences.
- **Negative inventory.** No "no stock footage", "no music", "no third-party imagery is used". Don't describe what the video isn't made of.

Hard limit **5,000 characters** — check it and trim before delivering. A first attempt came in at 6,877 and had to be rewritten. Structure that fits:

1. **Hook, 2–4 short paragraphs.** Open on the concrete image the video opens on, not on a summary of the topic. State the single strangest true fact.
2. **CHAPTERS.** Generate from real narration timings, never by hand.
3. **SOURCES.** Name the actual primary literature — authors, journal, volume, year. Nothing else: no note on how disputes were handled, no editorial framing.
4. **IMAGE CREDITS** — see below. Omit the section entirely when there is nothing to credit.

### Chapters

- Must start at `0:00`, need **at least three**, and each must run **at least 10 s** — or YouTube ignores the whole list.
- Derive them by picking segment indices from the script's structure and reading their start times out of the same `segment_start_times()` (`assets/seg_times.py`) the shot list uses, so chapters and picture changes agree.
- Aim for one every 60–90 s.
- Title them as *moments*, not sections: "Four, or six?" and "Book lice, petroleum, seventy-two years" beat "Numerals" and "Conservation".

### Image credits in the description

Credits are **credit for material we used — nothing more**. One line per third-party image naming whose work it is; no licence information, no reuse permissions, no commentary. Rules learned the hard way:

- **One compact line per unique third-party image**, in shot order: `Subject - Author, Collection`. URLs blow the character budget — keep the full records (links, licence strings) in `CREDITS-images.md`; those records are for our own verification, not for the description.
- **A sleep essay's single backdrop gets one credit line too** (e.g. `Backdrop - <photographer>, Unsplash`).
- **De-duplicate by plate**, not by shot; a reused image gets one credit.
- **Original material made for the video — diagrams, caption panels, plates — gets no line at all.** There is nobody to credit, so say nothing: no "made for this video", no "free to reuse", no licence statement.
- **Strip markdown when generating from your own manifest.** Pulling straight from a `**bold**` credits file put literal asterisks in the description.
- **Drop empty fields** rather than emitting `Author,` with a dangling comma.
- **Disclose any honest substitution, with its timestamp.** If a card on screen says a picture is not what the narration is describing, repeat that in the description: "the card at 1:11 shows Seti I instead and says so on screen."

## Tags

Hard limit **500 characters total**, comma-separated — YouTube silently drops the overflow, so trim programmatically until it fits. Roughly 25–30 tags, ordered most specific first, because the early ones carry the most weight:

1. The exact subject and its variants (`Liber Linteus`, `Liber Linteus Zagrabiensis`)
2. The field and adjacent objects a viewer might search (`Etruscan language`, `Pyrgi Tablets`, `epigraphy`, `decipherment`)
3. Named people and institutions in the video
4. Genre last (`documentary essay`, `video essay`, `history documentary`)

Skip generic single words like `history` or `ancient` on their own — they cost characters that a specific phrase would use better.

## Also worth emitting

If the person is publishing, offer:

- a **title under 60 characters**;
- **3–5 thumbnail frame suggestions with timestamps** — pick high-contrast diagram frames or a strong object shot;
- a **pinned-comment draft** carrying the source list if the description had to be trimmed (`make_metadata.py` writes one automatically when it trims).
