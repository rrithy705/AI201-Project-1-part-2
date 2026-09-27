"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


MIN_PREAMBLE = 80   # an intro shorter than this is just the title line


def _title_of(text: str) -> str:
    """The document's `# Heading`, or its filename-ish first line."""
    first = text.lstrip().split("\n", 1)[0].strip()
    return first.lstrip("#").strip()


def _split_oversized(body: str, ceiling: int, overlap: int) -> list[str]:
    """
    Break a section that came out longer than the ceiling.

    Splits on blank lines first, so paragraphs stay whole, and only falls back
    to a character window when a single paragraph is itself over the ceiling.
    Overlap is applied here and nowhere else — see split_documents.
    """
    if len(body) <= ceiling:
        return [body]

    pieces: list[str] = []
    current = ""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if len(para) > ceiling:
            if current:
                pieces.append(current)
                current = ""
            start = 0
            while start < len(para):
                pieces.append(para[start : start + ceiling].strip())
                start += ceiling - overlap
            continue
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > ceiling:
            pieces.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}".strip() if tail else para
        else:
            current = candidate
    if current:
        pieces.append(current)
    return [p for p in pieces if p]


ENTITY_PARA = re.compile(r"^\*\*([^*\n]+?)\*\*")


def _entity_paragraphs(body: str) -> list[tuple[str, str]] | None:
    """Split a section that lists places, one chunk per place.

    Added in unit 2. Nine of the fourteen guides are town guides, where a `##`
    section is already one answer about one town. The other five are
    cross-cutting — accessibility, walking, eating, seasons, transport — and
    there a single section is a *list*: three or four paragraphs, each opening
    with a bolded town name, each about a different place.

    Those sections were the failure unit 2 found. The accessibility guide's
    four chunks all begin "Getting around the region with limited mobility —",
    which is almost the test question word for word, so the embedding scored
    them on the nine words they share rather than the one word that tells them
    apart. "Straightforward" and "Difficult" are opposite answers and the
    embedding could not separate them: the section holding the answer came back
    at rank 4, below the section holding the opposite.

    Returns `(name, paragraph)` pairs, or None when this isn't that shape —
    which is every section of every town guide, so they are untouched.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if len(paragraphs) < 2:
        return None

    pairs: list[tuple[str, str]] = []
    for para in paragraphs:
        match = ENTITY_PARA.match(para)
        if not match:
            # One unlabelled paragraph and the section isn't a list of places.
            # Bail out rather than split it half one way and half the other.
            return None
        pairs.append((match.group(1).strip(), para))

    # Criterion 4's floor. A trailing one-liner gets folded back into the
    # paragraph above it rather than entering the index as a fragment.
    merged: list[tuple[str, str]] = []
    for name, para in pairs:
        if merged and len(para) < config.MIN_CHUNK:
            prev_name, prev_para = merged[-1]
            merged[-1] = (f"{prev_name} and {name}", f"{prev_para}\n\n{para}")
        else:
            merged.append((name, para))

    if len(merged) < 2:
        return None
    return merged


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split each guide on its `##` section headings, one section per chunk.

    Why this and not a character window. Every document in `city_guides` is a
    guide with labelled sections — Getting there, Getting around, Eat and drink,
    When to go — and each section is one self-contained answer to one question.
    Measured across the corpus, those sections run 175 to 710 characters with a
    median of 294, so a section already is the right size: not one of the 84 is
    over the 800-character window the starter used. What the starter's window
    did instead was ignore the headings and cut mid-section, producing 51 chunks
    where the shortest was 24 characters — a fragment of a heading with nothing
    under it.

    Two details that matter more than the size:

    - Every chunk is prefixed with the document title and its section heading.
      Nine of the fourteen documents are town guides with the *same* seven
      headings, so a bare "When to go" section reads identically whether it came
      from Brightwater or Halden Bay. The prefix is what makes a chunk say which
      town it is about, both to a reader and to the embedding.

    - There is no overlap between sections. Overlap exists to stop a sentence
      being cut in half, and splitting on a heading never cuts one — the
      boundary is already where the topic changes. Overlap is still applied
      inside `_split_oversized`, for a section that runs past the ceiling. On
      this corpus that path does not fire; it is there so the strategy does not
      break on a longer document.

    `config.CHUNK_SIZE` is therefore a ceiling, not a window, and
    `config.CHUNK_OVERLAP` only applies beneath it.
    """
    ceiling = config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP

    chunks: list[Chunk] = []
    for doc in documents:
        title = _title_of(doc.text)
        parts = re.split(r"(?m)^##\s+", doc.text)

        # parts[0] is everything before the first `## ` heading: the `# Title`
        # line plus, in the town guides, a paragraph introducing the place.
        preamble = parts[0].strip()
        intro = preamble.split("\n", 1)[1].strip() if "\n" in preamble else ""

        sections: list[tuple[str, str]] = []
        if len(intro) >= MIN_PREAMBLE:
            sections.append(("Overview", intro))
        for part in parts[1:]:
            heading, _, body = part.partition("\n")
            body = body.strip()
            if body:
                sections.append((heading.strip(), body))

        strategy = config.CHUNK_STRATEGY
        produced_by = f"chunker.py::split_documents [{strategy}]"

        index = 0
        for heading, body in sections:
            # Unit 2's change, and the only one: a section that is a list of
            # places becomes one chunk per place. Everything else falls through
            # to the section-per-chunk behaviour unit 1 shipped.
            listed = _entity_paragraphs(body) if strategy == "entity" else None
            units = (
                [(f"{heading} — {name}", para) for name, para in listed]
                if listed
                else [(heading, body)]
            )

            for label, text in units:
                for piece in _split_oversized(text, ceiling, overlap):
                    chunks.append(
                        Chunk(
                            text=f"{title} — {label}\n\n{piece}",
                            source=doc.source,
                            index=index,
                            produced_by=produced_by,
                        )
                    )
                    index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
