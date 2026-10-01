# Chapter 4: Production Reliability (Model Answers)

Open this file only after you've attempted `curriculum/04_production_reliability.ipynb`'s
context-freshness debugging question and reliability drill from memory.

---

## Debug this from the actual logs

> "Users complain the AI coding assistant ignores recent code changes." Walk through how
> you'd debug context freshness in production, using the `freshness_log` format this chapter
> actually generated.

Start with the log entries themselves, since that's the cheapest signal and doesn't require
reproducing anything: for the specific file/query users are complaining about, check
`context_age_seconds` on the responses being served. That single field splits the
investigation into two completely different bugs:

- If `context_age_seconds` is large (minutes or hours) and `source` is `"cache"`, that's
  exactly this chapter's break-it #1: a caching bug. The content being served is old
  because the cache is serving it past when it should have been invalidated. Next question:
  was the cache ever told the file changed at all (is there an invalidation event logged for
  that edit), or was it told and failed to act on it (a bug in the invalidation code path
  itself, not just a missing call to it)? Those are different fixes: the first is "wire up
  the missing invalidation trigger," the second is "the invalidation logic itself is
  wrong"; the log alone won't tell you which, but it tells you *where* to look next.
- If `context_age_seconds` is small or zero and `source` is `"live fetch"`, but the content
  is still wrong or missing the recent change, that's not a caching bug at all: the
  freshness log is telling you the system correctly went and fetched live content, and *that
  content itself* doesn't reflect the recent change. That points upstream: the ingestion/
  indexing pipeline hasn't picked up the edit yet (a sync delay, a failed webhook, a batch
  job that hasn't run), which is a different system and a different on-call than the one
  that owns the cache.

The reason this matters as an interview answer: "check the cache" is the generic-sounding
response; splitting on what the freshness log actually shows is what separates a real
debugging process from a guess. If you don't have `context_age_seconds` (or an equivalent)
logged at all, that's the first fix: this chapter's core claim is that staleness needs to be
made *detectable*, and without a field like this, you're debugging blind by definition,
regardless of which of the two bugs above it turns out to be.

---

## Reliability drill (1-4 single calls, 5-8 multi-step runs)

### 1. A downstream service is fully down for the next 20 minutes during a deploy.

Circuit breaker. The dependency isn't flaky, it's known-down for a bounded window.
Retrying against it wastes time and adds load to a system that's already struggling through
a deploy. Reach for retries here and you get calls that reliably fail after their full
backoff schedule plays out, over and over, for 20 minutes straight, for zero benefit. A
circuit breaker opens after the first few failures and stops trying, which is both faster to
fail and kinder to the deploying service.

### 2. A network call fails about 1 in 20 times with no discernible pattern.

Retry (with backoff and jitter). This is the textbook transient-failure case: no
sustained outage, just occasional noise. A circuit breaker here is actively counterproductive:
with a 5% failure rate, a breaker tuned to trip after a handful of consecutive failures might
never trip at all (good), but if tuned sensitively it can trip on ordinary bad luck and start
failing fast on a dependency that's actually fine. Reach for the wrong tool here and you
either don't help (breaker too loose) or start rejecting perfectly good requests (breaker too
tight) for a problem retries would have quietly absorbed.

### 3. A document was updated five minutes ago, but an agent is still citing the old version.

Cache invalidation. Neither retry nor circuit breaker touches this at all: nothing here
is failing, an old-but-successful cache read is just being served past its useful life. This
is this chapter's break-it #1: the fix is invalidating on write (or shortening the TTL, which
only reduces the window rather than closing it) plus logging context age so this class of bug
is visible next time instead of surfacing as a confused user report five minutes after the
fact.

### 4. A downstream service returns errors for 30 seconds during a brief traffic spike, then fully recovers on its own.

Retry, with a circuit breaker as a backstop if the spike is long or frequent enough to
matter. This is genuinely transient: the dependency isn't down, it's temporarily overloaded
and self-recovers. A well-tuned retry with backoff rides this out. Where it gets more
nuanced: if these spikes happen often enough, a circuit breaker with a short cooldown is
worth adding on top, not instead of retry. It protects the dependency from every client's
simultaneous retry storm making the spike worse (the exact failure mode jitter and circuit
breakers both exist to prevent), while retry-with-backoff still handles genuinely isolated
blips. Picking retry-only here isn't wrong for an isolated spike; it becomes wrong at scale,
when many clients retrying in lockstep is itself what turns a 30-second blip into a longer
outage.

### 5. A 20-step agent passes 95% of its individual steps in testing and the dashboard reports 95%. What fraction of full runs should you expect to succeed, and what would you report instead?

Roughly one run in three. If every step has to succeed, the run succeeds with probability 0.95^20, about 36%, so a dashboard of per-step accuracy flatters the agent badly. Report at the level a user experiences, which is the whole run. Run each task n times (n at least k) and report pass^k next to pass@1: pass@k asks "can it ever do this?" while pass^k asks "will it do this every time?", and it falls as k grows. Estimate it per task as C(c,k)/C(n,k) from c successes in n trials, and average over tasks; raising the mean success rate to the k-th power blurs easy and hard tasks together and overstates reliability. Count crashed trials as failures, reset state between trials so a warm cache cannot flatter the second one, and state n, k, the number of tasks, and the cost per success so the figure can be judged. If the number is too low, the levers are per-step reliability or fewer steps: to finish 90% of 20-step runs, each step needs about 99.5%.

### 6. An agent can issue refunds. Which checks do you put in front of the refund call, in what order, and what must each of them do when it fails or cannot answer?

Order the checks by cost and stop at the first rejection. Deterministic rules go first (the order exists, the amount is within what was paid, the caller is authorised), then tests or a dry run, then a consensus of independent verifiers if the stakes justify the model calls, and a person last, so people only see what survived everything cheaper. Every gate fails closed: a timeout, an exception, a None, or a bare truthy return is a denial and never a pass, and a chain with zero gates denies too, because "nothing objected" is not approval. The gates run before the action, and the action runs exactly once. If the refund call sits inside a retry wrapper, give it an idempotency key, otherwise a timeout after the refund went out repeats the refund. Then treat the gates as code that needs tests: run each one against known-good and known-bad cases and look at its false accepts, because a verifier that approves everything is a failure source dressed as a safeguard.

### 7. A colleague's refinement loop has the model draft an answer, critique it, and regenerate until the critique says there are no issues. Why is that not a reliability mechanism, and what do you change?

The stopping rule makes the model the only judge of its own work, which is where it is weakest. Models favour their own output, and studies of intrinsic self-correction found it often fails to improve reasoning answers and can overturn correct ones. A critic that approves everything ends the loop in round one with the first draft, so the success rate reads 100% while quality is unchanged. Keep the loop but move acceptance to a verifier outside the model: tests, a schema, business rules, or a person. Feed the verifier's reason into the next draft along with the critique, since the reason is ground truth about what failed. Bound it with a round budget, stop when the model returns the same draft twice, skip the critique for a draft that already passes and for the final round, and when the budget runs out return the last draft flagged as unverified instead of presenting it as a success. Then audit the verifier against drafts you know are good and bad.

### 8. Your agent's pass^8 fell from 0.70 to 0.55 after a release and nobody touched the prompt. How do you find out why, and what should every reliability report have disclosed to make this quick?

Diff the harness manifests of the two runs first; the fingerprints alone say whether they measured the same system. A manifest records the harness version, exact model id, prompt version, context policy, tools and their versions, retry policy, budgets, verifications, and sampling settings, so a moved model alias, a smaller step budget, a changed retry predicate, or a swapped tool shows up as one line in a diff instead of a hunt. If the manifests match, treat it as a real regression and walk the failure layers in order, stopping at the first one that explains the failing runs: specification, planning, context, tools, memory, coordination, verification. Look at verification twice, as a place failures start and as the gate everything passes through: a verifier that began approving more, or ending runs earlier, moves the number with no change to the agent at all. Check the noise as well. With few trials per task, pass^k swings between seeds, so confirm that the drop is larger than that spread before calling it a regression.
