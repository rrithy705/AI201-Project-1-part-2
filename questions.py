"""
Your test questions.

Milestone 2 asks you to write five questions your system should be able to
answer from your corpus, specific enough to have a right answer.

  ✗ "What are good dining halls?"          — no right answer
  ✓ "What do students say about wait times at Commons during lunch?"

Fill in `QUESTIONS` below. `expects` is a word or short phrase you'd expect a
correct answer to contain — you'll use it in unit 2 when you build a scorer,
and having written it now means you decided what "correct" meant before you saw
any results.

`OUT_OF_SCOPE` holds five questions your documents clearly don't cover. You
need these in Milestone 4 to find where your relevance cutoff belongs, and
again in unit 2, where `run_eval.py` runs them through the gate and writes what
happened into your run log — that's the evidence for criterion 3.

Swap them for your own if you like. Keep five of them either way: criterion 3
names a target of "4 of 5", and four of three is not a thing.
"""

QUESTIONS = [
    # Answer is in guide_brightwater.md, "Getting there".
    {
        "question": "How often does the train run from Brightwater to the regional hub on weekdays?",
        "expects": "eleven",
    },
    # Answer is in guide_seasons.md, "Summer" — NOT in the Halden Bay guide,
    # which is the point of including it.
    {
        "question": "Where should I park in Halden Bay in August?",
        "expects": "overflow",
    },
    # Answer is in guide_accessibility.md, "Straightforward".
    {
        "question": "Which town in the region is easiest to get around with limited mobility?",
        "expects": "Thornby Wells",
    },
    # Answer is in guide_eating.md — a market time, one of the few hard numbers
    # in the corpus.
    {
        "question": "What time does the Tuesday market in Brightwater finish?",
        "expects": "1pm",
    },
    # Answer is in guide_corry_vale.md, "Getting around".
    {
        "question": "Is there public transport within Corry Vale?",
        "expects": "no public transport",
    },
]

# Questions this region's guides do NOT answer, but which the relevance gate
# lets through anyway — every one scores under the 0.70 cutoff. Criterion 5 is
# measured against these. They are not out-of-scope in the OUT_OF_SCOPE sense:
# they are about the right places, and the retrieved chunks look plausible.
#
# "Is there a cinema in Kestrelford?" comes back at 0.366, closer than the
# fourth question above at 0.386 — a question the corpus genuinely answers. No
# cutoff separates these two groups, so the grounding prompt has to.
NEAR_MISS = [
    "Are dogs allowed on the beaches?",              # 0.649
    "What is the crime rate in Marchwood?",           # 0.523
    "How much does a hotel room cost per night?",     # 0.576
    "What is the population of Pellew Sands?",        # 0.422
    "Is there a cinema in Kestrelford?",              # 0.366
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]


def answered() -> list[dict]:
    """The questions you've actually filled in."""
    return [q for q in QUESTIONS if q.get("question", "").strip()]
