"""Graded task suites for Chapter 3 — RAG and Retrieval Evaluation.

Each case is a small function taking the implementation under test and asserting one
specific behaviour. Cases are written to fail the plausible wrong answers, not just the
absent one: the docstring on each case is what the learner sees as the failure's headline,
so it says what the case is probing rather than restating the assertion.
"""

from __future__ import annotations

from agentlib.grading import task


# --- ch03-precision-k ---


def _ref_precision():
    from solutions.reference.ch03 import precision_at_k

    return precision_at_k


def _p1(f):
    """one relevant doc inside the top 2"""
    got = f(["a", "b", "c", "d"], {"b", "d", "z"}, 2)
    assert got == 0.5, f"top 2 is ['a','b'], one of which is relevant -> 0.5, got {got}"


def _p2(f):
    """two relevant docs inside the top 4"""
    got = f(["a", "b", "c", "d"], {"b", "d", "z"}, 4)
    assert got == 0.5, f"top 4 has 2 relevant of 4 -> 0.5, got {got}"


def _p3(f):
    """everything retrieved is relevant"""
    got = f(["a", "b"], {"a", "b"}, 2)
    assert got == 1.0, f"both retrieved docs are relevant -> 1.0, got {got}"


def _p4(f):
    """nothing retrieved is relevant"""
    got = f(["a", "b"], {"z"}, 2)
    assert got == 0.0, f"no retrieved doc is relevant -> 0.0, got {got}"


def _p5(f):
    """fewer results came back than k asked for"""
    got = f(["a", "b"], {"a"}, 5)
    assert got == 0.5, (
        "precision is hits / how many documents you ACTUALLY got back, not hits / k. "
        f"2 results, 1 relevant -> 0.5, got {got}. Dividing by k gives 0.2 and unfairly "
        "punishes a retriever for a small index."
    )


def _p6(f):
    """the retriever returned nothing at all"""
    got = f([], {"a"}, 3)
    assert got == 0.0, (
        f"an empty retrieval must return 0.0, not raise and not error out: got {got}. "
        "Dividing straight through gives ZeroDivisionError."
    )


def _p7(f):
    """k=0 asks for no documents"""
    got = f(["a", "b"], {"a"}, 0)
    assert got == 0.0, f"k=0 means an empty top-k -> 0.0, got {got}"


def _p8(f):
    """a relevant doc sits just past the cutoff"""
    got = f(["a", "b", "c"], {"c"}, 2)
    assert got == 0.0, (
        f"only the top k=2 docs count; 'c' at rank 3 is outside them -> 0.0, got {got}"
    )


def _p9(f):
    """the caller's list is not modified"""
    retrieved = ["a", "b", "c"]
    f(retrieved, {"a"}, 2)
    assert retrieved == ["a", "b", "c"], (
        f"scoring must not mutate the caller's retrieved list; it is now {retrieved}"
    )


task(
    "ch03-precision-k",
    _ref_precision,
    [_p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9],
)


# --- ch03-recall-k ---


def _ref_recall():
    from solutions.reference.ch03 import recall_at_k

    return recall_at_k


def _r1(f):
    """two of three relevant docs made the top 4"""
    got = f(["a", "b", "c", "d"], {"b", "d", "z"}, 4)
    assert abs(got - 2 / 3) < 1e-9, (
        f"3 docs are relevant, 2 of them were retrieved -> 2/3, got {got}"
    )


def _r2(f):
    """k is larger than the number of relevant docs"""
    got = f(["x", "a"], {"a"}, 5)
    assert got == 1.0, (
        "recall is hits / how many documents were RELEVANT, not hits / k. 1 relevant doc "
        f"and it was found -> 1.0, got {got}. Dividing by k gives 0.2."
    )


def _r3(f):
    """every relevant doc was retrieved"""
    got = f(["a", "b"], {"a", "b"}, 2)
    assert got == 1.0, f"both relevant docs are in the top 2 -> 1.0, got {got}"


def _r4(f):
    """none of the relevant docs came back"""
    got = f(["x", "y"], {"a"}, 2)
    assert got == 0.0, f"the one relevant doc was missed -> 0.0, got {got}"


def _r5(f):
    """the query has no relevant docs at all"""
    got = f(["a", "b"], set(), 2)
    assert got == 0.0, (
        f"an empty relevant set must return 0.0, not raise: got {got}. Dividing by "
        "len(relevant_ids) straight through gives ZeroDivisionError."
    )


def _r6(f):
    """a relevant doc sits just past the cutoff"""
    got = f(["a", "b", "c"], {"c"}, 2)
    assert got == 0.0, (
        f"recall@k only counts hits inside the top k; 'c' is at rank 3 -> 0.0, got {got}"
    )


def _r7(f):
    """a relevant doc the retriever could never return"""
    got = f(["a"], {"a", "never-indexed"}, 3)
    assert got == 0.5, (
        "the denominator is every doc that SHOULD have been retrieved, including ones the "
        f"retriever missed entirely. 1 of 2 found -> 0.5, got {got}. Dividing by the number "
        "of hits instead always gives 1.0 and hides exactly the failure recall exists to "
        "measure."
    )


def _r8(f):
    """the retriever returned nothing at all"""
    got = f([], {"a"}, 3)
    assert got == 0.0, f"an empty retrieval must return 0.0, not raise: got {got}"


def _r9(f):
    """the caller's list is not modified"""
    retrieved = ["a", "b", "c"]
    f(retrieved, {"a"}, 2)
    assert retrieved == ["a", "b", "c"], (
        f"scoring must not mutate the caller's retrieved list; it is now {retrieved}"
    )


task("ch03-recall-k", _ref_recall, [_r1, _r2, _r3, _r4, _r5, _r6, _r7, _r8, _r9])


# --- ch03-mrr ---


def _ref_mrr():
    from solutions.reference.ch03 import mean_reciprocal_rank

    return mean_reciprocal_rank


def _m1(f):
    """the first relevant result is at rank 2"""
    got = f(["a", "b", "c"], {"b"})
    assert got == 0.5, (
        f"rank 2 -> 1/2 = 0.5, got {got}. Ranks are 1-based; enumerate() from 0 gives 1.0."
    )


def _m2(f):
    """the first relevant result is at rank 1"""
    got = f(["a", "b", "c"], {"a"})
    assert got == 1.0, f"rank 1 -> 1/1 = 1.0, got {got}"


def _m3(f):
    """nothing retrieved is relevant"""
    got = f(["a", "b", "c"], {"z"})
    assert got == 0.0, f"no relevant result anywhere -> 0.0, got {got}"


def _m4(f):
    """the retriever returned nothing at all"""
    got = f([], {"a"})
    assert got == 0.0, f"an empty retrieval must return 0.0, not raise: got {got}"


def _m5(f):
    """two relevant results, at ranks 2 and 3"""
    got = f(["a", "b", "c"], {"b", "c"})
    assert got == 0.5, (
        "MRR uses the FIRST relevant hit only. It answers 'how far down did the user have "
        f"to read before finding something useful', so later hits change nothing: expected "
        f"0.5, got {got}. Averaging all the reciprocal ranks gives (1/2 + 1/3)/2 = 0.4167."
    )


def _m6(f):
    """relevant results at ranks 1 and 3"""
    got = f(["a", "b", "c"], {"a", "c"})
    assert got == 1.0, (
        f"the first hit is at rank 1 -> 1.0 regardless of what follows, got {got}. "
        "Summing reciprocal ranks gives 1.333, which is not even a valid score."
    )


def _m7(f):
    """the only relevant result is at rank 3"""
    got = f(["a", "b", "c"], {"c"})
    assert abs(got - 1 / 3) < 1e-9, (
        f"rank 3 -> 1/3 = 0.333, got {got}. Returning 1.0 whenever anything relevant is "
        "present throws away the ranking information this metric exists to capture."
    )


def _m8(f):
    """the first relevant result is deep in the list"""
    got = f(["a", "b", "c", "d", "e", "f"], {"e"})
    assert abs(got - 0.2) < 1e-9, f"rank 5 -> 1/5 = 0.2, got {got}"


def _m9(f):
    """the caller's list is not modified"""
    retrieved = ["a", "b", "c"]
    f(retrieved, {"b"})
    assert retrieved == ["a", "b", "c"], (
        f"scoring must not mutate the caller's retrieved list; it is now {retrieved}"
    )


task("ch03-mrr", _ref_mrr, [_m1, _m2, _m3, _m4, _m5, _m6, _m7, _m8, _m9])
