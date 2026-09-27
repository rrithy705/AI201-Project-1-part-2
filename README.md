# The Unofficial Guide

**Name:** Rashidun Rithy
**Corpus:** `city_guides`

---
Unit 1
What This Does

This project is a question-answering system using 14 fictional travel guides. It answers questions about parking, visiting times, transportation, accessibility, and food.

It also shows the source file used for each answer. If the guides do not contain enough information, the system says so instead of making up an answer.

Chunking Strategy

I split each document using its ## section headings.

94 chunks
Average: 319 characters
Shortest: 183 characters
Longest: 758 characters
Chunk size limit: 1000
Overlap: None between sections

This method keeps each topic together instead of cutting sections in the middle.

The starter method created 51 chunks, while my method created 94 chunks.

I also added the town and section name to each chunk to make similar sections easier to identify.

The original chunker is still saved as fallback_split in chunker.py.

Changed in Unit 2: The project now also has an entity-based strategy that creates 99 chunks instead of 94. The Unit 1 strategy can still be used with AI201_CHUNK_STRATEGY=section.

Sample Chunks
1. Accessibility Guide

Source: guide_accessibility.md#0

Getting around the region with limited mobility — Overview

An honest assessment rather than a promotional one. Some of these places are difficult and it is better to know in advance.

This introduces the accessibility topic but does not answer a specific question.

2. Corry Vale — Where to stay

Source: guide_corry_vale.md#5

Corry Vale — Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.

This gives information about lodging and camping.

3. Givens Mill — Getting around

Source: guide_givens_mill.md#2

Givens Mill — Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.

This explains how to get around Givens Mill.

4. Kestrelford — What to see

Source: guide_kestrelford.md#4

Kestrelford — What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village.

This gives information about the market, church tower, and walking trail.

5. Pellew Sands — When to go

Source: guide_pellew_sands.md#6

Pellew Sands — When to go

June and September for the beach without the crowds. July and August are busy. Winter is bleak, largely closed, and has a following among people who like that sort of thing.

This explains when to visit Pellew Sands.

Chunks 2–5 can answer questions on their own. Chunk 1 mainly introduces a topic.

Sample Answer

Produced by `app.py::cmd_ask`, which calls `app.py::ask_pipeline` — retrieval in
`store.py::search`, the cutoff comparison in `gate.py::check`, the answer text from
`generate.py::answer_from_chunks`. The distance and cutoff lines are printed by
`print_distances` inside `app.py::_ask_one`. Command: `python app.py ask "Where should I park in Halden Bay in August?"`

Question: Where should I park in Halden Bay in August?

Answer:

In August, arrive before 10am or use the overflow lot in Halden Bay (guide_seasons.md).

Best distance: 0.216
Cutoff: 0.70

Sources retrieved:

guide_halden_bay.md
guide_regional_transport.md
guide_seasons.md

The answer uses guide_seasons.md because that guide contains the overflow-lot information.

Relevance Cutoff

I chose 0.70 because the five questions answered by the guides had distances of 0.216–0.386, while unrelated questions had distances of 0.810–0.969.

In-corpus question	Distance
Train from Brightwater to regional hub	0.277
Parking in Halden Bay	0.216
Accessibility around the region	0.386
Tuesday market in Brightwater	0.235
Public transport in Corry Vale	0.327

The out-of-corpus questions were 0.810–0.969, so the 0.70 cutoff separated the groups.

One related-looking question about a cinema in Kestrelford scored 0.366, even though the guides do not mention a cinema. This is why the grounding instruction is also important.

Top-k

I kept top-k = 5 because the first five results stayed on topic. The sixth result started bringing in information from other documents.

How I Used AI
I used AI to understand and improve the chunking code, then checked the suggested changes against my documents.
I used AI to review my retrieval and grounding approach.
I used AI to challenge my five criteria. This showed that Criterion 1 needed to measure the top three chunks instead of all five.
AI helped identify that the accessibility problem affected several chunks with the same title prefix.
I considered hybrid search, but testing showed it could favor the wrong chunk because the query used “limited mobility” while the correct answer did not.
AI helped write measurement scripts and fix a bug in scorer.py. I decided what each criterion should measure.
Unit 2
Where the Output in This Section Came From

Every number and every pasted block below was produced by one of these, and the
full transcripts are in `results/`:

File and function	What it produced	Transcript
`run_eval.py::main`	The five test questions, three runs each	`results/run_2026-09-23_2109_before.md`, `results/run_2026-09-23_2149_after.md`
`run_eval.py::check_out_of_scope`	Criterion 3, the gate on out-of-corpus questions	same two files
`app.py::ask_pipeline`, scored by `scorer.py::refused`	Criterion 5, the near-miss refusals	`results/near_miss_before.md`, `results/near_miss_after.md`
`store.py::search` and `scorer.py::hit_rank`	Criterion 1, the rank of the answer	`results/ranks_before_after.md`
`app.py::cmd_index`	Criterion 4, the corpus and chunk statistics	printed to the terminal, pasted below

Run Log — Before

Produced by `run_eval.py::main`; full transcript in `results/run_2026-09-23_2109_before.md`.

Run on 2026-09-23 using:

Corpus: city_guides
Top-k: 5
Cutoff: 0.70
python run_eval.py --label before
python app.py index
python app.py chunks -n 5
Before Results
Criterion	Target	Run 1	Run 2	Run 3	Verdict
1. Top three retrieved chunks contain the answer	4 of 5	4/5	4/5	4/5	MET
2. Every answer names a source	5 of 5	5/5	5/5	5/5	MET
3. Gate stops out-of-corpus questions	4 of 5	5/5	5/5	5/5	MET
4. Chunks stand on their own	4 of 5, none under 150 chars	4/5	4/5	4/5	MET
5. Near-miss questions still refused	4 of 5	5/5	5/5	5/5	MET

Criterion 1 was changed to check the top three chunks. Question 3's answer was at rank 4, so the original test hid a weakness.

The retrieval distances were identical across the three runs:

0.277, 0.216, 0.386, 0.235, 0.327

Verdicts
Criterion 1 — Top Three Chunks

Result: MET

4 of 5 questions had their answers in the top three chunks.

Question 3 was the exception because its answer appeared at rank 4.

Criterion 2 — Every Answer Names a Source

Result: MET

All 15 answers included a .md source filename.

Criterion 3 — Gate Stops Out-of-Corpus Questions

Result: MET

All five unrelated questions were above the 0.70 cutoff.

Distances and gate decisions produced by `run_eval.py::check_out_of_scope`, which
calls `store.py::search` and compares against the cutoff in `gate.py::check`.

Question	Best distance	Gate
What is the capital of Mongolia?	0.810	refused
How do I change the oil in a diesel engine?	0.881	refused
Who won the 1994 World Cup?	0.969	refused
Recommended dosage of ibuprofen?	0.835	refused
How do I write a for loop in Rust?	0.861	refused

The closest score was 0.810, which is 0.11 above the cutoff.

Criterion 4 — Chunks Stand on Their Own

Result: MET

Four of five sample chunks answered something on their own.

The accessibility Overview chunk did not answer a specific question.

Corpus statistics, printed by `app.py::cmd_index` — the `loaded` line comes from
`ingest.py::describe`, the `chunked` line from `chunker.py::describe`, and the
`stored` count is the return value of `store.py::build_index`:

$ AI201_CHUNK_STRATEGY=section python app.py --variant section index
Corpus: city_guides
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  94 chunks, 319 characters on average (shortest 183, longest 758), produced by chunker.py::split_documents [section]
  embedding 94 chunks (first run downloads the model)...
  stored   94 chunks in 14.3s

The `chunked` line names its own producer: `chunker.py::split_documents`, running the
`section` strategy. That string is built by `chunker.py::describe`, not written by hand.

The shortest chunk was 183 characters, above the 150-character minimum.

Criterion 5 — Near-Miss Questions

Result: MET

All five questions were refused in all three runs.

Produced by `app.py::ask_pipeline`, the same function `python app.py ask` calls, with
each reply checked against `gate.REFUSAL` by `scorer.py::refused`. Full transcript in
`results/near_miss_before.md`.

Near-miss question	Best distance	Run 1	Run 2	Run 3
Are dogs allowed on the beaches?	0.649	refused	refused	refused
What is the crime rate in Marchwood?	0.523	refused	refused	refused
Hotel room cost per night?	0.576	refused	refused	refused
Population of Pellew Sands?	0.422	refused	refused	refused
Is there a cinema in Kestrelford?	0.366	refused	refused	refused

The cinema question is important because 0.366 is below the 0.70 cutoff, so the gate allowed it through. The grounding instruction correctly prevented the model from inventing an answer.

Diagnosis

All five criteria initially passed, but two passed with no margin:

Criterion 1: 4/5 against a 4/5 target
Criterion 4: 4/5 against a 4/5 target

The main problem was Question 3.

The Miss

Question: Which town in the region is easiest to get around with limited mobility?

Expected: Thornby Wells

Before the change — ranks from `store.py::search`, the position of the answer found by
`scorer.py::hit_rank`, full output in `results/ranks_before_after.md`:

Rank	Distance	Chunk
1	0.3855	Accessibility — Overview
2	0.4997	Accessibility — Difficult
3	0.5348	Corry Vale — Getting around
4	0.5491	Accessibility — Straightforward

The correct answer was at rank 4.

Why This Happened

The accessibility guide had several sections starting with the same title:

“Getting around the region with limited mobility”

The query matched this title strongly. The Overview and Difficult sections therefore ranked above the actual answer.

The correct section was also 758 characters and discussed three towns. The answer about Thornby Wells was only one sentence inside the larger chunk.

The Pattern

Nine of the 14 documents are town guides. The other five are cross-cutting guides:

Accessibility
Walking
Eating
Seasons
Regional transport

The cross-cutting sections often contain information about several towns in one chunk. They also use similar titles, which caused retrieval problems.

The 183-character Overview chunk was another problem because it did not provide a useful answer.

What I Changed

I created a second chunking strategy.

Instead of keeping all town information in one section, the new strategy splits sections into one chunk per town when each paragraph starts with a bolded town name.

The rest of the system stayed the same:

Section splitting
Title and heading prefix
Chunk size limit
Overlap
Cutoff
Top-k
Grounding prompt

New code:

chunker.py::_entity_paragraphs

Commands:

AI201_CHUNK_STRATEGY=section python app.py --variant section index
# 94 chunks

AI201_CHUNK_STRATEGY=entity python app.py --variant entity index
# 99 chunks
Why I Chose This

Question 3's answer was hidden inside a 758-character, three-town section.

Splitting it by town gives the answer its own chunk.

I did not choose hybrid search because BM25 could make the problem worse. The query contains “limited mobility”, but the correct chunk does not use those exact words. The Overview chunk does, so keyword matching could still favor the wrong chunk.

Cost of the Change
Measurement	Before	After
Chunks	94	99
Average length	319	307
Longest chunk	758	661
Shortest chunk	183	183

Only five additional chunks were created.

Run Log — After

Produced by `run_eval.py::main` against the `entity` index; full transcript in
`results/run_2026-09-23_2149_after.md`.

AI201_CHUNK_STRATEGY=entity python app.py --variant entity index

python run_eval.py --label after --variant entity
After Results
Criterion	Target	Run 1	Run 2	Run 3	Verdict
1. Top three retrieved chunks contain the answer	4 of 5	5/5	5/5	5/5	MET
2. Every answer names a source	5 of 5	5/5	5/5	5/5	MET
3. Gate stops out-of-corpus questions	4 of 5	5/5	5/5	5/5	MET
4. Chunks stand on their own	4 of 5, none under 150 chars	4/5	4/5	4/5	MET
5. Near-miss questions still refused	4 of 5	5/5	5/5	5/5	MET
Before vs. After
Criterion	Target	Before	After	Change
1. Top three chunks contain answer	4 of 5	4/5	5/5	+1
2. Every answer names a source	5 of 5	5/5	5/5	No change
3. Gate stops out-of-corpus	4 of 5	5/5	5/5	No change
4. Chunks stand on their own	4 of 5, none under 150	4/5, 183	4/5, 183	No change
5. Near-miss questions refused	4 of 5	5/5	5/5	No change
Did It Help?

Yes. The change improved the criterion it targeted without changing the others.

Question 3 moved from:

Rank 4 → Rank 1

Criterion 1 improved from:

4/5 → 5/5

The new top result was, from `store.py::search` with the rank checked by
`scorer.py::hit_rank` (`results/ranks_before_after.md`):

rank 1  0.3713
Getting around the region with limited mobility — Straightforward — Thornby Wells

Thornby Wells is the easiest town in the region. It is flat, compact,
and everything is within three minutes of everything else.

The new chunk was 338 characters instead of the previous 758-character chunk.

The answer became — run 1 of 3, generated by `generate.py::answer_from_chunks` through
`app.py::ask_pipeline`, recorded by `run_eval.py::main` in
`results/run_2026-09-23_2149_after.md`:

Based on the documents, Thornby Wells is the easiest town in the region
to get around with limited mobility because it is flat, compact, and
everything is within three minutes of everything else (guide_accessibility.md).

The new distance was 0.3713.

The Overview was still close at 0.3855, so the improvement moved the correct chunk ahead rather than removing the problem completely.

Criterion 4 After the Change

Criterion 4 stayed at 4/5. Statistics printed by `app.py::cmd_index` again, this time
over the `entity` index:

$ AI201_CHUNK_STRATEGY=entity python app.py --variant entity index
Corpus: city_guides
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  99 chunks, 307 characters on average (shortest 183, longest 661), produced by chunker.py::split_documents [entity]
  embedding 99 chunks (first run downloads the model)...
  stored   99 chunks in 9.4s

The same `chunked` line, now reporting `chunker.py::split_documents [entity]` — the
strategy name in the brackets is the only thing that changed about how the numbers
were produced. Every chunk also carries its `produced_by` string into the store as
metadata, in `store.py::build_index`.

The same accessibility Overview remained the shortest chunk at 183 characters.

What's Still Broken
1. The Overview Chunk

The 183-character accessibility Overview is still in the index and does not answer a question.

What I would do: Combine it with the first useful section or remove it from the index while keeping it as context.

I stopped because that would be a second change, and I wanted to measure only the entity-based chunking change.

2. Criterion 1 Uses Only Five Questions

Five questions are a small test for 99 chunks. The other cross-cutting guides do not have specific test questions.

What I would do: Add a question for each cross-cutting guide and measure the retrieval ranks again.

3. Near-Miss Questions

The cinema question scored 0.366, which is closer than the real accessibility question at 0.386.

The gate cannot separate these two questions using the current cutoff.

The grounding instruction prevented an invented answer in all 30 runs before and after.

What I would do: Add a second check after generation to verify that each claim appears in a retrieved chunk.

4. Rate Limit Error

REQUESTS_PER_MINUTE was set to 30, but the free tier allows 15.

This caused a 429 error during one Criterion 5 run.

I changed it to 15 in config.py.

What I'd Do Differently
Criterion 1

I would define the criterion as “the top three chunks contain the answer” from the beginning.

This would have exposed Question 3's weakness earlier.

Criterion 4

I would test the whole index instead of only five sample chunks.

For example:

No chunk should contain only a heading and topic sentence without useful information.

Criteria 3 and 5

I would combine the two types of refusal tests but keep both question sets.

Criterion 3 uses easy out-of-corpus questions, while Criterion 5 tests harder questions that look like they belong to the corpus.

Targets

My original targets were mostly 4/5 or 5/5, and all five criteria passed immediately.

That does not necessarily mean the system was strong. The revised Criterion 1 quickly exposed a real retrieval problem.

For the next unit, I would set at least one target that I realistically expect the system to miss.