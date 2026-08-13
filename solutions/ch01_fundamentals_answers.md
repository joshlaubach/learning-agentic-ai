# Chapter 1: Fundamentals of AI Agents — Model Answers

Open this file only after you've attempted `curriculum/01_fundamentals.ipynb`'s cold-answer
questions from memory. These are full model answers, not just talking points — read them as
"here's a strong answer," not "here's the only correct answer."

---

## 1. Your AI agent keeps looping forever. How would you detect and stop it?

Start with what "looping" actually means, because there isn't just one failure shape:

- **Straight-line repetition** — the same action, the same observation, over and over. This
  is the case this chapter builds and fixes: hash each observation and compare it to the
  previous one (or a short recent window). If the same observation fires twice in a row with
  no change in state, stop and escalate instead of continuing. Cheap, deterministic, catches
  the common case.
- **A hard iteration cap** as a backstop — even with detection logic, cap the number of
  steps an agent can take on a single task. This is a blunt instrument (it doesn't diagnose
  *why* something looped), but it bounds the worst case: cost, latency, and blast radius all
  stay finite even if the smarter detection logic has a gap.
- **Cycles, not just loops** — Chapter 2 covers a harder variant: two agents (or two calls)
  that don't repeat an identical action, but keep deferring the same decision back and forth
  (A asks B to clarify, B asks A to clarify, forever). A duplicate-hash check on individual
  actions won't catch this, because no single action repeats — you need to look at whether
  *progress* is being made toward resolution, not just whether an action string repeats.
  Semantic similarity across the recent trace, or a "has the actual state of the task changed
  in N turns" check, catches this where hash-matching doesn't.
- **In production**, add: a wall-clock timeout per task independent of iteration count (a
  slow tool can loop "fast" on iteration count but slowly in real time), and logging/alerting
  on iteration count distributions so an unusual spike is visible before it's a cost problem,
  not after.

The one thing I'd flag as a red flag in an interview answer: relying on the model to
"just know" to stop. It won't reliably. The stop condition has to live in your code, not in
a prompt instruction hoping the model behaves.

## 2. A stakeholder says "we don't need an agent here, a simple script would do." When are they right?

Often. This is one of those questions where the strong answer pushes back on the premise of
"agents are the sophisticated choice" rather than defending agents by default.

They're right when:
- **The task is fully deterministic** — same input always maps to the same correct output via
  fixed logic. An agent adds latency, cost, and a new failure surface (hallucinated
  reasoning, non-determinism) for zero benefit over a script that already gets it right every
  time.
- **The decision space is small and enumerable** — if there are three possible branches and
  you can write the `if/elif/else` in twenty minutes, a rules engine is more debuggable,
  faster, cheaper, and doesn't require prompt engineering to keep working after a model
  upgrade changes its behavior slightly.
- **Latency or cost budgets don't tolerate an LLM call** — a sub-100ms API path has no room
  for a model call in the loop, agent or not.
- **The action is high-stakes and irreversible** — auto-approving a refund, sending an
  external email, executing a financial transaction. Even a well-behaved agent introduces a
  probability of a wrong call that a human-reviewed or rules-gated path doesn't.

They're *wrong* when the actual complaint is really "this feels like overkill" but the task
genuinely has: unpredictable inputs that don't map cleanly to fixed logic, a need to combine
several tools/sources dynamically based on what's found along the way, or open-ended
natural-language input where a fixed script would need to enumerate every phrasing in
advance. The tell, in an interview: can you actually write the deterministic version? If
you can sketch it in a few branches, you probably should.

## 3. Explain the difference between a chatbot, a workflow, and an agent to a non-technical colleague.

A **chatbot** is like a help-desk employee who only ever answers the question directly in
front of them, one at a time, and forgets everything the moment the conversation ends unless
you remind them.

A **workflow** is like someone following a fixed checklist: step 1, step 2, step 3, always in
that order, no matter what actually happens along the way. It's reliable when reality matches
the checklist, and it breaks the moment it doesn't — it has no way to notice something's gone
sideways and adapt.

An **agent** is like an employee you've given a goal and access to some tools, who decides
for themselves which tool to use, in what order, based on what they find as they go. That's
the whole difference: a chatbot decides what to *say*, a workflow's steps are decided by
*you* in advance, and an agent decides what to *do* next, dynamically, at each step.

The tradeoff worth naming out loud to a stakeholder: that flexibility is also where the risk
comes from. A workflow can't wander off-task. An agent can, if you don't build in the right
guardrails — which is most of what the rest of this course is about.

## 4. What's the difference between a model's context window and "memory" across a conversation?

The context window is a hard technical limit: the maximum number of tokens a model can
attend to in a single call, covering everything — system prompt, conversation history so far,
retrieved documents, tool outputs, and the model's own response as it's generated.

"Memory" across a conversation isn't a separate mechanism the model has — it's just whatever
part of the prior conversation you (the application) choose to re-send inside that context
window on the next call. If you don't thread the earlier turns back in, the model has no idea
they happened; there's no persistent state on the model's side between API calls. This
chapter's memory-on/memory-off demo makes this concrete: "memory off" isn't the model
forgetting — it's the application simply not including the earlier turn in the next prompt.

This distinction matters practically because context windows are finite and threading in
*everything* forever isn't free — it costs tokens (and money) on every single call, and past
a certain length can degrade the model's ability to attend to the most relevant parts. Real
systems manage this with summarization, truncation, or retrieval (pulling back only the
relevant slice of history) rather than naively appending the entire conversation forever.
Chapter 4 covers what happens when that context gets stale rather than just large.

## 5. Why can a RAG-grounded model still hallucinate?

Because retrieval only guarantees that *relevant source material was placed in front of the
model* — it does not guarantee the model actually uses it faithfully. Several concrete
failure modes, all real and all covered hands-on in Chapter 3:

- **The generator ignores the retrieved context anyway** and answers from what it learned
  during training instead — this happens even when retrieval worked perfectly, because
  nothing forces the model to prioritize the provided context over its parametric knowledge.
- **Retrieval itself fails** — the wrong document gets pulled (a near-duplicate, a stale
  version, an irrelevant match), and the model faithfully — and confidently — summarizes the
  wrong source.
- **The answer requires synthesizing across multiple chunks**, and naive top-k retrieval only
  surfaced one of them — the model fills the gap with a plausible-sounding guess instead of
  the missing fact.
- **The model over-generalizes from a partial match** — the retrieved passage is *related*
  but doesn't actually contain the specific fact being asked about, and the model blends what
  it found with what it assumes.

The honest, slightly uncomfortable framing for a non-technical stakeholder: RAG reduces the
*rate* of hallucination by giving the model something real to ground in, but it does not
change the fundamental fact that the model is still a next-token predictor with no built-in
mechanism that forces "only say things directly supported by the retrieved text." That
enforcement — faithfulness checking, citation requirements, abstention when confidence is
low — has to be built on top of retrieval, not assumed to come free with it.
