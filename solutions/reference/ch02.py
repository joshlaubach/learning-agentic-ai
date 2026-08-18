"""Chapter 2 reference answers — Agent Control Flow.

Planning, subagent dispatch with real context isolation, and the structural check that
catches a subagent handing back its raw transcript instead of a compressed synthesis.
"""

from __future__ import annotations

import json

_TEAM_FACTS_KEYS = ("anthropic", "react")


def plan_subtasks(task: str) -> list:
    """Jack, the planner: split a task into self-contained subtask strings.

    Always returns a list, even for a task that needs no decomposition."""
    lowered = task.lower()
    if "anthropic" in lowered and "react" in lowered:
        return ["who founded anthropic?", "what is the react pattern?"]
    return [task]


def run_subagent(
    subtask: str,
    brain,
    tools: dict,
    max_iterations: int = 4,
    leaky: bool = False,
    verbose: bool = False,
):
    """Run one subagent on one bounded subtask, in its own fresh context.

    Returns (result, steps_used). `leaky=True` returns the entire raw transcript instead of
    the compressed synthesis -- the bug this chapter's break-it section demonstrates."""
    messages = [{"role": "user", "content": subtask}]
    for step in range(1, max_iterations + 1):
        decision = brain(messages)
        if verbose:
            print(f"  [subagent step {step}] {decision}")

        if decision["action"] == "final_answer":
            if leaky:
                full_transcript = messages + [
                    {"role": "assistant", "content": decision["action_input"]}
                ]
                return json.dumps(full_transcript), step
            return decision["action_input"], step

        tool_fn = tools.get(decision["action"])
        result = (
            tool_fn(decision["action_input"])
            if tool_fn
            else {"status": "error", "error": "unknown tool"}
        )
        if verbose:
            print(f"  [subagent step {step}] observation: {result}")
        messages.append(
            {"role": "observation", "tool": decision["action"], "content": result}
        )

    return "Subagent did not finish within its iteration budget.", max_iterations


def is_leaky_result(raw_result: str) -> bool:
    """Did a subagent hand back its raw transcript instead of a compressed synthesis?

    Decided on structure, not size: a transcript is a JSON array of message objects, so
    that is what this looks for."""
    try:
        parsed = json.loads(raw_result)
    except (ValueError, TypeError):
        return False
    if not isinstance(parsed, list) or not parsed:
        return False
    return all(isinstance(m, dict) and "role" in m and "content" in m for m in parsed)
