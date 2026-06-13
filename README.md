# ai-skills

A collection of [Claude Agent Skills](https://agentskills.io) by Moshe Zadka.

This repo doubles as a **Claude Code plugin marketplace**, so you can install everything in it with two commands. It's also a plain folder of skills following the open `SKILL.md` standard, so the skills work in claude.ai, Cowork, the Claude API, and any other tool that reads Agent Skills.

## What's inside

Everything lives in one plugin, **`dev-skill-up`** — an "automated Moshe" that packages how I approach recurring knowledge work.

| Skill | What it does |
| :---- | :----------- |
| **talk-finder** | Interviews you to find the conference talk you're most energized to give, sanity-checks that it would land with an audience, then writes CFP-ready answers (title, abstract, description, audience takeaways). Works zero-shot too: tell it the conference, topic, and your angle and it drafts the whole thing. |

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
3. Upload a zip of the skill folder. A prebuilt one is in [`dist/talk-finder.zip`](dist/talk-finder.zip), or build your own:

   ```bash
   cd plugins/dev-skill-up/skills && zip -r ../../../dist/talk-finder.zip talk-finder
   ```

   The zip must contain a top-level `talk-finder/` folder whose name matches the `name` in its `SKILL.md`.

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
│           └── talk-finder/
│               ├── SKILL.md
│               ├── references/
│               ├── assets/
│               └── evals/         # test cases used to develop the skill
└── dist/
    └── talk-finder.zip            # prebuilt for claude.ai / Cowork upload
```

## Adding a new skill

Drop a new `<skill-name>/SKILL.md` (plus any `references/`, `assets/`) into `plugins/dev-skill-up/skills/`. Claude Code discovers it automatically — no change to `marketplace.json` or `plugin.json` needed. Commit, and users get it on their next `marketplace update`. (Versions track git commits, so there's no version number to bump.)

## A note on trust

These skills are plain Markdown instructions plus, in the case of `talk-finder`, one static HTML template. No scripts, no network calls, no dependencies — nothing executes on its own. You're encouraged to read any skill before enabling it.

## License

MIT — see [LICENSE](LICENSE).
