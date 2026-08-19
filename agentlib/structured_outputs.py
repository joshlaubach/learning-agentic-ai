"""Shared machinery for Chapter 7's structured-output lab.

Why this is a module rather than notebook cells: the whole argument of the lab is that three
different strategies, run against *the same model on the same input*, do not perform the
same. That comparison is only honest if none of the three can quietly change the model to
suit itself. Keeping the generator here, out of reach of the cells the learner edits, is what
makes the comparison mean something.

`MockModel` below is the model surface. It is a stand-in, but not a strawman: it is built to
fail the way real models actually fail when you ask them for JSON. It wants to be helpful, so
it wraps output in markdown fences and adds a sentence of prose; and it is imprecise about
syntax, so it sometimes drops the quotes on a key or leaves a trailing comma. Crucially, the
*correct* token is always somewhere in its candidate list -- just not always the one with the
highest score. That last detail is the entire reason constrained decoding works at all: the
mass is there, the argmax is simply pointed somewhere else, and a decoder that can mask the
invalid options will find it.

`is_allowed` is the grammar surface: given what has been emitted so far, may this token come
next? It is deliberately written against a narrow grammar -- a flat JSON object whose keys are
exactly a known field list and whose values are strings -- because that is the shape almost
every real extraction task has, and because a decoder for it fits in a screenful. Real
implementations (llama.cpp's GBNF, Outlines' regex-to-FSM compiler, the `response_format`
parameter on hosted APIs) do the same thing over a much larger grammar.
"""

from __future__ import annotations

import hashlib
import json

# The three fields every record in this lab carries. A flat object of string-valued keys --
# the shape of nearly every extraction task, and small enough that a grammar for it is
# readable rather than a parser-generator exercise.
FIELDS = ("name", "version", "summary")

# The blurbs the model is asked to extract from, paired with what a correct extraction is.
# Kept as data so the same records drive the naive path, the retry path, and the constrained
# path, and any difference in outcome is attributable to the strategy rather than the input.
RECORDS = (
    {"name": "numpy", "version": "2.4.6", "summary": "Fundamental package for array computing"},
    {"name": "pydantic", "version": "2.13.4", "summary": "Data validation using Python type hints"},
    {"name": "tiktoken", "version": "0.13.0", "summary": "Fast BPE tokeniser for OpenAI models"},
)

# Every way this lab's model departs from valid JSON. The first three are *formatting* noise
# that lives outside the JSON itself; the last two corrupt the JSON's own syntax. That split
# is the point of the lab: a repair pass that strips wrappers handles the first group
# completely and the second group not at all.
QUIRKS = ("fence", "preamble", "epilogue", "unquoted_key", "trailing_comma")

# A sixth failure that belongs to neither group above: the model returns syntactically perfect
# JSON that is simply missing a field, usually because it could not find one in the source and
# quietly moved on. It is kept out of QUIRKS because it is not a formatting problem at all --
# it is the reason "did it parse?" is the wrong success condition. See `drop_field` below.
DROP_FIELD = "drop_field"

_WRAPPER_QUIRKS = frozenset({"fence", "preamble", "epilogue"})
_SYNTAX_QUIRKS = frozenset({"unquoted_key", "trailing_comma"})


def _canonical_tokens(record: dict, fields=FIELDS) -> list[str]:
    """The token sequence for a correct, minimal JSON encoding of `record`.

    Tokens are meaningful chunks rather than BPE pieces -- a whole key literal, a whole value
    literal, one structural character. Nothing in the lab depends on the tokenizer being
    realistic, only on there being a token boundary everywhere a decision gets made.
    """
    tokens = ["{"]
    for i, field in enumerate(fields):
        if i:
            tokens.append(",")
        tokens.append(json.dumps(field))
        tokens.append(":")
        tokens.append(json.dumps(record[field]))
    tokens.append("}")
    return tokens


class MockModel:
    """A model that has been asked for JSON and does not reliably produce it.

    Drive it one token at a time: `candidates()` reports what it would consider emitting
    next, and `accept(token)` commits one of them. `generate()` runs that loop the way an
    ordinary caller would -- take the highest-scoring candidate every time, no masking -- and
    returns the raw string, which is where the fences and the broken syntax come from.

    `calls` counts completed `generate()` runs, so a retry loop's cost is measurable rather
    than asserted.
    """

    def __init__(self, record: dict, quirks=("fence", "preamble", "epilogue"), *, flaky_until: int = 0):
        self.record = dict(record)
        self.quirks = tuple(quirks)
        # When flaky_until is n, the first n generations misbehave and every one after is
        # clean. That is the transient case -- the one a retry loop genuinely does fix.
        # Leave it at 0 and the model is systematically broken: retrying changes nothing.
        self.flaky_until = flaky_until
        self.calls = 0
        # A model carrying the drop_field quirk never emits the last field at all. Its output
        # is valid JSON on every attempt, so a retry loop that stops at "it parsed" accepts an
        # incomplete record and reports success.
        self._fields = FIELDS[:-1] if DROP_FIELD in self.quirks else FIELDS
        self._path = _canonical_tokens(self.record, self._fields)
        self.reset()
        # reset() bumps this, so zero it after the constructor's own call. It counts decodes
        # STARTED, which is what separates a strategy that re-prompts from one that does not.
        self.generations = 0

    # -- generation state -------------------------------------------------------------

    def reset(self) -> None:
        """Start a fresh generation. Does not reset `calls`."""
        self.generations = getattr(self, "generations", 0) + 1
        self._pos = 0
        self._emitted: list[str] = []
        self._spent: set[str] = set()

    def _active_quirks(self) -> frozenset:
        """Which quirks apply to the generation currently in progress."""
        if self.flaky_until and self.calls >= self.flaky_until:
            return frozenset()
        return frozenset(self.quirks)

    @property
    def done(self) -> bool:
        """True once the model has emitted everything it intends to emit."""
        return self._pos >= len(self._path) and "epilogue" not in (
            self._active_quirks() - self._spent
        )

    def candidates(self) -> list[tuple[str, float]]:
        """What this model would consider emitting next, as (token, score) pairs.

        Returned in a deliberately arbitrary order rather than sorted by score. Real APIs hand
        back a distribution, not a ranking, and a decoder that assumes the first entry is the
        best one is making an assumption it has not earned.
        """
        active = self._active_quirks() - self._spent
        out: list[tuple[str, float]] = []

        # The token that would actually be correct here. Always present, so the model is never
        # the reason a constrained decode fails -- only the ranking is.
        if self._pos < len(self._path):
            correct = self._path[self._pos]
            out.append((correct, 0.55))

            # A plausible-but-wrong value: right shape, truncated content. Scored below the
            # correct token, so a decoder that masks correctly and then takes the *best*
            # survivor is safe, while one that takes the *first* survivor is not.
            if self._is_value_slot() and len(json.loads(correct)) > 4:
                out.append((json.dumps(json.loads(correct)[:4]), 0.20))

        # Formatting noise, scored above the correct token -- which is exactly why plain
        # greedy decoding walks into it.
        if self._pos == 0:
            if "fence" in active:
                out.append(("```json\n", 0.85))
            if "preamble" in active:
                out.append(("Here is the JSON you asked for:\n", 0.90))
        if self._pos >= len(self._path):
            if "fence" in active:
                out.append(("\n```", 0.90))
            if "epilogue" in active:
                out.append(("\n\nLet me know if you need anything else!", 0.80))

        # Broken syntax, also scored above the correct token. Unlike the noise above, no
        # amount of stripping wrappers will recover from these.
        if "unquoted_key" in active and self._is_key_slot():
            out.append((json.loads(self._path[self._pos]), 0.85))
        if "trailing_comma" in active and self._pos == len(self._path) - 1:
            out.append((",", 0.85))

        # Deliberately not sorted -- neither by score nor with the correct token first. A real
        # API hands back a distribution keyed by token, and a decoder that treats position in
        # that list as a ranking is relying on something it was never promised. Ordering by a
        # digest keeps it stable across runs while making that assumption fail loudly.
        out.sort(key=lambda pair: hashlib.md5(pair[0].encode()).hexdigest())
        return out

    def _is_key_slot(self) -> bool:
        return self._pos < len(self._path) and self._path[self._pos] in {
            json.dumps(f) for f in self._fields
        }

    def _is_value_slot(self) -> bool:
        return self._pos > 0 and self._path[self._pos - 1] == ":"

    def accept(self, token: str) -> None:
        """Commit `token` as the next emitted token."""
        self._emitted.append(token)
        on_path = self._pos < len(self._path) and token == self._path[self._pos]
        # An unquoted key still satisfies the model's own sense of progress; it just does not
        # satisfy a parser. Count it as progress, so the generation terminates either way and
        # the damage shows up at parse time rather than as a hang.
        unquoted_key = self._is_key_slot() and token == json.loads(self._path[self._pos])
        if on_path or unquoted_key:
            self._pos += 1
        else:
            # Wrappers, prose, stray commas: emitted, but no progress through the record.
            self._spent.add(_quirk_for(token))

    @property
    def text(self) -> str:
        """Everything emitted so far, concatenated."""
        return "".join(self._emitted)

    def generate(self) -> str:
        """One ordinary, unconstrained call: greedy argmax at every step.

        This is what "just ask the model for JSON" gets you, and what the naive-repair and
        retry strategies both have to work with.
        """
        self.reset()
        guard = 0
        while not self.done and guard < 200:
            guard += 1
            cands = self.candidates()
            if not cands:
                break
            token, _ = max(cands, key=lambda pair: pair[1])
            self.accept(token)
        self.calls += 1
        return self.text


def _quirk_for(token: str) -> str:
    """Which quirk a non-canonical token belongs to, for one-shot bookkeeping."""
    if token.startswith("```") or token.endswith("```"):
        return "fence"
    if token.startswith("Here is"):
        return "preamble"
    if token.startswith("\n\nLet me know"):
        return "epilogue"
    if token == ",":
        return "trailing_comma"
    return "unquoted_key"


# -- the grammar ----------------------------------------------------------------------


def _state(emitted: list[str], fields=FIELDS) -> tuple[str, frozenset]:
    """Walk `emitted` and report (what is expected next, which fields remain unused).

    States are named for what they want: "open", "key", "colon", "value", "sep", "done".
    Anything that cannot be walked lands in "dead", which allows nothing.
    """
    remaining = set(fields)
    state = "open"
    for token in emitted:
        if state == "open" and token == "{":
            state = "key"
        elif state == "key" and _is_string_literal(token) and json.loads(token) in remaining:
            remaining.discard(json.loads(token))
            state = "colon"
        elif state == "colon" and token == ":":
            state = "value"
        elif state == "value" and _is_string_literal(token):
            state = "sep"
        elif state == "sep" and token == "," and remaining:
            state = "key"
        elif state == "sep" and token == "}" and not remaining:
            state = "done"
        else:
            return "dead", frozenset(remaining)
    return state, frozenset(remaining)


def _is_string_literal(token: str) -> bool:
    """True if `token` is a complete JSON string literal on its own."""
    if not (token.startswith('"') and token.endswith('"') and len(token) >= 2):
        return False
    try:
        return isinstance(json.loads(token), str)
    except ValueError:
        return False


def is_allowed(emitted: list[str], token: str, fields=FIELDS) -> bool:
    """May `token` follow `emitted` and still leave a valid object over `fields` reachable?

    This is the mask. Everything that makes constrained decoding work is right here: it is a
    pure function of the prefix and the grammar, it never consults the model, and it answers
    before a single invalid character is committed. Note what it rules out -- a bare `version`
    with no quotes, a second `,` where the object should close, a key already used, a closing
    brace with fields still missing. None of those are recoverable after the fact, which is
    why catching them at emit time is categorically different from repairing them later.
    """
    state, remaining = _state(list(emitted), fields)
    if state == "open":
        return token == "{"
    if state == "key":
        return _is_string_literal(token) and json.loads(token) in remaining
    if state == "colon":
        return token == ":"
    if state == "value":
        return _is_string_literal(token)
    if state == "sep":
        return (token == "," and bool(remaining)) or (token == "}" and not remaining)
    return False


def is_complete(emitted: list[str], fields=FIELDS) -> bool:
    """True once `emitted` spells a finished object with every field populated."""
    return _state(list(emitted), fields)[0] == "done"


# -- reference strategies -------------------------------------------------------------


def reference_repair(raw: str):
    """Strip markdown fences and surrounding prose, then parse. Returns None on failure.

    Handles every wrapper quirk and no syntax quirk, which is the honest ceiling of this
    approach and the reason it is in the lab.
    """
    text = raw.strip()
    if "```" in text:
        start = text.find("```")
        body = text[start + 3 :]
        if body.lstrip().startswith("json"):
            body = body.lstrip()[4:]
        end = body.find("```")
        text = (body if end == -1 else body[:end]).strip()
    first, last = text.find("{"), text.rfind("}")
    if first == -1 or last == -1 or last < first:
        return None
    try:
        return json.loads(text[first : last + 1])
    except ValueError:
        return None


def reference_retry(model: MockModel, max_attempts: int = 4):
    """Re-prompt until the output parses or the budget runs out. Returns (record, attempts)."""
    for attempt in range(1, max_attempts + 1):
        parsed = reference_repair(model.generate())
        if parsed is not None and set(parsed) == set(FIELDS):
            return parsed, attempt
    return None, max_attempts


def reference_constrained(model: MockModel, fields=FIELDS) -> dict:
    """Decode under the mask: filter to legal tokens, then take the best survivor."""
    model.reset()
    emitted: list[str] = []
    while not is_complete(emitted, fields):
        legal = [(t, s) for t, s in model.candidates() if is_allowed(emitted, t, fields)]
        if not legal:
            raise ValueError(f"no legal continuation after {''.join(emitted)!r}")
        token, _ = max(legal, key=lambda pair: pair[1])
        model.accept(token)
        emitted.append(token)
    model.calls += 1
    return json.loads("".join(emitted))
