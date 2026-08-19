# Chapter 2: Agent Control Flow - Model Answers

Open this file only after you've attempted `curriculum/02_control_flow.ipynb`'s cold
diagnosis exercise and architectural tradeoff questions from memory.

---

## Cold diagnosis exercise

### 1. An agent keeps calling the same tool over and over, and every response looks identical.

Diagnosis: a loop. The observation is byte-identical every time, which is exactly what a
straight-line loop looks like, and it's this chapter's break-it #1 (the bait-tool scenario).
A duplicate-observation check (Chapter 1) or a max-iteration guard (this chapter) both catch
this, because the repeated signal is an exact match you can hash and compare directly.

### 2. Two agents keep sending each other slightly different messages, but neither ever makes progress.

Diagnosis: a cycle. The tell is "slightly different messages": if it were a loop, the
messages would repeat verbatim. A cycle involves paraphrasing or alternating speakers, so a
naive exact-match or hash-based duplicate check never fires, since nothing is ever identical
to what came immediately before it, even though the two parties are demonstrably stuck. This
needs a detector that tolerates near-duplicates, using string similarity or embedding
distance, comparing each party's messages to their own prior messages rather than just to the
immediately preceding line.

### 3. Adding a second reviewer step made latency worse, but the two reviewers always agree.

Diagnosis: an unnecessary or redundant hop. Nothing is stuck and nothing is malformed;
latency simply went up with zero corresponding change in outcome. The diagnostic signature is
specifically "always agree." If the two reviewers ever disagreed, the second one would be
adding real value by catching something the first missed, and this would be a legitimate
design choice rather than a bug. Fix it with a latency/value-add profiler, not a loop or
cycle guard; neither of those tools is the right instrument for this failure mode.

### 4. After adding a subagent, the orchestrator's context ballooned and its next decision got worse.

Diagnosis: a leaky subagent. The signature is a context-size spike correlated with a specific
architectural change (adding a subagent), plus a downstream quality regression: not a stuck
loop, not a stalled negotiation, just slower and worse. This is what happens when a subagent
returns its raw transcript instead of a compressed synthesis, violating the
context-isolation guarantee that's supposed to be the entire point of using a subagent in the
first place.

---

## Architectural tradeoff questions

### 5. When is adding more agents actually a bad architectural decision?

Most often: when the task doesn't actually decompose into independent, verifiable sub-steps.
If a single well-prompted agent with the right tools could do the whole thing in one pass,
splitting it into a planner/worker/critic pipeline adds latency and cost (this chapter's
cost/latency calculator makes that concrete: three times the hops is roughly three times the
tokens and latency, scaled by task complexity) for a benefit that only shows up if the extra
agents catch something a single agent would have missed.

Concretely, watch for the "reviewers always agree" pattern from this chapter's break-it #3,
where an extra hop that never changes the outcome is pure overhead. Watch also for tasks with
tight latency budgets, where every hop is a serialization point (unless you're using
fan-out) and multi-agent pipelines are usually slower wall-clock than a single well-designed
agent call, not faster. And watch for simple, well-specified tasks, where the ROI of a critic
step is highest when the worker's output space is large and error-prone, and near zero when
the worker's task is narrow and the tool it's calling is already reliable.

The honest framing for an interview: more agents is a reliability/quality investment, paid
for in latency and cost. It's worth it exactly when the quality gain is real and measurable,
not by default, and not because multi-agent architectures sound like the more sophisticated
answer.

### 6. What's the actual difference between a subagent and just calling another agent?

Context isolation, specifically, not just "there are two agents involved now." When Bob in
this chapter calls his subagent, the subagent starts from a completely fresh context that
contains only its bounded subtask, with zero visibility into Bob's own conversation history,
and it returns only a compressed synthesis, not its full reasoning trace, back into Bob's
context. Compare that to simply having two agents both operating on the same shared
conversation or context: that's still "multiple agents," but without the isolation boundary,
nothing stops one agent's intermediate noise from polluting the other's context (this
chapter's break-it #4 is exactly what happens when that boundary is skipped). The practical
test: if agent A's full internal reasoning trace ends up inside agent B's context by default,
A isn't functioning as a subagent to B, no matter what you call it.

### 7. When would you reach for fan-out instead of a persistent agent pool?

Fan-out, meaning dispatching multiple independent subagents in parallel for one task and then
collecting their results, is the right call when the work is genuinely parallelizable and
each piece is a one-off: research five different sources simultaneously, generate three
candidate drafts to pick the best of, validate a batch of independent items concurrently.
There's no need for any of those workers to persist state between tasks.

Persistent agent pools, meaning long-lived, stateful workers reused across many tasks, earn
their complexity when there's real value in not starting from scratch each time: a worker
that's built up useful context about an ongoing project, one that's expensive to initialize
(a large loaded index, an established session with an external system), or one you
specifically want to route related follow-up work back to for continuity. The cost is real:
persistent pools mean lifecycle management, spinning workers up, keeping them healthy, and
eventually retiring them, that a fan-out dispatch never has to think about, since fan-out
workers are disposable by design.

The one-line version for an interview: fan-out for parallel, disposable, independent work;
persistent pools when continuity or expensive setup makes starting fresh every time wasteful.
