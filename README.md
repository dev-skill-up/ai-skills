# ai-skills

A collection of [Claude Agent Skills](https://agentskills.io) by Moshe Zadka.

This repo doubles as a **Claude Code plugin marketplace**, so you can install everything in it with two commands. It's also a plain folder of skills following the open `SKILL.md` standard, so the skills work in claude.ai, Cowork, the Claude API, and any other tool that reads Agent Skills.

## What's inside

Everything lives in one plugin, **`dev-skill-up`** — an "automated Moshe" that packages how I approach recurring knowledge work.

| Skill | What it does |
| :---- | :----------- |
| **talk-finder** | Interviews you to find the conference talk you're most energized to give, sanity-checks that it would land with an audience, then writes CFP-ready answers (title, abstract, description, audience takeaways). Works zero-shot too: tell it the conference, topic, and your angle and it drafts the whole thing. |
| **celebration-invite** | Turns a restaurant reservation — usually a screenshot — into a calendar event with a real, routable street address, plus a print-quality 5×7″ invitation (PDF master and 1500×2100 PNG at 300 dpi). Resolves the venue's full address by web search, themes the card to the venue's cuisine, composes it from CC0 artwork, and verifies the PDF renders identically in every viewer. Runs unattended: it never blocks on a question and reports every assumption it made. |
| **meditation-video** | Makes narrated spoken-word videos — a warm voice over still imagery, rendered as a shareable MP4, fully offline (Kokoro for the open-source voice, ffmpeg for the video, no API keys or GPU). Three modes: **guided meditations** (paced with deliberate silence), **sleep essays** (long-form narrated deep-dives on obscure topics, written to fall asleep to), and **casual essays** (awake documentaries — many licence-verified images, original diagrams, slow pans and dissolves, plus YouTube description/chapters/tags). Handles the whole pipeline from writing the words with the right pacing through to the final render. |

More skills will be added to the same plugin over time.

## Install in Claude Code

```bash
claude plugin marketplace add dev-skill-up/ai-skills
claude plugin install dev-skill-up@ai-skills
```

Then just ask naturally ("help me write a CFP for PyCon", "I want to give a talk but don't know about what") or invoke a skill directly with `/dev-skill-up:talk-finder`. To get later additions, run `claude plugin marketplace update ai-skills`.

You can also pin to this repo from another project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ai-skills": { "source": { "source": "github", "repo": "dev-skill-up/ai-skills" } }
  },
  "enabledPlugins": { "dev-skill-up@ai-skills": true }
}
```

## Use in claude.ai or Cowork

claude.ai and Cowork don't install from third-party marketplaces — you upload a skill as a zip.

1. Turn on **Code execution and file creation** in **Settings → Capabilities**.
2. Go to **Customize → Skills**, click **+ → Create skill → Upload a skill**.
3. Upload a zip of the skill folder. Prebuilt ones are in [`dist/`](dist/), or rebuild them all:

   ```bash
   python3 scripts/build_dist.py
   ```

   Each zip contains a top-level folder whose name matches the `name` in its `SKILL.md`. The builder is deterministic (sorted entries, fixed timestamps), and CI fails if the committed zips don't match the skill tree.

## Use with the Claude API / Agent SDK

Skills run with the code-execution tool. Upload `dist/talk-finder.zip` as a file, or point the Python SDK's `files_from_dir` helper at `plugins/dev-skill-up/skills/talk-finder/`. See the [API skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

## Repository layout

```
ai-skills/
├── .claude-plugin/
│   └── marketplace.json          # the marketplace catalog
├── plugins/
│   └── dev-skill-up/
│       ├── .claude-plugin/
│       │   └── plugin.json        # the plugin manifest
│       └── skills/
│           ├── talk-finder/
│           │   ├── SKILL.md
│           │   ├── references/
│           │   ├── assets/
│           │   └── evals/         # test cases used to develop the skill
│           ├── meditation-video/
│           │   ├── SKILL.md
│           │   ├── references/    # script craft + Kokoro/ffmpeg deep-dive
│           │   └── assets/        # the pipeline scripts (setup, generate, build, render)
│           └── celebration-invite/
│               ├── SKILL.md
│               ├── references/    # the rendering + verification checklist
│               ├── scripts/       # background baking, CC0 sticker cleanup
│               └── assets/        # the 5x7in card template
└── dist/
    ├── talk-finder.zip            # prebuilt for claude.ai / Cowork upload
    ├── meditation-video.zip
    └── celebration-invite.zip
```

## Adding a new skill

Drop a new `<skill-name>/SKILL.md` (plus any `references/`, `assets/`) into `plugins/dev-skill-up/skills/`. Claude Code discovers it automatically — no change to `marketplace.json` or `plugin.json` needed. Run `python3 scripts/build_dist.py` to refresh `dist/`, commit, and users get it on their next `marketplace update`. (Versions track git commits, so there's no version number to bump.)

CI (`.github/workflows/ci.yml`) checks every push: `scripts/check_skills.py` validates SKILL.md frontmatter (name/description, naming rules, length limits), the marketplace and plugin manifests, that every `references/`/`assets/` path mentioned in a skill's Markdown exists, and that all asset scripts parse (`py_compile`, `bash -n`, JSON). It then rebuilds `dist/` and fails if the committed zips are stale.

## A note on trust

`talk-finder` is plain Markdown instructions plus one static HTML template — no scripts, no network calls, nothing that executes on its own.

`celebration-invite` ships two small Python scripts (image processing with PIL/numpy/scipy — no network calls of their own) and one static HTML template. The skill itself does reach the network as part of its job: web search to confirm the venue's address, and the Openverse API to fetch CC0 artwork. It also creates a calendar event through whichever calendar MCP server you have connected, or writes an `.ics` file if you have none.

`meditation-video` is different: it ships small, readable Python and shell scripts in its `assets/` that Claude runs as part of the pipeline. They install the open-source [`kokoro-onnx`](https://github.com/thewh1teagle/kokoro-onnx) package, download the Kokoro model weights, fetch a backdrop image, and call `ffmpeg`. Nothing runs on its own and there are no hidden network calls beyond those documented downloads — but because it does execute code and reach the network, you're especially encouraged to read the scripts before enabling it.

## License

MIT — see [LICENSE](LICENSE).
