"""Shared data loaders and generators for Chapter 3 (RAG and Retrieval Evaluation) onward.

Every loader here follows the same pattern: check for a locally cached file first (shipped
in `data/rag_corpus/`, committed to the repo) and only fall back to a live network fetch if
the cache is missing, so a normal `pytest`/CI run never needs network access. All synthetic
generation is seeded for reproducibility (Hard Constraint: deterministic data).

Real-data source notes (see PROGRESS.md's Unit 4 section and REFERENCES.md for the full
story): the original build spec called for Hugging Face's `datasets` library and SEC EDGAR.
Both are unreachable from this repo's build environment, so:
  - SQuAD 1.1 is fetched from `rajpurkar/SQuAD-explorer`'s own GitHub repo (canonical source,
    same license) via `raw.githubusercontent.com` instead of `datasets.load_dataset(...)`.
  - The messy real-world ingestion source is a real file (`anthropic-sdk-python`'s
    `CHANGELOG.md`) instead of SEC EDGAR filings or the Hugging-Face-hosted
    `bigcode/the-stack-github-issues`.
Both are still genuinely real, unfabricated content — just reached through a different,
reachable channel. A learner or CI running in an environment with normal internet access can
still swap these back to the spec's original sources if they prefer; nothing here is
mock/fake data standing in for real data.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

import requests

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "rag_corpus"

SQUAD_CACHE_PATH = _DATA_DIR / "squad_sample.json"
SQUAD_SOURCE_URL = (
    "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json"
)

MESSY_CORPUS_CACHE_PATH = _DATA_DIR / "messy_source_changelog.md"
MESSY_CORPUS_SOURCE_URL = (
    "https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/CHANGELOG.md"
)


def _extract_squad_sample(squad_json: dict, n_docs: int = 28, seed: int = 42) -> dict:
    all_paragraphs = []
    for article in squad_json["data"]:
        for para in article["paragraphs"]:
            all_paragraphs.append((article["title"], para))

    rng = random.Random(seed)
    rng.shuffle(all_paragraphs)
    sample = all_paragraphs[:n_docs]

    docs, qa_pairs = [], []
    for i, (title, para) in enumerate(sample):
        doc_id = f"squad-{i:03d}"
        docs.append({"doc_id": doc_id, "title": title, "text": para["context"]})
        for qa in para["qas"][:2]:
            answer_text = qa["answers"][0]["text"] if qa["answers"] else None
            qa_pairs.append({
                "qa_id": qa["id"],
                "question": qa["question"],
                "answer": answer_text,
                "gold_doc_id": doc_id,
            })

    return {
        "source": "SQuAD 1.1 dev set (Rajpurkar et al., 2016), official rajpurkar/SQuAD-explorer GitHub repo",
        "license": "CC BY-SA 4.0 (inherited from underlying Wikipedia content; see REFERENCES.md)",
        "sampled_with_seed": seed,
        "docs": docs,
        "qa_pairs": qa_pairs,
    }


def load_squad_sample() -> dict:
    """Real SQuAD 1.1 passages + human-annotated QA pairs. Loads from the committed cache if
    present; otherwise fetches and extracts a fresh (still seeded, still deterministic)
    sample and writes the cache for next time."""
    if SQUAD_CACHE_PATH.exists():
        with open(SQUAD_CACHE_PATH) as f:
            return json.load(f)

    response = requests.get(SQUAD_SOURCE_URL, timeout=60)
    response.raise_for_status()
    sample = _extract_squad_sample(response.json())

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SQUAD_CACHE_PATH, "w") as f:
        json.dump(sample, f, indent=2)
    return sample


_YEAR_POOL = ["1979", "1985", "1992", "2001", "2008", "2015", "2019"]
_NAME_POOL = ["Michael Chen", "Sarah Thompson", "David Kim", "Emily Rodriguez"]


def _perturb_text(text: str, rng: random.Random) -> tuple[str, str | None]:
    """One deliberate factual change: swap a year or a proper-noun pair for a different,
    equally plausible one. Returns (perturbed_text, description) or (text, None) if the
    passage has nothing swappable."""
    year_match = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", text)
    if year_match:
        choices = [y for y in _YEAR_POOL if y != year_match.group()]
        replacement = rng.choice(choices)
        perturbed = text[: year_match.start()] + replacement + text[year_match.end() :]
        return perturbed, f"year {year_match.group()} -> {replacement}"

    name_match = re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text)
    if name_match:
        replacement = rng.choice(_NAME_POOL)
        perturbed = text[: name_match.start()] + replacement + text[name_match.end() :]
        return perturbed, f"name {name_match.group()!r} -> {replacement!r}"

    return text, None


def generate_confusable_documents(base_docs: list[dict], n: int = 5, seed: int = 42) -> list[dict]:
    """Synthetic near-duplicate ("confusable") documents layered on top of real SQuAD
    passages: each is a real passage with exactly one fact swapped, similar enough in
    wording to be retrieved in place of the original but wrong if you check the swapped
    fact. Real SQuAD passages don't reliably contain the specific near-duplicate pairs the
    Chapter 3 break-it section needs, so this generates them deterministically instead of
    hand-writing them."""
    rng = random.Random(seed)
    candidates = [
        d for d in base_docs
        if re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", d["text"])
        or re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", d["text"])
    ]
    chosen = rng.sample(candidates, min(n, len(candidates)))

    confusables = []
    for doc in chosen:
        perturbed_text, change = _perturb_text(doc["text"], rng)
        if change is None:
            continue
        confusables.append({
            "doc_id": f"{doc['doc_id']}-confusable",
            "title": doc["title"],
            "text": perturbed_text,
            "confusable_of": doc["doc_id"],
            "synthetic_change": change,
        })
    return confusables


def load_messy_corpus() -> str:
    """A real, unfabricated messy document (a real CHANGELOG.md) for the ingestion/chunking
    exercise. Loads from the committed cache if present; otherwise fetches and caches it."""
    if MESSY_CORPUS_CACHE_PATH.exists():
        return MESSY_CORPUS_CACHE_PATH.read_text()

    response = requests.get(MESSY_CORPUS_SOURCE_URL, timeout=60)
    response.raise_for_status()
    text = "\n".join(response.text.splitlines()[:900])

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    MESSY_CORPUS_CACHE_PATH.write_text(text)
    return text
