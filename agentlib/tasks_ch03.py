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


# --- ch03-chunk-overlap ---


def _ref_overlap():
    from solutions.reference.ch03 import chunk_with_overlap

    return chunk_with_overlap


_LOREM = "".join(f"sentence number {i} carries one fact. " for i in range(40))


def _o1(f):
    """overlap=0 reproduces plain fixed-size chunking"""
    got = f(_LOREM, 100, 0)
    expected = [_LOREM[i : i + 100] for i in range(0, len(_LOREM), 100)]
    assert got == expected, (
        f"with no overlap this has to behave exactly like the fixed-size chunker it "
        f"replaces; got {len(got)} chunks, expected {len(expected)}"
    )


def _o2(f):
    """consecutive chunks share exactly `overlap` characters"""
    chunks = f(_LOREM, 120, 30)
    for a, b in zip(chunks, chunks[1:]):
        assert a[-30:] == b[:30], (
            "the tail of each chunk must be the head of the next, by exactly `overlap` "
            f"characters. Got tail {a[-30:]!r} then head {b[:30]!r}"
        )


def _o3(f):
    """no character is lost"""
    for size, overlap in ((100, 0), (100, 25), (250, 100), (60, 45)):
        joined = "".join(f(_LOREM, size, overlap))
        for probe in ("sentence number 0 ", "sentence number 21 ", "sentence number 39 "):
            assert probe in joined, (
                f"chunking dropped {probe!r} at size={size}, overlap={overlap}. Advancing by "
                "`size` while slicing `size - overlap` silently deletes text between chunks, "
                "which is far worse than the boundary problem overlap is meant to solve."
            )


def _o4(f):
    """the tail of the document survives"""
    text = "A" * 250 + "ZEBRA"
    assert any("ZEBRA" in c for c in f(text, 100, 20)), (
        "a loop that stops once the next start passes len(text) can drop the final partial "
        "chunk, so the end of every document silently becomes unretrievable"
    )


def _o5(f):
    """more overlap means more chunks"""
    counts = [len(f(_LOREM, 150, o)) for o in (0, 30, 60, 90)]
    assert counts == sorted(counts), (
        f"shrinking the step has to produce at least as many chunks; got {counts}"
    )
    assert counts[-1] > counts[0], (
        f"and strictly more at the extremes -- that growth is the storage cost overlap "
        f"buys you. Got {counts}"
    )


def _o6(f):
    """overlap >= chunk_size is rejected"""
    for bad in (100, 150):
        try:
            f(_LOREM, 100, bad)
        except ValueError:
            continue
        raise AssertionError(
            f"overlap={bad} with chunk_size=100 means a step of zero or less, so the loop "
            "never advances. Raise ValueError rather than hanging or returning garbage."
        )


def _o7(f):
    """text shorter than one chunk comes back as a single chunk"""
    got = f("short document", 100, 20)
    assert got == ["short document"], f"expected one chunk back unchanged; got {got!r}"


def _o8(f):
    """empty input produces no chunks"""
    assert f("", 100, 20) == [], "nothing in, nothing out"


task(
    "ch03-chunk-overlap",
    _ref_overlap,
    [_o1, _o2, _o3, _o4, _o5, _o6, _o7, _o8],
)


# --- ch03-bm25 ---


def _ref_bm25():
    from solutions.reference.ch03 import bm25_scores

    return bm25_scores


def _docs(*texts):
    return [{"doc_id": f"d{i}", "text": t} for i, t in enumerate(texts)]


def _rank(f, query, docs, **kw):
    scores = f(query, docs, **kw)
    return [d for d, _ in sorted(scores.items(), key=lambda p: -p[1])]


def _b1(f):
    """a term present in one document only"""
    docs = _docs("the reactor reached criticality", "a portable cooling appliance", "foil tape")
    scores = f("criticality", docs)
    assert scores["d0"] > 0, f"d0 contains the term; it should score above zero. Got {scores}"
    assert scores["d1"] == 0 and scores["d2"] == 0, (
        f"documents with none of the query terms score zero, got {scores}"
    )


def _b2(f):
    """a term in every document carries almost no signal"""
    docs = _docs("water heater unit", "water cooling unit", "water filter unit")
    scores = f("water", docs)
    assert max(scores.values()) < 0.2, (
        "IDF is the point of the formula: a term appearing in every document distinguishes "
        f"nothing and must score near zero. Got {scores}"
    )


def _b3(f):
    """term frequency saturates"""
    docs = _docs("alpha " * 1 + "filler " * 20, "alpha " * 12 + "filler " * 20, "beta")
    scores = f("alpha", docs)
    ratio = scores["d1"] / scores["d0"]
    assert ratio < 3.0, (
        "this is what separates BM25 from raw TF-IDF. Twelve occurrences is not twelve times "
        "more relevant than one -- the k1 term makes the contribution saturate, so a keyword "
        f"stuffed page cannot dominate. The ratio here is {ratio:.1f}x, which looks linear."
    )
    assert scores["d1"] > scores["d0"], (
        f"more occurrences should still score higher, just sub-linearly. Got {scores}"
    )


def _b4(f):
    """long documents are normalized"""
    short = "reactor criticality"
    long = "reactor criticality " + "unrelated padding text " * 40
    docs = _docs(short, long)
    scores = f("reactor criticality", docs)
    assert scores["d0"] > scores["d1"], (
        "both documents contain the query terms exactly once, but the second buries them in "
        "800 words of padding. The b parameter penalises length so a sprawling document "
        f"cannot win on volume alone. Got {scores}"
    )


def _b5(f):
    """b=0 turns length normalization off"""
    docs = _docs("reactor criticality", "reactor criticality " + "padding " * 40)
    off = f("reactor criticality", docs, b=0.0)
    assert abs(off["d0"] - off["d1"]) < 1e-9, (
        f"with b=0 document length must stop mattering entirely; got {off}"
    )


def _b6(f):
    """an exact identifier retrieves its own document"""
    from agentlib.retrieval_lab import CATALOG_DOCS, IDENTIFIER_QUERIES

    docs = list(CATALOG_DOCS)
    for query, gold in IDENTIFIER_QUERIES:
        top = _rank(f, query, docs)[0]
        assert top == gold, (
            f"{query!r} should retrieve {gold} first -- this is the case lexical retrieval "
            f"exists for, and the one a semantic model cannot learn. Got {top}"
        )


def _b7(f):
    """every document gets a score, including zeros"""
    docs = _docs("alpha", "beta", "gamma")
    scores = f("alpha", docs)
    assert set(scores) == {"d0", "d1", "d2"}, (
        f"return a score for every document keyed by doc_id, not just the matches; got "
        f"{sorted(scores)}"
    )


def _b8(f):
    """a query term absent from the whole corpus is harmless"""
    docs = _docs("alpha one", "alpha two")
    scores = f("alpha nonexistentterm", docs)
    assert all(s > 0 for s in scores.values()), (
        f"an unseen term contributes nothing and must not zero out or crash the rest of the "
        f"query. Got {scores}"
    )


def _b9(f):
    """the caller's documents are not modified"""
    docs = _docs("alpha", "beta")
    before = [dict(d) for d in docs]
    f("alpha", docs)
    assert docs == before, f"scoring must not mutate the input documents; they are now {docs}"


task(
    "ch03-bm25",
    _ref_bm25,
    [_b1, _b2, _b3, _b4, _b5, _b6, _b7, _b8, _b9],
)
