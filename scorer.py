"""
How I decide whether a question passed.

`run_eval.py` finds `judge` automatically and uses it to fill the Run columns
in the file it writes into `results/`.

What `judge` measures is **criterion 1**: did retrieval bring back a chunk that
contains the answer? Not "was the generated answer right" — that is a different
question, and mixing the two would leave me unable to tell a retrieval failure
from a generation one when a question fails.

I judge it against the retrieved chunks rather than against the printed output
of `python app.py retrieve`, because that command truncates each chunk to a
52-character preview. The answer to a question is usually further into the
chunk than that, so the preview cannot settle it. `results` here carries the
full text.

The `expects` string for each question lives in `questions.py` and was written
in unit 1, before I had seen any results.
"""


# Criterion 1 counts a hit only inside the top this many results.
#
# Unit 1 wrote the criterion against everything retrieval returned, which with
# TOP_K = 5 meant the whole list. That made the criterion measure two things at
# once — retrieval quality and the top-k setting — and the second one is a knob
# I can turn. Raising TOP_K to 10 would have "improved" it without improving
# anything. Three is the tightened bar; see the revision under criterion 1 in
# criteria.md.
TOP_N = 3


def judge(question: str, expects: str, answer: str, results) -> bool:
    """Criterion 1 — is the answer in the top `TOP_N` chunks retrieval returned?

    Case-insensitive, because the corpus writes "Thornby Wells" and my
    `expects` strings are lowercase. Substring rather than word matching,
    because two of my `expects` are phrases ("no public transport") and one is
    a time written without spaces ("1pm").
    """
    if not expects:
        return False

    needle = expects.strip().lower()
    return any(needle in (r.text or "").lower() for r in results[:TOP_N])


def hit_rank(expects: str, results) -> int | None:
    """Where the answer first appears in the ranking, or None if it doesn't.

    The rank is the diagnosis. "Passed" and "passed at rank 4 of 5" are very
    different states of health, and only the second one tells me how much room
    I had.
    """
    if not expects:
        return None

    needle = expects.strip().lower()
    for i, r in enumerate(results, 1):
        if needle in (r.text or "").lower():
            return i
    return None


def names_source(answer: str) -> bool:
    """Criterion 2 — does this answer name a source document?

    Every source in this corpus is a `.md` file and `build_prompt` in
    `generate.py` hands the model the filenames as `[from <filename>]`, so a
    `.md` in the answer text is the filename and nothing else.
    """
    return ".md" in (answer or "")


def refused(answer: str) -> bool:
    """Criteria 3 and 5 — did the system decline to answer?

    Criterion 5 asks for *exactly* the refusal line, so this compares against
    `gate.REFUSAL` instead of looking for "I don't" anywhere in the text. An
    answer that refuses and then guesses anyway is not a refusal.
    """
    import gate

    return (answer or "").strip() == gate.REFUSAL
