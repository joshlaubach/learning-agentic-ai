"""Graded task suites for Chapter 2 — Agent Control Flow.

Planning, subagent context isolation, and leak detection. The isolation cases work by handing
the subagent a brain that reports exactly what it was shown, which is the only way to prove
isolation actually happened rather than merely looking like it did.
"""

from __future__ import annotations

import json

from agentlib.grading import task


def _ok(value):
    return {"status": "ok", "result": value}


# --- ch02-planner ---


def _ref_planner():
    from solutions.reference.ch02 import plan_subtasks

    return plan_subtasks


def _n1(f):
    """the chapter's two-part demo task"""
    got = f("Prepare a short knowledge brief: who founded Anthropic, and what is the ReAct pattern?")
    assert isinstance(got, list), (
        f"a plan is a LIST of subtask strings, one per unit of work Bob can dispatch. "
        f"Got {type(got).__name__}: {got!r}. Returning one string means Bob has nothing to "
        "iterate over, so the whole team collapses back into a single agent."
    )
    assert len(got) == 2, f"this task splits into two subtasks; got {len(got)}: {got!r}"


def _n2(f):
    """every element of a plan is a string"""
    got = f("who founded Anthropic, and what is the ReAct pattern?")
    assert all(isinstance(s, str) for s in got), (
        f"each subtask must be a plain string Bob can hand to a subagent; got {got!r}"
    )


def _n3(f):
    """the subtasks between them cover the original task"""
    got = f("who founded Anthropic, and what is the ReAct pattern?")
    joined = " ".join(got).lower()
    assert "anthropic" in joined, f"no subtask covers the Anthropic half of the task: {got!r}"
    assert "react" in joined, f"no subtask covers the ReAct half of the task: {got!r}"


def _n4(f):
    """a task that needs no decomposition"""
    got = f("What is 2 + 2?")
    assert isinstance(got, list), (
        f"even an undecomposable task returns a LIST, so Bob's dispatch loop works "
        f"unchanged; got {type(got).__name__}: {got!r}"
    )
    assert len(got) == 1, f"one indivisible task is a one-item plan; got {got!r}"


def _n5(f):
    """a plan is never empty"""
    for task_text in ["What is 2 + 2?", "anything at all", ""]:
        got = f(task_text)
        assert len(got) >= 1, (
            f"an empty plan gives Bob nothing to dispatch and silently produces an empty "
            f"draft; task {task_text!r} planned to {got!r}"
        )


def _n6(f):
    """each subtask stands on its own"""
    got = f("who founded Anthropic, and what is the ReAct pattern?")
    for subtask in got:
        assert subtask.strip(), f"a blank subtask is not dispatchable; got {got!r}"
        assert len(subtask) > 3, (
            f"a subtask has to carry enough to answer on its own -- a subagent starts from a "
            f"fresh context and sees nothing but this string. Got {subtask!r}"
        )


def _n7(f):
    """planning is case-insensitive"""
    got = f("WHO FOUNDED ANTHROPIC, AND WHAT IS THE REACT PATTERN?")
    assert len(got) == 2, (
        f"a real task arrives in whatever case the user typed; match on lowered text. "
        f"Got {got!r}"
    )


def _n8(f):
    """the returned list is not shared between calls"""
    a = f("What is 2 + 2?")
    a.append("mutated")
    b = f("What is 2 + 2?")
    assert "mutated" not in b, (
        "each call must build a fresh list; returning a shared module-level list means one "
        f"caller's edits leak into the next plan. Second call returned {b!r}"
    )


task("ch02-planner", _ref_planner, [_n1, _n2, _n3, _n4, _n5, _n6, _n7, _n8])


# --- ch02-subagent ---


def _ref_subagent():
    from solutions.reference.ch02 import run_subagent

    return run_subagent


def _simple_brain(messages):
    observations = [m for m in messages if m.get("role") == "observation"]
    if not observations:
        return {"action": "mock_search", "action_input": messages[0]["content"]}
    return {"action": "final_answer", "action_input": observations[-1]["content"].get("result", "")}


def _tool(value=_ok("Dario and Daniela Amodei")):
    calls = []

    def t(action_input):
        calls.append(action_input)
        return value

    t.calls = calls
    return t


def _s1(f):
    """a one-tool subtask returns its synthesis and step count"""
    got = f("who founded anthropic?", _simple_brain, {"mock_search": _tool()})
    assert isinstance(got, tuple) and len(got) == 2, (
        f"run_subagent returns (result, steps_used); got {got!r}"
    )
    result, steps = got
    assert result == "Dario and Daniela Amodei", f"expected the tool's result back; got {result!r}"
    assert steps == 2, f"one search then one final_answer is 2 steps; got {steps}"


def _s2(f):
    """the subagent starts from a context containing only its own subtask"""
    seen = {}

    def spy(messages):
        seen.setdefault("first_call", list(messages))
        return {"action": "final_answer", "action_input": "done"}

    f("my bounded subtask", spy, {})
    assert seen["first_call"] == [{"role": "user", "content": "my bounded subtask"}], (
        "a subagent's whole point is a FRESH context: on its first call it must see exactly "
        "one message, its own subtask, and nothing from the parent's conversation. It saw "
        f"{seen['first_call']!r}. Threading the parent's messages in defeats the isolation "
        "and re-imports the token cost the subagent was spawned to avoid."
    )


def _s3(f):
    """nothing the subagent does leaks back out"""
    result, _ = f("who founded anthropic?", _simple_brain, {"mock_search": _tool()})
    assert isinstance(result, str), f"the compressed synthesis is a string; got {result!r}"
    assert "observation" not in result and "role" not in result, (
        "only the final answer crosses back to the parent -- not the tool observations or "
        f"the message scaffolding that produced it. Got {result!r}"
    )


def _s4(f):
    """leaky=True hands back the whole transcript instead"""
    result, _ = f("who founded anthropic?", _simple_brain, {"mock_search": _tool()}, leaky=True)
    parsed = json.loads(result)
    assert isinstance(parsed, list) and len(parsed) >= 2, (
        f"leaky=True returns the full message list as JSON -- this chapter's break-it "
        f"section depends on it; got {result!r}"
    )
    assert any(m.get("role") == "observation" for m in parsed), (
        f"the leaked transcript should include the tool observations; got {parsed!r}"
    )


def _s5(f):
    """observations are threaded back inside the subagent's own loop"""
    tool = _tool()
    result, _ = f("who founded anthropic?", _simple_brain, {"mock_search": tool})
    assert tool.calls == ["who founded anthropic?"], (
        f"the subagent's brain drives its own ReAct loop; the tool saw {tool.calls}"
    )
    assert result == "Dario and Daniela Amodei", (
        "isolation is about what crosses the boundary, not about crippling the subagent -- "
        f"inside its own loop it still needs to see its observations. Got {result!r}"
    )


def _s6(f):
    """a subagent that never finishes is capped"""
    tool = _tool()
    result, steps = f("endless", lambda m: {"action": "mock_search", "action_input": "x"},
                      {"mock_search": tool}, max_iterations=3)
    assert len(tool.calls) == 3, (
        f"max_iterations=3 bounds the subagent at 3 tool calls; got {len(tool.calls)}"
    )
    assert steps == 3 and isinstance(result, str), (
        f"an exhausted subagent still returns (message, steps); got ({result!r}, {steps})"
    )


def _s7(f):
    """an unknown tool does not crash the subagent"""
    result, _ = f("bad tool", lambda m: {"action": "nope", "action_input": "x"},
                  {}, max_iterations=2)
    assert isinstance(result, str), (
        f"a tool the subagent does not have must be handled, not raise KeyError; got {result!r}"
    )


def _s8(f):
    """two subagents in a row do not share context"""
    seen = []

    def spy(messages):
        seen.append(len(messages))
        return {"action": "final_answer", "action_input": "done"}

    f("first subtask", spy, {})
    f("second subtask", spy, {})
    assert seen == [1, 1], (
        "every subagent gets its own fresh message list -- the second must not inherit "
        f"anything from the first. First saw {seen[0]} message(s), second saw {seen[1]}. "
        "A module-level messages list is the usual cause."
    )


def _s9(f):
    """the subtask is what seeds the fresh context"""
    seen = {}

    def spy(messages):
        seen["content"] = messages[0]["content"]
        return {"action": "final_answer", "action_input": "done"}

    f("what is the react pattern?", spy, {})
    assert seen["content"] == "what is the react pattern?", (
        f"the subagent's first message is its subtask, verbatim; got {seen['content']!r}"
    )


task("ch02-subagent", _ref_subagent, [_s1, _s2, _s3, _s4, _s5, _s6, _s7, _s8, _s9])


# --- ch02-leak-check ---


_COMPRESSED = "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei."
_LONG_COMPRESSED = (
    "Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei, along with several "
    "colleagues who had previously worked at OpenAI. The ReAct pattern, introduced by Yao "
    "et al. in 2022, interleaves reasoning traces with actions so a model can plan and use "
    "tools inside the same loop rather than separating the two into distinct phases."
)
_LEAKY = json.dumps([
    {"role": "user", "content": "who founded anthropic?"},
    {"role": "observation", "tool": "mock_search", "content": {"status": "ok", "result": _COMPRESSED}},
    {"role": "assistant", "content": _COMPRESSED},
])
_SHORT_LEAKY = json.dumps([{"role": "user", "content": "hi"}])


def _ref_leak():
    from solutions.reference.ch02 import is_leaky_result

    return is_leaky_result


def _k1(f):
    """a full raw transcript"""
    assert f(_LEAKY) is True, "a JSON array of message objects is a leaked transcript"


def _k2(f):
    """a compressed one-sentence synthesis"""
    assert f(_COMPRESSED) is False, f"plain prose is what a subagent is supposed to return"


def _k3(f):
    """a long but legitimate synthesis"""
    got = f(_LONG_COMPRESSED)
    assert got is False, (
        "length is not the signal. This is 60-odd words of ordinary prose -- a perfectly "
        "well-behaved subagent answering a broad question -- and flagging it as a leak "
        f"would truncate a correct answer. Got {got!r}. What makes a result leaky is its "
        "STRUCTURE: a serialized list of role/content message objects."
    )


def _k4(f):
    """a short leaked transcript"""
    got = f(_SHORT_LEAKY)
    assert got is True, (
        "a leak is a leak at any size. This transcript is shorter than the legitimate "
        f"answer above, so a word-count threshold lets it straight through. Got {got!r}."
    )


def _k5(f):
    """an empty string"""
    assert f("") is False, "nothing at all is not a transcript"


def _k6(f):
    """prose that merely mentions the word 'role'"""
    got = f("The founder's role was to set research direction; content strategy came later.")
    assert got is False, (
        "searching for the substrings 'role' or 'content' flags ordinary English. "
        f"Got {got!r} -- parse the structure instead."
    )


def _k7(f):
    """a JSON scalar rather than a transcript"""
    for value in ['"just a quoted string"', "42", "null", "true"]:
        got = f(value)
        assert got is False, (
            f"valid JSON is not the test; a transcript is specifically an ARRAY of message "
            f"objects. {value!r} returned {got!r}"
        )


def _k8(f):
    """a JSON array that is not messages"""
    got = f(json.dumps(["anthropic", "react"]))
    assert got is False, (
        f"an array of plain strings is not a transcript -- the elements have to look like "
        f"messages, with role and content. Got {got!r}"
    )


def _k9(f):
    """an empty JSON array"""
    got = f("[]")
    assert got is False, f"an empty array carries no leaked context; got {got!r}"


def _k10(f):
    """the answer is a real bool"""
    got = f(_LEAKY)
    assert isinstance(got, bool), (
        f"return True or False, not a truthy value -- callers branch on this directly. "
        f"Got {type(got).__name__}: {got!r}"
    )


task("ch02-leak-check", _ref_leak, [_k1, _k2, _k3, _k4, _k5, _k6, _k7, _k8, _k9, _k10])
