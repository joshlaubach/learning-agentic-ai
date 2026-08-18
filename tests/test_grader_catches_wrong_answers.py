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


# --- Chapter 4 ---


class _ApiErr(Exception):
    def __init__(self, status_code):
        super().__init__(f"{status_code}: api error")
        self.status_code = status_code


def test_ch04_ttl_cache_rejects_checking_the_ttl_on_write():
    """Plausible wrong answer: evict stale keys when you write, and let reads trust whatever
    is in the store. Every test that writes and immediately reads passes; an entry written
    once and read six hours later is served stale forever, because nothing between those two
    moments ever prompted the cache to reconsider it."""

    class Wrong:
        def __init__(self, ttl_seconds):
            self.ttl = ttl_seconds
            self.store = {}

        def get(self, key, now):
            if key in self.store:
                value, cached_at = self.store[key]
                return value, cached_at
            return None, None

        def set(self, key, value, now):
            for k, (_, cached_at) in list(self.store.items()):
                if now - cached_at >= self.ttl:
                    del self.store[k]
            self.store[key] = (value, now)

        def invalidate(self, key):
            self.store.pop(key, None)

    _rejects("ch04-ttl-cache", Wrong)
    _accepts("ch04-ttl-cache")


def test_ch04_backoff_rejects_linear_growth():
    """Plausible wrong answer: base_delay * attempt. Grows, backs off, logs correctly, and
    over three attempts produces 1/2/3 against the correct 1/2/4 -- close enough to look
    right and not nearly fast enough to outrun a filling queue."""
    import random as _random

    def wrong(fn, max_retries=6, base_delay=1.0, jitter=0.5, seed=1, sleep_fn=None,
              retry_predicate=None):
        rng = _random.Random(seed)

        def wrapped(*args, **kwargs):
            attempts_log, last_exc = [], None
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs), attempts_log
                except Exception as exc:
                    last_exc = exc
                    delay = base_delay * attempt + rng.uniform(0, jitter)
                    attempts_log.append({"attempt": attempt, "error": str(exc),
                                         "backoff_s": round(delay, 2)})
                    if sleep_fn is not None:
                        sleep_fn(delay)
            raise RuntimeError(f"gave up after {max_retries} attempts") from last_exc

        return wrapped

    _rejects("ch04-backoff", wrong)
    _accepts("ch04-backoff")


def test_ch04_backoff_rejects_sleeping_before_the_first_attempt():
    """Plausible wrong answer: sleep at the top of the loop so the retry delay is "already
    applied" when the call happens. Correct on every retry, and it adds a full base_delay of
    latency to every healthy request in production."""
    import random as _random

    def wrong(fn, max_retries=6, base_delay=1.0, jitter=0.5, seed=1, sleep_fn=None,
              retry_predicate=None):
        rng = _random.Random(seed)

        def wrapped(*args, **kwargs):
            attempts_log, last_exc = [], None
            for attempt in range(1, max_retries + 1):
                delay = base_delay * (2 ** (attempt - 1)) + rng.uniform(0, jitter)
                if sleep_fn is not None:
                    sleep_fn(delay)
                try:
                    return fn(*args, **kwargs), attempts_log
                except Exception as exc:
                    last_exc = exc
                    attempts_log.append({"attempt": attempt, "error": str(exc),
                                         "backoff_s": round(delay, 2)})
            raise RuntimeError(f"gave up after {max_retries} attempts") from last_exc

        return wrapped

    _rejects("ch04-backoff", wrong)


def test_ch04_no_retry_4xx_rejects_blanket_4xx_refusal():
    """Plausible wrong answer: retry 5xx, refuse the whole 4xx range. Reads like the textbook
    rule and throws away the two 4xx statuses that most need a retry -- 429 rate limits and
    408 timeouts."""

    def wrong(error):
        status = getattr(error, "status_code", None)
        if status is None:
            return True
        return not 400 <= status < 500

    _rejects("ch04-no-retry-4xx", wrong)
    _accepts("ch04-no-retry-4xx")


def test_ch04_no_retry_4xx_rejects_retrying_everything():
    """Plausible wrong answer: the predicate nobody got around to writing. Retries a 400
    five times, so the caller waits through the full backoff schedule to be told what the
    first response already said."""

    def wrong(error):
        return True

    _rejects("ch04-no-retry-4xx", wrong)


def test_ch04_circuit_breaker_rejects_never_half_opening():
    """Plausible wrong answer: open on the threshold, fail fast while open, and stop there.
    Everything about the outage is handled correctly -- the dependency stops being hammered,
    the caller fails fast -- and the circuit never re-tests anything, so the outage outlives
    its own cause and only a redeploy clears it."""

    class Wrong:
        def __init__(self, failure_threshold=3, cooldown=5):
            self.failure_threshold = failure_threshold
            self.cooldown = cooldown
            self.failure_count = 0
            self.state = "closed"
            self.opened_at = None

        def call(self, fn, now):
            if self.state == "open":
                raise RuntimeError("circuit open -- failing fast")
            try:
                result = fn()
            except Exception:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    self.opened_at = now
                raise
            else:
                self.failure_count = 0
                self.state = "closed"
                return result

    _rejects("ch04-circuit-breaker", Wrong)
    _accepts("ch04-circuit-breaker")


def test_ch04_circuit_breaker_rejects_counting_lifetime_failures():
    """Plausible wrong answer: count every failure ever seen instead of consecutive ones. A
    service with a 1% error rate trips the breaker eventually no matter how healthy it is."""

    class Wrong:
        def __init__(self, failure_threshold=3, cooldown=5):
            self.failure_threshold = failure_threshold
            self.cooldown = cooldown
            self.failure_count = 0
            self.state = "closed"
            self.opened_at = None

        def call(self, fn, now):
            if self.state == "open":
                if now - self.opened_at >= self.cooldown:
                    self.state = "half-open"
                else:
                    raise RuntimeError("circuit open -- failing fast")
            try:
                result = fn()
            except Exception:
                self.failure_count += 1
                if self.state == "half-open" or self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    self.opened_at = now
                raise
            else:
                self.state = "closed"  # state reset, counter deliberately not
                return result

    _rejects("ch04-circuit-breaker", Wrong)


# --- Chapter 5 ---


def test_ch05_token_cost_rejects_one_price_for_input_and_output():
    """Plausible wrong answer: a single per-token price. Output is 5x input in every real
    price sheet, so this understates the cost of exactly the long, verbose responses a cost
    model exists to catch."""

    def wrong(input_tokens, output_tokens, cached_prefix_tokens, cache_hit,
              input_price=3.0, output_price=15.0, cache_price=0.30):
        fresh = input_tokens - cached_prefix_tokens if cache_hit else input_tokens
        cost = (fresh + output_tokens) / 1e6 * input_price
        if cache_hit:
            cost += cached_prefix_tokens / 1e6 * cache_price
        return {"cache_hit": cache_hit, "fresh_input_tokens": fresh,
                "cost_usd": round(cost, 6)}

    _rejects("ch05-token-cost", wrong)
    _accepts("ch05-token-cost")


def test_ch05_token_cost_rejects_treating_cached_tokens_as_free():
    """Plausible wrong answer: a cache hit means you don't pay for the prefix. Directionally
    right, and it under-reports every cached call -- a cache read is discounted, not free."""

    def wrong(input_tokens, output_tokens, cached_prefix_tokens, cache_hit,
              input_price=3.0, output_price=15.0, cache_price=0.30):
        fresh = input_tokens - cached_prefix_tokens if cache_hit else input_tokens
        cost = fresh / 1e6 * input_price + output_tokens / 1e6 * output_price
        return {"cache_hit": cache_hit, "fresh_input_tokens": fresh,
                "cost_usd": round(cost, 6)}

    _rejects("ch05-token-cost", wrong)


def test_ch05_latency_profile_rejects_reporting_means():
    """Plausible wrong answer: report each stage's mean latency instead of its share of the
    total. A perfectly reasonable statistic answering a different question -- it tells you a
    stage is slow, never which stage a regression landed in."""

    def wrong(requests):
        stages = ["queue_time_ms", "network_time_ms", "inference_time_ms", "generation_time_ms"]
        n = len(requests) or 1
        totals = {s: sum(r[s] for r in requests) for s in stages}
        return {s: {"total_ms": totals[s], "pct": totals[s] / n} for s in stages}

    _rejects("ch05-latency-profile", wrong)
    _accepts("ch05-latency-profile")


def test_ch05_latency_profile_rejects_unguarded_division():
    """Plausible wrong answer: correct share arithmetic with nothing guarding an idle
    window. A profiler handed a quiet 30 seconds raises ZeroDivisionError instead of
    reporting zeros."""

    def wrong(requests):
        stages = ["queue_time_ms", "network_time_ms", "inference_time_ms", "generation_time_ms"]
        totals = {s: sum(r[s] for r in requests) for s in stages}
        grand = sum(totals.values())
        return {s: {"total_ms": totals[s], "pct": totals[s] / grand * 100} for s in stages}

    _rejects("ch05-latency-profile", wrong)


def test_ch05_router_rejects_routing_on_length_alone():
    """Plausible wrong answer: escalate long prompts, ignore requires_tool_use. Correct on
    every example where the two signals agree, and it silently sends every short tool-using
    request -- the ones where a weak model's mistakes compound -- to the cheap tier."""
    from agentlib import llm_client as _llm

    def wrong(prompt, requires_tool_use=False):
        if len(prompt.split()) > 80:
            return _llm.STRONG_MODELS[_llm.LLM_PROVIDER]
        return _llm.DEFAULT_MODELS[_llm.LLM_PROVIDER]

    _rejects("ch05-router", wrong)
    _accepts("ch05-router")


def test_ch05_router_rejects_measuring_length_in_characters():
    """Plausible wrong answer: len(prompt) > 80 rather than a word count. Three long words
    trip an 80-character threshold, so short technical prompts get escalated for nothing."""
    from agentlib import llm_client as _llm

    def wrong(prompt, requires_tool_use=False):
        if requires_tool_use or len(prompt) > 80:
            return _llm.STRONG_MODELS[_llm.LLM_PROVIDER]
        return _llm.DEFAULT_MODELS[_llm.LLM_PROVIDER]

    _rejects("ch05-router", wrong)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
