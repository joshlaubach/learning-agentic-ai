"""Graded task suites for Chapter 4 — Production Reliability.

Every case here drives a clock or a counter rather than a real timer, so the suites are fast
and deterministic and a failure points at the policy rather than at scheduling noise.
"""

from __future__ import annotations

from agentlib.grading import task


class _ApiError(Exception):
    """Stands in for a provider SDK's HTTP error, which carries a status code."""

    def __init__(self, status_code, message="api error"):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code


def _counting_sleep():
    calls = []

    def sleep_fn(seconds):
        calls.append(seconds)

    sleep_fn.calls = calls
    return sleep_fn


def _fails_then_succeeds(n_failures, exc=None):
    state = {"n": 0}

    def fn():
        state["n"] += 1
        if state["n"] <= n_failures:
            raise (exc or RuntimeError(f"transient failure {state['n']}"))
        return "ok"

    fn.state = state
    return fn


# --- ch04-ttl-cache ---


def _ref_cache():
    from solutions.reference.ch04 import TTLCache

    return TTLCache


def _c1(f):
    """reading a key that was never written"""
    got = f(ttl_seconds=10).get("billing.py", now=0)
    assert got == (None, None), f"a miss returns (None, None); got {got!r}"


def _c2(f):
    """reading back a fresh entry"""
    c = f(ttl_seconds=10)
    c.set("billing.py", "def charge(): ...", now=100)
    got = c.get("billing.py", now=103)
    assert got == ("def charge(): ...", 100), (
        f"a live hit returns (value, the time it was cached); got {got!r}"
    )


def _c3(f):
    """the entry goes stale while nothing else happens"""
    c = f(ttl_seconds=10)
    c.set("billing.py", "old contents", now=0)
    assert c.get("billing.py", now=3) == ("old contents", 0), "should still be live at t=3"
    got = c.get("billing.py", now=50)
    assert got == (None, None), (
        "staleness has to be judged when you READ, against the clock at read time. Nothing "
        "was written between t=3 and t=50, so a cache that only checks the TTL on set() "
        f"never notices and serves this forever. Got {got!r}. That is the outdated-printout "
        "bug this section is about."
    )


def _c4(f):
    """exactly at the TTL boundary"""
    c = f(ttl_seconds=10)
    c.set("k", "v", now=0)
    got = c.get("k", now=10)
    assert got == (None, None), (
        f"an entry lives for strictly less than ttl seconds, so at exactly ttl it is "
        f"expired; got {got!r}"
    )


def _c5(f):
    """one tick under the boundary"""
    c = f(ttl_seconds=10)
    c.set("k", "v", now=0)
    got = c.get("k", now=9.999)
    assert got == ("v", 0), f"still inside the TTL window; got {got!r}"


def _c6(f):
    """rewriting a key restarts its clock"""
    c = f(ttl_seconds=10)
    c.set("k", "first", now=0)
    c.set("k", "second", now=8)
    got = c.get("k", now=15)
    assert got == ("second", 8), (
        f"the second write is what the entry's age is measured from now; got {got!r}"
    )


def _c7(f):
    """invalidate drops an entry that is still live"""
    c = f(ttl_seconds=100)
    c.set("k", "v", now=0)
    c.invalidate("k")
    got = c.get("k", now=1)
    assert got == (None, None), (
        f"invalidate is the manual escape hatch for a key you know changed; got {got!r}"
    )


def _c8(f):
    """invalidating something that was never cached"""
    c = f(ttl_seconds=10)
    c.invalidate("never-cached")  # must not raise


def _c9(f):
    """keys expire independently"""
    c = f(ttl_seconds=10)
    c.set("old", "a", now=0)
    c.set("new", "b", now=8)
    assert c.get("old", now=12) == (None, None), "'old' is 12s past its write and should be stale"
    assert c.get("new", now=12) == ("b", 8), "'new' is only 4s old and should still be live"


def _c10(f):
    """a stale read does not resurrect on a later, earlier-looking read"""
    c = f(ttl_seconds=10)
    c.set("k", "v", now=0)
    c.get("k", now=99)
    got = c.get("k", now=5)
    assert got == ("v", 0), (
        "expiry is computed per read from cached_at, not latched on the first stale read; "
        f"a read at t=5 is still inside the window. Got {got!r}"
    )


task("ch04-ttl-cache", _ref_cache, [_c1, _c2, _c3, _c4, _c5, _c6, _c7, _c8, _c9, _c10])


# --- ch04-backoff ---


def _ref_backoff():
    from solutions.reference.ch04 import retry_with_backoff

    return retry_with_backoff


def _b1(f):
    """the call succeeds first time"""
    got = f(lambda: "ok", jitter=0)()
    assert got == ("ok", []), (
        f"a first-attempt success returns (result, an empty attempts log); got {got!r}"
    )


def _b2(f):
    """nothing sleeps when nothing failed"""
    sleep_fn = _counting_sleep()
    f(lambda: "ok", jitter=0, sleep_fn=sleep_fn)()
    assert sleep_fn.calls == [], (
        "back off AFTER a failure, never before the first attempt. This wrapper sleeps "
        f"{len(sleep_fn.calls)} time(s) on a call that succeeded immediately, which adds "
        "latency to every healthy request in production for no reason at all."
    )


def _b3(f):
    """two failures then a success"""
    result, log = f(_fails_then_succeeds(2), jitter=0)()
    assert result == "ok", f"the eventual success is returned; got {result!r}"
    assert len(log) == 2, f"one log entry per failed attempt, so 2; got {len(log)}: {log!r}"


def _b4(f):
    """the delay doubles each attempt"""
    sleep_fn = _counting_sleep()
    f(_fails_then_succeeds(3), base_delay=1.0, jitter=0, sleep_fn=sleep_fn)()
    assert sleep_fn.calls == [1.0, 2.0, 4.0], (
        "backoff is EXPONENTIAL: base * 2**(attempt-1), so 1, 2, 4. Got "
        f"{sleep_fn.calls}. Linear growth (base * attempt) gives 1, 2, 3 -- it looks similar "
        "over three attempts and stops helping exactly when you need it, because it never "
        "backs off faster than the queue is filling up."
    )


def _b5(f):
    """base_delay scales the whole schedule"""
    sleep_fn = _counting_sleep()
    f(_fails_then_succeeds(3), base_delay=0.5, jitter=0, sleep_fn=sleep_fn)()
    assert sleep_fn.calls == [0.5, 1.0, 2.0], (
        f"with base_delay=0.5 the schedule is 0.5, 1, 2; got {sleep_fn.calls}"
    )


def _b6(f):
    """the logged delay matches the delay actually taken"""
    sleep_fn = _counting_sleep()
    _, log = f(_fails_then_succeeds(2), base_delay=1.0, jitter=0, sleep_fn=sleep_fn)()
    assert [e["backoff_s"] for e in log] == sleep_fn.calls, (
        f"the log should record what was actually waited; log says "
        f"{[e['backoff_s'] for e in log]}, sleep_fn saw {sleep_fn.calls}"
    )


def _b7(f):
    """each log entry names the attempt and the error"""
    _, log = f(_fails_then_succeeds(2), jitter=0)()
    assert [e["attempt"] for e in log] == [1, 2], (
        f"attempts are numbered from 1; got {[e.get('attempt') for e in log]}"
    )
    assert all("error" in e and "backoff_s" in e for e in log), (
        f"each entry needs attempt, error and backoff_s; got {log!r}"
    )


def _b8(f):
    """the dependency never recovers"""
    fn = _fails_then_succeeds(99)
    try:
        f(fn, max_retries=4, jitter=0)()
    except RuntimeError:
        pass
    else:
        raise AssertionError("exhausting max_retries must raise RuntimeError, not return")
    assert fn.state["n"] == 4, (
        f"max_retries=4 means 4 total attempts; the function was called {fn.state['n']} times"
    )


def _b9(f):
    """the original error is not swallowed"""
    original = ValueError("the real cause")
    try:
        f(_fails_then_succeeds(99, exc=original), max_retries=2, jitter=0)()
    except RuntimeError as e:
        assert e.__cause__ is original, (
            "raise the give-up error `from` the last exception, so the real cause survives "
            f"in the traceback; __cause__ is {e.__cause__!r}"
        )


def _b10(f):
    """arguments reach the wrapped function"""
    seen = {}

    def fn(a, b=None):
        seen["args"] = (a, b)
        return "ok"

    f(fn, jitter=0)("x", b="y")
    assert seen["args"] == ("x", "y"), (
        f"the wrapper must forward *args/**kwargs through to fn; it saw {seen.get('args')!r}"
    )


def _b11(f):
    """jitter stays inside its band"""
    sleep_fn = _counting_sleep()
    f(_fails_then_succeeds(3), base_delay=1.0, jitter=0.5, seed=7, sleep_fn=sleep_fn)()
    for taken, floor in zip(sleep_fn.calls, [1.0, 2.0, 4.0]):
        assert floor <= taken < floor + 0.5, (
            f"jitter adds between 0 and `jitter` seconds on top of the exponential delay; "
            f"expected [{floor}, {floor + 0.5}), got {taken}"
        )


def _b12(f):
    """no sleep before giving up"""
    sleep_fn = _counting_sleep()
    try:
        f(_fails_then_succeeds(99), max_retries=3, jitter=0, sleep_fn=sleep_fn)()
    except RuntimeError:
        pass
    assert sleep_fn.calls == [1.0, 2.0], (
        f"3 attempts need 2 waits, between them; got {sleep_fn.calls}. A sleep after the final "
        "failure delays the error by the longest wait in the schedule and buys nothing, "
        "because no attempt follows it."
    )


task(
    "ch04-backoff",
    _ref_backoff,
    [_b1, _b2, _b3, _b4, _b5, _b6, _b7, _b8, _b9, _b10, _b11, _b12],
)


# --- ch04-no-retry-4xx ---


def _ref_should_retry():
    from solutions.reference.ch04 import should_retry

    return should_retry


def _r1(f):
    """a rate limit"""
    assert f(_ApiError(429)) is True, "429 means slow down and try again -- retryable"


def _r2(f):
    """server-side failures"""
    for status in (500, 502, 503, 504):
        assert f(_ApiError(status)) is True, f"{status} is the server's problem and may pass"


def _r3(f):
    """a malformed request"""
    got = f(_ApiError(400))
    assert got is False, (
        "a 400 says the request itself is wrong. It will be exactly as wrong on the sixth "
        f"attempt as the first, so retrying only multiplies the delay before the caller "
        f"sees the real error. Got {got!r}."
    )


def _r4(f):
    """auth and addressing failures"""
    for status in (401, 403, 404, 422):
        got = f(_ApiError(status))
        assert got is False, (
            f"{status} will not fix itself between attempts -- surface it immediately. "
            f"Got {got!r}"
        )


def _r5(f):
    """a 4xx that IS worth retrying"""
    got = f(_ApiError(408))
    assert got is True, (
        "408 Request Timeout is a 4xx, and it is transient -- so is 429. Treating the whole "
        f"4xx range as non-retryable throws away the two statuses that most need a retry. "
        f"Got {got!r}."
    )


def _r6(f):
    """a transport failure with no status at all"""
    assert f(ConnectionError("connection reset")) is True, (
        "a dropped connection never reaches the server; retrying is the whole point"
    )
    assert f(TimeoutError("timed out")) is True, "a timeout is transient by definition"


def _r7(f):
    """an unclassifiable error"""
    got = f(RuntimeError("something odd"))
    assert got is True, (
        f"with no status to go on, treat the error as transient rather than giving up on "
        f"the first blip; got {got!r}"
    )


def _r8(f):
    """the answer is a real bool"""
    got = f(_ApiError(400))
    assert isinstance(got, bool), (
        f"return True or False -- the retry loop branches on this directly. Got "
        f"{type(got).__name__}: {got!r}"
    )


task("ch04-no-retry-4xx", _ref_should_retry, [_r1, _r2, _r3, _r4, _r5, _r6, _r7, _r8])


# --- ch04-circuit-breaker ---


def _ref_breaker():
    from solutions.reference.ch04 import CircuitBreaker

    return CircuitBreaker


def _boom():
    raise ConnectionError("dependency is down")


def _counted(fn):
    calls = []

    def wrapper():
        calls.append(1)
        return fn()

    wrapper.calls = calls
    return wrapper


def _trip(breaker, tool, threshold=3, start=0):
    for t in range(start, start + threshold):
        try:
            breaker.call(tool, now=t)
        except Exception:
            pass


def _x1(f):
    """a healthy dependency stays closed"""
    b = f(failure_threshold=3, cooldown=5)
    assert b.call(lambda: "ok", now=0) == "ok", "a closed breaker just returns the result"
    assert b.state == "closed", f"nothing failed, so the state stays 'closed'; got {b.state!r}"


def _x2(f):
    """failures below the threshold keep it closed"""
    b = f(failure_threshold=3, cooldown=5)
    _trip(b, _boom, threshold=2)
    assert b.state == "closed", (
        f"2 failures with a threshold of 3 is not enough to open; got {b.state!r}"
    )


def _x3(f):
    """the threshold opens the circuit"""
    b = f(failure_threshold=3, cooldown=5)
    _trip(b, _boom, threshold=3)
    assert b.state == "open", f"3 failures at a threshold of 3 opens it; got {b.state!r}"


def _x4(f):
    """an open circuit stops calling the dependency"""
    b = f(failure_threshold=3, cooldown=5)
    tool = _counted(_boom)
    _trip(b, tool, threshold=3)  # opens at now=2
    before = len(tool.calls)
    for t in range(3, 7):  # still inside the 5s cooldown that started at now=2
        try:
            b.call(tool, now=t)
        except Exception:
            pass
    assert len(tool.calls) == before, (
        f"while open, the breaker must fail fast WITHOUT invoking the dependency -- that is "
        f"the entire saving. It was called {len(tool.calls) - before} more time(s)."
    )


def _x5(f):
    """failing fast raises rather than returning"""
    b = f(failure_threshold=1, cooldown=100)
    _trip(b, _boom, threshold=1)
    try:
        b.call(lambda: "ok", now=1)
    except Exception:
        pass
    else:
        raise AssertionError("an open breaker must raise, not silently return a value")


def _x6(f):
    """after the cooldown, one trial call goes through"""
    b = f(failure_threshold=2, cooldown=5)
    _trip(b, _boom, threshold=2)
    tool = _counted(lambda: "recovered")
    got = b.call(tool, now=100)
    assert len(tool.calls) == 1 and got == "recovered", (
        "once `cooldown` has elapsed the breaker must go half-open and let exactly one "
        "trial call reach the dependency. Without that transition it stays open forever "
        "and NEVER recovers, even after the dependency is healthy again -- an outage that "
        f"outlives its own cause. The dependency was called {len(tool.calls)} time(s)."
    )
    assert b.state == "closed", (
        f"a successful trial call closes the circuit again; got {b.state!r}"
    )


def _x7(f):
    """the cooldown is respected"""
    b = f(failure_threshold=2, cooldown=50)
    _trip(b, _boom, threshold=2)
    tool = _counted(lambda: "recovered")
    try:
        b.call(tool, now=3)
    except Exception:
        pass
    assert tool.calls == [], (
        f"only 3 of the 50-second cooldown have passed, so nothing should reach the "
        f"dependency yet; it was called {len(tool.calls)} time(s)"
    )


def _x8(f):
    """a failed trial call re-opens the circuit"""
    b = f(failure_threshold=2, cooldown=5)
    _trip(b, _boom, threshold=2)
    try:
        b.call(_boom, now=100)
    except Exception:
        pass
    assert b.state == "open", (
        "if the half-open trial call fails, the dependency is still sick: go straight back "
        f"to open rather than letting more traffic through. Got {b.state!r}"
    )


def _x9(f):
    """a success clears the failure count"""
    b = f(failure_threshold=3, cooldown=5)
    _trip(b, _boom, threshold=2)
    b.call(lambda: "ok", now=2)
    _trip(b, _boom, threshold=2, start=3)
    assert b.state == "closed", (
        "the counter tracks CONSECUTIVE failures -- a success in between resets it, so "
        f"2 + 2 failures either side of a success is not 4. Got {b.state!r}"
    )


def _x10(f):
    """the underlying error still reaches the caller"""
    b = f(failure_threshold=5, cooldown=5)
    try:
        b.call(_boom, now=0)
    except ConnectionError:
        pass
    else:
        raise AssertionError(
            "while closed, the breaker counts the failure and re-raises the original "
            "exception; swallowing it hides the outage from the caller"
        )


task(
    "ch04-circuit-breaker",
    _ref_breaker,
    [_x1, _x2, _x3, _x4, _x5, _x6, _x7, _x8, _x9, _x10],
)


# --- ch04-pass-hat-k ---


def _ref_pass_hat_k():
    from solutions.reference.ch04 import pass_hat_k

    return pass_hat_k


def _close(got, want):
    return isinstance(got, (int, float)) and abs(got - want) < 1e-9


def _expect_value_error(f, why, *args):
    try:
        f(*args)
    except ValueError:
        return
    except NotImplementedError:
        raise
    except Exception as e:
        raise AssertionError(f"{why}: expected a ValueError, got {type(e).__name__}: {e}")
    raise AssertionError(f"{why}: expected a ValueError, but nothing was raised")


def _k1(f):
    """a perfectly reliable agent scores 1.0 at every k"""
    results = {"a": [True] * 4, "b": [True] * 4}
    for k in (1, 2, 3, 4):
        got = f(results, k)
        assert _close(got, 1.0), f"every trial passed, so pass^{k} must be 1.0; got {got!r}"


def _k2(f):
    """3 of 4 trials pass, k=2: exactly 0.5, not 0.5625"""
    got = f({"a": [True, True, True, False]}, 2)
    assert _close(got, 0.5), (
        f"of the 6 ways to pick 2 of the 4 trials, 3 avoid the failure: 3/6 = 0.5. Got {got!r}. "
        f"(0.75 ** 2 = 0.5625 treats the trials as drawn with replacement, which a 4-trial "
        f"sample is not.)"
    )


def _k3(f):
    """k=1 is the plain mean success rate"""
    results = {
        "a": [True, True, False, False],
        "b": [True, False, False, False],
        "c": [True, True, True, True],
    }
    got = f(results, 1)
    want = (0.5 + 0.25 + 1.0) / 3
    assert _close(got, want), (
        f"pass^1 is just the average of the per-task success rates, {want:.4f}. Got {got!r}"
    )


def _k4(f):
    """one failure in 4 trials: k=3 gives 0.25, k=4 gives 0"""
    results = {"a": [True, True, True, False]}
    got3, got4 = f(results, 3), f(results, 4)
    assert _close(got3, 0.25), (
        f"only 1 of the 4 ways to pick 3 trials avoids the failure: 0.25. Got {got3!r}. "
        f"Checking whether the first k trials passed answers a different question and gives "
        f"1.0 here."
    )
    assert _close(got4, 0.0), f"the failure is inside any 4 trials, so pass^4 is 0; got {got4!r}"


def _k5(f):
    """the order of the trials does not change the score"""
    early_fail = f({"a": [False, True, True, True]}, 3)
    late_fail = f({"a": [True, True, True, False]}, 3)
    assert _close(early_fail, late_fail), (
        f"the same 4 outcomes in a different order must score the same; got {early_fail!r} "
        f"and {late_fail!r}. If you slice trials[:k], where the failure sits decides the answer."
    )


def _k6(f):
    """tasks are averaged one by one, not pooled"""
    results = {"a": [True] * 4, "b": [False] * 4}
    got = f(results, 2)
    assert _close(got, 0.5), (
        f"one task always works and one never does, so half the tasks are reliable: 0.5. "
        f"Got {got!r}. Pooling all 8 trials into one bucket blurs which task each came from."
    )


def _k7(f):
    """pass^k never rises as k grows"""
    results = {
        "a": [True, True, True, False, False],
        "b": [True, False, True, True, True],
        "c": [True, True, True, True, True],
    }
    values = [f(results, k) for k in (1, 2, 3, 4, 5)]
    for earlier, later in zip(values, values[1:]):
        assert later <= earlier + 1e-12, (
            f"asking for more consecutive successes cannot make success likelier; got "
            f"{[round(v, 3) for v in values]}. A score that rises with k is pass@k, the "
            f"opposite question."
        )
    assert values[-1] < values[0], "pass^5 should be strictly below pass^1 for these results"


def _k8(f):
    """inputs it cannot estimate raise ValueError"""
    _expect_value_error(f, "empty results", {}, 1)
    _expect_value_error(f, "k below 1", {"a": [True, False]}, 0)
    _expect_value_error(
        f, "k above the number of trials: 2 trials cannot estimate 3 in a row",
        {"a": [True, False]}, 3,
    )


task("ch04-pass-hat-k", _ref_pass_hat_k, [_k1, _k2, _k3, _k4, _k5, _k6, _k7, _k8])


# --- ch04-gate-chain ---


def _ref_run_gated():
    from solutions.reference.ch04 import run_gated

    return run_gated


def _gate(log, name, outcome):
    """A gate that records its calls and returns, or raises, a scripted outcome."""

    def g(*args, **kwargs):
        log.append((name, args, kwargs))
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    return g


def _action(log):
    def act(*args, **kwargs):
        log.append(("ACTION", args, kwargs))
        return "refund issued"

    return act


def _called(log, name):
    return sum(1 for entry in log if entry[0] == name)


def _g1(f):
    """every gate passes: the action runs once, with the same arguments"""
    log = []
    gates = [("rules", 0, _gate(log, "rules", (True, "within limit"))),
             ("tests", 10, _gate(log, "tests", (True, "tests green")))]
    out = f(_action(log), gates, "order-7", amount=50)
    assert out["executed"] is True and out["result"] == "refund issued", (
        f"all gates passed, so the action runs and its result comes back; got {out!r}"
    )
    assert _called(log, "ACTION") == 1, "the action must run exactly once"
    assert ("ACTION", ("order-7",), {"amount": 50}) in log, "the action got different arguments"
    assert ("rules", ("order-7",), {"amount": 50}) in log, "gates must see the same arguments"
    assert out["denied_by"] is None
    assert [t["gate"] for t in out["trail"]] == ["rules", "tests"] and all(
        t["passed"] for t in out["trail"]
    ), f"the trail should list each gate that ran and what it said; got {out['trail']!r}"


def _g2(f):
    """a gate says no: the action never runs"""
    log = []
    gates = [("rules", 0, _gate(log, "rules", (False, "over limit")))]
    out = f(_action(log), gates, "order-7", amount=5000)
    assert _called(log, "ACTION") == 0, (
        "the action ran even though a gate denied it. An irreversible step has to be gated "
        "BEFORE it runs; checking afterwards just documents the damage."
    )
    assert out["executed"] is False and out["result"] is None and out["denied_by"] == "rules", (
        f"expected executed=False, result=None, denied_by='rules'; got {out!r}"
    )
    assert out["trail"][-1] == {"gate": "rules", "passed": False, "reason": "over limit"}, (
        f"the denying gate's reason belongs in the trail; got {out['trail']!r}. "
        f"(Is `if not gate(...)` the check? A (False, 'reason') tuple is truthy.)"
    )


def _g3(f):
    """a gate that raises denies instead of crashing or being skipped"""
    for name, exc in (("rules", RuntimeError("db down")), ("human", TimeoutError("no reply"))):
        log = []
        gates = [(name, 0, _gate(log, name, exc))]
        try:
            out = f(_action(log), gates, "order-7")
        except NotImplementedError:
            raise
        except Exception as e:
            raise AssertionError(
                f"a gate that raised {type(exc).__name__} escaped as {type(e).__name__}; the "
                f"chain should catch it and deny"
            )
        assert out["executed"] is False and _called(log, "ACTION") == 0, (
            f"a gate that could not decide ({type(exc).__name__}) must not wave the action "
            f"through: fail closed. Got {out!r}"
        )
        assert out["denied_by"] == name and type(exc).__name__ in out["trail"][-1]["reason"], (
            f"deny, and put the exception type in the reason so the audit log says why; got "
            f"{out['trail']!r}"
        )


def _g4(f):
    """a gate that returns nothing useful denies"""
    for label, outcome in (("None", None), ("a bare truthy string", "looks good")):
        log = []
        gates = [("tests", 0, _gate(log, "tests", outcome))]
        out = f(_action(log), gates, "order-7")
        assert out["executed"] is False and _called(log, "ACTION") == 0, (
            f"a gate that returned {label} did not say (True, reason), so it did not approve. "
            f"Approval has to be explicit. Got {out!r}"
        )


def _g5(f):
    """gates run cheapest first and stop at the first denial"""
    log = []
    gates = [
        ("human", 100, _gate(log, "human", (True, "approved"))),
        ("rules", 0, _gate(log, "rules", (False, "over limit"))),
        ("tests", 10, _gate(log, "tests", (True, "green"))),
    ]
    out = f(_action(log), gates, "order-7")
    assert _called(log, "human") == 0 and _called(log, "tests") == 0, (
        "the free rule check denied, yet a costlier gate still ran. A human who is paged for "
        "something a rule already rejected is the most expensive way to learn nothing."
    )
    assert out["denied_by"] == "rules", f"expected the cheap rule gate to deny; got {out!r}"


def _g6(f):
    """cost decides the order, and ties keep the order you declared"""
    log = []
    gates = [("a", 10, _gate(log, "a", (True, "ok"))),
             ("b", 0, _gate(log, "b", (True, "ok"))),
             ("c", 10, _gate(log, "c", (True, "ok")))]
    out = f(_action(log), gates, "x")
    order = [t["gate"] for t in out["trail"]]
    assert order == ["b", "a", "c"], (
        f"expected cheapest first with ties in declared order: ['b', 'a', 'c']; got {order}"
    )


def _g7(f):
    """no gates means no approval"""
    log = []
    out = f(_action(log), [], "order-7")
    assert out["executed"] is False and _called(log, "ACTION") == 0, (
        "with zero gates nothing approved the action. `all([])` is True, but an irreversible "
        "step with no gate in front of it is the bug, not a pass."
    )
    assert out["denied_by"] == "no-gates", f"name the cause: denied_by='no-gates'; got {out!r}"


def _g8(f):
    """the action's own failure is not mistaken for a gate denial"""
    log = []

    def failing_action(*args, **kwargs):
        log.append(("ACTION", args, kwargs))
        raise ValueError("payment provider rejected the card")

    gates = [("rules", 0, _gate(log, "rules", (True, "ok")))]
    try:
        f(failing_action, gates, "order-7")
    except ValueError as e:
        assert "payment provider" in str(e)
    else:
        raise AssertionError(
            "the action ran and failed, but run_gated reported a result instead of raising. "
            "Catch exceptions around the gates only; wrapping the action hides a failed "
            "irreversible step behind a tidy dict."
        )


task("ch04-gate-chain", _ref_run_gated, [_g1, _g2, _g3, _g4, _g5, _g6, _g7, _g8])


# --- ch04-refine-loop ---


def _ref_refine():
    from solutions.reference.ch04 import refine

    return refine


class _Generate:
    """Scripted drafts. Raises if called absurdly often, so a loop with no budget fails the
    case instead of hanging the grader."""

    def __init__(self, drafts, limit=25):
        self.drafts, self.limit, self.calls, self.feedback = drafts, limit, 0, []

    def __call__(self, feedback=None):
        self.calls += 1
        assert self.calls <= self.limit, (
            f"generate was called more than {self.limit} times: the loop has no round budget"
        )
        self.feedback.append(feedback)
        return self.drafts[min(self.calls - 1, len(self.drafts) - 1)]


class _Critique:
    def __init__(self, text="LGTM, ship it"):
        self.text, self.calls = text, 0

    def __call__(self, draft):
        self.calls += 1
        return self.text


class _Verify:
    """The external check: only drafts in `good` pass, and it says why the others do not."""

    def __init__(self, good=(), limit=25):
        self.good, self.limit, self.calls = set(good), limit, 0

    def __call__(self, draft):
        self.calls += 1
        assert self.calls <= self.limit, (
            f"verify was called more than {self.limit} times: the loop has no round budget"
        )
        if draft in self.good:
            return True, "all checks pass"
        return False, "missing unit test"


def _f1(f):
    """a first draft that verifies is returned without any critique"""
    gen, crit, ver = _Generate(["good"]), _Critique(), _Verify(good={"good"})
    out = f(gen, crit, ver)
    assert out["draft"] == "good" and out["verified"] is True and out["stop"] == "verified", (
        f"the first draft passed verification; got {out!r}"
    )
    assert out["rounds"] == 1 and gen.calls == 1, "one draft, one generate call"
    assert crit.calls == 0, (
        "a draft that already verified was critiqued anyway. Polishing a passing answer is "
        "not free: regenerating can flip a correct answer into a wrong one."
    )


def _f2(f):
    """the first call gets no feedback; the next gets the verifier's reason and the critique"""
    gen = _Generate(["bad", "good"])
    crit, ver = _Critique("the tests are absent"), _Verify(good={"good"})
    f(gen, crit, ver)
    assert gen.feedback[0] is None, f"round 1 has nothing to react to; got {gen.feedback[0]!r}"
    second = gen.feedback[1]
    assert isinstance(second, str) and "missing unit test" in second, (
        f"the verifier's reason is the ground truth about what is wrong; it has to reach "
        f"generate. Got {second!r}"
    )
    assert "the tests are absent" in second, (
        f"the critique explains why; pass it along with the reason. Got {second!r}"
    )


def _f3(f):
    """a critic that approves everything does not end the loop"""
    gen = _Generate(["bad", "good"])
    out = f(gen, _Critique("LGTM"), _Verify(good={"good"}))
    assert out["draft"] == "good" and out["verified"] is True and out["rounds"] == 2, (
        f"the critic said LGTM about a draft the verifier rejected; the loop must keep going "
        f"until the verifier approves. Got {out!r}"
    )


def _f4(f):
    """a draft nothing verifies comes back flagged unverified, never accepted"""
    gen = _Generate(["a", "b", "c", "d"])
    out = f(gen, _Critique("LGTM"), _Verify(good=()), 3)
    assert out["verified"] is False and out["stop"] == "budget", (
        f"nothing passed verification, so the result is unverified and stopped on budget; "
        f"got {out!r}. A sycophantic critic must not be able to buy acceptance."
    )
    assert out["draft"] == "c" and out["rounds"] == 3, (
        f"return the last draft and the rounds used; got {out!r}"
    )


def _f5(f):
    """max_rounds bounds both generate and verify (default 3)"""
    gen, ver = _Generate(["a", "b", "c", "d", "e", "f"]), _Verify(good=())
    f(gen, _Critique(), ver)
    assert gen.calls == 3 and ver.calls == 3, (
        f"the default budget is 3 rounds: 3 generates and 3 verifies; got {gen.calls} and "
        f"{ver.calls}"
    )
    gen, ver = _Generate(["a", "b", "c", "d", "e", "f"]), _Verify(good=())
    f(gen, _Critique(), ver, max_rounds=5)
    assert gen.calls == 5 and ver.calls == 5, (
        f"max_rounds=5 means 5 drafts; got {gen.calls} generates and {ver.calls} verifies"
    )


def _f6(f):
    """no critique after the final failed draft"""
    gen, crit = _Generate(["a", "b", "c", "d"]), _Critique()
    f(gen, crit, _Verify(good=()), 4)
    assert crit.calls == 3, (
        f"4 drafts leave room for 3 rounds of feedback; the 4th has no next round to use a "
        f"critique. Got {crit.calls} critique calls."
    )


def _f7(f):
    """an identical redraft stops the loop as stalled"""
    gen, ver = _Generate(["same"]), _Verify(good=())
    out = f(gen, _Critique(), ver, 5)
    assert out["stop"] == "stalled" and out["verified"] is False, (
        f"the model returned the same draft twice; more rounds cannot help. Expected "
        f"stop='stalled'; got {out!r}"
    )
    assert gen.calls <= 2, (
        f"generate ran {gen.calls} times on a loop that stopped changing after round 1; "
        f"that is budget burned for nothing (compare the duplicate-observation guard from "
        f"Chapter 2)"
    )


def _f8(f):
    """a one-round budget, a zero budget, and a numbered trace"""
    gen, crit = _Generate(["a"]), _Critique()
    out = f(gen, crit, _Verify(good=()), 1)
    assert out["rounds"] == 1 and crit.calls == 0 and out["stop"] == "budget", (
        f"max_rounds=1 is one draft and no critique; got {out!r}, {crit.calls} critique calls"
    )
    assert [t["round"] for t in out["trace"]] == [1] and {"draft", "verified", "reason"} <= set(
        out["trace"][0]
    ), f"the trace is the audit log: one numbered entry per round; got {out['trace']!r}"
    try:
        f(_Generate(["a"]), _Critique(), _Verify(good=()), 0)
    except ValueError:
        pass
    else:
        raise AssertionError("max_rounds=0 asks for no drafts at all; raise ValueError")


task("ch04-refine-loop", _ref_refine, [_f1, _f2, _f3, _f4, _f5, _f6, _f7, _f8])


# --- ch04-harness-fingerprint ---


def _ref_fingerprint():
    from solutions.reference.ch04 import fingerprint

    return fingerprint


def _manifest():
    return {
        "harness_version": "1.2.0",
        "model": "model-a",
        "prompt_version": "v7",
        "context_policy": {"window": 8000, "truncate": "oldest-first"},
        "tools": ["search", "lookup"],
        "retry_policy": {"max_retries": 3, "base_delay": 1.0},
        "budgets": {"max_steps": 20, "max_calls": 50, "max_seconds": 120},
        "verifications": ["schema", "refund-policy"],
        "sampling": {"temperature": None, "seed": None},
    }


def _h1(f):
    """a 12-character lowercase hex string, the same every call"""
    import re

    a, b = f(_manifest()), f(_manifest())
    assert isinstance(a, str) and re.fullmatch(r"[0-9a-f]{12}", a), (
        f"expected 12 lowercase hex characters; got {a!r}"
    )
    assert a == b, "two separately built, equal manifests must have the same fingerprint"


def _h2(f):
    """top-level key order does not matter"""
    m = _manifest()
    reordered = dict(reversed(list(m.items())))
    assert f(m) == f(reordered), (
        "the same settings listed in a different order are the same harness; str(manifest) "
        "and plain json.dumps both treat them as different"
    )


def _h3(f):
    """nested key order does not matter either"""
    m = _manifest()
    shuffled = _manifest()
    shuffled["budgets"] = dict(reversed(list(m["budgets"].items())))
    shuffled["context_policy"] = dict(reversed(list(m["context_policy"].items())))
    assert f(m) == f(shuffled), (
        "sorting only the top level leaves nested dicts order-dependent; canonicalise at "
        "every depth"
    )


def _h4(f):
    """list order matters: a different tool order is a different harness"""
    m = _manifest()
    swapped = _manifest()
    swapped["tools"] = ["lookup", "search"]
    assert f(m) != f(swapped), (
        "tool order and retry schedules are behaviour, not set membership; sorting lists to "
        "be 'order-insensitive' erases a real difference"
    )


def _h5(f):
    """changing any disclosed setting changes the fingerprint, budgets included"""
    base = f(_manifest())
    edits = {
        "model": lambda m: m.update(model="model-b"),
        "prompt_version": lambda m: m.update(prompt_version="v8"),
        "temperature": lambda m: m["sampling"].update(temperature=0.7),
        "max_retries": lambda m: m["retry_policy"].update(max_retries=4),
        "max_steps": lambda m: m["budgets"].update(max_steps=21),
        "max_calls": lambda m: m["budgets"].update(max_calls=51),
        "max_seconds": lambda m: m["budgets"].update(max_seconds=121),
        "window": lambda m: m["context_policy"].update(window=4000),
    }
    for label, edit in edits.items():
        m = _manifest()
        edit(m)
        assert f(m) != base, (
            f"changing {label} did not change the fingerprint. A reliability number measured "
            f"under a different {label} is about a different system; hash the whole manifest, "
            f"not a chosen subset."
        )


def _h6(f):
    """adding a verification step or a new field changes it"""
    base = f(_manifest())
    more_checks = _manifest()
    more_checks["verifications"].append("human-approval")
    assert f(more_checks) != base, "an added verification step is a different harness"
    extra = _manifest()
    extra["rate_limit"] = {"per_minute": 30}
    assert f(extra) != base, "a field the hash did not know about must still change it"


def _h7(f):
    """values that are not plain data raise TypeError"""
    for label, bad in (("a function", lambda: None), ("a set", {"search", "lookup"})):
        m = _manifest()
        m["tools"] = bad
        try:
            got = f(m)
        except TypeError:
            continue
        except NotImplementedError:
            raise
        except Exception as e:
            raise AssertionError(f"{label} should raise TypeError, got {type(e).__name__}: {e}")
        raise AssertionError(
            f"a manifest holding {label} produced {got!r}. Falling back to str() embeds a "
            f"memory address, so the fingerprint changes every run; refuse instead."
        )


def _h8(f):
    """hashing does not modify the manifest"""
    import copy

    m = _manifest()
    before = copy.deepcopy(m)
    f(m)
    assert m == before and list(m) == list(before), (
        "the fingerprint call changed the manifest it was given (contents or key order); "
        "canonicalise a copy"
    )


def _h9(f):
    """values JSON would silently convert are refused"""
    for label, mutate in (
        ("a tuple", lambda m: m.update(tools=("search", "lookup"))),
        ("an int key", lambda m: m["budgets"].update({1: "x"})),
        ("NaN", lambda m: m["retry_policy"].update(base_delay=float("nan"))),
    ):
        m = _manifest()
        mutate(m)
        try:
            got = f(m)
        except (TypeError, ValueError):
            continue
        except NotImplementedError:
            raise
        raise AssertionError(
            f"a manifest holding {label} produced {got!r}. json.dumps turns tuples into "
            "lists and int keys into strings, so {1: 'x'} and {'1': 'x'} would share a "
            "fingerprint -- the one thing a fingerprint must never do. NaN isn't valid JSON "
            "at all. Check for these and raise TypeError (or ValueError for NaN)."
        )


task(
    "ch04-harness-fingerprint",
    _ref_fingerprint,
    [_h1, _h2, _h3, _h4, _h5, _h6, _h7, _h8, _h9],
)
