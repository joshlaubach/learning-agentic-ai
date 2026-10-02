"""Chapter 4 reference answers — Production Reliability.

Caching with staleness, retry with exponential backoff, the retryable/non-retryable split,
and a circuit breaker; then the multi-step half: the pass^k estimator, a fail-closed gate
chain, a verifier-driven refine loop, and a harness fingerprint.
"""

from __future__ import annotations

import hashlib
import json
import math
import random


class TTLCache:
    """A cache whose entries go stale on a clock, checked when you read them."""

    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self.store = {}  # key -> (value, cached_at)

    def get(self, key, now: float):
        """Returns (value, cached_at) on a live hit, or (None, None) on a miss/expiry."""
        if key in self.store:
            value, cached_at = self.store[key]
            if now - cached_at < self.ttl:
                return value, cached_at
        return None, None

    def set(self, key, value, now: float):
        self.store[key] = (value, now)

    def invalidate(self, key):
        self.store.pop(key, None)


def should_retry(error: Exception) -> bool:
    """Is retrying this error worth anything, or will it fail identically every time?

    Retry transport-level failures and the server-side statuses that mean "try again":
    429, 408, and 5xx. Refuse to retry the 4xx statuses that describe a broken request --
    a malformed body or a bad key is exactly as broken on the fourth attempt as the first,
    and retrying it just multiplies the latency before the user sees the error.

    An error carrying no status at all is treated as transient.
    """
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    status = getattr(error, "status_code", None)
    if status is None:
        return True
    if status in (408, 429):
        return True
    return not 400 <= status < 500


def retry_with_backoff(
    fn,
    max_retries: int = 6,
    base_delay: float = 1.0,
    jitter: float = 0.5,
    seed: int = 1,
    sleep_fn=None,
    retry_predicate=None,
):
    """Reusable exponential backoff + jitter wrapper. sleep_fn defaults to None, which logs
    the delay each attempt WOULD have taken without actually sleeping (keeps this notebook
    fast); pass sleep_fn=time.sleep for real behavior against a real dependency."""
    rng = random.Random(seed)

    def wrapped(*args, **kwargs):
        attempts_log = []
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                return fn(*args, **kwargs), attempts_log
            except Exception as exc:
                last_exc = exc
                if retry_predicate is not None and not retry_predicate(exc):
                    raise
                if attempt == max_retries:
                    break  # sleeping before giving up only delays the error
                delay = base_delay * (2 ** (attempt - 1)) + rng.uniform(0, jitter)
                attempts_log.append(
                    {"attempt": attempt, "error": str(exc), "backoff_s": round(delay, 2)}
                )
                if sleep_fn is not None:
                    sleep_fn(delay)
        raise RuntimeError(f"gave up after {max_retries} attempts") from last_exc

    return wrapped


class CircuitBreaker:
    """States: closed (normal) -> open (failing fast, not calling the dependency at all)
    -> half-open (after a cooldown, allow one trial call through) -> closed on success,
    back to open on failure."""

    def __init__(self, failure_threshold: int = 3, cooldown: float = 5):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.failure_count = 0
        self.state = "closed"
        self.opened_at = None

    def call(self, fn, now: float):
        if self.state == "open":
            if now - self.opened_at >= self.cooldown:
                self.state = "half-open"
            else:
                raise RuntimeError("circuit open -- failing fast (dependency not called)")

        try:
            result = fn()
        except Exception:
            self.failure_count += 1
            if self.state == "half-open" or self.failure_count >= self.failure_threshold:
                self.state = "open"
                self.opened_at = now
            raise
        else:
            self.failure_count = 0
            self.state = "closed"
            return result


# --- Multi-step reliability ---------------------------------------------------------------


def pass_hat_k(results: dict, k: int) -> float:
    """Unbiased pass^k (tau-bench): the chance that k trials drawn from the n you ran ALL
    succeed, averaged over tasks. Per task that is C(c, k) / C(n, k) with c successes in n."""
    if not results:
        raise ValueError("results is empty")
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    total = 0.0
    for task, trials in results.items():
        n, c = len(trials), sum(trials)
        if n < k:
            raise ValueError(f"task {task!r} has {n} trials, fewer than k={k}")
        total += math.comb(c, k) / math.comb(n, k)
    return total / len(results)


def run_gated(action, gates, *args, **kwargs) -> dict:
    """Run `action` only if every gate passes. Gates run cheapest first and stop at the first
    denial. Fail closed: anything but a (True, reason) pair denies, and so does a gate that
    raises or an empty gate list."""
    trail: list[dict] = []
    if not gates:
        return {"executed": False, "result": None, "denied_by": "no-gates", "trail": trail}
    for name, _cost, gate in sorted(gates, key=lambda g: g[1]):  # sorted() is stable
        try:
            outcome = gate(*args, **kwargs)
        except Exception as exc:
            passed, reason = False, f"{type(exc).__name__}: {exc}"
        else:
            if isinstance(outcome, tuple) and len(outcome) == 2:
                passed, reason = outcome[0] is True, outcome[1]
            else:
                passed, reason = False, f"malformed gate result: {outcome!r}"
        trail.append({"gate": name, "passed": passed, "reason": reason})
        if not passed:
            return {"executed": False, "result": None, "denied_by": name, "trail": trail}
    # Outside the try above on purpose: an action that fails is the caller's problem to see,
    # not a gate denial.
    result = action(*args, **kwargs)
    return {"executed": True, "result": result, "denied_by": None, "trail": trail}


def refine(generate, critique, verify, max_rounds: int = 3) -> dict:
    """Generate -> verify -> (critique -> regenerate). Acceptance belongs to the external
    `verify`, never to the model's own critique, which only feeds the next draft."""
    if max_rounds < 1:
        raise ValueError(f"max_rounds must be at least 1, got {max_rounds}")
    trace: list[dict] = []
    feedback = None
    previous = None
    for round_no in range(1, max_rounds + 1):
        draft = generate(feedback)
        if previous is not None and draft == previous:
            # The same draft already failed verification; running it again cannot help.
            trace.append({"round": round_no, "draft": draft, "verified": False,
                          "reason": "unchanged from the previous draft", "critique": None})
            return {"draft": draft, "verified": False, "rounds": round_no,
                    "stop": "stalled", "trace": trace}
        ok, reason = verify(draft)
        entry = {"round": round_no, "draft": draft, "verified": bool(ok),
                 "reason": reason, "critique": None}
        trace.append(entry)
        if ok:
            return {"draft": draft, "verified": True, "rounds": round_no,
                    "stop": "verified", "trace": trace}
        if round_no == max_rounds:
            break  # budget spent: a critique now would be a wasted call
        entry["critique"] = critique(draft)
        feedback = f"verifier: {reason}\ncritique: {entry['critique']}"
        previous = draft
    return {"draft": draft, "verified": False, "rounds": max_rounds,
            "stop": "budget", "trace": trace}


def _reject_lossy(value) -> None:
    """json.dumps quietly turns tuples into lists and int keys into strings, so two different
    manifests would share a fingerprint. Refuse anything it would convert."""
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError(f"manifest keys must be strings; got {k!r}")
            _reject_lossy(v)
    elif isinstance(value, list):
        for v in value:
            _reject_lossy(v)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        raise TypeError(f"{type(value).__name__} is not plain JSON data: {value!r}")


def fingerprint(manifest: dict) -> str:
    """12 hex chars of sha256 over canonical JSON: key order is ignored at every depth, list
    order is not, and anything that is not plain JSON data raises TypeError."""
    _reject_lossy(manifest)
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
