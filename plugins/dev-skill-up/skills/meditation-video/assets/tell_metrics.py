#!/usr/bin/env python3
"""Measure the grep-able AI-tell metrics for an essay draft.

Run after EVERY editing pass (see references/ai-tells.md for the procedure and
the per-~3,000-word targets). The point of measuring is that each pass removes
a tell and the tell comes back wearing different clothes — the comma-coda is
the paragraph-final kicker with its full stop swapped for a comma.

Two metrics from the reference are deliberately absent: named individuals and
slack sentences are judgment calls, counted in the structural review pass.

Usage:
    python3 tell_metrics.py ESSAY.md
"""
import collections
import re
import statistics
import sys

# Blocklist for the lexical pass. Zero hits is the target; extend freely.
AI_VOCAB = [
    r"\bdelv(?:e|es|ed|ing)\b", r"\btapestr(?:y|ies)\b",
    r"\bunderscor(?:e|es|ed|ing)\b", r"\ba testament to\b",
    r"\bboasts?\b", r"\bvibrant\b", r"\bnestled\b", r"\bpivotal\b",
    r"\bmyriad\b", r"\bplethora\b", r"\bmultifaceted\b", r"\bintricate\b",
    r"\bit is worth noting\b", r"\bin conclusion\b", r"\bstark reminder\b",
    r"\brich history\b", r"\bnot just\b[^.!?]*\bbut\b",
]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as fh:
        body = re.sub(r"^#.*$", "", fh.read(), flags=re.M)

    ps = [p.strip() for p in body.split("\n\n") if p.strip()]
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    w = [len(s.split()) for s in sents]

    # The comma-coda: [long clause], and [<=10-word flat coda].
    coda = [s for s in sents
            if re.search(r",\s+and\s+\S+", s)
            and len(re.split(r",\s+and\s+", s)[-1].split()) <= 10
            and len(s.split()) > 12]

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

    print(f"words {len(body.split())}  sentences {len(sents)}  "
          f"stdev {statistics.pstdev(w):.1f}")
    print(f"comma-coda {len(coda)}  (para-final {coda_final})")
    print(f"kickers {len(kick)}/{len(ps)} = {100 * len(kick) // max(1, len(ps))}%")
    print(f"initial-The {initial_the}  ,which {which}  em-dash {em_dashes}")
    print(f"'a X named Y' {named_appositive}  'In YEAR, Name' {in_year}  "
          f"first-person {first_person}")
    print(f"AI vocab hits {len(vocab_hits)}"
          + (f": {sorted(set(h.lower() for h in vocab_hits))}" if vocab_hits else ""))
    openers = collections.Counter(s.split()[0] for s in sents)
    print("openers:", openers.most_common(6))


if __name__ == "__main__":
    main()
