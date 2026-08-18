"""Graded task suites for Chapter 8 — System Design and Engineering Judgment.

These two are structural, and deliberately so. There is no single correct design doc, so
grading against a hidden model answer would be worse than useless -- it would teach the
learner to guess at wording. What these suites check instead is that every question was
actually answered, at a depth that would survive one follow-up question in an interview,
which is the failure mode this chapter is really about: a design answer that sounds complete
and turns out to be three words per heading.
"""

from __future__ import annotations

import re
from dataclasses import fields

from agentlib.grading import task

_MIN_WORDS = 40

_PLACEHOLDERS = (
    "todo",
    "tbd",
    "fill this in",
    "fill in",
    "your answer here",
    "replace this",
    "xxx",
    "lorem ipsum",
)

# Each of the five reasons from this chapter's "When not to use an agent at all" section,
# with enough synonyms that a learner who understood the idea is not failed for word choice.
_REASON_MARKERS = {
    "the task is actually deterministic": (
        "deterministic", "if/else", "if/elif", "rule-based", "rules engine", "plain code",
        "ordinary code", "fixed sequence", "hard-code", "hardcode", "just code", "regular code",
    ),
    "a single LLM call already solves it": (
        "single call", "single llm call", "single model call", "one call", "one llm call",
        "one-shot", "one shot", "single-shot", "single shot", "no loop", "without a loop",
        "no tools", "single completion",
    ),
    "failure cost is high at volume with no verification": (
        "irreversible", "failure cost", "high volume", "high-volume", "blast radius",
        "error rate", "at scale", "unacceptable", "cost of being wrong", "no verification",
        "cannot be undone", "can't be undone",
    ),
    "the latency budget is tighter than a round trip": (
        "latency", "millisecond", "round trip", "round-trip", "real time", "real-time",
        "p99", "p95", "response time", "too slow",
    ),
    "success cannot be defined or evaluated": (
        "evaluat", "cannot define success", "can't define success", "define what success",
        "no way to tell", "cannot tell", "can't tell", "cannot measure", "can't measure",
        "no ground truth", "how would you know",
    ),
}


def _named_reasons(text: str) -> set[str]:
    lowered = text.lower()
    return {
        reason
        for reason, markers in _REASON_MARKERS.items()
        if any(marker in lowered for marker in markers)
    }


def _doc_fields(doc):
    return [f.name for f in fields(doc) if f.name != "scenario"]


# --- ch08-design-doc ---


def _ref_doc():
    from solutions.reference.ch08 import DESIGN_DOC

    return DESIGN_DOC


def _d1(f):
    """the doc has all nine framework questions plus a scenario"""
    names = [x.name for x in fields(f)]
    assert "scenario" in names, f"the doc needs a scenario to be a design for; got {names}"
    assert len(_doc_fields(f)) == 9, (
        f"the framework is nine questions, so nine fields besides scenario; got "
        f"{_doc_fields(f)}"
    )


def _d2(f):
    """the scenario is stated"""
    assert len(f.scenario.split()) >= 15, (
        "name the system you are designing, concretely enough that the answers below mean "
        f"something. Got {f.scenario!r}"
    )


def _d3(f):
    """no question is left unanswered"""
    blank = [name for name in _doc_fields(f) if not getattr(f, name).strip()]
    assert not blank, (
        f"unanswered: {blank}. Every one of the nine is load-bearing -- an interviewer picks "
        "the one you skipped, and 'I'd have to think about that' is the answer they remember."
    )


def _d4(f):
    """every answer is developed rather than gestured at"""
    thin = {
        name: len(getattr(f, name).split())
        for name in _doc_fields(f)
        if len(getattr(f, name).split()) < _MIN_WORDS
    }
    assert not thin, (
        f"too thin, in words: {thin} (each needs at least {_MIN_WORDS}). A heading with a "
        "phrase under it reads as complete on the page and collapses on the first follow-up. "
        "The point of writing it out at length is that you find the gaps yourself, before "
        "someone else does."
    )


def _d5(f):
    """no placeholder text survived"""
    found = [
        name
        for name in _doc_fields(f) + ["scenario"]
        if any(p in getattr(f, name).lower() for p in _PLACEHOLDERS)
    ]
    assert not found, f"placeholder text still in {found}; write the real answer"


def _d6(f):
    """the answers are not the same paragraph nine times"""
    seen = {}
    for name in _doc_fields(f):
        body = " ".join(getattr(f, name).lower().split())
        if body in seen:
            raise AssertionError(
                f"{name!r} and {seen[body]!r} contain identical text. Nine questions with "
                "one answer between them is one answer."
            )
        seen[body] = name


def _d7(f):
    """question 0 actually takes a position"""
    answer = f.needs_an_agent.lower()
    assert re.search(r"\b(yes|no|not|should|would|wouldn't|shouldn't)\b", answer), (
        "commit. 'Does this need an agent' wants a yes or a no and then the reasoning -- "
        f"a survey of considerations is what a candidate says when they haven't decided. "
        f"Got {f.needs_an_agent!r}"
    )


def _d8(f):
    """the budget has numbers in it"""
    assert re.search(r"\d", f.cost_latency_budget), (
        "a budget without a number is not a budget. Put a latency target and a cost-per-"
        f"request figure in it, even rough ones. Got {f.cost_latency_budget!r}"
    )


def _d9(f):
    """the evaluation plan says how, not just that"""
    answer = f.evaluation_plan.lower()
    assert any(
        marker in answer
        for marker in (
            "metric", "accuracy", "precision", "recall", "rate", "score", "golden",
            "label", "human", "a/b", "canary", "offline", "online", "benchmark", "eval set",
        )
    ), (
        "name something you would actually measure and how you would get the ground truth. "
        f"'We would evaluate it' is the answer this field exists to stop. Got "
        f"{f.evaluation_plan!r}"
    )


def _d10(f):
    """blank_fields() reports honestly"""
    assert f.blank_fields() == [], (
        f"the doc's own blank_fields() still reports {f.blank_fields()}"
    )


task(
    "ch08-design-doc",
    _ref_doc,
    [_d1, _d2, _d3, _d4, _d5, _d6, _d7, _d8, _d9, _d10],
)


# --- ch08-no-agent-case ---


def _ref_no_agent():
    from solutions.reference.ch08 import NO_AGENT_CASE

    return NO_AGENT_CASE


def _a1(f):
    """the answer is written out"""
    assert isinstance(f, str) and f.strip(), f"write the answer as a string; got {f!r}"


def _a2(f):
    """it is long enough to be an answer"""
    assert len(f.split()) >= 100, (
        f"this is the question that separates a competent design answer from a good one, and "
        f"it takes more than a sentence. Got {len(f.split())} words; aim for 100 or more."
    )


def _a3(f):
    """at least two distinct reasons are named"""
    reasons = _named_reasons(f)
    assert len(reasons) >= 2, (
        f"only {len(reasons)} of the five reasons came through: {sorted(reasons) or 'none'}. "
        "The five are: the task is actually deterministic; a single LLM call already solves "
        "it; the failure cost is high at volume with no verification step; the latency budget "
        "is tighter than a round trip; and success cannot be defined well enough to evaluate. "
        "Naming one and elaborating on it is a narrower answer than naming two and being "
        "brief about both."
    )


def _a4(f):
    """the reasons are genuinely different from each other"""
    reasons = _named_reasons(f)
    assert len(reasons) >= 2, (
        f"the reasons found all collapse to the same one: {sorted(reasons)}. Restating a "
        "point in different words is not a second point."
    )


def _a5(f):
    """it says what to build instead"""
    lowered = f.lower()
    assert any(
        marker in lowered
        for marker in (
            "instead", "rather than", "i would build", "i'd build", "i would write",
            "i'd write", "simpler", "plain code", "single call", "one call", "would ship",
        )
    ), (
        "the honest answer is 'no, and here is the simpler thing I would build instead'. "
        "Stopping at 'don't use an agent' leaves the interviewer to guess whether you have "
        "an alternative in mind."
    )


def _a6(f):
    """no placeholder text"""
    lowered = f.lower()
    found = [p for p in _PLACEHOLDERS if p in lowered]
    assert not found, f"placeholder text still present: {found}"


def _a7(f):
    """it is not just the question restated"""
    lowered = " ".join(f.lower().split())
    assert lowered not in ("when not to use an agent", "when not to use an agent at all"), (
        "that is the heading, not the answer"
    )


task("ch08-no-agent-case", _ref_no_agent, [_a1, _a2, _a3, _a4, _a5, _a6, _a7])
