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
