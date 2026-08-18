"""Chapter 4 reference answers — Production Reliability.

Caching with staleness, retry with exponential backoff, the retryable/non-retryable split,
and a circuit breaker.
"""

from __future__ import annotations

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
