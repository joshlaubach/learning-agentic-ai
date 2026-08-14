# Capstone: Ava, a Combined Agent Project

A portfolio piece, not a 10th chapter. `capstone_agent.ipynb` is one built, working agent,
not another concept→build→break-it→interview-drill notebook like the numbered chapters.
Its purpose is to demonstrate that the individual techniques Chapters 1-9 taught in isolation
actually compose into a single real system, using an actual agent framework instead of the
from-scratch loops the early chapters built by hand.

## What it does

Ava is a small research/support assistant with two tools and a memory of the conversation:

- Retrieval over Chapter 3's real SQuAD-based corpus, via the exact same `TfidfRetriever`
  class Chapter 3 built: reused, not re-implemented.
- Tool use against Chapter 7's real, schema-validated MCP server
  (`curriculum/_ch07_mcp_server.py`): a genuine stdio connection to that same server, calling
  its real `get_package_info` tool and validating the response with the same Pydantic
  `PackageInfo` model Chapter 7 used.
- Memory across turns, via LangGraph's checkpointer, proven concretely in the notebook (not
  just asserted): a second turn in the same conversation thread answers a question that is
  only answerable from real accumulated state, using nothing but the new message plus
  whatever the checkpointer already holds.
- A safeguard from Chapter 6: retrieved content is treated as untrusted data and sanitized
  (the same instruction/data-separation mechanism Chapter 6's ticket-triage agent used)
  before it re-enters the conversation. The notebook proves this is wired into the actual
  code path the graph executes, not just callable in isolation, by running a deliberately
  poisoned document through the real `tool_node` function and showing the injected directive
  never reaches the conversation.

## What it demonstrates

That the techniques from Chapters 1-9 aren't isolated exercises: retrieval evaluation
(Ch3), tool integration and schema validation (Ch7), and security safeguards (Ch6) all
compose cleanly into one agent, orchestrated by a real framework (LangGraph) instead of a
hand-rolled loop, with the same reliability discipline (a real-vs-mock toggle, so it runs
with or without an API key) used everywhere else in this course.

## How to run it

Nothing to set up twice. Ava reuses the exact account/key/spend-limit setup from Chapter 1:

- With a real API key (see `.env.example`): set `LLM_PROVIDER` to `anthropic` or `openai` and
  the matching API key. Ava runs on the stronger-tier model
  (`agentlib.llm_client.STRONG_MODELS`), since this is the capstone quality bar, not the
  cost-optimized default tier Chapters 5's model-routing section discusses.
- With no key present: everything still runs, deterministically, end-to-end, through the same
  `HAS_KEY` mock-fallback path used in every other chapter. This is how CI verifies this
  notebook, and how anyone without an API key set up yet can still see the whole thing work.

Either way: `jupyter nbconvert --to notebook --execute capstone/capstone_agent.ipynb`, or
open it in Jupyter and run all cells.

## How this compares to a real system

[OpenClaw](https://docs.openclaw.ai/) is a real production agent system that combines the
same pieces this capstone does at real scale: retrieval/context assembly, tool use, and
persistent memory across sessions (its own documented architecture describes a
context-assembly stage and a "persist memory" stage as part of its core agentic loop; see
`REFERENCES.md`'s Chapter 2 entry). It also documents, in its own security guidance, the
exact class of risk Chapter 6 and this capstone's safeguard address: untrusted external
content reaching a model's context without being treated as data rather than instructions.
OpenClaw's own docs recommend the same layered mitigation (treat external content as data,
scope tool access narrowly, gate sensitive actions) this course's Chapter 6 and this
capstone both implement.

Ava is a small, deliberately simplified version of the same shape of system. The point isn't
that Ava is production-grade. It isn't; it's a single-agent teaching project with two tools.
The point is that the underlying architecture (retrieval, tool use, memory, and the security
discipline that has to accompany all three once real users and real tools are involved) is
the same architecture real agent systems run in production.
