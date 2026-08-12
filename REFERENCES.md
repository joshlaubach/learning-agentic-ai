# References

**Last verified: 2026-08-12** (the date this repository's build began). Every citation below
— dataset, technique, paper, library — was checked against a live source as of that date, not
copied from memory. Model names, pricing, product UI paths, spec/version numbers, and similar
fast-moving specifics referenced anywhere in this repo reflect the state of the field as of
that date and **move fast**. Check the provider's or project's current documentation directly
rather than trusting a hardcoded figure written months or years after this repo was built.

Format: `Author(s) (Year). "Title." Venue. URL or DOI/arXiv ID.` Each entry is added, and its
accuracy verified via search, during the same build session as the chapter that first cites
it — this file fills in incrementally as `PROGRESS.md`'s units complete, not all at once.
Inline citations appear the first time a concept is named in a chapter's concept markdown
(e.g. "the ReAct pattern (Yao et al., 2022)"), linking back to the full entry here.

---

## Datasets

*(Populated in the units that first use each dataset — SQuAD and SEC EDGAR in Unit 4/Chapter
3, GH Archive in Unit 8/Chapter 7. PubMedQA, BEIR, and `the-stack-github-issues` are optional
complementary corpora also cited in Unit 4.)*

## Chapter 1 — Fundamentals of AI Agents

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). "ReAct:
  Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629.
  https://arxiv.org/abs/2210.03629 — the Thought → Action → Observation loop this chapter's
  `run_agent()` implements. Verified via the live arXiv abstract page at build time (see
  `curriculum/01_fundamentals.ipynb`).

Model names and pricing cited in Chapter 1's setup section (Claude Haiku 4.5 at $1/$5 per
million tokens; Claude Sonnet 5 at $2/$10 per million tokens, made permanent by Anthropic on
2026-08-11; OpenAI's GPT-5.6 Luna as the cheapest current OpenAI tier) were verified via live
web search on this file's "last verified" date above, not carried over from the original
build specification unchecked. OpenAI's exact per-token price for GPT-5.6 Luna was reported
inconsistently across sources at verification time, so `agentlib/llm_client.py` and the
notebook deliberately do not hardcode a number — see the live pricing page pointer in both
instead.

## Chapter 2 — Agent Control Flow

- LangChain, Inc. "Graph API overview." *Docs by LangChain.*
  https://docs.langchain.com/oss/python/langgraph/graph-api — live documentation, no
  canonical paper; cited for the nodes/edges/conditional-edges model this chapter's bridge
  section sketches. Verified live at build time.
- OpenClaw. Official documentation. https://docs.openclaw.ai/ — cited for the project's
  documented three-layer architecture (channel, brain, body) and seven-stage agentic loop
  (normalize, route, assemble context, infer, ReAct, load skills, persist memory), both
  confirmed via the live docs and multiple independent third-party architecture write-ups at
  build time. The spec that produced this course flagged that the project "has been renamed
  twice" — as of this verification, the current, live name and URL are OpenClaw /
  `docs.openclaw.ai`; re-check before treating either as current if reading this much later.
- Schmid, P. (2026, May 5). "How Agents Manage Other Agents: Four Subagents Patterns in
  2026." *philschmid.de.* https://www.philschmid.de/subagent-patterns-2026 — source for the
  four subagent management patterns (inline tool-call spawn, fan-out, persistent agent
  pools, peer-to-peer teams) and the framing of supervisor-worker as the current production
  default. Title and URL verified live at build time; this is an actively updated personal
  blog, not a static/peer-reviewed reference, so both may have moved by the time this is
  read.
- The claim that supervisor-worker is the "current production default," and that skills and
  subagents are typically composed together in production systems, reflects **practitioner
  consensus from multiple 2026 industry sources** (including the Schmid piece above and
  OpenClaw's own shipped skills layer as a concrete example) rather than one canonical or
  peer-reviewed reference — noted here explicitly rather than presented as an academic fact.

(ReAct, cited in Chapter 1's section above, is also the pattern underlying each subagent's
internal loop in this chapter's build section — not re-cited here.)

## Chapter 3 — RAG and Retrieval Evaluation

*(Populated in Unit 4 — RAG, TF-IDF, embeddings, FAISS, RAGAS, IR-metrics textbook, Chroma/
DeepEval, plus the datasets listed above.)*

## Chapter 4 — Production Reliability

*(Populated in Unit 5 — circuit breaker pattern, exponential backoff and jitter.)*

## Chapter 5 — Cost, Performance, and Model Selection

*(Populated in Unit 6 — tiktoken, LoRA, QLoRA, RLHF, optional real-traffic-trace sources.)*

## Chapter 6 — Security and Safeguards

*(Populated in Unit 7 — OpenClaw security guidance, Snowflake MCP governance guidance,
indirect prompt injection.)*

## Chapter 7 — Tool Integration

*(Populated in Unit 8 — Model Context Protocol spec and governance, Snowflake MCP server,
GitHub MCP server, Pydantic, plus the GH Archive dataset entry above.)*

## Chapter 8 — System Design and Engineering Judgment

*(No citations expected — Chapter 8 is original scenario/judgment content, not derived from a
specific external source.)*

## Chapter 9 — LLMOps and Deployment

*(Populated in Unit 10 — canary/progressive delivery, Docker, OpenClaw containerized
deployment.)*

## Capstone and Appendices

*(Populated in Unit 12 for the capstone — LangGraph or Claude Agent SDK, OpenClaw comparison.
Prerequisite-section concepts like async I/O, testing, and Docker cite official docs only, no
paper needed.)*
