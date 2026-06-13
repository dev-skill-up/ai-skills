# Writing the script and timing the silence

The script is a sequence of short spoken cues separated by deliberate pauses. Writing it well is mostly about restraint: say less, leave more room, and trust the listener to do the practice in the quiet.

## The core principle: silence is the content

The space between words is where the listener actually meditates — processes the instruction, follows the breath, rests. Silence isn't a gap between the real material; it *is* the material. Concretely, in a finished guided meditation the spoken words usually fill only about a third of the runtime. A 5-minute meditation might contain 90 seconds of speech and three and a half minutes of quiet.

The most common failure mode is talking too much: narrating continuously so there's never room to follow along. If you're tempted to add words to fill time, add silence instead.

## The two pause lengths

Almost all pauses fall into two buckets. Pick based on what you just asked the listener to do.

- **Short, ≈3 seconds.** A breath-sized beat. Use during breath instructions and quick transitions where a long gap would break the rhythm you're establishing.
- **Long, ≈7–30 seconds.** Use after sending someone into a visualization, a body sensation, or a rest — anything where they need real time to actually be there. A 3-second pause feels brief; a 10-second pause feels spacious; 20–30 seconds of stillness in the open-awareness section feels luxurious and is correct.

The rule underneath both: **after any instruction, pause long enough for the person to do the thing before you say the next thing.**

## The arc

A reliable structure for a general mindfulness meditation, in order:

1. **Arrive / settle** — get them into position and signal there's nothing to achieve. Short pauses; you're just landing.
2. **Anchor on the breath** — bring attention to the breath without changing it; name where it's felt. Begin lengthening pauses.
3. **Work with the wandering mind** — *this is the actual skill being taught.* Name that attention will drift, that this is normal, and that noticing the drift and returning, without judgment, **is the practice.** Don't leave this implicit — it's the one instruction that makes mindfulness mindfulness. Follow it with a long pause so they can practice the return.
4. **Body** — widen to the whole body, contact points, weight, softening tension. Long pauses.
5. **Open awareness / rest** — drop the effort; just sit and be aware of whatever's present. The longest pauses of the whole piece live here.
6. **Close** — bring attention back to the room, invite eyes open, and end with an explicit verbal close (see below).

Other themes rearrange the middle: a body scan replaces steps 3–5 with a slow head-to-toe sweep; loving-kindness cycles phrases toward self and others; a sleep meditation drops the "return to the room" wake-up and lets the end dissolve. The arrive-anchor-…-close skeleton holds.

## Calibrate to the audience

The right amount of guidance depends on experience level:

- **Beginners** want a cue every 30–60 seconds. Too much unbroken silence and they drift off or start wondering whether they're "doing it right." More structure, gentler reassurance.
- **Experienced practitioners** want the opposite: long silences, minimal interruption, more trust.

When in doubt, write for beginners — it's the more common audience for a produced video, and over-cueing is a milder sin than abandoning someone in silence.

## Two rules that are easy to miss

- **Start almost immediately.** A long silent lead-in just makes the listener wonder if the audio is broken. Open within about half a second. (The `lead_in` field controls this.)
- **End with an explicit spoken close — never trailing silence.** When the words simply stop and fade into quiet, the listener is left unsure whether it's over, eyes closed, waiting. Say so: the practice is complete, and they can return to their day when ready. Then stop cleanly. (Keep the `tail` short — just enough to not clip the last word.)

## Tone and language

- Speak *to* the listener in "you" language, in the present tense.
- Short sentences. Simple words. One instruction at a time.
- Invitations, not commands: "you might notice," "see if it can soften," "when you're ready."
- Avoid jargon and anything that sounds clinical or saccharine. Warm and plain beats poetic and dense.
- Read it aloud. If a sentence is hard to say slowly and calmly, rewrite it.

## A note on TTS-friendly phrasing

Because a text-to-speech voice will read this, prefer commas and periods over dashes and ellipses for pauses inside a line — the model handles them more predictably. (The long pauses *between* lines are added as real silence later, not voiced by the model, so never write "[pause]" into the text.) The example script in `assets/meditation.example.json` is written this way.

## Sources

Best practices above are synthesized from:

- Mindfulness Exercises — *How to Write a Meditation Script*: https://mindfulnessexercises.com/how-to-write-a-meditation-script/
- GetStillMind — *How to Structure a Meditation Script*: https://getstillmind.com/blog/how-to-structure-meditation-script/
- PositivePsychology — *Guided Meditation Scripts*: https://positivepsychology.com/guided-meditation-scripts/
- Positivity.org — *Creating a Guided Meditation for Beginners*: https://positivity.org/meditation/creating-a-guided-meditation
