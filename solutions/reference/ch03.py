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
