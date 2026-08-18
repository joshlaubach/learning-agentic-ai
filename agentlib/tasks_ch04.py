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


task(
    "ch04-backoff",
    _ref_backoff,
    [_b1, _b2, _b3, _b4, _b5, _b6, _b7, _b8, _b9, _b10, _b11],
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
