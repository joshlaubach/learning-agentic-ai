"""Graded task suites for Chapter 1 — Fundamentals of AI Agents.

The loop, the guard, and memory threading. Every case here drives the implementation under
test with a scripted brain and a recording tool, so a failure points at the learner's control
flow rather than at anything the mock brains do.
"""

from __future__ import annotations

from agentlib.grading import task


def _ok(value):
    """A tool result shaped like the rest of Chapter 1's tools return."""
    return {"status": "ok", "result": value}


def _recording_tool(results):
    """A tool that returns `results` in order (repeating the last one) and logs its inputs."""
    calls = []

    def tool(action_input):
        calls.append(action_input)
        return results[min(len(calls) - 1, len(results) - 1)]

    tool.calls = calls
    return tool


# --- ch01-react-loop ---


def _ref_run_agent():
    from solutions.reference.ch01 import run_agent

    return run_agent


def _l1(f):
    """the brain answers immediately"""
    got = f("hi", lambda m: {"action": "final_answer", "action_input": "done"}, {}, verbose=False)
    assert got == "done", f"a final_answer decision returns its action_input; got {got!r}"


def _l2(f):
    """the task is seeded into messages as the first user turn"""
    seen = {}

    def brain(messages):
        seen["first"] = messages[0]
        return {"action": "final_answer", "action_input": "done"}

    f("summarize Q3", brain, {}, verbose=False)
    assert seen["first"] == {"role": "user", "content": "summarize Q3"}, (
        "the loop must start messages with {'role': 'user', 'content': task} so the brain "
        f"can read the task; the brain saw {seen.get('first')!r}"
    )


def _l3(f):
    """the tool the brain named is the one that runs"""
    tool = _recording_tool([_ok(84)])
    steps = iter([{"action": "calculator", "action_input": "12 * 7"}])

    def brain(messages):
        return next(steps, {"action": "final_answer", "action_input": "84"})

    f("what is 12 * 7?", brain, {"calculator": tool}, verbose=False)
    assert tool.calls == ["12 * 7"], (
        f"the loop must call tools[action](action_input); the tool saw {tool.calls}"
    )


def _l4(f):
    """the observation is fed back so the brain can see the tool's result"""
    tool = _recording_tool([_ok(84)])

    def brain(messages):
        observations = [m for m in messages if m.get("role") == "observation"]
        if not observations:
            return {"action": "calculator", "action_input": "12 * 7"}
        return {"action": "final_answer", "action_input": "the answer is 84"}

    got = f("what is 12 * 7?", brain, {"calculator": tool}, max_iterations=4, verbose=False)
    assert got == "the answer is 84", (
        "the loop must append each observation to messages before calling the brain again. "
        f"This brain only answers once it can SEE an observation, and it never did: got "
        f"{got!r}. Without that append the brain is blind to every tool result and the loop "
        "just repeats the same action until the iteration budget runs out."
    )


def _l5(f):
    """the observation carries the tool's actual return value"""
    tool = _recording_tool([_ok(84)])

    def brain(messages):
        observations = [m for m in messages if m.get("role") == "observation"]
        if not observations:
            return {"action": "calculator", "action_input": "12 * 7"}
        return {"action": "final_answer", "action_input": observations[-1]["content"]}

    got = f("what is 12 * 7?", brain, {"calculator": tool}, max_iterations=4, verbose=False)
    assert got == _ok(84), (
        "the observation appended to messages must carry the tool's return value under "
        f"'content', unchanged; the brain read back {got!r} instead of {_ok(84)!r}"
    )


def _l6(f):
    """the observation records which tool produced it"""
    tool = _recording_tool([_ok(84)])

    def brain(messages):
        observations = [m for m in messages if m.get("role") == "observation"]
        if not observations:
            return {"action": "calculator", "action_input": "12 * 7"}
        return {"action": "final_answer", "action_input": observations[-1].get("tool")}

    got = f("what is 12 * 7?", brain, {"calculator": tool}, max_iterations=4, verbose=False)
    assert got == "calculator", (
        "each observation needs a 'tool' key naming the action that produced it -- the mock "
        f"brains in this chapter branch on it; the brain read back {got!r}"
    )


def _l7(f):
    """two different tools across two steps"""
    calc = _recording_tool([_ok(84)])
    search = _recording_tool([_ok("Dario and Daniela Amodei")])
    plan = iter([
        {"action": "calculator", "action_input": "12 * 7"},
        {"action": "mock_search", "action_input": "anthropic founder"},
    ])

    def brain(messages):
        return next(plan, {"action": "final_answer", "action_input": "both done"})

    got = f("two things", brain, {"calculator": calc, "mock_search": search},
            max_iterations=5, verbose=False)
    assert got == "both done", f"expected the loop to run both steps then finish; got {got!r}"
    assert calc.calls == ["12 * 7"] and search.calls == ["anthropic founder"], (
        f"each step must call its own tool; calculator saw {calc.calls}, search saw {search.calls}"
    )


def _l8(f):
    """the brain never says it is done"""
    tool = _recording_tool([_ok("still working")])
    got = f("never ends", lambda m: {"action": "spin", "action_input": "x"},
            {"spin": tool}, max_iterations=3, verbose=False)
    assert isinstance(got, str), f"the loop must return a string when it runs out of budget, got {got!r}"
    assert len(tool.calls) == 3, (
        f"max_iterations=3 means at most 3 tool calls; the tool was called {len(tool.calls)} "
        "times. An unbounded loop is the runaway-cost bug this chapter is about."
    )


def _l9(f):
    """the brain names a tool that does not exist"""
    got = f("bad action", lambda m: {"action": "nonexistent", "action_input": "x"},
            {"calculator": _recording_tool([_ok(1)])}, max_iterations=3, verbose=False)
    assert isinstance(got, str) and "nonexistent" in got, (
        "an unrecognized action must return a string naming the bad action, not raise "
        f"KeyError or TypeError; got {got!r}"
    )


def _l10(f):
    """a final_answer decision runs no tool at all"""
    tool = _recording_tool([_ok(1)])
    f("done already", lambda m: {"action": "final_answer", "action_input": "ok"},
      {"calculator": tool}, verbose=False)
    assert tool.calls == [], (
        f"no tool should run when the brain answers directly; the tool saw {tool.calls}"
    )


task("ch01-react-loop", _ref_run_agent, [_l1, _l2, _l3, _l4, _l5, _l6, _l7, _l8, _l9, _l10])


# --- ch01-dup-guard ---


def _ref_guard():
    from solutions.reference.ch01 import run_agent_with_guard

    return run_agent_with_guard


def _spin_brain(messages):
    """Never gives up on its own -- the guard is the only thing that can stop it."""
    return {"action": "spin", "action_input": "any"}


def _g1(f):
    """the identical observation fires twice in a row"""
    tool = _recording_tool([_ok("still processing")])
    got = f("stuck task", _spin_brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert isinstance(got, str), f"expected an escalation string, got {got!r}"
    assert "escalat" in got.lower(), (
        f"the guard must return a message saying it is escalating; got {got!r}"
    )


def _g2(f):
    """escalation happens on the repeat, not after the whole budget"""
    tool = _recording_tool([_ok("still processing")])
    f("stuck task", _spin_brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert len(tool.calls) == 2, (
        f"the guard should stop on the SECOND identical observation, so the tool runs "
        f"exactly twice; it ran {len(tool.calls)} times. Burning all 50 iterations first is "
        "the bug the guard exists to fix."
    )


def _g3(f):
    """an observation repeats, but not consecutively"""
    tool = _recording_tool([_ok("A"), _ok("B"), _ok("A")])
    calls = {"n": 0}

    def brain(messages):
        calls["n"] += 1
        if calls["n"] > 3:
            return {"action": "final_answer", "action_input": "finished after real progress"}
        return {"action": "spin", "action_input": "any"}

    got = f("A then B then A", brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert got == "finished after real progress", (
        "the rule is TWO CONSECUTIVE identical observations, not 'seen this one before'. "
        "A -> B -> A is real progress: something changed in between, so the agent is not "
        f"stuck in a loop and must be allowed to continue. Got {got!r}. Tracking every "
        "observation in a set kills legitimate work that revisits a state."
    )


def _g4(f):
    """three identical observations in a row still stops at the second"""
    tool = _recording_tool([_ok("same"), _ok("same"), _ok("same")])
    f("stuck", _spin_brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert len(tool.calls) == 2, (
        f"the guard must fire the first time a repeat appears, after 2 calls; got {len(tool.calls)}"
    )


def _g5(f):
    """the very first observation is not a repeat of anything"""
    tool = _recording_tool([_ok("first")])
    calls = {"n": 0}

    def brain(messages):
        calls["n"] += 1
        return (
            {"action": "spin", "action_input": "any"}
            if calls["n"] == 1
            else {"action": "final_answer", "action_input": "one step was enough"}
        )

    got = f("one step", brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert got == "one step was enough", (
        f"a single observation cannot be a repeat -- there is nothing before it to match. "
        f"Got {got!r}"
    )


def _g6(f):
    """every observation differs, so the loop runs to completion"""
    tool = _recording_tool([_ok(1), _ok(2), _ok(3)])
    calls = {"n": 0}

    def brain(messages):
        calls["n"] += 1
        if calls["n"] > 3:
            return {"action": "final_answer", "action_input": "all three done"}
        return {"action": "spin", "action_input": "any"}

    got = f("three distinct steps", brain, {"spin": tool}, max_iterations=50, verbose=False)
    assert got == "all three done", (
        f"distinct observations mean real progress; the guard must not interfere. Got {got!r}"
    )


def _g7(f):
    """the guard still behaves like the plain loop otherwise"""
    got = f("hi", lambda m: {"action": "final_answer", "action_input": "done"}, {}, verbose=False)
    assert got == "done", f"a final_answer decision still returns its action_input; got {got!r}"


def _g8(f):
    """observations still reach the brain"""
    tool = _recording_tool([_ok(84)])

    def brain(messages):
        observations = [m for m in messages if m.get("role") == "observation"]
        if not observations:
            return {"action": "calculator", "action_input": "12 * 7"}
        return {"action": "final_answer", "action_input": observations[-1]["content"]}

    got = f("what is 12 * 7?", brain, {"calculator": tool}, max_iterations=5, verbose=False)
    assert got == _ok(84), (
        "adding the guard must not stop observations being threaded back to the brain; "
        f"the brain read back {got!r}"
    )


def _g9(f):
    """distinct observations still respect max_iterations"""
    tool = _recording_tool([_ok(1), _ok(2), _ok(3), _ok(4), _ok(5), _ok(6)])
    got = f("endless but always new", _spin_brain, {"spin": tool}, max_iterations=4, verbose=False)
    assert len(tool.calls) == 4, (
        f"max_iterations=4 caps the loop at 4 tool calls even when nothing repeats; "
        f"got {len(tool.calls)}"
    )
    assert isinstance(got, str), f"expected a string when the budget runs out, got {got!r}"


def _g10(f):
    """the brain names a tool that does not exist"""
    got = f("bad action", lambda m: {"action": "nope", "action_input": "x"}, {}, verbose=False)
    assert isinstance(got, str) and "nope" in got, (
        f"an unrecognized action must return a string naming it, not raise; got {got!r}"
    )


task("ch01-dup-guard", _ref_guard, [_g1, _g2, _g3, _g4, _g5, _g6, _g7, _g8, _g9, _g10])


# --- ch01-memory ---


def _ref_chat_turn():
    from solutions.reference.ch01 import chat_turn

    return chat_turn


def _echo_brain(history, user_input):
    """Answers 'what is my name?' only if the name is somewhere in history."""
    import re

    context = " ".join(m["content"] for m in history)
    if "what is my name" in user_input.lower():
        match = re.search(r"my name is (\w+)", context, re.IGNORECASE)
        return f"Your name is {match.group(1)}." if match else "I don't know your name."
    return "Noted."


def _t1(f):
    """the turn returns the brain's reply"""
    got = f([], "My name is Jack.", _echo_brain)
    assert got == "Noted.", f"chat_turn returns whatever the brain replied; got {got!r}"


def _t2(f):
    """one turn adds both sides to history"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    assert len(history) == 2, (
        f"a turn is two messages -- what the user said and what the agent replied -- so "
        f"history should have grown by 2; it has {len(history)}: {history}"
    )


def _t3(f):
    """the user's own words survive into the next turn"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    got = f(history, "What is my name?", _echo_brain)
    assert got == "Your name is Jack.", (
        "the USER's turn has to go into history, not just the agent's reply. The name only "
        "ever appears in what the user said, so dropping the user turn loses it forever: "
        f"got {got!r}. This is the single most common way 'memory' gets half-implemented."
    )


def _t4(f):
    """the agent's reply survives into the next turn"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    roles = [m["role"] for m in history]
    assert "assistant" in roles, (
        f"the agent's reply belongs in history too, tagged 'assistant'; roles are {roles}"
    )


def _t5(f):
    """user comes before assistant"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    roles = [m["role"] for m in history]
    assert roles == ["user", "assistant"], (
        f"history is chronological: the user spoke first, so roles should be "
        f"['user', 'assistant']; got {roles}"
    )


def _t6(f):
    """messages carry the raw text under 'content'"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    assert history[0] == {"role": "user", "content": "My name is Jack."}, (
        f"each message is {{'role': ..., 'content': ...}} with the text unchanged; "
        f"got {history[0]!r}"
    )
    assert history[1] == {"role": "assistant", "content": "Noted."}, (
        f"the reply message should be {{'role': 'assistant', 'content': <reply>}}; "
        f"got {history[1]!r}"
    )


def _t7(f):
    """the brain sees history as it stood before this turn"""
    seen = {}

    def spy(history, user_input):
        seen["len"] = len(history)
        seen["input"] = user_input
        return "Noted."

    history = [{"role": "user", "content": "earlier"}, {"role": "assistant", "content": "ok"}]
    f(history, "now", spy)
    assert seen["len"] == 2, (
        "the brain is handed the prior history plus the new input separately, so the "
        f"current turn must not already be in the list it receives; it saw {seen['len']} "
        "messages instead of 2"
    )
    assert seen["input"] == "now", f"the brain receives the new input verbatim; got {seen['input']!r}"


def _t8(f):
    """three turns in a row"""
    history = []
    f(history, "My name is Jack.", _echo_brain)
    f(history, "I like Python.", _echo_brain)
    got = f(history, "What is my name?", _echo_brain)
    assert len(history) == 6, f"three turns is six messages; history has {len(history)}"
    assert got == "Your name is Jack.", (
        f"the name is still two turns back and must still be reachable; got {got!r}"
    )


def _t9(f):
    """an empty history is a valid starting point"""
    history = []
    got = f(history, "What is my name?", _echo_brain)
    assert got == "I don't know your name.", (
        f"with nothing in history the brain has nothing to recall; got {got!r}"
    )
    assert len(history) == 2, f"the turn is still recorded; history has {len(history)}"


def _t10(f):
    """history is appended to in place, not replaced"""
    history = []
    same = history
    f(history, "My name is Jack.", _echo_brain)
    assert same is history and len(same) == 2, (
        "append to the list you were handed rather than building a new one -- the caller "
        f"holds a reference to it; the caller's list has {len(same)} messages"
    )


task("ch01-memory", _ref_chat_turn, [_t1, _t2, _t3, _t4, _t5, _t6, _t7, _t8, _t9, _t10])
