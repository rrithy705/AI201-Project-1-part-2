# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

The five questions are in `QUESTIONS` in `questions.py`, each with the word an
answer has to contain. A stranger can check this by running
`python app.py retrieve "<question>"` and looking for that word in the five
chunks that come back.

**Why this target:** 4 of 5 rather than 5 of 5 because in this corpus the answer
is often in a different document from the one the question names. "Where should
I park in Halden Bay in August?" is answered in `guide_seasons.md`, not in
`guide_halden_bay.md`, and "which town is easiest to get around with limited
mobility" is answered in `guide_accessibility.md`, which came back at rank 4 of
5 — one place from falling off the list entirely. With `TOP_K = 5`, the question
I expect to lose is one whose answer sits in a cross-cutting guide rather than
in the town guide the question names.

> **Revised in unit 2:** For at least 4 of my 5 test questions, the **top three**
> retrieved chunks include one that contains the answer.
>
> **Why revised:** the original measured two things at once and I could not tell
> them apart. "The retrieved chunks" means whatever `TOP_K` happens to be, so
> the criterion scored retrieval quality *and* a setting in `config.py` that I
> control. I could have raised `TOP_K` to 10 and "improved" this criterion
> without improving retrieval at all. Naming a fixed three makes it a fact about
> the ranking instead of a fact about my configuration.
>
> This is not a lower bar. At top-5 the original scored 5 of 5; at top-3 the
> same three runs score 4 of 5, because the accessibility question's answer came
> back at rank 4 — exactly the failure I predicted above, one position from
> falling off the list, and the loose version could not see it. The target stays
> at 4 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

A stranger can check this by running all five questions and looking for a `.md`
filename in each answer.

**Why this target:** all five and not four, because three separate things have
to fail at once for a filename to go missing. `build_prompt` in `generate.py`
prefixes every excerpt with `[from <filename>]`; the chunk text itself opens
with the place and section, because my chunker puts it there; and
`GROUNDING_INSTRUCTION` tells the model to name the file. The only failure I can
picture is the model paraphrasing an answer and dropping the filename on its
own, which would be a generation-stage fault rather than a retrieval one — so if
this one misses, I already know which stage to look in.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about
that" — in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** there is a clean gap with nothing sitting in it. My five
test questions come back at **0.216–0.386**; the five in `OUT_OF_SCOPE` come
back at **0.810–0.969**. The cutoff at 0.70 sits 0.11 below the nearest
out-of-corpus question, and all five refuse today. I still wrote 4 of 5 rather
than 5 of 5 because those distances are measured against *these* chunk
embeddings — if I change the chunking in unit 2, as I might, every number in
both groups moves and the gap could close from either side.

---

## 4. Chunks stand on their own

At least 4 of any 5 chunks printed by `python app.py chunks -n 5` stand on their
own: each begins and ends at a sentence boundary, names in its first line the
place or guide it came from, and answers something without the text around it.
Separately, no chunk in the index is shorter than 150 characters.

A stranger can check the first half by reading five printed chunks, and the
second by running `python app.py index` and reading the "shortest" figure in the
summary line it prints.

**Why this target:** 150 characters because the real sections in these documents
run 175 to 710, so anything below 150 is not a short section — it is a section
that got cut. The starter's chunker produced a 24-character chunk on this
corpus: a heading with nothing underneath it. The "names its place" half matters
because nine of my fourteen documents are town guides carrying the *same seven
headings*, so a chunk that says only "When to go" is ambiguous to a reader and
to the embedding alike.

4 of 5 and not 5 of 5 because of the Overview chunks — the intro paragraph of
each town guide, which my chunker keeps as a chunk of its own. The accessibility
guide's is 183 characters and announces a topic without answering anything. I
expect that kind of chunk to fail this test, and I would rather find that out
than write a target it passes by definition.

---

## 5. In-domain questions the guides don't answer still get refused

For at least 4 of the 5 questions in `NEAR_MISS` in `questions.py`, the system
returns exactly "I don't have enough information about that." rather than an
answer — even though the relevance gate lets all five through.

The five are: are dogs allowed on the beaches; what is the crime rate in
Marchwood; how much does a hotel room cost per night; what is the population of
Pellew Sands; is there a cinema in Kestrelford. A stranger can check this by
running `python app.py ask "<question>"` on each one and reading the reply.

**Why this target:** this is the failure I actually care about, because it is the
one the gate cannot catch. These five are about the right region and the right
towns, so they score *inside* the range of questions the corpus does answer —
0.366 to 0.649, against my test questions' 0.216 to 0.386. "Is there a cinema in
Kestrelford?" comes back at **0.366, closer than my own fourth test question at
0.386**, and there is no cinema anywhere in the corpus. No cutoff could separate
those two. So every one of these reaches the model with plausible-looking chunks
in hand, and the grounding prompt is the only thing standing between them and an
invented answer.

4 of 5 rather than 5 of 5 because unlike the gate, which is arithmetic and gives
the same result every time, this depends on the model's behaviour run to run. A
target of 5 of 5 would be claiming the model never drifts, which I have no
reason to believe.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
