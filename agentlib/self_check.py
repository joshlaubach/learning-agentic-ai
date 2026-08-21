"""Answer slots and on-demand reveals for the chapters' written interview drills.

The drills used to be a markdown list and nothing else: five questions, no place to put an
answer, and a closing line telling you to go open a file in `solutions/`. That is a reading
exercise wearing an exercise's clothes. Writing the answer down is most of the value, and
comparing it to a model answer immediately afterwards -- while you still remember what you
were unsure about -- is the rest.

The reveal is deliberately a method call rather than a printed answer. Nothing here shows you
an answer you did not ask for, and `check()` refuses to show one until you have written
something of your own, because the moment you have read the model answer you can no longer
find out what you actually knew.

Questions and answers are both parsed out of `solutions/chNN_*_answers.md` at runtime, so the
notebooks never contain an answer and there is only one copy to keep correct.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from agentlib.prose_checks import PLACEHOLDERS

_SOLUTIONS = Path(__file__).resolve().parent.parent / "solutions"

# Numbered answers appear at ## in some files and ### in others, depending on whether the
# chapter groups its drill under a section heading. Accept either rather than reformatting
# nine files to satisfy a regex.
_HEADING = re.compile(r"^(#{2,3})\s+(\d+)\.\s*(.+?)\s*$", re.M)

_MIN_WORDS = 25


def _answers_path(chapter: int) -> Path:
    matches = sorted(_SOLUTIONS.glob(f"ch{chapter:02d}_*_answers.md"))
    if not matches:
        raise FileNotFoundError(
            f"no answers file for chapter {chapter} in {_SOLUTIONS}; expected "
            f"ch{chapter:02d}_<name>_answers.md"
        )
    return matches[0]


def _parse(path: Path) -> dict:
    """{number: (question_text, answer_markdown)} for one chapter's answers file."""
    text = path.read_text()
    hits = list(_HEADING.finditer(text))
    parsed = {}
    for i, match in enumerate(hits):
        number = int(match.group(2))
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        parsed[number] = (match.group(3), text[match.end() : end].strip())
    return parsed


def _looks_unanswered(text: str) -> str | None:
    """Why this text is not a real attempt, or None if it is one."""
    stripped = (text or "").strip()
    if not stripped:
        return "it is empty"
    lowered = stripped.lower()
    if any(marker in lowered for marker in PLACEHOLDERS):
        return "it is still the placeholder"
    words = len(stripped.split())
    if words < _MIN_WORDS:
        return f"it is {words} words, and these questions need at least {_MIN_WORDS} to answer"
    return None


class Drill:
    """One chapter's written drill: somewhere to answer, and a reveal when you're ready."""

    def __init__(self, chapter: int):
        self.chapter = chapter
        self._path = _answers_path(chapter)
        self._bank = _parse(self._path)
        self._attempts: dict[int, str] = {}
        if not self._bank:
            raise ValueError(f"no numbered answers found in {self._path.name}")

    # -- reading the questions ---------------------------------------------------------

    def questions(self) -> None:
        """Print every question in this chapter's drill, with its number."""
        print(f"Chapter {self.chapter} written drill — {len(self._bank)} questions\n")
        for number in sorted(self._bank):
            question, _ = self._bank[number]
            print(f"{number}. {textwrap.fill(question, 92, subsequent_indent='   ')}")

    # -- answering ---------------------------------------------------------------------

    def attempt(self, number: int, text: str) -> None:
        """Record your answer to question `number`."""
        if number not in self._bank:
            raise KeyError(
                f"chapter {self.chapter} has questions {sorted(self._bank)}, not {number}"
            )
        problem = _looks_unanswered(text)
        if problem:
            print(f"  {number}. not recorded — {problem}")
            return
        self._attempts[number] = text.strip()
        print(f"  {number}. recorded ({len(text.split())} words)")

    def status(self) -> None:
        """Show which questions you have answered and which are still open."""
        done = sorted(self._attempts)
        todo = [n for n in sorted(self._bank) if n not in self._attempts]
        print(f"Chapter {self.chapter}: {len(done)}/{len(self._bank)} answered")
        if done:
            print(f"  answered:   {done}")
        if todo:
            print(f"  still open: {todo}")
        else:
            print("  all answered — check(n) to compare each against the model answer")

    # -- revealing ---------------------------------------------------------------------

    def check(self, number: int) -> None:
        """Show your answer to `number`, then the model answer, for comparison."""
        if number not in self._bank:
            raise KeyError(
                f"chapter {self.chapter} has questions {sorted(self._bank)}, not {number}"
            )
        question, model = self._bank[number]

        if number not in self._attempts:
            print(
                f"Question {number} has no recorded answer yet.\n\n"
                f"  {textwrap.fill(question, 92, subsequent_indent='  ')}\n\n"
                "Write one with attempt() first. Reading the model answer before you have "
                "committed to your own turns this into a reading exercise -- once you have "
                "seen it you can no longer find out what you actually knew.\n"
                f"(If you really want it anyway: reveal({number}).)"
            )
            return

        print(f"QUESTION {number}\n{textwrap.fill(question, 92)}\n")
        print("-" * 92)
        print("YOUR ANSWER\n")
        print(textwrap.indent(self._attempts[number], "  "))
        print("\n" + "-" * 92)
        print("MODEL ANSWER\n")
        print(textwrap.indent(model, "  "))

    def reveal(self, number: int) -> None:
        """Print the model answer for `number` regardless of whether you attempted it."""
        if number not in self._bank:
            raise KeyError(
                f"chapter {self.chapter} has questions {sorted(self._bank)}, not {number}"
            )
        question, model = self._bank[number]
        print(f"QUESTION {number}\n{textwrap.fill(question, 92)}\n")
        print("MODEL ANSWER\n")
        print(textwrap.indent(model, "  "))


def drill(chapter: int) -> Drill:
    """Open one chapter's written drill."""
    return Drill(chapter)
