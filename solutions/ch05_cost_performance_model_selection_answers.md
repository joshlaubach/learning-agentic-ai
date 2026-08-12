# Chapter 5: Cost, Performance, and Model Selection — Model Answers

Open this file only after you've attempted `curriculum/05_cost_performance_model_selection.ipynb`'s
interview drill from memory.

---

## 1. Cold diagnosis: per-request GPU cost doubled overnight, no model or traffic change

Start from the fact pattern itself: cost is what changed, not traffic volume, and no model
was redeployed. That rules out "we're just serving more requests" and "we swapped to a more
expensive model" as the explanation before you've looked at a single log line — so the cause
has to be something about what each individual request now costs.

Cost scales with tokens, so the next question is which side of the ledger moved:

- **Check input and output token counts per request, this chapter's `req-00100`-style step
  change.** If input tokens roughly doubled with no change in what users are actually asking,
  that's this chapter's break-it #1 signature almost exactly — a duplicate-call bug (a retry
  path that isn't idempotent, a webhook firing twice, a double-submit on the client). The fix
  is an idempotency check before execution, not after.
- **If token counts per request look normal but the number of *distinct* calls per user
  session went up,** suspect something upstream retrying or fanning out more than before —
  same root cause, different layer (session-level duplication instead of per-request
  duplication).
- **If input tokens are climbing steadily rather than doubling in a step change,** check
  whether this is a conversational agent and whether context is being truncated at all —
  that's break-it #2's unbounded-context-growth signature, and it degrades gradually rather
  than overnight, so "overnight" would be a point against this explanation unless something
  also changed the average conversation length overnight (e.g., a UX change that keeps
  sessions open longer).
- **Only after ruling out both of the above** would "the model routing logic broke and
  everything is silently going to the strong tier" be worth checking directly — comparing
  the model field in the logs before and after the change window.

The reason to check duplication before routing: a routing regression would show up as *"this
whole class of simple requests is now on the expensive model,"* a categorical shift, whereas
"cost doubled" with no accompanying quality/behavior complaint is much more consistent with
each request quietly costing 2x than with requests being routed somewhere different.

---

## 2. Cold diagnosis: p99 latency jumped from ~2s to ~12s

Use the four-stage decomposition before touching anything else: queueing, network,
inference (prefill), generation (decode). The first move is checking *which stage* grew,
because "add more GPUs" (a queueing fix) and "the model is slow" (an inference/generation
fix) require completely different actions, and guessing wrong wastes the exact window when
the problem is actively hurting users.

- **If `queue_time_ms`'s share of total latency jumped** (this chapter's break-it #3 —
  input/output tokens stay normal, `queue_depth` spikes) — that's a capacity/backpressure
  problem: too many concurrent requests for available capacity, most likely a burst (a batch
  job, a retry storm, a real traffic spike) rather than anything about any individual
  request. The fix is capacity and load-shedding (reject past a depth threshold so latency
  degrades predictably instead of catastrophically), not touching prompts or models.
- **If `inference_time_ms` or `generation_time_ms` grew instead, with token counts roughly
  normal,** suspect a model or infrastructure change — a slower model got deployed, GPU
  contention from a co-located workload, or a regression in the serving stack itself.
- **If input tokens per request grew a lot (break-it #2's signature) while stage *shares*
  stayed proportionally normal,** the "spike" is really "prefill/decode cost more because
  there's more to process," which is a context-growth problem wearing a latency costume —
  the fix is a context window policy, not more GPUs.

What you'd expect to see if the queueing hypothesis is right: a *disproportionate* jump in
`queue_time_ms`'s share of the total (this chapter's example: queueing goes from ~5% to
~75%+ of total latency) with `inference_time_ms`/`generation_time_ms` staying close to their
normal per-token rate. If instead every stage grew roughly proportionally, that points away
from queueing and toward something systemic (a slower network path, a degraded shared
resource) affecting the whole pipeline evenly.

---

## 3. Judgment call: fine-tuning to fix chatbot tone

Before agreeing fine-tuning is the right lever, the questions worth asking are really about
whether cheaper, faster, reversible options have actually been ruled out — fine-tuning is a
multi-hour-to-multi-day training run producing a new artifact to version and serve, so it
should be the fallback, not the first move:

- **Has this actually been tried with a better system prompt and a few tone examples
  (few-shot) first?** Tone is exactly the kind of thing prompting is usually good at fixing.
  If nobody's tried a tightened system prompt with explicit tone guidance and 3-5 examples of
  the desired voice, that's the first thing to do — it ships in minutes and is trivially
  reversible if it doesn't work.
- **Is this a consistent, high-volume, stable requirement, or is the desired tone still
  being figured out?** Fine-tuning locks in a behavior; if "what tone should this be" is
  still under active iteration internally, fine-tuning against a moving target means
  retraining every time the target shifts — a much better fit once the target has stabilized.
- **How is "wrong tone" being measured?** If there's no way to systematically evaluate
  whether an attempted fix (prompt or fine-tune) actually improved tone, fine-tuning would
  be flying blind in the same way prompting would — this is a prerequisite question
  regardless of which lever gets picked, not an argument specifically against fine-tuning.
- **Whose time and infrastructure does a fine-tune consume, and is that justified relative
  to the size of the tone problem?** A training run, a new model artifact to store and route
  to, and a new evaluation pass all cost more than a prompt change — worth naming explicitly
  as a cost/benefit question rather than assuming it away.

If the answer comes back "yes, we've tried prompting seriously, the desired behavior is
stable and high-volume, and we have a way to measure tone quality" — fine-tuning (likely
LoRA/QLoRA rather than a full fine-tune, given the far lower cost) becomes a reasonable next
step. Reaching for it before those are true is the reflexive-fine-tuning red flag interviewers
in this space are often specifically listening for.

---

## 4. Conceptual: where does RLHF show up for an agent engineer, if at all?

Directly, almost nowhere in day-to-day work — RLHF (and its successors like RLAIF /
constitutional AI) is part of how the underlying model was trained before an agent engineer
ever calls it; it's not a step in building or operating an agent system, and it's not
something most agent engineers run themselves.

Where it becomes conceptually relevant is the mechanic underneath it: RLHF's reward signal
is fundamentally *a judgment about response quality*, produced by having something (a human,
or in RLAIF's case, another model) score or compare outputs. That's the same underlying
pattern as Chapter 3's faithfulness scoring and LLM-as-judge evaluation — "have a model (or a
human) judge whether a response is good, and use that judgment as a signal." Chapter 3 uses
that judgment purely at inference/evaluation time to score a system's outputs, with no
weight updates involved; RLHF uses a structurally similar judgment as a training signal
inside the reward model that then updates the policy model's weights. Recognizing that
those are the same underlying idea applied at two different points (evaluating a deployed
system vs. training the base model) is a stronger answer than treating "fine-tuning/RLHF"
and "evals" as two unrelated topics on an interview's syllabus.
