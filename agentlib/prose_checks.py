"""Shared helpers for grading written answers.

Some of this course's exercises are diagnoses and judgment calls, not functions, and those
cannot be graded by comparing against a model answer -- there isn't one, and checking wording
would teach a learner to guess at phrasing instead of to think.

What these helpers grade instead is whether an answer names the thing it has to name. Each
concept is a FAMILY of markers rather than one required word, generously enough that someone
who understood the idea is not failed for word choice. Grading prose is inherently a blunt
instrument; the families exist to keep it blunt in the forgiving direction.
"""

from __future__ import annotations

PLACEHOLDERS = (
    "todo",
    "tbd",
    "fill this in",
    "fill in",
    "your answer here",
    "replace this",
    "write your",
    "xxx",
    "lorem ipsum",
)


def mentions(text: str, markers) -> bool:
    """Does the answer contain any marker from this family?"""
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def matched(text: str, markers) -> list:
    """Which markers from this family the answer used -- for building failure messages."""
    lowered = text.lower()
    return [marker for marker in markers if marker in lowered]


def is_written_answer(text, min_words: int) -> None:
    """Shared shape checks every written answer has to clear before anything else."""
    assert isinstance(text, str), (
        f"write your answer as a string; got {type(text).__name__}"
    )
    stripped = text.strip()
    assert stripped, "the answer is empty"
    found = [p for p in PLACEHOLDERS if p in stripped.lower()]
    assert not found, f"placeholder text still present: {found}"
    words = len(stripped.split())
    assert words >= min_words, (
        f"{words} words, and this one needs at least {min_words}. A diagnosis that fits in a "
        "sentence is a guess; the reasoning is the part worth writing down, and the part an "
        "interviewer asks about."
    )
