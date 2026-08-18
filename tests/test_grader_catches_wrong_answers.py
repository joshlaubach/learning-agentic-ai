"""Adversarial tests for the autograder: one plausible wrong answer per graded task, each
asserted to be REJECTED.

A check suite that every reasonable attempt passes teaches nothing. Every task in this course
therefore has at least one case aimed at a specific mistake a learner is likely to actually
make -- not a typo, not an empty function, but a version that looks right, runs cleanly, and
returns a number or a value of the correct type. This file is where that claim gets proved:
each test below implements the wrong answer for real and asserts that `check()` raises.

`_rejects` runs a task's suite directly in learner mode, so these tests behave identically
whether or not GRADER_MODE=reference is set for the notebooks. If you add a task, add its
entry here; if a test here starts failing, the case suite has a hole in it.
"""

from __future__ import annotations

import pytest

from agentlib.grading import load_all_tasks


def _rejects(task_id: str, wrong_fn) -> str:
    """Run task_id's cases against wrong_fn and return the failure text.

    Fails the test if the wrong implementation slips through, which is the whole point.
    """
    spec = load_all_tasks()[task_id]
    failures = []
    for case in spec["cases"]:
        try:
            case(wrong_fn)
        except Exception as e:  # AssertionError, or anything the wrong answer blows up with
            failures.append(f"{getattr(case, '__doc__', '') or case.__name__}: {e}")
    assert failures, (
        f"{task_id}: the wrong implementation passed every case. The suite has a hole in it "
        f"-- add a case that catches this mistake."
    )
    return "\n".join(failures)


def _accepts(task_id: str) -> None:
    """Sanity check: the reference answer passes every case in the same suite."""
    spec = load_all_tasks()[task_id]
    ref = spec["reference"]()
    for case in spec["cases"]:
        case(ref)


# --- Chapter 3 ---


def test_ch03_precision_k_rejects_dividing_by_k():
    """Plausible wrong answer: hits / k. Reads correctly ("precision AT K"), and agrees with
    the reference whenever the retriever happens to return at least k documents."""

    def wrong(retrieved_ids, relevant_ids, k):
        top_k = retrieved_ids[:k]
        hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
        return hits / k if k else 0.0

    _rejects("ch03-precision-k", wrong)
    _accepts("ch03-precision-k")


def test_ch03_precision_k_rejects_unguarded_division():
    """Plausible wrong answer: the arithmetic is right but nothing guards the empty case, so
    a retriever that returns nothing raises ZeroDivisionError instead of scoring 0.0."""

    def wrong(retrieved_ids, relevant_ids, k):
        top_k = retrieved_ids[:k]
        hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
        return hits / len(top_k)

    _rejects("ch03-precision-k", wrong)


def test_ch03_recall_k_rejects_dividing_by_k():
    """Plausible wrong answer: hits / k, copied across from precision@k. The two metrics
    differ only in their denominator, which is exactly what makes this easy to get wrong."""

    def wrong(retrieved_ids, relevant_ids, k):
        top_k = retrieved_ids[:k]
        hits = sum(1 for doc_id in top_k if doc_id in relevant_ids)
        return hits / k if k else 0.0

    _rejects("ch03-recall-k", wrong)
    _accepts("ch03-recall-k")


def test_ch03_recall_k_rejects_dividing_by_hits_found():
    """Plausible wrong answer: intersect first, then divide by the size of the intersection.
    Always returns 1.0 when anything was found, hiding every missed document."""

    def wrong(retrieved_ids, relevant_ids, k):
        found = [d for d in retrieved_ids[:k] if d in relevant_ids]
        return len(found) / len(found) if found else 0.0

    _rejects("ch03-recall-k", wrong)


def test_ch03_mrr_rejects_averaging_all_hits():
    """Plausible wrong answer: average the reciprocal rank of every relevant hit. The name
    says "mean", so averaging feels right -- but the mean in MRR is across queries, not
    across hits within one query."""

    def wrong(retrieved_ids, relevant_ids):
        rrs = [
            1.0 / rank
            for rank, doc_id in enumerate(retrieved_ids, start=1)
            if doc_id in relevant_ids
        ]
        return sum(rrs) / len(rrs) if rrs else 0.0

    _rejects("ch03-mrr", wrong)
    _accepts("ch03-mrr")


def test_ch03_mrr_rejects_zero_based_ranks():
    """Plausible wrong answer: enumerate() without start=1, so the top result is rank 0 and
    every score is one position too generous."""

    def wrong(retrieved_ids, relevant_ids):
        for rank, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                return 1.0 / (rank if rank else 1)
        return 0.0

    _rejects("ch03-mrr", wrong)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
