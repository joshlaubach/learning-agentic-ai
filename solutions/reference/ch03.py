"""Chapter 3 reference answers — RAG and Retrieval Evaluation.

These three metrics used to live in agentlib/eval_metrics.py as finished code. They moved
here when Chapter 3's eval-harness section became a graded build: the learner writes them in
the notebook, `evaluate_retrieval` takes them as arguments so the learner's versions are what
actually score the corpus, and this module is what CI grades under GRADER_MODE=reference.
"""

from __future__ import annotations


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Of the top-k retrieved documents, what fraction are actually relevant?"""
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / len(top_k)


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Of all the documents that were actually relevant, what fraction showed up in the
    top-k?"""
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
    return hits / len(relevant_ids)


def mean_reciprocal_rank(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    """1 / (rank of the first relevant result), or 0 if none of the retrieved results are
    relevant. Averaging this across queries gives MRR."""
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def chunk_with_overlap(text: str, chunk_size: int = 400, overlap: int = 0) -> list:
    """Fixed-size chunks that each repeat the last `overlap` characters of the previous one.

    The step is `chunk_size - overlap`, and that is the whole idea: the window slides by less
    than its own width, so any span shorter than the overlap is guaranteed to sit intact
    inside at least one chunk. A fact split across a boundary stops being unretrievable.

    It is not free. Halving the step roughly doubles the number of chunks, and every extra
    chunk is another vector to store, index, and search. Overlap buys recall against boundary
    splits and pays for it in index size.
    """
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size}); "
            "a step of zero or less never advances"
        )
    if not text:
        return []

    step = chunk_size - overlap
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        # Stop once this chunk already reached the end, so the final partial chunk is emitted
        # exactly once rather than followed by empty slices.
        if start + chunk_size >= len(text):
            break
        start += step
    return chunks


def bm25_scores(query: str, docs: list, k1: float = 1.5, b: float = 0.75) -> dict:
    """Score every document against `query` with Okapi BM25. Returns {doc_id: score}.

    Two parameters carry the two ideas that make this better than raw TF-IDF for retrieval:

    k1 saturates term frequency. The contribution of a term rises with tf but converges to a
    ceiling, so a document repeating a keyword forty times does not outrank one that uses it
    twice in a genuinely relevant sentence.

    b normalises for length. Without it, long documents win simply by containing more words.
    At b=1 the penalty is full, at b=0 it is off entirely.
    """
    import math
    from collections import Counter

    from agentlib.retrieval_lab import tokenize

    corpus = [tokenize(d["text"]) for d in docs]
    n_docs = len(corpus)
    if n_docs == 0:
        return {}
    avg_len = sum(len(c) for c in corpus) / n_docs

    # Document frequency: how many documents each term appears in at all.
    doc_freq = Counter(term for tokens in corpus for term in set(tokens))

    scores = {}
    for doc, tokens in zip(docs, corpus):
        tf = Counter(tokens)
        score = 0.0
        for term in tokenize(query):
            if term not in tf:
                continue
            # The +0.5 terms are the standard smoothing; the outer 1 + keeps the idf of a term
            # present in every document at ~0 rather than negative.
            idf = math.log(1 + (n_docs - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            norm = 1 - b + b * len(tokens) / avg_len
            score += idf * tf[term] * (k1 + 1) / (tf[term] + k1 * norm)
        scores[doc["doc_id"]] = score
    return scores
