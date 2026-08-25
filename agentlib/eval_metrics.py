"""Retrieval and generation evaluation harness: an aggregator over per-query metrics, plus a
faithfulness scorer.

Built in Chapter 3 (curriculum/03_rag_evaluation.ipynb) and reused by its break-it section
and interview drill. See a chapter's own concept cells for what each metric answers; a short
mapping to what RAGAS/DeepEval compute lives in the notebook itself.

precision@k, recall@k, and MRR deliberately do NOT live here: they are graded builds the
learner writes in the notebook (task ids ch03-precision-k, ch03-recall-k, ch03-mrr), and
`evaluate_retrieval` below takes them as arguments so the learner's own implementations are
what score the real SQuAD corpus. The model answers are in solutions/reference/ch03.py.
F1 *is* here, because it derives from precision and recall rather than from the ranked list:
it is plumbing over the learner's two functions, not a fourth thing to write.
"""

from __future__ import annotations

import re

_STOPWORDS = {
    "the", "a", "an", "is", "was", "were", "of", "in", "on", "at", "to", "and", "or",
    "for", "with", "by", "that", "this", "it", "as", "be", "are", "from", "has", "have",
}


def f1_at_k(precision: float, recall: float) -> float:
    """Harmonic mean of precision@k and recall@k — one number for retrievers that trade one
    against the other.

    Why harmonic rather than arithmetic: the harmonic mean is dragged down by the smaller of
    the two, so it refuses to reward a lopsided retriever. A retriever that returns every
    document in the corpus scores recall@k = 1.0 and precision@k near 0; the arithmetic mean
    calls that ~0.5, F1 calls it ~0. Both being decent is the only way to score well.

    Returns 0.0 when both are 0 (the harmonic mean is undefined there, and a retriever that
    found nothing relevant has earned a 0, not a crash)."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluate_retrieval(
    queries: list[dict],
    retrieve_fn,
    k: int = 3,
    *,
    precision_fn,
    recall_fn,
    mrr_fn,
) -> dict:
    """Run precision@k / recall@k / F1@k / MRR across a list of {"query": str,
    "relevant_doc_ids": set[str]} entries, using retrieve_fn(query, k) -> ranked list of
    doc_ids. Returns the averages plus how many queries were scored.

    The three metric functions are passed in rather than imported: this harness is the
    plumbing, and the metrics themselves are yours to write."""
    precisions, recalls, f1s, rrs = [], [], [], []
    for q in queries:
        retrieved = retrieve_fn(q["query"], k)
        relevant = q["relevant_doc_ids"]
        p = precision_fn(retrieved, relevant, k)
        r = recall_fn(retrieved, relevant, k)
        precisions.append(p)
        recalls.append(r)
        # F1 per query, then averaged -- not F1 of the two averages. The two disagree, and
        # this order is the honest one: averaging first lets a query with high precision
        # cover for a different query with high recall, inventing a balance no single query
        # actually achieved.
        f1s.append(f1_at_k(p, r))
        rrs.append(mrr_fn(retrieved, relevant))

    n = len(queries)
    return {
        "precision@k": sum(precisions) / n if n else 0.0,
        "recall@k": sum(recalls) / n if n else 0.0,
        "f1@k": sum(f1s) / n if n else 0.0,
        "mrr": sum(rrs) / n if n else 0.0,
        "n_queries": n,
    }


def faithfulness_score(answer: str, retrieved_texts: list[str]) -> float:
    """Rough faithfulness proxy: what fraction of the answer's significant (non-stopword)
    words appear somewhere in the retrieved context. Not a substitute for a real NLI-based
    faithfulness metric (see RAGAS, covered in Chapter 3's notebook) — a simple, from-scratch
    signal for the same question: is this answer grounded in what was retrieved, or did the
    model wander off on its own?"""
    combined_context = " ".join(retrieved_texts).lower()
    answer_words = set(re.findall(r"[a-z0-9]+", answer.lower()))
    significant_words = answer_words - _STOPWORDS
    if not significant_words:
        return 1.0
    supported = sum(1 for w in significant_words if w in combined_context)
    return supported / len(significant_words)
