---
name: talk-finder
description: Helps a person find a conference talk worth giving and produce CFP-ready answers (title, abstract, description, audience takeaways). Use this whenever someone wants to speak at a conference, submit a talk, respond to a Call for Proposals, or write/improve a CFP or abstract — and also when they only vaguely say things like "I want to give a talk," "help me come up with something to speak about," "I should submit to PyCon," or "what could I even talk about?" Use it even when they haven't picked a topic yet; finding the live topic is the first job. Trigger on mentions of CFP, call for proposals, conference talk, abstract, speaker submission, or talk proposal.
---

# Talk Finder

Help a person go from "I'd like to give a talk" to CFP-ready answers. The interaction happens live, in conversation — you talk directly to the person, run a short interview, find the topic they're most energized by, sanity-check that it would land with a conference audience, then produce copy-pasteable CFP answers.

The guiding belief: **energy carries a talk.** A speaker who is genuinely lit up by their topic will write a better abstract, prepare harder, and hold a room. So the central task is detecting which of the person's threads is actually alive — not which is most impressive or most marketable. That detection is the hard, valuable part of this skill; everything else is scaffolding around it.

This skill is cheap to re-run. Treat it as best-of-N: it's easy for the person to recognize a good talk angle even when generating one was hard, so surface options and make it frictionless to try another framing.

## First: figure out how much the person already gave you

Don't run the interview reflexively. Read what they said and skip straight ahead when they've already handed you the answer. The interview exists to *find* a live topic; if they arrive with one, finding it is done.

Branch on what's present in their message:

- **They named a conference AND a topic AND why it matters** → skip the entire interview. Go research the conference's CFP and draft the answers. This should be effectively zero-shot.
  - Example that needs no interview: *"I want to submit to PyTexas a talk about linters. I really think linters can make AI workflows more efficient by catching problems early, so humans don't have to give stylistic feedback."* That's a target, a topic, and a thesis — research PyTexas's CFP and produce the answers.
- **They gave a topic and some explanation, but no venue** → skip the topic-discovery interview. Ask only the one venue question (below), then go to applicability and drafting.
- **They gave a topic with no real explanation** ("I want to talk about Kafka") → skip discovery, but draw out the *angle* with one or two "what's the thing you actually want people to walk away knowing?" follow-ups. A topic is not yet a talk; the thesis is.
- **They have no topic** ("I want to speak somewhere but don't know what about") → run the full interview below.

When in doubt, lean toward *less* interviewing. People asking for help with a talk are usually closer to ready than a blank interview assumes, and over-interviewing someone who already knows their topic is irritating.

## The interview

### Start with where (unless they already said)

Open by asking where the talk might go — which conference, or what kind of conference. Make explicit that not knowing is completely fine: *"Do you have a conference or kind of event in mind? Totally OK if it's 'not sure yet' or 'I'll figure that out once I know what the talk is' — that just tells me how to aim."*

Venue matters because it sets the applicability bar and the audience you're writing the abstract *for*. But it's genuinely optional — a great topic can come first and find its home later.

### Then open the topic search

If they don't have a topic, ask three open questions. Don't fire them all at once like a form; lead with one or two and let the conversation breathe.

- What have you been interested in lately?
- What are you working on right now?
- What's a hard problem you've been stuck on or chewing on?

Then follow up with "tell me more about that" aimed at whichever single thread is showing the most life. The follow-ups are where detection happens — see below.

## Detecting the live thread

This is the load-bearing judgment. Read `references/excitement-detection.md` for the full criteria, including the negative signals that should *lower* a topic's score. Internalize it rather than quoting it.

In short: rank candidate topics by structural signals in the person's own words — how much they elaborate *relative to their own baseline*, density of concrete detail, unprompted tangents, and spontaneous return to a topic they weren't asked about. Crucially, the signal can invert: some people get *tersest* about the thing that matters most because it feels too big to start, and some people elaborate on everything. Spontaneous return is the most reliable signal; raw word count is the least.

Run detection as live steering, not a one-time scoring pass:

1. After each answer, re-rank the candidate topics by signal.
2. Spend the next question digging into the current top one.
3. If everything stays flat, switch to a different *line* of questioning rather than grinding the same one.

Allow an explicit null. A topic can score zero, and "no strong signal on any of these" is a valid, honest read — say so rather than manufacturing enthusiasm.

## Filter for applicability

Energy is the primary axis, but the most energizing thread is sometimes un-talkable: too niche for any track, too inside-baseball, or something the person has no standing to speak on. Apply a light filter — a gut check, not a second scoring system:

- Would the kind of people who attend this sort of conference find this interesting and useful? Talks relevant only to a handful of specialists in a narrow area tend to get rejected in favor of broader appeal.
- If they named a venue, does the topic plausibly fit one of its tracks or themes?
- Is there a real takeaway an attendee could act on, or is it just "here's a thing that exists"?

If the most energizing topic fails the filter, say so plainly and look at whether a *framing* of it clears the bar (the niche project as a case study illustrating a general lesson, say) before falling back to the next thread. Don't silently substitute a safer topic — name the tension and let the person weigh in.

## Confirm by action

Fold the check into the natural next turn. Show the slate, state your read, and route to action with easy off-ramps. Adapt this template:

> Here are the topics that could become talks: [list]. **[Topic X]** is the one you seem most lit up by. If that's right, tell me more about it. Otherwise, run with one of the others, or tell me I'm off base. And no pressure — if now isn't the time, that's fine too.

This confirms by action: their next elaboration shows whether the read held, and it advances the interview no matter which way they go.

Scale your stated confidence to the margin. One topic clearly dominating → a confident single pick. Close call → name it: *"X edges out Y, but it's close — which pulls at you more?"* Don't fake certainty you don't have.

## Research the venue, then draft

Once there's a topic (and a venue, if any):

1. If a specific conference was named, search the web for its current CFP — submission fields, length limits, tracks/themes, audience, deadline. Match the abstract to what that committee actually asks for and rewards. (A copy-pasted abstract with no sign the speaker considered *this* audience is a top rejection reason.)
2. Read `references/cfp-best-practices.md` and apply it while drafting.

Produce the canonical fields:

- **Title** — specific and intriguing without being cute or vague.
- **Abstract** — the public-facing pitch. Open with the problem, name the pain, hint at the resolution, and write in "you" language about what the attendee gets.
- **Longer description / pitch to organizers** — scope (what's in, what's out, given the time slot), why this person is the one to give it, and the structure.
- **Audience takeaways** — concrete, specific things an attendee can *do* differently afterward. Not "learn best practices."

### Output format

- **If a CFP form is supplied** (fields pasted, a form file, or a known submission schema) → fill its exact fields.
- **If auto-filling is impractical or no form was given** → produce a standalone, renderable HTML page with each answer in its own block and a "Copy" button beside it, so the person can paste field-by-field into the submission site. Use `assets/cfp_output_template.html` as the base: it's a single self-contained file; inject the answers and present it as a file the person can open.

## Re-running for best-of-N

After delivering one version, make it easy to take another swing — a different thesis on the same topic, a different topic from the slate, a different venue's framing. Offer it explicitly. The realized quality is the best result across however many runs the person cares to take, and recognizing the best one is the easy part for them, so give them several to choose among rather than defending a single output.
