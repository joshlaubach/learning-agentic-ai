"""Retrieval and generation evaluation metrics: precision@k, recall@k, MRR, and a
faithfulness scorer.

Built in Chapter 3 (curriculum/03_rag_evaluation.ipynb) and reused by its break-it section
and interview drill. See a chapter's own concept cells for what each metric answers; a short
mapping to what RAGAS/DeepEval compute lives in the notebook itself.
"""

from __future__ import annotations

import re

_STOPWORDS = {
    "the", "a", "an", "is", "was", "were", "of", "in", "on", "at", "to", "and", "or",
    "for", "with", "by", "that", "this", "it", "as", "be", "are", "from", "has", "have",
}


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


def evaluate_retrieval(queries: list[dict], retrieve_fn, k: int = 3) -> dict:
    """Run precision@k / recall@k / MRR across a list of {"query": str,
    "relevant_doc_ids": set[str]} entries, using retrieve_fn(query, k) -> ranked list of
    doc_ids. Returns the averages plus how many queries were scored."""
    precisions, recalls, rrs = [], [], []
    for q in queries:
        retrieved = retrieve_fn(q["query"], k)
        relevant = q["relevant_doc_ids"]
        precisions.append(precision_at_k(retrieved, relevant, k))
        recalls.append(recall_at_k(retrieved, relevant, k))
        rrs.append(mean_reciprocal_rank(retrieved, relevant))

    n = len(queries)
    return {
        "precision@k": sum(precisions) / n if n else 0.0,
        "recall@k": sum(recalls) / n if n else 0.0,
        "mrr": sum(rrs) / n if n else 0.0,
        "n_queries": n,
    }


def faithfulness_score(answer: str, retrieved_texts: list[str]) -> float:
    """Rough faithfulness proxy: what fraction of the answer's significant (non-stopword)
    words actually appear somewhere in the retrieved context. Not a substitute for a real
    NLI-based faithfulness metric (see RAGAS, covered in Chapter 3's notebook) — a simple,
    fully explainable, from-scratch signal for the same underlying question: is this answer
    actually grounded in what was retrieved, or did the model wander off on its own?"""
    combined_context = " ".join(retrieved_texts).lower()
    answer_words = set(re.findall(r"[a-z0-9]+", answer.lower()))
    significant_words = answer_words - _STOPWORDS
    if not significant_words:
        return 1.0
    supported = sum(1 for w in significant_words if w in combined_context)
    return supported / len(significant_words)
