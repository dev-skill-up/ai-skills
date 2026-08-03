# Publishing metadata: description, chapters, tags

A finished video is not a deliverable on its own. Any casual-essay or sleep-essay run must also emit **`youtube-description.txt`** and **`youtube-tags.txt`** alongside the MP4, and deliver them in the same `SendUserFile` call. This is a pipeline step, not a footnote — it was forgotten on the run this skill update comes from and had to be asked for.

Generate the whole thing with `assets/make_metadata.py` from `shots.resolved.json`, the credits manifest, and a small `meta.json` (hook text, chapter picks, sources, tags). **Writing it by hand guarantees it drifts from the video after the next re-render.**

## The description

Hard limit **5,000 characters** — check it and trim before delivering. A first attempt came in at 6,877 and had to be rewritten. Structure that fits:

1. **Hook, 2–4 short paragraphs.** Open on the concrete image the video opens on, not on a summary of the topic. State the single strangest true fact.
2. **CHAPTERS.** Generate from real narration timings, never by hand.
3. **SOURCES.** Name the actual primary literature — authors, journal, volume, year. Add one line on how disputes were handled.
4. **IMAGE CREDITS** — see below.
5. **Production note.** Tools used, and "no stock footage, no music" if true.

### Chapters

- Must start at `0:00`, need **at least three**, and each must run **at least 10 s** — or YouTube ignores the whole list.
- Derive them by picking segment indices from the script's structure and reading their start times out of the same `segment_start_times()` (`assets/seg_times.py`) the shot list uses, so chapters and picture changes agree.
- Aim for one every 60–90 s.
- Title them as *moments*, not sections: "Four, or six?" and "Book lice, petroleum, seventy-two years" beat "Numerals" and "Conservation".

### Image credits in the description

Include them even when the licence does not require it. Rules learned the hard way:

- **One compact line per unique image**, in shot order: `Subject - Author, Collection [licence]`. URLs blow the character budget — keep the full records in `CREDITS-images.md` and say where they live.
- **De-duplicate by plate**, not by shot; a reused image gets one credit.
- **Strip markdown when generating from your own manifest.** Pulling straight from a `**bold**` credits file put literal asterisks in the description.
- **Drop empty fields** rather than emitting `Author,  [PD]` with a dangling comma.
- **Lead with the licence position in one sentence** — "Every photograph here is Public Domain or CC0; nothing carries an attribution or share-alike obligation; credits are given anyway."
- **Disclose any honest substitution, with its timestamp.** If a card on screen says a picture is not what the narration is describing, repeat that in the description: "the card at 1:11 shows Seti I instead and says so on screen."
- Note that original diagrams and caption panels are free to reuse.

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
