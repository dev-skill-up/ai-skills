# Sourcing images honestly

A single calm backdrop for a meditation or sleep essay is easy: an Unsplash CDN direct URL or `picsum.photos` via `assets/fetch_image.sh` is fine. A **casual essay is a different problem** — ~30 topical images, each of which must actually show what the narration claims, each carrying **no licence obligation whatsoever**. This file is that discipline, learned on a real documentary run.

## Tier A — "no obligation" — is the ONLY allowable tier

**Every image must be tier A: Public Domain, PD-old, PD-US, PD-art, CC0, or a US federal work. These licences carry zero obligation — no attribution requirement, no share-alike, no restriction of any kind — and nothing else is ever acceptable.** There is no lower tier in this pipeline: any licence that carries any obligation at all is rejected on sight. This is a fixed policy, not a preference — do **not** ask the user about licensing, and do not weigh an obligation-carrying image "just this once". Sourcing runs fully autonomously on this rule.

Getting this wrong is the single most expensive mistake in the run — it means re-sourcing every image and re-rendering. "Free for commercial use" on a stock site does **not** make an image tier A; only the licence string itself does. **Credit generously anyway**; zero obligation and the courtesy of credit are different things (see `references/publishing-metadata.md` for the credit format).

## The technique that makes tier A possible

Modern photographs of museum objects on Commons are overwhelmingly CC BY-SA. But **19th-century scholarly engravings, lithographs and facsimiles of the same objects are PD-old**, and in a documentary they often look better than a vitrine snapshot. When a tier-A photo doesn't exist, go looking for the 1867 engraving.

Also strong for tier A: botanical and medical plates (Köhler, Thomé, Sowerby), Library of Congress photochroms, early expedition photography, and any pre-1930 book plate on Internet Archive or Google Books.

## Sources, all verified reachable

- **Wikimedia Commons API** — the workhorse. Search, then read the licence.
- **The Met Open Access** — `collectionapi.metmuseum.org`; use only where `isPublicDomain` is true.
- **Getty Open Content**, **Rijksmuseum**, **NYPL Digital Collections**, **Yale**, **Library of Congress** (`?fo=json`), **Smithsonian Open Access**.
- **Internet Archive / Google Books / BHL** for book plates.
- **Unsplash CDN** for generic landscape/texture only.

> **GOTCHA — guessing `upload.wikimedia.org` paths returns HTTP 400.** The path contains an MD5 hash you cannot construct. Always resolve through the API.

```python
# resolve + verify licence in one call
api(action="query", titles=title, prop="imageinfo",
    iiprop="url|size|sha1|extmetadata", iiurlwidth="4000")
# then check extmetadata.LicenseShortName literally
OK = {"cc0", "public domain", "pd-old-100", "pd-us", "pd-art", "cc-pd-mark"}
```

Reject if the licence string contains `BY`, `SA`, `NC`, `ND` or `NoC` — do not interpret, just match. Set a descriptive User-Agent or requests may be refused.

Keep every result in a manifest as you go (`credits.json`: subject, author, collection, licence string, source URL, SHA-1) — the publishing metadata is generated from it later.

## Verifying an image you already have

**SHA-1 reverse lookup.** Hash the local bytes and ask Commons what file that is. This proves provenance instead of trusting a manifest:

```python
sha = hashlib.sha1(open(path,'rb').read()).hexdigest()
api(action="query", list="allimages", aisha1=sha, aiprop="url|extmetadata")
```

It only matches unmodified downloads. If you cropped the file, hash the original you kept in `images_raw/` — so **always keep the untouched original**. If nothing matches and you cannot re-verify, **replace the image**. On the source run one opening shot was dropped for exactly that reason and the replacement was better.

## Verification rules

1. **Check the picture shows what it claims.** A shot captioned "Heinrich Brugsch" was actually his brother Emil. Nobody catches this from a filename.
2. **A digitiser's rights claim is not the work's licence, but it is a signal.** Bayerische Staatsbibliothek stamps NoC-NC on scans of 1892 books. The work is PD; the claim is contestable. Don't argue — find another digitisation.
3. **Trim archival furniture.** Scans arrive with white mounts, colour calibration charts, accession labels and page margins. Auto-detect near-white borders and crop; check the result by eye.
4. **Re-verify a subagent's licence table yourself.** Spot-check at minimum.
5. **Never delete a manifest before the replacement exists.** Deleting the old one mid-swap orphaned the licence records for every image that hadn't been replaced, and they had to be re-derived by SHA-1.
6. **Resolution floor is context-dependent.** A 900 px portrait is unusable full-frame and perfectly good in a 700 px split-panel column. One image was wrongly rejected as "too small" when the real answer was to change the layout (see the split panel in `references/casual-essay.md`).

## When no honest image exists

Say so on screen. The source run had no freely-licensed photograph of a specific mummy, so the shot became a split panel headed **"Not her"**, showing a different mummy and explaining in the caption why. It is more interesting than the image would have been, and the film never implies something false. Prefer this over a misleading shot, and prefer it over a caption-only card when a related picture exists. Disclose the substitution in the description too, with its timestamp (`references/publishing-metadata.md`).
