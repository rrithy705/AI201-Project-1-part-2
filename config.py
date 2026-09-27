"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "city_guides")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# `chunker.py::split_documents` splits city_guides on its `##` section
# headings, so these two are no longer a window and a slide.
#
# CHUNK_SIZE is a CEILING. Measured across the corpus, the 84 sections run
# 175–710 characters (median 294), so nothing reaches it and no section gets
# cut. It exists so the strategy degrades sensibly on a longer document
# instead of emitting one enormous chunk.
#
# CHUNK_OVERLAP applies only beneath that ceiling, inside `_split_oversized`.
# Between sections the overlap is zero on purpose: a heading is already the
# point where the topic changes, so there is no half-sentence to protect.

CHUNK_SIZE = 1000       # ceiling before a section gets sub-split
CHUNK_OVERLAP = 150     # only used when a section exceeds the ceiling

# ─── Chunking strategy (unit 2) ──────────────────────────────────────────────
# "section"  one chunk per `##` heading. What unit 1 shipped.
# "entity"   the same, except that a section whose paragraphs each open with a
#            bolded name — the five cross-cutting guides list towns that way —
#            is split one chunk per town instead of one chunk per section.
#
# Unit 2's diagnosis: "Which town is easiest to get around with limited
# mobility?" put the answer at rank 4, behind the accessibility guide's
# contentless Overview and behind its *Difficult* section, which is the
# opposite answer. All four of that guide's chunks open with the same nine-word
# title, so the only thing telling them apart was one word — "Straightforward"
# against "Difficult" — and that word loses to the shared prefix. Splitting per
# town puts the town's name and its own sentences in the chunk instead.
#
# Kept switchable so both indexes can be built and queried side by side:
#   AI201_CHUNK_STRATEGY=section python app.py index --variant section
#   AI201_CHUNK_STRATEGY=entity  python app.py index --variant entity
CHUNK_STRATEGY = os.getenv("AI201_CHUNK_STRATEGY", "entity")

# No chunk in the index should be shorter than this — criterion 4's second
# half. A section that splits into a fragment under it gets merged back.
MIN_CHUNK = 150


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

TOP_K = 5               # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# Measured on city_guides at the section chunking above (Milestone 4):
#
#   the five in QUESTIONS          0.216 – 0.386
#   the five in OUT_OF_SCOPE       0.810 – 0.969
#
# A gap 0.42 wide. Its midpoint is about 0.60, and 0.70 sits deliberately
# nearer the top of it, because a third group decided the number: questions
# this corpus *does* answer, asked loosely — "do I need cash?", "anywhere good
# for a rainy day?", "is it worth bringing a car?" — come back at 0.637, 0.616
# and 0.688. The shipped 0.6 refuses all three, and the answers are sitting in
# guide_marchwood.md, guide_brightwater.md and guide_regional_transport.md.
# 0.70 admits them and still refuses all five out-of-scope questions with 0.11
# to spare.
THRESHOLD = 0.70


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

# 15, not 30. The free tier for gemini-3.5-flash-lite allows 15 requests per
# minute, and at 30 the limiter let a run through fast enough to earn a 429 —
# it killed a criterion 5 pass in unit 2 four questions in. Not a quality
# change and it touches no criterion; it just stops the eval dying mid-run.
REQUESTS_PER_MINUTE = 15       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
