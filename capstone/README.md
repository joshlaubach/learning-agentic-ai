# Capstone: Combined Agent Project

**Status: placeholder — built in Unit 12 of the repository build.** See the root
[`PROGRESS.md`](../PROGRESS.md) for the current build state.

## What this will be

A single, combined, built agent — not another concept→build→break→drill notebook like the
numbered chapters. It will bring together, in one project:

- Retrieval over the Chapter 3 synthetic/SQuAD-based corpus.
- Tool use with the Chapter 7 schema-validated MCP tools.
- Memory across conversation turns.
- At least one safeguard from Chapter 6 (least-privilege scoping and/or output filtering).

It will be implemented using an actual agent framework (LangGraph or the Claude Agent SDK)
rather than the from-scratch ReAct loop used in the early chapters, reuse
`agentlib/llm_client.py` and the account/key/spend-limit setup already done in Chapter 1
(nothing to set up twice), and default to the stronger-tier model on whichever provider is
active — with a clear mock-mode fallback if no key is present.

This is intentionally framed as a **portfolio piece**, not a 10th chapter — see the design
rationale in the root README.

## How this compares to a real system

Once built, this section will point to OpenClaw — a real, viral, production agent combining
the same pieces this capstone does (retrieval/context, tool use, memory, and, per its own
security docs, the exact injection risk Chapter 6 covers) — so the capstone reads as a small
version of something that actually exists at scale, not just a course exercise.
