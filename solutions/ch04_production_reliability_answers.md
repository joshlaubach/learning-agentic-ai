# Chapter 4: Production Reliability — Model Answers

Open this file only after you've attempted `curriculum/04_production_reliability.ipynb`'s
context-freshness debugging question and reliability-pattern recall drill from memory.

---

## Debug this from the actual logs

**"Users complain the AI coding assistant ignores recent code changes." Walk through how
you'd debug context freshness in production, using the `freshness_log` format this chapter
actually generated.**

Start with the log entries themselves, since that's the cheapest signal and doesn't require
reproducing anything: for the specific file/query users are complaining about, check
`context_age_seconds` on the responses being served. That single field splits the
investigation into two completely different bugs:

- **`context_age_seconds` is large (minutes/hours) and `source` is `"cache"`.** This is
  exactly this chapter's break-it #1 — a caching bug. The content being served is old
  because the cache is serving it past when it should have been invalidated. Next question:
  was the cache ever told the file changed at all (is there an invalidation event logged for
  that edit), or was it told and failed to act on it (a bug in the invalidation code path
  itself, not just a missing call to it)? Those are different fixes — the first is "wire up
  the missing invalidation trigger," the second is "the invalidation logic itself is
  wrong" — and the log alone won't tell you which, but it tells you *where* to look next.
- **`context_age_seconds` is small/zero and `source` is `"live fetch"`, but the content is
  still wrong or missing the recent change.** This is not a caching bug at all — the
  freshness log is telling you the system correctly went and fetched live content, and *that
  content itself* doesn't reflect the recent change. That points upstream: the ingestion/
  indexing pipeline hasn't picked up the edit yet (a sync delay, a failed webhook, a batch
  job that hasn't run), which is a different system and a different on-call than the one
  that owns the cache.

The reason this matters as an interview answer: "check the cache" is the generic-sounding
response; splitting on what the freshness log actually shows is what separates a real
debugging process from a guess. If you don't have `context_age_seconds` (or an equivalent)
logged at all, that's the first fix — this chapter's core claim is that staleness needs to be
made *detectable*, and without a field like this, you're debugging blind by definition,
regardless of which of the two bugs above it turns out to be.

---

## Reliability-pattern recall drill

### 1. A downstream service is fully down for the next 20 minutes during a deploy.

**Circuit breaker.** The dependency isn't flaky, it's known-down for a bounded window.
Retrying against it wastes time and adds load to a system that's already struggling through
a deploy — reach for retries here and you get calls that reliably fail after their full
backoff schedule plays out, over and over, for 20 minutes straight, for zero benefit. A
circuit breaker opens after the first few failures and stops trying, which is both faster to
fail and kinder to the deploying service.

### 2. A network call fails about 1 in 20 times with no discernible pattern.

**Retry (with backoff and jitter).** This is the textbook transient-failure case — no
sustained outage, just occasional noise. A circuit breaker here is actively counterproductive:
with a 5% failure rate, a breaker tuned to trip after a handful of consecutive failures might
never trip at all (good), but if tuned sensitively it can trip on ordinary bad luck and start
failing fast on a dependency that's actually fine — reach for the wrong tool here and you
either don't help (breaker too loose) or start rejecting perfectly good requests (breaker too
tight) for a problem retries would have quietly absorbed.

### 3. A document was updated five minutes ago, but an agent is still citing the old version.

**Cache invalidation.** Neither retry nor circuit breaker touches this at all — nothing here
is failing, an old-but-successful cache read is just being served past its useful life. This
is this chapter's break-it #1: the fix is invalidating on write (or shortening the TTL, which
only reduces the window rather than closing it) plus logging context age so this class of bug
is visible next time instead of surfacing as a confused user report five minutes after the
fact.

### 4. A downstream service returns errors for 30 seconds during a brief traffic spike, then fully recovers on its own.

**Retry, with a circuit breaker as a backstop if the spike is long/frequent enough to matter.**
This is genuinely transient — the dependency isn't down, it's temporarily overloaded and
self-recovers. A well-tuned retry with backoff rides this out. Where it gets more nuanced:
if these spikes happen often enough, a circuit breaker with a short cooldown is worth adding
on top, not instead of retry — it protects the dependency from every client's simultaneous
retry storm making the spike worse (the exact failure mode jitter and circuit breakers both
exist to prevent), while retry-with-backoff still handles genuinely isolated blips. Picking
retry-only here isn't wrong for an isolated spike; it becomes wrong at scale, when many
clients retrying in lockstep is itself what turns a 30-second blip into a longer outage.
