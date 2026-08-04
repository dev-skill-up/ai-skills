#!/usr/bin/env python3
"""Measure the grep-able AI-tell metrics for an essay draft.

Run at the mechanical stage of EVERY convergence-loop cycle (see
references/ai-tells.md): mechanical findings get fixed before any subagent
review is paid for, and any fix restarts the cycle from the top. Audio is
gated on one full cycle returning zero findings from every pass, so the final
clean cycle must include a clean run of this script.

First person and metanarration target 0 — those tells are banned outright.
Every other target has a stated reason for its residual in ai-tells.md, and a
number sitting on its boundary is a finding to read, not a green light.

The metanarration count here is a directional floor, not a measurement: the
register pass (3b) supplies the true figure. One metric from the reference is
deliberately absent — named individuals is a judgment call, counted in the
structure pass (3a). The old "slack sentences >= 4" floor is gone entirely;
it contradicted the cut pass.

Usage:
    python3 tell_metrics.py ESSAY.md
"""
import collections
import re
import statistics
import sys

# Blocklist for the lexical pass. Zero hits is the target. Phrase-shaped
# tells only — a structure-shaped tell belongs to a pass with a question,
# never to this list (see "What not to do" in references/ai-tells.md).
# Resist growing it: this list once went from 0 to 18 hits on unchanged
# text, because every entry scores future essays against the last essay's
# mistakes.
AI_VOCAB = [
    r"\bdelv(?:e|es|ed|ing)\b", r"\btapestr(?:y|ies)\b",
    r"\bunderscor(?:e|es|ed|ing)\b", r"\ba testament to\b",
    r"\bboasts?\b", r"\bvibrant\b", r"\bnestled\b", r"\bpivotal\b",
    r"\bmyriad\b", r"\bplethora\b", r"\bmultifaceted\b", r"\bintricate\b",
    r"\bit is worth noting\b", r"\bin conclusion\b", r"\bstark reminder\b",
    r"\brich history\b", r"\bnot just\b[^.!?]*\bbut\b",
    # Unattributed rumor hedges — attribute to a real source or omit.
    r"\bit is said\b", r"\bsome say\b", r"\blegend has it\b",
    r"\brumou?r has it\b",
    # Narrating what the essay is not — excise, don't reword.
    r"\bevery(?:body|one) knows\b", r"\bthis is not that\b",
    # Narrator guesses — keep the fact, drop the speculation.
    r"\bmy guess\b", r"\bone suspects\b", r"\bnobody (?:writes down|knows) why\b",
    # Negation transitions ("Not to the crash. To a foundry…") — the
    # sentence-initial anchor keeps ordinary mid-sentence "not to" out.
    r"(?m)(?:^|[.!?]\s+)Not (?:to|the|that)\b",
    # Performed failure — fix the draft, don't narrate the fixing.
    r"\bshould have (?:been )?(?:said|mentioned|flagged|introduced|explained)\b",
    r"(?m)(?:^|[.!?]\s+)Sorry\b",
    # Self-commenting flourish ("Three superlatives, none of them good").
    r"\b(?:Two|Three|Four|Five) \w+s?, (?:none|all|each|neither) of (?:them|which)\b",
    # Narrated transitions — make the move, don't announce it.
    r"\b(?:jump|skip|flash|fast-forward) (?:forward|back|ahead)\b",
    r"\bbelongs here\b",
    # Manufactured doubt — report the documented conclusion instead.
    r"\bnever gets? resolved\b", r"\bnothing in the record\b",
    r"\buncomfortable (?:coincidence|truth|question)\b",
]

# Metanarration — the essay talking about or grading its own telling.
# Target 0: the tell is banned outright. A regex is necessarily incomplete
# for a structure-shaped tell, so this count is a directional FLOOR that
# makes the trend between cycles visible; the register pass (3b) supplies
# the true figure by asking, sentence by sentence, "is the subject the topic
# or the telling of the topic?". Do not grow this list to chase instances a
# pass should catch.
METANARRATION = [
    r"\bthis (?:episode|essay|video|film|story|section|chapter)\b",
    r"\bthis is the part (?:of|where)\b",
    r"\bonly sentence\b",
    r"\bwill be (?:quick|brief) about\b",
    r"(?m)(?:^|[.!?]\s+)As (?:to|for) why\b",
    r"\b(?:stupidly|absurdly|laughably|comically) "
    r"(?:mundane|simple|banal|small|ordinary|boring)\b",
    # Shape patterns: deixis at the telling, deferral, pre-grading.
    r"\bhere is (?:the|a|an|what|where|why|how)\b",
    r"\bmore on (?:that|this|him|her|them) (?:later|shortly|in a moment)\b",
    r"\b(?:as|so) (?:we|you)(?: will|'ll| have)? (?:see|seen|saw)\b",
    r"\b(?:worth|bears) (?:noting|mentioning|repeating)\b",
]

# The flat coda: [clause][separator] [<=10-word flat coda]. Originally only
# ", and" was counted; the failed run shipped the same shrug behind an em
# dash ("— it does not need to") while the comma count read fine and the
# em-dash total sat inside its target. Count the shape across all four
# punctuation mutations, each reported explicitly, so a zero that was looked
# for is distinguishable from a category that was never counted.
CODA_SEPARATORS = {
    ", and": r",\s+and\s+",
    "—": r"\s*—\s*",
    ";": r";\s+",
    ":": r":\s+",
}


def coda_kind(sentence):
    """Return the separator name if the sentence ends in a flat coda."""
    if len(sentence.split()) <= 12:
        return None
    for kind, pat in CODA_SEPARATORS.items():
        parts = re.split(pat, sentence)
        if len(parts) > 1 and 0 < len(parts[-1].split()) <= 10:
            return kind
    return None


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as fh:
        body = re.sub(r"^#.*$", "", fh.read(), flags=re.M)

    ps = [p.strip() for p in body.split("\n\n") if p.strip()]
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    w = [len(s.split()) for s in sents]

    coda = {s: k for s in sents if (k := coda_kind(s))}
    coda_by_kind = collections.Counter(coda.values())

    def last(p):
        return [x for x in re.split(r"(?<=[.!?])\s+", p) if x.strip()]

    coda_final = sum(1 for p in ps if last(p)[-1] in coda)

    # Kicker paragraphs, INCLUDING standalone one-liners — a one-line paragraph
    # is the same tic with a spotlight on it, and skipping it once hid a 58%
    # rate behind a reported "6".
    kick = [p for p in ps if len(last(p)[-1].split()) < 12
            and (len(last(p)) > 1 or len(p.split()) < 12)]

    initial_the = sum(1 for s in sents if s.startswith("The "))
    which = len(re.findall(r",\s+which\b", body))
    em_dashes = body.count("—")
    named_appositive = len(re.findall(
        r"\ban? [A-Za-z]+(?: [a-z]+)? named [A-Z]", body))
    in_year = len(re.findall(r"\bIn \d{4}, [A-Z]", body))
    first_person = len(re.findall(r"\bI\b|\bI'[a-z]+\b", body))
    vocab_hits = [m.group(0) for pat in AI_VOCAB
                  for m in re.finditer(pat, body, flags=re.I)]
    meta_hits = [m.group(0) for pat in METANARRATION
                 for m in re.finditer(pat, body, flags=re.I)]

    print(f"words {len(body.split())}  sentences {len(sents)}  "
          f"stdev {statistics.pstdev(w):.1f}")
    print("coda  "
          + "  ".join(f"'{k}' {coda_by_kind.get(k, 0)}" for k in CODA_SEPARATORS)
          + f"  total {len(coda)}  (para-final {coda_final})")
    print(f"kickers {len(kick)}/{len(ps)} = {100 * len(kick) // max(1, len(ps))}%")
    print(f"initial-The {initial_the}  ,which {which}  em-dash {em_dashes}")
    print(f"'a X named Y' {named_appositive}  'In YEAR, Name' {in_year}  "
          f"first-person {first_person}")
    print(f"metanarration (regex floor) {len(meta_hits)}"
          + (f": {sorted(set(h.lower() for h in meta_hits))}" if meta_hits else ""))
    print(f"AI vocab hits {len(vocab_hits)}"
          + (f": {sorted(set(h.lower() for h in vocab_hits))}" if vocab_hits else ""))
    openers = collections.Counter(s.split()[0] for s in sents)
    print("openers:", openers.most_common(6))


if __name__ == "__main__":
    main()
