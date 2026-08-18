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


# --- Chapter 1 ---


def test_ch01_react_loop_rejects_never_appending_the_observation():
    """Plausible wrong answer: run the tool, print the result, and loop -- but never put the
    observation back into messages. Looks complete, and the first step even works; the brain
    is simply blind to every result and repeats itself until the budget runs out."""

    def wrong(task, brain, tools, max_iterations=6, verbose=True):
        messages = [{"role": "user", "content": task}]
        for _ in range(max_iterations):
            decision = brain(messages)
            if decision.get("action") == "final_answer":
                return decision.get("action_input")
            tool_fn = tools.get(decision.get("action"))
            if tool_fn is None:
                return f"Agent produced an unrecognized action: {decision.get('action')!r}"
            tool_fn(decision.get("action_input"))  # result computed, then dropped
        return "Agent did not reach a final answer within the iteration budget."

    _rejects("ch01-react-loop", wrong)
    _accepts("ch01-react-loop")


def test_ch01_react_loop_rejects_unbounded_loop():
    """Plausible wrong answer: a while-True loop with the iteration cap forgotten. Passes
    every happy-path case and hangs forever on the runaway agent this chapter is about."""

    def wrong(task, brain, tools, max_iterations=6, verbose=True):
        messages = [{"role": "user", "content": task}]
        steps = 0
        while steps < 1000:  # bounded only so this test terminates
            steps += 1
            decision = brain(messages)
            if decision.get("action") == "final_answer":
                return decision.get("action_input")
            tool_fn = tools.get(decision.get("action"))
            if tool_fn is None:
                return f"Agent produced an unrecognized action: {decision.get('action')!r}"
            result = tool_fn(decision.get("action_input"))
            messages.append({"role": "observation", "tool": decision.get("action"), "content": result})
        return "Agent did not reach a final answer within the iteration budget."

    _rejects("ch01-react-loop", wrong)


def test_ch01_dup_guard_rejects_seen_anywhere_instead_of_consecutive():
    """Plausible wrong answer: remember every observation in a set and escalate on any
    repeat. Catches the actual stuck loop correctly, which is what makes it convincing --
    and also kills an agent that legitimately revisits a state after real work."""

    def wrong(task, brain, tools, max_iterations=50, verbose=True):
        import json as _json

        messages = [{"role": "user", "content": task}]
        seen = set()
        for step in range(1, max_iterations + 1):
            decision = brain(messages)
            action = decision.get("action")
            if action == "final_answer":
                return decision.get("action_input")
            tool_fn = tools.get(action)
            if tool_fn is None:
                return f"Agent produced an unrecognized action: {action!r}"
            result = tool_fn(decision.get("action_input"))
            observation_hash = hash(_json.dumps(result, sort_keys=True))
            if observation_hash in seen:
                return f"Escalating after step {step}: this observation has been seen before."
            seen.add(observation_hash)
            messages.append({"role": "observation", "tool": action, "content": result})
        return "Agent did not reach a final answer within the iteration budget."

    _rejects("ch01-dup-guard", wrong)
    _accepts("ch01-dup-guard")


def test_ch01_memory_rejects_recording_only_the_assistant_turn():
    """Plausible wrong answer: append the reply to history and nothing else. The history
    grows every turn, so it looks like memory is working -- but everything the USER said is
    thrown away, which is the half of the conversation that carries the facts."""

    def wrong(history, user_input, brain):
        reply = brain(history, user_input)
        history.append({"role": "assistant", "content": reply})
        return reply

    _rejects("ch01-memory", wrong)
    _accepts("ch01-memory")


def test_ch01_memory_rejects_appending_the_user_turn_before_the_brain_runs():
    """Plausible wrong answer: record the user turn first, then call the brain. Reads more
    naturally, and quietly changes the brain's contract -- it now sees the current input
    twice, once in history and once as the argument."""

    def wrong(history, user_input, brain):
        history.append({"role": "user", "content": user_input})
        reply = brain(history, user_input)
        history.append({"role": "assistant", "content": reply})
        return reply

    _rejects("ch01-memory", wrong)


# --- Chapter 2 ---


def test_ch02_planner_rejects_returning_a_string():
    """Plausible wrong answer: return the joined subtasks as one string. Prints beautifully,
    and Bob's dispatch loop then iterates over its characters."""

    def wrong(task):
        lowered = task.lower()
        if "anthropic" in lowered and "react" in lowered:
            return "who founded anthropic?, what is the react pattern?"
        return task

    _rejects("ch02-planner", wrong)
    _accepts("ch02-planner")


def test_ch02_planner_rejects_empty_plan_for_atomic_tasks():
    """Plausible wrong answer: only return subtasks when the task actually decomposes, and
    an empty list otherwise. Bob then dispatches nothing and assembles an empty draft --
    a silent failure rather than a loud one."""

    def wrong(task):
        lowered = task.lower()
        if "anthropic" in lowered and "react" in lowered:
            return ["who founded anthropic?", "what is the react pattern?"]
        return []

    _rejects("ch02-planner", wrong)


def test_ch02_subagent_rejects_threading_parent_messages_in():
    """Plausible wrong answer: accept the parent's messages and start from them "so the
    subagent has context". Every result is correct; the isolation the subagent exists to
    provide is gone, and the parent's tokens are now paid for twice."""
    parent_messages = [
        {"role": "user", "content": "the parent's whole conversation"},
        {"role": "assistant", "content": "lots of prior context"},
    ]

    def wrong(subtask, brain, tools, max_iterations=4, leaky=False, verbose=False):
        import json as _json

        messages = parent_messages + [{"role": "user", "content": subtask}]
        for step in range(1, max_iterations + 1):
            decision = brain(messages)
            if decision["action"] == "final_answer":
                if leaky:
                    return _json.dumps(
                        messages + [{"role": "assistant", "content": decision["action_input"]}]
                    ), step
                return decision["action_input"], step
            tool_fn = tools.get(decision["action"])
            result = tool_fn(decision["action_input"]) if tool_fn else {"status": "error", "error": "unknown tool"}
            messages.append({"role": "observation", "tool": decision["action"], "content": result})
        return "Subagent did not finish within its iteration budget.", max_iterations

    _rejects("ch02-subagent", wrong)
    _accepts("ch02-subagent")


def test_ch02_subagent_rejects_a_module_level_message_list():
    """Plausible wrong answer: hoist `messages` out of the function so it can be inspected
    afterwards. One subagent works perfectly; the second inherits everything the first did."""
    shared_messages = []

    def wrong(subtask, brain, tools, max_iterations=4, leaky=False, verbose=False):
        import json as _json

        shared_messages.append({"role": "user", "content": subtask})
        for step in range(1, max_iterations + 1):
            decision = brain(shared_messages)
            if decision["action"] == "final_answer":
                if leaky:
                    return _json.dumps(
                        shared_messages + [{"role": "assistant", "content": decision["action_input"]}]
                    ), step
                return decision["action_input"], step
            tool_fn = tools.get(decision["action"])
            result = tool_fn(decision["action_input"]) if tool_fn else {"status": "error", "error": "unknown tool"}
            shared_messages.append({"role": "observation", "tool": decision["action"], "content": result})
        return "Subagent did not finish within its iteration budget.", max_iterations

    _rejects("ch02-subagent", wrong)


def test_ch02_leak_check_rejects_a_length_threshold():
    """Plausible wrong answer: call anything over 30 words a leak. Correct on the two
    examples the notebook happens to show, and wrong in both directions -- it truncates a
    long legitimate answer and waves through a short transcript."""

    def wrong(raw_result):
        return len(raw_result.split()) > 30

    _rejects("ch02-leak-check", wrong)
    _accepts("ch02-leak-check")


def test_ch02_leak_check_rejects_substring_sniffing():
    """Plausible wrong answer: look for the words a transcript contains instead of parsing
    it. Flags any prose that happens to use the word "role"."""

    def wrong(raw_result):
        return "role" in raw_result and "content" in raw_result

    _rejects("ch02-leak-check", wrong)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
