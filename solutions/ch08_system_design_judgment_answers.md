# Chapter 8: System Design and Engineering Judgment — Model Answers

Open this file only after you've attempted `curriculum/08_system_design_judgment.ipynb`'s
three design-doc studios and interview drill from memory.

---

## Studio 1: a support-ticket triage agent

**0. Does this actually need an agent?** Yes, conditionally. Answering simple FAQ-style
questions is closer to a single retrieval+generation call than an agent (Chapter 1's
distinction) — but deciding *which* tool to invoke (look something up vs. issue a refund),
handling a multi-turn back-and-forth with a customer, and enforcing a policy limit before
acting is genuine multi-step, tool-using decision-making. Worth explicitly separating: the
FAQ-answering half could ship as a simpler single-call system; the refund-issuing half is
what actually justifies an agent.

**1. Success and failure cost.** Success: correctly answered FAQs, refunds issued only when
policy-eligible and only up to the real order total. Failure cost is asymmetric and high on
one side: an incorrectly issued or inflated refund is real money out the door and hard to
claw back, while a missed FAQ answer just routes to a human — this asymmetry should drive
where the reliability investment goes.

**2. Control flow.** A single ReAct-style agent with tool access (Chapter 2) is enough — no
need for a multi-agent team here, since there's one clear decision-maker and no benefit to
splitting the task across specialized roles the way Jack/Bob/Mike's setup does for genuinely
parallel or adversarial-review work.

**3. Retrieval/grounding.** Yes — the FAQ-answering half needs RAG (Chapter 3) against the
company's real help-center corpus, with citations so a wrong answer is at least traceable.

**4. Reliability story.** Chapter 4's full toolkit applies: cache FAQ lookups (with
invalidation on doc updates, so Chapter 4's stale-cache lesson doesn't repeat here), retry
transient failures in whatever backend the tools call, and — this is the one worth defending
explicitly against "isn't this overkill" — a circuit breaker isn't really about the refund
tool itself; it's about not hammering a struggling downstream payment system during an
incident, protecting a dependency the whole company relies on, not just this one feature.

**5. Cost/latency budget.** Moderate — a support interaction can tolerate a few seconds, so
this is a case for cost-optimized model routing (Chapter 5): a fast/cheap model for FAQ
lookups, escalating to a stronger model only for ambiguous refund-eligibility judgment calls.

**6. Security surface.** This *is* Chapter 6's exact scenario — untrusted ticket content is
the primary attack surface, so instruction/data separation, a narrowly-scoped `issue_refund`
tool (never a general-purpose database tool), and an independent policy check on every refund
amount regardless of how the tool call was decided are all required, not optional hardening.

**7. Tools and failure modes.** `search_knowledge_base`, `issue_refund`, `send_email` — and
per Chapter 7's taxonomy, the refund tool specifically needs semantic validation (does the
order ID in the response match what was requested) on top of schema validation, since a
wrong-but-valid-looking refund target is the most damaging failure mode this system has.

**8. Evaluation plan.** Offline: precision/recall against a held-out set of tickets with known
correct actions (Chapter 3's metrics, applied to actions instead of retrieved documents).
Online: refund-amount distribution monitoring (a Chapter 5-style request log, but for refund
amounts) to catch drift or abuse patterns before they compound, plus human spot-review of a
sample of auto-approved refunds.

**Why "isn't this overkill" is worth pushing back on directly:** each layer answers a
*different* question — retries handle "the call failed," circuit breakers handle "the
dependency is down," the policy check handles "the amount is wrong regardless of why." None
of the three substitutes for either of the others, which is the actual argument for having
all three, not "more defense is always better."

---

## Studio 2: a codebase-aware pull-request review assistant

**0. Does this actually need an agent?** Marginal, and worth saying so directly in an
interview rather than assuming yes. Drafting comments from a diff could be a single call
(diff in, comments out) if the task doesn't require the model to decide *what to look at
next* — but a stronger version (checking whether a flagged concern is already addressed
elsewhere in the codebase, or verifying a claimed missing test doesn't already exist under a
different name) genuinely needs tool use and multi-step investigation, which tips it into
agent territory.

**1. Success and failure cost.** Success: comments a human reviewer finds genuinely useful
and acts on. Failure cost is low and recoverable — a human reviews every comment before it's
posted, so a wrong or unhelpful comment costs reviewer time, not a shipped bug. This low
failure cost is what justifies a lighter reliability/security investment than Studio 1.

**2. Control flow.** A single agent with read-only tool access (search the codebase, run the
test suite, look at file history) — again, no need for a multi-agent team; there's no
adversarial or parallel structure here that would benefit from splitting roles.

**3. Retrieval/grounding.** Yes, but structurally different from Studio 1's document RAG —
this is retrieval over the *codebase itself* (related files, existing tests, past PRs
touching the same code), closer to code search than document QA.

**4. Reliability story.** Lighter than Studio 1's, proportional to the lower failure cost —
retries for transient tool failures, but no circuit breaker or policy-gate infrastructure is
justified here; that would be over-engineering relative to what's actually at stake.

**5. Cost/latency budget.** Can tolerate real latency (tens of seconds to a couple minutes) —
PR review isn't a real-time interaction, so this is a case where a stronger, slower model is
often the right default rather than the cost-optimized routing Studio 1 needed.

**6. Security surface.** Lower stakes than Studio 1 (no money moving, no destructive tools),
but the diff/codebase content is still untrusted input to the model in the same structural
sense as Chapter 6's tickets — a comment embedded in a PR description or a code comment
shouldn't be able to make the agent take an action outside "post a review comment."

**7. Tools and failure modes.** Codebase search, test-runner, git-history lookup — a stale
codebase index (Chapter 4's freshness lesson again, different context) is the most likely
real failure mode: a comment about "this function doesn't exist" that's wrong because the
index is out of date is worse than no comment at all.

**8. Evaluation plan.** Track the human-acceptance rate of suggested comments over time as
the primary signal — a comment a reviewer immediately dismisses is a direct, cheap,
continuously-available quality signal this system gets almost for free, unlike Studio 1
where good signal requires deliberate instrumentation.

---

## Studio 3: a research assistant over a large internal document set

**0. Does this actually need an agent?** Likely yes, but the more interesting design question
is *how much* agent — a single retrieve-then-generate call (Chapter 3's basic RAG pipeline)
may suffice for straightforward lookups; multi-step agentic behavior (reformulating a query
after a poor first retrieval, cross-referencing multiple documents) helps most on genuinely
hard, multi-hop legal questions specifically.

**1. Success and failure cost.** Explicitly the highest-stakes studio of the three: the
premise states the team "will lose trust immediately" if the tool ever states something
confidently that isn't grounded. Success isn't just "a correct answer" — it's "an answer that
is provably grounded in a cited source," which is a stricter bar than raw correctness.

**2. Control flow.** A ReAct-style agent that can iteratively refine its retrieval (try a
query, evaluate whether the results actually answer the question, reformulate if not) rather
than a single-shot retrieve-and-answer — the stakes justify the extra latency this costs.

**3. Retrieval/grounding.** The central requirement of this entire studio, not just one
question among nine — this needs Chapter 3's full toolkit: chunking strategy appropriate to
legal documents (likely section-boundary-aware, not fixed-size, given how contract clauses
are structured), a real evaluation harness (precision/recall/MRR against a held-out set of
legal QA pairs), and Chapter 3's faithfulness scoring specifically, since "faithful to the
retrieved source" is this studio's actual success criterion, not just "retrieved something
relevant."

**4. Reliability story.** Document freshness matters a lot here — a stale index serving an
outdated version of a policy document is a Chapter 4-style staleness bug with legal
consequences, not just an inconvenience, so cache invalidation on document updates needs to
be treated as a correctness requirement, not a performance nice-to-have.

**5. Cost/latency budget.** Can tolerate meaningfully higher latency than either other studio
— a legal team asking a substantive question is not expecting sub-second response, and
correctness matters far more than speed here, arguing for the strongest available model
rather than cost-optimized routing.

**6. Security surface.** Access control is the dominant concern, more than injection — if
the document corpus contains documents of varying sensitivity/confidentiality, the retrieval
layer needs to respect the *asking user's* actual permissions, not just what's technically
indexed; this is a different security question than Chapter 6's injection focus, worth
naming explicitly as a *different* risk than "someone tricks the agent."

**7. Tools and failure modes.** Primarily one tool (retrieval against the document index),
but the interesting failure mode is Chapter 7's "semantically wrong" category specifically:
a retrieval that returns documents that are topically related but not actually the governing
document for the question asked — schema-valid, plausible-looking, and wrong, exactly the
failure type generic error handling can't catch.

**8. Evaluation plan.** The most rigorous of the three studios, matching the stakes:
faithfulness scoring (Chapter 3) on every response as a standing metric, not just at build
time; a held-out set of legal questions with known correct source documents, re-run
periodically as the corpus changes; and human legal review of a sample of production answers
as an ongoing check, not a one-time launch gate.

---

## Interview drill

### 1. "Just add an agent" to a deterministic pipeline

Push back, but with a specific question rather than a flat no: *what part of this pipeline
currently requires a human to make a judgment call the code can't make on its own?* If the
answer is "none — it's fully deterministic and works," an agent adds nondeterminism, cost,
and (per Chapter 6) a real security surface to a system that had neither, for no offsetting
benefit — this is exactly the "does this need an agent" gate from question 0, applied
directly. What would change the answer to yes: a genuine new requirement that needs judgment
under uncertainty the existing rules can't express — e.g., the pipeline needs to handle
inputs varied enough that hardcoded branches are becoming unmaintainable, or a step now needs
to weigh several plausible interpretations rather than match a fixed pattern. The tell worth
naming for an interviewer: agreeing immediately, without asking what's actually driving the
request, is the same "skip straight to architecture" mistake this chapter opened with.

### 2. Justifying multiple reliability/security layers without "piling on techniques"

Answer each layer's *distinct* question, not its general virtue: retries answer "the call
failed, is it worth trying again" (transient); the circuit breaker answers "is the whole
dependency down right now, in which case retrying is actively harmful" (sustained outage);
the policy check answers "regardless of how the tool call was decided, is the amount
actually valid" (a check on the *result*, independent of how it was produced). The concrete
tell that distinguishes justified layering from technique-stacking: for each layer, can you
describe a concrete failure it catches that the *other* layers wouldn't? If two layers catch
the exact same failure, one of them is redundant and should be cut; if each catches something
the others miss, that's the actual argument for defense in depth (Chapter 6), not "more
safety nets are always good."

### 3. Cold: "design an agent that restarts failed cloud services automatically"

First three moves, in order, before any architecture: **(1)** Establish failure cost and
blast radius first — "automatically restart" on a stateless, horizontally-scaled service is
low-risk; the same action on a stateful service (a database, a service mid-transaction) can
cause data loss or a cascading outage, and the right design differs enormously between these,
so this has to be pinned down before anything else. **(2)** Ask what "failed" actually means
and how confidently it can be detected — a false positive that restarts a healthy service
under load is its own outage; this is a request for the actual failure-detection signal, not
an assumption that "the monitoring system will just tell us." **(3)** Ask about the current
human-in-the-loop process this is meant to replace or augment — is this fully autonomous from
day one, or does it start by proposing a restart to an on-call engineer and only automate
further once the failure-detection signal has demonstrated it's reliable? Only after those
three are answered does control flow, tooling, or reliability architecture become worth
discussing — proposing an architecture before establishing these is the same premature-jump
mistake this chapter's framework exists to prevent.

### 4. Listing techniques vs. demonstrating judgment

A **listing** answer names Chapters 1-7's techniques in response to a prompt without
connecting each one to a specific requirement of *this* scenario — "I'd use RAG, add
retries, use least-privilege tools" as a checklist recited regardless of what the scenario
actually needs. A **judgment** answer ties each choice to a reason specific to the scenario
in front of them, and — critically — is willing to say a technique from an earlier chapter
*doesn't* apply here and explain why not (e.g., "I wouldn't add a circuit breaker here because
there's no sustained-outage-prone dependency in this design, just occasional transient
calls"). What to listen for as an interviewer: ask "why *this* control flow and not a
simpler one" or "what would make you cut one of these layers" — a candidate reciting a
checklist will struggle to answer either, while a candidate with real judgment will have a
specific, scenario-grounded reason ready, the same way this file's studio answers tie every
choice back to something particular about that studio's stakes, not a generic best-practices
list.
