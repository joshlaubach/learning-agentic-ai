# Capstone: Ava — a specification

This is a specification, not a walkthrough. Chapters 1-9 taught the pieces; this is where you
put them together yourself, against a written contract, with a test suite that decides whether
you met it.

Nothing here is new material. The retriever is Chapter 3's. The MCP call is Chapter 7's. The
sanitizer is Chapter 6's idea. The loop shape is Chapter 1's. What is new is that they have to
compose into one agent that satisfies five requirements simultaneously — and that satisfying
four of them is a fail.

## What you build

`capstone/ava.py`. It is stubbed; every `raise NotImplementedError` in it is yours.

A LangGraph agent, Ava, with two tools and memory across turns:

| Piece | Comes from | You write |
| --- | --- | --- |
| `search_knowledge_base` | Chapter 3's TF-IDF retriever over the real SQuAD corpus | given |
| `lookup_package_info` | Chapter 7's real MCP server, over real stdio | given |
| `sanitize_retrieved_text` | Chapter 6's instruction/data separation | **yes** |
| `decide` | Chapter 1's brain interface, real/mock split | **yes** |
| `agent_node`, `tool_node`, `route_after_agent` | the graph's three moving parts | **yes** |
| `build_ava` | wiring and the checkpointer | **yes** |

The reference implementation lives in `solutions/reference/capstone.py`, and a fully worked
notebook in `solutions/capstone_reference.ipynb`. Read them after you have your own version
passing, not before.

## The contract

Five requirements. `capstone/test_capstone.py` checks each one, and each one is a real
property of the system rather than a shape your code happens to have.

### 1. Answers cite their sources

Every answer that came from retrieval must carry the `doc_id` of the document it came from,
and that `doc_id` must be one that actually exists in the corpus.

This is the requirement that makes a wrong answer diagnosable. Without it, a hallucination and
a retrieval failure look identical from the outside, and Chapter 3's whole point was that they
are different bugs with different fixes.

### 2. A failing tool is handled, not fatal

At least one tool call must survive the tool raising. When a tool fails, the agent reports
that into the conversation and answers from what it has; it does not propagate the exception
out of the graph.

A dependency being down is an ordinary Tuesday, not an exceptional condition. Chapter 4 spent
a chapter on this.

### 3. A fact survives across two turns of one session

Ask something, then in the same `thread_id` ask a follow-up that is only answerable from the
first turn. The answer has to be right, and it has to come from the checkpointer rather than
from you re-sending a transcript.

### 4. An injected directive is neutralized

Put a document carrying an embedded directive through the real retrieval path — the actual
`tool_node` the graph executes, not the sanitizer called in isolation — and the directive must
not reach the conversation.

Chapter 6's lesson applies verbatim: retrieved content is untrusted input. The corpus is not
"yours" in any sense that matters; it is text from somewhere else that your agent reads on a
user's behalf.

### 5. At most 20 model calls on the 5-question eval set

`EVAL_QUESTIONS` holds five questions. Answering all five must cost 20 model calls or fewer.

The budget is deliberately loose — the reference uses about half of it. It exists to catch the
loop that never terminates, which is the failure Chapter 1 opened with and the one that shows
up on a bill rather than in a stack trace.

## Running the tests

```
pytest capstone/test_capstone.py
```

No API key needed, and none is used. Everything runs through the same deterministic mock path
that CI uses. If you have a key configured, `decide` routes to the real model instead and the
same five requirements still apply — but the tests are written to pass without one, on
purpose, because a test suite that costs money to run is a test suite nobody runs.

`GRADER_MODE=reference pytest capstone/test_capstone.py` grades
`solutions/reference/capstone.py` instead of your version, which is how CI proves the contract
is satisfiable.

## Where to start

1. Read `capstone/ava.py` top to bottom before writing anything. The tools and the state shape
   are given; the gaps are marked.
2. Get `build_ava` compiling and one question answered end to end. Requirement 5 will pass
   trivially and the rest will fail.
3. Take the other four in any order. They are independent.
4. `pytest capstone/test_capstone.py -x` until it is green, then compare against the reference.

## How this compares to a real system

[OpenClaw](https://docs.openclaw.ai/) is a real production agent system that combines the same
pieces at real scale: retrieval/context assembly, tool use, and persistent memory across
sessions (its own documented architecture describes a context-assembly stage and a "persist
memory" stage as part of its core agentic loop; see `REFERENCES.md`'s Chapter 2 entry). It also
documents, in its own security guidance, the exact class of risk requirement 4 addresses:
untrusted external content reaching a model's context without being treated as data rather
than instructions. OpenClaw's own docs recommend the same layered mitigation (treat external
content as data, scope tool access narrowly, gate sensitive actions) this course's Chapter 6
and this capstone both implement.

Ava is a deliberately simplified version of the same shape of system. The point is not that
Ava is production-grade — it is a single-agent teaching project with two tools. The point is
that the underlying architecture, and the five properties above that it has to hold onto, are
the same ones a real agent system is judged on.
