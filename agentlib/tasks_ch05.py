"""Graded task suites for Chapter 5 — Cost, Performance, and Model Selection.

Cost arithmetic, the four-stage latency decomposition, and tier routing. The latency cases
use hand-built logs whose per-stage means and per-stage shares are deliberately different
numbers, so the two cannot be confused for one another.
"""

from __future__ import annotations

from agentlib import llm_client
from agentlib.grading import task
from agentlib.prose_checks import is_written_answer, matched, mentions

_STAGES = ["queue_time_ms", "network_time_ms", "inference_time_ms", "generation_time_ms"]


def _request(queue=0, network=0, inference=0, generation=0):
    return {
        "queue_time_ms": queue,
        "network_time_ms": network,
        "inference_time_ms": inference,
        "generation_time_ms": generation,
    }


# --- ch05-token-cost ---


def _ref_cost():
    from solutions.reference.ch05 import estimate_cost_with_caching

    return estimate_cost_with_caching


def _o1(f):
    """a plain call with no caching"""
    got = f(input_tokens=1000, output_tokens=1000, cached_prefix_tokens=0, cache_hit=False)
    assert got["cost_usd"] == 0.018, (
        "1000 input at $3/M is $0.003, 1000 output at $15/M is $0.015, so $0.018. Got "
        f"{got['cost_usd']}. Charging output at the input rate gives $0.006 -- output "
        "tokens are the expensive half, typically 4-5x input, and pricing them the same "
        "understates the cost of exactly the verbose responses you most want to catch."
    )


def _o2(f):
    """output-heavy versus input-heavy at the same total"""
    input_heavy = f(input_tokens=2000, output_tokens=0, cached_prefix_tokens=0, cache_hit=False)
    output_heavy = f(input_tokens=0, output_tokens=2000, cached_prefix_tokens=0, cache_hit=False)
    assert output_heavy["cost_usd"] > input_heavy["cost_usd"], (
        "the same 2000 tokens cost more as output than as input; got "
        f"{output_heavy['cost_usd']} vs {input_heavy['cost_usd']}"
    )


def _o3(f):
    """a cache miss ignores the cached prefix entirely"""
    got = f(input_tokens=2050, output_tokens=300, cached_prefix_tokens=2000, cache_hit=False)
    assert got["fresh_input_tokens"] == 2050, (
        "on a miss you pay full freight for every input token, prefix included; got "
        f"{got['fresh_input_tokens']}"
    )
    assert got["cost_usd"] == round(2050 / 1e6 * 3.0 + 300 / 1e6 * 15.0, 6), (
        f"a miss costs the plain input+output total; got {got['cost_usd']}"
    )


def _o4(f):
    """a cache hit bills the prefix at the cache rate"""
    got = f(input_tokens=2050, output_tokens=300, cached_prefix_tokens=2000, cache_hit=True)
    assert got["fresh_input_tokens"] == 50, (
        f"only the 50 non-prefix tokens are fresh on a hit; got {got['fresh_input_tokens']}"
    )
    expected = round(50 / 1e6 * 3.0 + 300 / 1e6 * 15.0 + 2000 / 1e6 * 0.30, 6)
    assert got["cost_usd"] == expected, (
        f"cached tokens are cheap, not free -- they still bill at cache_price. Expected "
        f"{expected}, got {got['cost_usd']}"
    )


def _o5(f):
    """caching is cheaper than not caching"""
    miss = f(input_tokens=2050, output_tokens=300, cached_prefix_tokens=2000, cache_hit=False)
    hit = f(input_tokens=2050, output_tokens=300, cached_prefix_tokens=2000, cache_hit=True)
    assert hit["cost_usd"] < miss["cost_usd"], (
        f"a hit must cost less than a miss or the cache is pointless; hit "
        f"{hit['cost_usd']} vs miss {miss['cost_usd']}"
    )


def _o6(f):
    """the cache_hit flag is echoed back"""
    for flag in (True, False):
        got = f(input_tokens=10, output_tokens=10, cached_prefix_tokens=5, cache_hit=flag)
        assert got["cache_hit"] is flag, f"cache_hit should come back as {flag}; got {got!r}"


def _o7(f):
    """a call with no tokens at all"""
    got = f(input_tokens=0, output_tokens=0, cached_prefix_tokens=0, cache_hit=False)
    assert got["cost_usd"] == 0.0, f"nothing sent, nothing billed; got {got['cost_usd']}"


def _o8(f):
    """custom prices are honoured"""
    got = f(
        input_tokens=1_000_000, output_tokens=1_000_000, cached_prefix_tokens=0,
        cache_hit=False, input_price=1.0, output_price=2.0,
    )
    assert got["cost_usd"] == 3.0, (
        "prices are per MILLION tokens, so 1M in at $1 plus 1M out at $2 is $3.00; got "
        f"{got['cost_usd']}"
    )


def _o9(f):
    """the whole prompt is a cached prefix"""
    got = f(input_tokens=2000, output_tokens=0, cached_prefix_tokens=2000, cache_hit=True)
    assert got["fresh_input_tokens"] == 0, f"nothing is fresh; got {got['fresh_input_tokens']}"
    assert got["cost_usd"] == round(2000 / 1e6 * 0.30, 6), (
        f"only the cache read is billed; got {got['cost_usd']}"
    )


def _o10(f):
    """the three reported keys are present"""
    got = f(input_tokens=10, output_tokens=10, cached_prefix_tokens=0, cache_hit=False)
    for key in ("cache_hit", "fresh_input_tokens", "cost_usd"):
        assert key in got, f"the result needs a {key!r} key; got {sorted(got)}"


task("ch05-token-cost", _ref_cost, [_o1, _o2, _o3, _o4, _o5, _o6, _o7, _o8, _o9, _o10])


# --- ch05-latency-profile ---


def _ref_profile():
    from solutions.reference.ch05 import profile_latency

    return profile_latency


def _y1(f):
    """all four stages are reported"""
    got = f([_request(1, 1, 1, 1)])
    assert sorted(got) == sorted(_STAGES), (
        f"the decomposition covers exactly the four stages {_STAGES}; got {sorted(got)}"
    )


def _y2(f):
    """shares, not averages"""
    log = [_request(50, 50, 50, 50), _request(50, 50, 50, 50)]
    got = f(log)
    assert got["queue_time_ms"]["pct"] == 25.0, (
        "pct is this stage's SHARE OF THE TOTAL: four equal stages means 25% each, whatever "
        f"the absolute numbers are. Got {got['queue_time_ms']['pct']}. The mean of this "
        "stage is 50, which is a different question -- a mean tells you how slow a stage is, "
        "a share tells you which stage a regression landed in, and only the second one "
        "diagnoses a spike."
    )


def _y3(f):
    """the shares add up to the whole"""
    log = [_request(10, 20, 30, 40), _request(5, 15, 25, 35)]
    total_pct = sum(stats["pct"] for stats in f(log).values())
    assert abs(total_pct - 100.0) < 1e-9, (
        f"shares of a total must sum to 100%; they sum to {total_pct}"
    )


def _y4(f):
    """totals are sums across the log"""
    log = [_request(10, 0, 0, 0), _request(30, 0, 0, 0)]
    got = f(log)
    assert got["queue_time_ms"]["total_ms"] == 40, (
        f"total_ms sums the stage across every request: 10 + 30 = 40; got "
        f"{got['queue_time_ms']['total_ms']}"
    )


def _y5(f):
    """one stage dominating"""
    got = f([_request(0, 0, 75, 25)])
    assert got["inference_time_ms"]["pct"] == 75.0, (
        f"inference is 75 of the 100ms spent; got {got['inference_time_ms']['pct']}"
    )
    assert got["queue_time_ms"]["pct"] == 0.0, (
        f"a stage that consumed nothing has a 0% share; got {got['queue_time_ms']['pct']}"
    )


def _y6(f):
    """a queueing spike shifts the shares"""
    normal = f([_request(10, 10, 60, 20)])
    spike = f([_request(500, 10, 60, 20)])
    assert spike["queue_time_ms"]["pct"] > normal["queue_time_ms"]["pct"], (
        "the whole point of shares is that a spike shows up as a shifted proportion; "
        f"normal {normal['queue_time_ms']['pct']}, spike {spike['queue_time_ms']['pct']}"
    )


def _y7(f):
    """an empty log"""
    got = f([])
    assert sorted(got) == sorted(_STAGES), (
        f"an empty window still reports all four stages rather than raising; got {sorted(got)}"
    )
    assert all(stats["pct"] == 0 for stats in got.values()), (
        f"with no data every share is 0, not a ZeroDivisionError; got {got!r}"
    )


def _y8(f):
    """a log where every stage is zero"""
    got = f([_request(0, 0, 0, 0)])
    assert all(stats["pct"] == 0 for stats in got.values()), (
        f"a zero grand total must not divide by zero; got {got!r}"
    )


def _y9(f):
    """each stage reports both numbers"""
    got = f([_request(1, 2, 3, 4)])
    for stage, stats in got.items():
        assert "total_ms" in stats and "pct" in stats, (
            f"{stage} needs both total_ms and pct; got {stats!r}"
        )


task("ch05-latency-profile", _ref_profile, [_y1, _y2, _y3, _y4, _y5, _y6, _y7, _y8, _y9])


# --- ch05-router ---


_CHEAP = llm_client.DEFAULT_MODELS[llm_client.LLM_PROVIDER]
_STRONG = llm_client.STRONG_MODELS[llm_client.LLM_PROVIDER]
_LONG_PROMPT = " ".join(["word"] * 100)


def _ref_router():
    from solutions.reference.ch05 import route_request

    return route_request


def _u1(f):
    """a short single-fact lookup"""
    got = f("What's the capital of France?")
    assert got == _CHEAP, f"a trivial lookup belongs on the cheap tier; got {got!r}"


def _u2(f):
    """a long, involved request"""
    got = f(_LONG_PROMPT)
    assert got == _STRONG, f"100 words is past the length cutoff; got {got!r}"


def _u3(f):
    """a SHORT request that needs tools"""
    got = f("Refund order ORD-1002.", requires_tool_use=True)
    assert got == _STRONG, (
        "requires_tool_use is an independent reason to escalate, and it is the one that "
        "actually matters: multi-step tool use is where a cheap model's failures get "
        f"expensive, and the request that needs it is often SHORT. Got {got!r}. Routing on "
        "length alone silently sends every tool-using request to the weak tier."
    )


def _u4(f):
    """long AND tool-using"""
    got = f(_LONG_PROMPT, requires_tool_use=True)
    assert got == _STRONG, f"both reasons apply; got {got!r}"


def _u5(f):
    """right at the length cutoff"""
    assert f(" ".join(["word"] * 80)) == _CHEAP, "80 words is not yet over the cutoff"
    assert f(" ".join(["word"] * 81)) == _STRONG, "81 words is over it"


def _u6(f):
    """length is counted in words, not characters"""
    got = f("supercalifragilisticexpialidocious " * 3)
    assert got == _CHEAP, (
        "three long words is a short prompt; counting characters would misroute it. "
        f"Got {got!r}"
    )


def _u7(f):
    """an empty prompt"""
    got = f("")
    assert got == _CHEAP, f"nothing to reason about; got {got!r}"


def _u8(f):
    """tool use still escalates an empty prompt"""
    got = f("", requires_tool_use=True)
    assert got == _STRONG, f"the tool-use flag stands on its own; got {got!r}"


def _u9(f):
    """the answer is one of the two real model ids"""
    got = f("What's the capital of France?")
    assert got in (_CHEAP, _STRONG), (
        f"return a model id from llm_client's DEFAULT_MODELS/STRONG_MODELS, not a tier "
        f"label -- the caller passes it straight to call_model(). Got {got!r}"
    )


def _u10(f):
    """tool use defaults to off"""
    assert f("What's the capital of France?") == f(
        "What's the capital of France?", requires_tool_use=False
    ), "omitting requires_tool_use must mean the same as passing False"


task(
    "ch05-router",
    _ref_router,
    [_u1, _u2, _u3, _u4, _u5, _u6, _u7, _u8, _u9, _u10],
)


# --- The three written diagnoses ---
#
# Graded on whether the answer names the cause, rules out the plausible-but-wrong cause, and
# proposes a fix that follows from the diagnosis. Not on wording: each concept is a family of
# markers wide enough that someone who understood it is not failed for vocabulary.
#
# The case that carries the weight in each of these is the one that rejects a CONFIDENT WRONG
# ANSWER -- the diagnosis a competent engineer actually reaches for first and that the data
# does not support. An empty answer failing proves nothing.

_MIN_WORDS = 60


def _needs(answer, family, what, hint, wrong=None, wrong_hint=""):
    """Assert the answer names `family`, with a tailored message when it named `wrong`."""
    if mentions(answer, family):
        return
    if wrong is not None and mentions(answer, wrong):
        raise AssertionError(
            f"this settles on {', '.join(matched(answer, wrong))!r}, which is the answer the "
            f"data does not support. {wrong_hint} {hint}"
        )
    raise AssertionError(f"the answer never names {what}. {hint}")


# ch05-diagnose-duplicate-calls

_DUP_CAUSE = ("duplicate", "twice", "double-submit", "double submit", "resubmit",
              "re-submit", "replay", "repeated request", "same request", "idempot",
              "retry", "fired twice", "sent twice")
_DUP_WRONG = ("harder question", "more complex", "complexity", "longer prompt",
              "bigger prompt", "users asked", "harder batch", "difficult question")
_DUP_FIX = ("idempot", "request id", "request_id", "dedup", "de-dup", "before execution",
            "check before", "unique id", "already processed")
_DUP_EVIDENCE = ("token", "double", "2x", "twice", "step change", "no change in")


def _ref_dup():
    from solutions.reference.ch05 import DIAGNOSE_DUPLICATE_CALLS

    return DIAGNOSE_DUPLICATE_CALLS


def _dd1(f):
    """the answer is written out at length"""
    is_written_answer(f, _MIN_WORDS)


def _dd2(f):
    """it names what in the log points at the cause"""
    _needs(f, _DUP_EVIDENCE, "the evidence in the log",
           "Say what you actually looked at -- the token counts against their neighbours.")


def _dd3(f):
    """it names the cause the data supports"""
    _needs(f, _DUP_CAUSE, "the cause",
           "Token volume stepped up with no matching change in what was asked. The same work "
           "is being done more than once.",
           wrong=_DUP_WRONG,
           wrong_hint="If the questions had genuinely got harder, the token counts would "
                      "track query complexity -- and here they do not.")


def _dd4(f):
    """it proposes a fix that follows from the cause"""
    _needs(f, _DUP_FIX, "a fix",
           "A duplicate call has to be recognised and dropped, which means identifying the "
           "request before executing it rather than after.")


def _dd5(f):
    """it rules out the plausible-but-wrong explanation rather than ignoring it"""
    assert mentions(f, _DUP_CAUSE), (
        "a diagnosis is a choice between hypotheses. Name the one the data supports; saying "
        "what it is NOT is what makes the answer convincing in an interview."
    )


task("ch05-diagnose-duplicate-calls", _ref_dup, [_dd1, _dd2, _dd3, _dd4, _dd5])


# ch05-diagnose-context-growth

_CTX_CAUSE = ("history", "context", "accumulat", "grow", "linear", "re-sent", "resent",
              "every turn", "each turn", "never truncat", "unbounded", "full conversation",
              "prior turn", "previous turn")
_CTX_WRONG = ("cheaper model", "switch model", "smaller model", "different model",
              "downgrade", "model routing")
_CTX_FIX = ("window", "truncat", "summar", "bounded", "cap", "trim", "sliding", "prune",
            "drop older", "limit the")
_CTX_RISK = ("context window", "context limit", "exceed", "overflow", "expensive", "cost",
             "grows", "compound")


def _ref_ctx():
    from solutions.reference.ch05 import DIAGNOSE_CONTEXT_GROWTH

    return DIAGNOSE_CONTEXT_GROWTH


def _cg1(f):
    """the answer is written out at length"""
    is_written_answer(f, _MIN_WORDS)


def _cg2(f):
    """it names the shape of the growth"""
    _needs(f, ("linear", "steadi", "climb", "grow", "rising", "increas", "monoton"),
           "the shape of the curve",
           "It is the SHAPE that identifies this one -- steady linear growth, not the "
           "log-normal spread a healthy mix of requests produces.")


def _cg3(f):
    """it names the cause"""
    _needs(f, _CTX_CAUSE, "the cause",
           "Something is being re-sent every turn and never removed.",
           wrong=_CTX_WRONG,
           wrong_hint="Moving to a cheaper model makes an unbounded context cheaper per "
                      "token and still unbounded -- it postpones the wall instead of "
                      "removing it.")


def _cg4(f):
    """it names what this eventually breaks, not just what it costs"""
    _needs(f, _CTX_RISK, "the consequence",
           "This is a cost problem right up until it is an outage -- unbounded growth "
           "eventually exceeds the context window itself.")


def _cg5(f):
    """it proposes a bounded-context fix"""
    _needs(f, _CTX_FIX, "a fix",
           "The history has to be bounded somehow: a window over recent turns, "
           "summarization of older ones, or both.")


task("ch05-diagnose-context-growth", _ref_ctx, [_cg1, _cg2, _cg3, _cg4, _cg5])


# ch05-diagnose-queueing

_Q_CAUSE = ("queue", "queuing", "queueing", "backpressure", "back-pressure", "waiting",
            "backlog", "admission")
_Q_WRONG = ("inference got slower", "inference is slower", "huge prompt", "bigger prompt",
            "larger prompt", "prompt got", "more tokens", "model got slower",
            "add more gpu", "add gpus", "buy more gpu")
_Q_RULED_OUT = ("token", "ordinary", "normal", "unchanged", "did not change", "didn't change",
                "flat", "same as")
_Q_FIX = ("capacity", "backpressure", "back-pressure", "admission", "scale", "concurrency",
          "shed", "rate limit", "which stage", "throughput")


def _ref_queue():
    from solutions.reference.ch05 import DIAGNOSE_QUEUEING

    return DIAGNOSE_QUEUEING


def _q1(f):
    """the answer is written out at length"""
    is_written_answer(f, _MIN_WORDS)


def _q2(f):
    """it names queueing as the stage that moved"""
    _needs(f, _Q_CAUSE, "the stage that actually grew",
           "Four stages were profiled. Name the one whose share of total latency changed.",
           wrong=_Q_WRONG,
           wrong_hint="'Inference got slower' and 'someone sent a huge prompt' are the two "
                      "reflex answers to a latency jump, and the per-request token counts "
                      "here rule out both -- the work per request did not change at all.")


def _q3(f):
    """it says what the token counts ruled out"""
    _needs(f, _Q_RULED_OUT, "what the token counts told you",
           "The token counts are the evidence that this is not a per-request-work problem. "
           "Saying what they ruled out is most of the diagnosis.")


def _q4(f):
    """it proposes a fix aimed at the queue"""
    _needs(f, _Q_FIX, "a fix",
           "A queueing problem is solved with capacity and backpressure, not with anything "
           "that makes an individual request faster.")


def _q5(f):
    """it does not stop at the reflex answer"""
    assert mentions(f, _Q_CAUSE), (
        "'add more GPUs' is only accidentally right here -- it helps insofar as it adds "
        "queue capacity, and not at all because inference got slower. An answer that stops "
        "there has pattern-matched on the symptom instead of reading the stage breakdown."
    )


task("ch05-diagnose-queueing", _ref_queue, [_q1, _q2, _q3, _q4, _q5])
