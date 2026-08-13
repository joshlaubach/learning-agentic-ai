# Chapter 9: LLMOps and Deployment — Model Answers

Open this file only after you've attempted `curriculum/09_llmops_deployment.ipynb`'s
interview drill from memory.

---

## 1. Cold diagnosis: refusals climbed, no infrastructure alert fired

Start from the fact that "no infrastructure alert" is itself informative, not just an
absence of signal: the request succeeded, returned a normal-looking response, in normal
time — nothing about the *shape* of the interaction looked wrong to a system watching
latency, error rates, or uptime. That rules out an outage or a broken dependency and points
straight at a **behavioral** regression, this chapter's central distinction between
infrastructure health and output-quality health.

The investigation:

- **Confirm it first, quantitatively, don't just take the report at face value.** Pull the
  refusal rate over time, split by prompt version if that's tracked (this chapter's
  `PromptRegistry.history` is exactly the artifact that makes this possible) — a stakeholder
  impression can be right or it can be recency bias; the data settles it either way.
- **Correlate the refusal-rate change against the timeline of prompt/model changes**, not
  just "a week ago" from memory — this chapter's break-it #1 is exactly why an immutable,
  timestamped version history matters: without it, there's no reliable way to know what
  actually changed when, only guesses.
- **If a prompt change lines up with the timing, compare the old and new prompt text
  directly** for anything that would plausibly shift refusal behavior — an added caveat, a
  "when in doubt, decline" instruction, a tone change that reads as more conservative. This
  chapter's break-it #2 regression came from exactly this kind of wording change.
- **If no prompt change lines up, check for upstream model drift** — the underlying model
  behind a stable-sounding API name changed without anyone on this side making a change at
  all (see question 4's answer below).

Why infrastructure monitoring alone couldn't have caught this: a refusal is a **successful**
response by every infrastructure-level definition — it returned, it wasn't an error, it
didn't time out. The dashboards that catch outages are answering "is the system up," and
this system was up the entire time; "is the system's behavior still correct" is a completely
different question that needs its own metric, which is this chapter's actual point.

---

## 2. Design judgment: skip shadow deployment, go straight to a 5% canary

Push back when the change is the kind whose failure mode is **quiet** — a prompt rewrite, a
model swap, anything where a regression looks like a normal, well-formed response and would
only show up as a shift in an aggregate metric (refusal rate, average length, a quality
score) rather than an error. For exactly that kind of change, even 5% of real traffic is 5%
of real users getting a response that might be measurably worse, for the length of time it
takes the canary-monitoring window to notice — shadow deployment catches this *before* any
real user is exposed, at the cost of only comparing offline rather than on live traffic.

Agree it's fine to skip shadow and go straight to canary when the change is **structurally
safe or trivially reversible** — a well-tested formatting tweak, a typo fix, anything where
the failure mode (if any) would be immediately and unambiguously obvious rather than a subtle
metric shift, or where the team already has strong historical confidence in this exact class
of change from having shipped many similar ones safely before. The general principle worth
stating explicitly: shadow deployment is proportional to *how quiet a regression from this
change could plausibly be*, not a blanket step every change needs regardless of risk — the
same idea driving Chapter 8's "not every layer of defense is justified for every scenario."

---

## 3. Judgment call: picking a threshold with no historical data

Don't pick a round number and call it "conservative" — this chapter's break-it #2 is
precisely a threshold (`0.5`) that sounded conservative and was actually far too loose to
catch a real 32-point regression. A defensible process instead:

- **Establish the natural noise floor first.** Run the *same* prompt version against itself
  (or two random splits of the same stable traffic) and measure how much the metric normally
  varies from pure sampling noise at whatever traffic volume the canary stage will actually
  see. The threshold needs to sit meaningfully above this floor, or it'll trip on noise
  constantly and nobody will trust it.
- **Reason backward from what magnitude of change would actually matter to users or the
  business**, not forward from "what number sounds safe." A refusal-rate shift of 1-2 points
  might be within normal variation for some products and genuinely consequential for others
  — this is a product/domain judgment, not a purely statistical one, and needs input from
  whoever owns the actual user impact.
- **Pair the threshold with a minimum sample size**, not just a percentage — a 5% canary
  stage with only a handful of requests can show noisy swings on either side of any
  threshold; the check needs enough samples for the comparison to be statistically
  meaningful before it's trusted at all.
- **Treat the first threshold as provisional and revisit it once real historical data
  exists.** The honest answer to "how do you pick it with no data" is that you pick your
  best defensible estimate, instrument it well enough to tell if it's wrong, and tighten or
  loosen it once you've actually seen a few real rollouts — not that there's a clean formula
  that produces a permanently-correct number on day one.

---

## 4. Conceptual: silent upstream model drift

Every other failure mode in this chapter is something **your own system changed** — a prompt
edit, a rollout you initiated, a version you promoted — which means it's something your own
version history and rollback machinery can address directly: find the change, roll back to
the version before it. Silent upstream drift is categorically different: the provider updated
what's actually running behind a model identifier your system never touched, so there is no
corresponding entry in your own prompt/version history to roll back to, and `current_version`
in your own registry never moved at all. Your system did nothing wrong by its own records,
and yet its behavior shifted anyway.

What you can actually do about it, since you can't roll back a change you didn't make:

- **The same drift-detection machinery this chapter built for canary rollouts still applies**
  — running it continuously against production traffic (not just during a rollout) is what
  actually catches this, since the "change" here isn't tied to any deploy event on your side
  at all and could happen at any time.
- **Pin to explicit model versions/snapshots where the provider offers them**, rather than a
  stable "latest"-style alias, so a provider-side update requires an explicit opt-in on your
  side instead of arriving silently. This doesn't prevent drift entirely (a pinned version
  can still be deprecated eventually) but converts a silent change into a visible one.
- **Treat "which exact model version served this response" as something worth logging**,
  the same instinct as Chapter 4's context-freshness logging — without it, correlating a
  behavior shift with a provider-side change is guesswork after the fact instead of a direct
  lookup.

The honest limit to name explicitly in an interview: unlike every other failure mode in this
chapter, this one isn't fully preventable from your side — the best available response is
fast detection and a documented mitigation (pinning, monitoring), not a guarantee it can
never happen.
