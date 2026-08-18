"""Chapter 1 reference answers — Fundamentals of AI Agents.

The ReAct loop, its duplicate-observation guard, and conversational memory threading. These
are the three pieces of Chapter 1 the learner builds; the notebook's tools, brains, and
demos around them stay as they were.
"""

from __future__ import annotations

import json


def run_agent(task: str, brain, tools: dict, max_iterations: int = 6, verbose: bool = True) -> str:
    """The Thought -> Action -> Observation loop."""
    messages = [{"role": "user", "content": task}]

    for step in range(1, max_iterations + 1):
        decision = brain(messages)
        action = decision.get("action")
        action_input = decision.get("action_input")

        if verbose:
            print(f"[step {step}] Thought -> Action: {action}({action_input!r})")

        if action == "final_answer":
            if verbose:
                print(f"[step {step}] Final answer: {action_input}")
            return action_input

        tool_fn = tools.get(action)
        if tool_fn is None:
            if verbose:
                print(f"[step {step}] Unrecognized action {action!r}; stopping.")
            return f"Agent produced an unrecognized action: {action!r}"

        result = tool_fn(action_input)
        if verbose:
            print(f"[step {step}] Observation: {result}")
        messages.append({"role": "observation", "tool": action, "content": result})

    if verbose:
        print(f"Stopped after {max_iterations} iterations without a final answer.")
    return "Agent did not reach a final answer within the iteration budget."


def run_agent_with_guard(task: str, brain, tools: dict, max_iterations: int = 50, verbose: bool = True) -> str:
    """Same loop as run_agent(), but escalates instead of repeating once the exact same
    observation fires twice in a row."""
    messages = [{"role": "user", "content": task}]
    last_observation_hash = None

    for step in range(1, max_iterations + 1):
        decision = brain(messages)
        action = decision.get("action")
        action_input = decision.get("action_input")

        if verbose:
            print(f"[step {step}] Thought -> Action: {action}({action_input!r})")

        if action == "final_answer":
            if verbose:
                print(f"[step {step}] Final answer: {action_input}")
            return action_input

        tool_fn = tools.get(action)
        if tool_fn is None:
            return f"Agent produced an unrecognized action: {action!r}"

        result = tool_fn(action_input)
        observation_hash = hash(json.dumps(result, sort_keys=True))

        if observation_hash == last_observation_hash:
            escalation = (
                f"Escalating after step {step}: received the identical observation twice "
                f"in a row ({result}) with no progress. A real employee would ask for help "
                "here instead of repeating the same request forever."
            )
            if verbose:
                print(f"[step {step}] {escalation}")
            return escalation
        last_observation_hash = observation_hash

        if verbose:
            print(f"[step {step}] Observation: {result}")
        messages.append({"role": "observation", "tool": action, "content": result})

    return "Agent did not reach a final answer within the iteration budget."


def chat_turn(history: list, user_input: str, brain) -> str:
    """Run one conversational turn and thread it into history.

    The brain sees the history as it stood BEFORE this turn, plus the new input; both sides
    of the exchange are appended afterwards so the next turn can see them."""
    reply = brain(history, user_input)
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    return reply
