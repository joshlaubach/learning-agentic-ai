"""Chapter 5 reference answers — Cost, Performance, and Model Selection.

Token cost with prompt caching, the four-stage latency decomposition, and tier routing.
"""

from __future__ import annotations

from agentlib import llm_client

STAGES = ["queue_time_ms", "network_time_ms", "inference_time_ms", "generation_time_ms"]


def estimate_cost_with_caching(
    input_tokens: int,
    output_tokens: int,
    cached_prefix_tokens: int,
    cache_hit: bool,
    input_price: float = 3.0,
    output_price: float = 15.0,
    cache_price: float = 0.30,
) -> dict:
    """Per-million-token prices in dollars (illustrative, Sonnet-class ballpark) -- cached
    input tokens are billed at a steep discount relative to fresh input tokens on a cache
    hit, and free of the fresh-input charge entirely."""
    fresh_input_tokens = input_tokens - cached_prefix_tokens if cache_hit else input_tokens
    cost = (fresh_input_tokens / 1e6) * input_price + (output_tokens / 1e6) * output_price
    if cache_hit:
        cost += (cached_prefix_tokens / 1e6) * cache_price
    return {
        "cache_hit": cache_hit,
        "fresh_input_tokens": fresh_input_tokens,
        "cost_usd": round(cost, 6),
    }


def profile_latency(requests: list) -> dict:
    """Decompose a request log into the four stages, as totals AND as shares of the whole.

    The share is what makes a spike diagnosable: a bigger total tells you something got
    slower, a shifted share tells you which stage did."""
    totals = {stage: sum(r[stage] for r in requests) for stage in STAGES}
    grand_total = sum(totals.values())
    if not grand_total:
        return {stage: {"total_ms": 0, "pct": 0.0} for stage in STAGES}
    return {
        stage: {"total_ms": totals[stage], "pct": totals[stage] / grand_total * 100}
        for stage in STAGES
    }


def route_request(prompt: str, requires_tool_use: bool = False) -> str:
    """A simple, legible routing policy: short, single-fact lookups and simple formatting
    tasks go to the cheap/fast tier; anything long, anything requiring multi-step tool use,
    or anything that looks like it needs real reasoning goes to the strong tier."""
    word_count = len(prompt.split())
    if requires_tool_use or word_count > 80:
        return llm_client.STRONG_MODELS[llm_client.LLM_PROVIDER]
    return llm_client.DEFAULT_MODELS[llm_client.LLM_PROVIDER]


# --- Written diagnoses (the three "diagnose before reading on" scenarios) ---
#
# These used to sit in the notebook as a Reveal directly below the question, which made the
# exercise an honour system with the answer inside the same rendered cell. They live here
# now, and the notebook grades what the learner writes instead.

DIAGNOSE_DUPLICATE_CALLS = (
    "Requests 100-119 carry roughly double the input and output tokens of their neighbours, "
    "with no corresponding change in what the user actually asked for. That specific "
    "signature -- a token-volume step change with no query-complexity explanation -- points "
    "at a duplicate-call bug rather than a genuinely harder batch of questions: a "
    "non-idempotent retry, a double-submit, or a webhook firing twice. I would confirm it by "
    "grouping the slice by request id and looking for the same id executing more than once, "
    "which separates it cleanly from the 'users asked harder things' hypothesis. The fix is "
    "idempotency: a request id checked before execution rather than after, so a replayed "
    "request is recognised and dropped instead of being paid for a second time."
)

DIAGNOSE_CONTEXT_GROWTH = (
    "input_tokens climbs steadily and roughly linearly across this slice instead of sitting "
    "in its normal log-normal range. That linear growth is the signature of a conversation "
    "whose full history is re-sent on every turn with nothing ever truncated or summarized, "
    "so each turn pays for every turn before it. Output tokens staying flat is what rules "
    "out 'the answers got longer' as an explanation. Left alone this gets more expensive "
    "turn over turn and eventually risks exceeding the model's context window outright, at "
    "which point it stops being a cost problem and starts being an outage. The fix is a "
    "bounded context policy: a sliding window over recent turns, periodic summarization of "
    "older ones, or both together."
)

DIAGNOSE_QUEUEING = (
    "input_tokens and output_tokens in this slice are perfectly ordinary, which rules out "
    "both 'someone sent a huge prompt' and a genuine inference slowdown -- the per-request "
    "work has not changed at all. What actually moved is queue_depth and, downstream of it, "
    "queue_time_ms, which now accounts for the overwhelming majority of total_latency_ms. "
    "This is a queueing problem, not an inference one, which is why the reflex answer of "
    "'add more GPUs' is only accidentally right: it helps insofar as it adds queue capacity, "
    "and not at all because inference got slower. The first move is to check which stage "
    "grew before reaching for any fix, and the real levers are capacity and backpressure -- "
    "admission control that sheds or delays load rather than letting the queue grow without "
    "bound."
)
