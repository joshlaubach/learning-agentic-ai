"""Retrieval and generation evaluation harness: an aggregator over per-query metrics, plus a
faithfulness scorer.

Built in Chapter 3 (curriculum/03_rag_evaluation.ipynb) and reused by its break-it section
and interview drill. See a chapter's own concept cells for what each metric answers; a short
mapping to what RAGAS/DeepEval compute lives in the notebook itself.

precision@k, recall@k, and MRR deliberately do NOT live here: they are graded builds the
learner writes in the notebook (task ids ch03-precision-k, ch03-recall-k, ch03-mrr), and
`evaluate_retrieval` below takes them as arguments so the learner's own implementations are
what score the real SQuAD corpus. The model answers are in solutions/reference/ch03.py.
"""

from __future__ import annotations

import re

_STOPWORDS = {
    "the", "a", "an", "is", "was", "were", "of", "in", "on", "at", "to", "and", "or",
    "for", "with", "by", "that", "this", "it", "as", "be", "are", "from", "has", "have",
}


def evaluate_retrieval(
    queries: list[dict],
    retrieve_fn,
    k: int = 3,
    *,
    precision_fn,
    recall_fn,
    mrr_fn,
) -> dict:
    """Run precision@k / recall@k / MRR across a list of {"query": str,
    "relevant_doc_ids": set[str]} entries, using retrieve_fn(query, k) -> ranked list of
    doc_ids. Returns the averages plus how many queries were scored.

    The three metric functions are passed in rather than imported: this harness is the
    plumbing, and the metrics themselves are yours to write."""
    precisions, recalls, rrs = [], [], []
    for q in queries:
        retrieved = retrieve_fn(q["query"], k)
        relevant = q["relevant_doc_ids"]
        precisions.append(precision_fn(retrieved, relevant, k))
        recalls.append(recall_fn(retrieved, relevant, k))
        rrs.append(mrr_fn(retrieved, relevant))

    n = len(queries)
    return {
        "precision@k": sum(precisions) / n if n else 0.0,
        "recall@k": sum(recalls) / n if n else 0.0,
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
