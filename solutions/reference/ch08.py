"""Chapter 8 reference answers — System Design and Engineering Judgment.

Both tasks here are structural rather than functional: there is no single correct design doc,
so the grader checks that every question was actually answered at a depth that would survive
a follow-up, not that it matches some hidden model answer. The prose below is one worked
studio, kept deliberately plain.
"""

from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass
class DesignDoc:
    scenario: str
    needs_an_agent: str = ""
    success_and_failure_cost: str = ""
    control_flow: str = ""
    retrieval_and_grounding: str = ""
    reliability_story: str = ""
    cost_latency_budget: str = ""
    security_surface: str = ""
    tools_and_failure_modes: str = ""
    evaluation_plan: str = ""

    def blank_fields(self) -> list[str]:
        return [
            f.name
            for f in fields(self)
            if f.name != "scenario" and not getattr(self, f.name)
        ]


DESIGN_DOC = DesignDoc(
    scenario=(
        "Studio 1: a support-ticket triage agent for a mid-size e-commerce company. It reads "
        "an inbound ticket, answers from the help centre where it can, looks up order state, "
        "and issues refunds under a policy cap, escalating anything else to a human."
    ),
    needs_an_agent=(
        "Yes, but only just, and the boundary is worth stating precisely. The multi-step "
        "decision is real: whether a ticket needs a knowledge-base lookup, an order lookup, "
        "both, or neither is not knowable until the first result comes back, which is the "
        "definition of judgment under uncertainty across steps rather than a fixed sequence. "
        "If the scope were narrowed to 'answer help-centre questions' alone it would be a "
        "single classified LLM call with retrieval and no loop, and I would build that "
        "instead. The refund path is what pulls it over the line into agent territory."
    ),
    success_and_failure_cost=(
        "Success is a correctly resolved ticket without human involvement, measured as "
        "deflection rate against a human-audited sample. Failure is asymmetric and that "
        "asymmetry drives the whole design. A wrong help-centre answer costs a follow-up "
        "ticket and some goodwill. A wrong refund moves money out of the business "
        "irreversibly, and a leaked order record is a data-protection incident. So the "
        "target is high deflection on the informational path and near-zero tolerance on the "
        "financial one, which argues for a hard policy gate rather than a better prompt."
    ),
    control_flow=(
        "A single agent with a small ReAct loop, capped at four iterations, and no subagents. "
        "The task decomposes into at most two lookups, so the coordination overhead of a "
        "planner-dispatcher-critic team buys nothing and costs a round trip per hop plus the "
        "context to carry between them (Chapter 2). A duplicate-observation guard escalates "
        "to a human when the same observation fires twice consecutively, which is the "
        "realistic stuck case here: an order id that does not resolve."
    ),
    retrieval_and_grounding=(
        "TF-IDF over the help-centre corpus, not embeddings. The corpus is a few hundred "
        "short articles with heavy jargon overlap between them, which is where lexical "
        "matching holds up well and where a general-purpose embedding model tends to collapse "
        "near-duplicates. Answers cite the article id they came from, so a wrong answer is "
        "traceable to a wrong retrieval rather than being indistinguishable from a "
        "hallucination. Order state is a direct database read, never retrieval."
    ),
    reliability_story=(
        "Retry with exponential backoff on transport failures and 5xx, and on 429 and 408; "
        "no retry on the rest of the 4xx range, since a malformed request is exactly as "
        "malformed on the sixth attempt. A circuit breaker in front of the order database "
        "fails fast after three consecutive failures and half-opens after thirty seconds. "
        "The degraded mode is explicit: if the order service is down, the agent answers "
        "informational tickets and queues everything financial for a human."
    ),
    cost_latency_budget=(
        "Target under 8 seconds end to end at p95, which is generous because this is an "
        "asynchronous email queue rather than a live chat. Budget is roughly $0.02 per "
        "ticket at 5,000 tickets a day, so about $100 a day. The help-centre system prompt "
        "is 2,000 tokens and identical on every call, so prompt caching takes most of the "
        "input cost out. Routing sends the informational path to the cheap tier and anything "
        "touching a refund to the strong tier."
    ),
    security_surface=(
        "Ticket text is untrusted input and is treated as data, never as instructions. A "
        "sanitizer strips the obvious directive shapes, and it is assumed to be incomplete, "
        "because a blocklist cannot enumerate plain English. The load-bearing control is a "
        "policy check on the refund tool call itself: the amount is validated against the "
        "order book, never against anything in the ticket. The tool surface is narrow by "
        "construction, so there is no general-purpose database tool for an injection to reach."
    ),
    tools_and_failure_modes=(
        "Three tools: search_knowledge_base, get_order_status, and issue_refund behind the "
        "policy check. Every tool response is schema-validated on the way back, and a "
        "validation failure is returned as an error rather than as a None the happy path can "
        "mistake for an empty result. The four failure shapes are handled separately: "
        "transient gets a retry, malformed gets a fresh source, a missing field means the "
        "upstream contract moved and needs a developer, and semantically wrong data goes to "
        "a human because no retry will ever change it."
    ),
    evaluation_plan=(
        "Offline: a golden set of 200 historical tickets with human-labelled correct "
        "outcomes, scored on resolution accuracy and on refund-decision accuracy separately, "
        "since the second one carries all the risk. Online: deflection rate, escalation rate, "
        "and reopen rate within 48 hours, which is the metric that catches a confidently "
        "wrong answer that offline scoring approved. Prompt changes ship behind a canary at "
        "5 percent with an automatic rollback on a 5-point move in escalation rate."
    ),
)


NO_AGENT_CASE = (
    "The strongest reason not to reach for an agent is that the task turns out to be "
    "deterministic. If the decision the agent would supposedly make is really an if/elif "
    "chain over a handful of well-understood cases, plain code is faster, cheaper, and "
    "testable, and it does not drag in a nondeterministic component or the entire prompt "
    "injection threat model along with it. I would write the rules and keep the whole "
    "security surface out of the system.\n"
    "\n"
    "The second is that a single LLM call already solves it. Summarization, classification, "
    "extraction and rewriting are usually genuinely one-shot: there is no loop, no tool use, "
    "and nothing to decide after the first result comes back. An agent loop wrapped around a "
    "single-shot task adds latency and failure modes and buys nothing at all, so I would ship "
    "one call with a good prompt and an output schema.\n"
    "\n"
    "A third that matters more than it gets credit for is evaluability. If I cannot define "
    "what a correct outcome looks like well enough to measure it, I cannot tell whether the "
    "agent is working, and I cannot safely iterate on it in production either. That is a "
    "design smell independent of whether an agent could technically do the task, and I would "
    "spend the time building the evaluation before building anything else.\n"
    "\n"
    "Latency is the fourth. If the budget is tens of milliseconds, no amount of model routing "
    "or caching closes the gap to even a single round trip, let alone a multi-step loop."
)
