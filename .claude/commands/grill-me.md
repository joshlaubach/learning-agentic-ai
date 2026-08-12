---
description: Build the "ai-agent-interview-prep" repository (9-chapter agentic-AI curriculum + interview drilling layer), one unit per session per PROGRESS.md
---

Build Prompt for Claude Code — "AI Agent Interview Prep" Repository

Role and Operating Instructions
You are building a complete, publishable, interactive GitHub repository from scratch. Build everything described in this document. Do not ask for permission before each individual step — use your best judgment on implementation details, and document any assumptions you make in the README. If something is genuinely ambiguous or would change the scope significantly, ask; otherwise, proceed.

This build happens across many separate sessions, one unit of work per session, to stay within usage limits — see "Build Process" near the end of this document for the exact unit list and how to resume between sessions. Do not attempt to build the entire repository in one continuous session, even if you have budget left after finishing a unit.

If this is the first invocation (no `PROGRESS.md` exists yet at the repo root), start with Step 0 below, then do Unit 1 only. If `PROGRESS.md` already exists, read it first, sanity-check that the repo's actual state matches what it claims, then do exactly the next unchecked unit and nothing more. To resume between sessions, the human only needs to say "continue the build" (or invoke this command again) — read `PROGRESS.md` and pick up from there without needing this whole document repeated.

Step 0 — Environment and Tooling Survey (do this first, before writing any code)

Before starting:

1. Check what skills, plugins, or MCP servers are currently available to you in this environment. Look specifically for anything related to: GitHub repo/PR management, Python/Jupyter project scaffolding, notebook execution or testing, and markdown/documentation generation.
2. If a GitHub-related MCP server or plugin is available, use it to actually initialize the repository, create the directory structure, and make commits — don't just write files to local disk if you have the tooling to do this properly through git with real commit history.
3. If a Jupyter/notebook execution tool is available (e.g. one that can run `.ipynb` files headlessly), use it throughout development to verify each notebook actually executes, rather than only checking it at the very end.
4. If none of the above are available, fall back to standard tooling: `git` CLI, `python3`, `pip`/`uv`, and manual `jupyter nbconvert --execute` or `pytest --nbmake` for verification.
5. Confirm the Python version you're targeting and your package manager choice, and note both in the README.
6. Do not install or invoke any skill, plugin, or MCP server that isn't actually relevant to this task merely because it exists — use judgment.

Once you've surveyed your environment, proceed to build the full project below.

Project Overview

Build `ai-agent-interview-prep`: a 9-chapter, hands-on Jupyter notebook curriculum plus a separate interactive interview-drilling layer, designed to take a data scientist or ML engineer with no prior agentic-AI experience through a realistic transition into AI agent engineering, and to prepare them for real technical interviews on the topic. Target total time investment across the whole repo: roughly 75–90 hours.

This is explicitly a "ML to AI engineer" transition course — it assumes the learner already has statistics, core Python, and ML/embeddings fundamentals (e.g. from a data science background), and focuses entirely on the orchestration/integration layer: agent control flow, tool use, RAG, reliability, cost, security, and system design for LLM-based applications. It does not cover classical MLE, model training/fine-tuning as a primary skill, or MLOps infrastructure — note this scope boundary explicitly in the README so it's discoverable and accurately described.

Hard Constraints — Do Not Violate These

1. Real API usage is the primary path, not an optional add-on. This course is meant to emulate real AI engineering, so the intended way to work through it is with a real API key from either Anthropic or OpenAI — learner's choice, selected via an `LLM_PROVIDER` environment variable. Every notebook must still be able to fall back to a deterministic, mock/offline path when no key is present — but that fallback exists for exactly two reasons (accessibility for learners without budget, and so CI can run without secrets), not as the course's headline experience. Markdown cells should present the real-API path as the default and the mock path as the fallback, not the reverse.
2. Deterministic data. All synthetic data generation must use fixed random seeds so outputs are reproducible across machines and across CI runs.
3. Every notebook must actually execute, top to bottom, with no errors, in a fresh environment with only `requirements.txt` installed. This is a hard acceptance criterion. Verify this for every notebook before considering it complete — do not just visually check the code, actually run it headlessly and confirm zero exceptions and sensible output.
4. Every "break it" section must be real and runnable. It must contain an actual bug that produces the described failure with visible output, followed by an actual fix that resolves it, with output that visibly demonstrates the before/after difference. No "imagine if this happened" — it must actually happen when the cell runs.
5. No reproduction of copyrighted material. When grounding scenarios in real public incidents (see Humanization section), paraphrase the failure pattern in your own words and link to the original source. Never reproduce verbatim text from postmortems, articles, or any other source.
6. No scraped interview questions. Do not scrape Glassdoor, Blind, LeetCode discussion boards, or similar sites for interview questions — this is both a terms-of-service problem and a quality problem (such content is often wrong or misremembered). Generate original scenarios modeled on real failure patterns instead.

Narrative Framing — Agents as Employees

Throughout the entire curriculum, frame agents as employees, not abstract "agents." This is a consistent narrative layer to apply everywhere, not just where explicitly called out below:

* Every named agent gets a job title tied to its role. The Chapter 2 cast is explicit: Jack is the Team Lead/Planner, Bob is the Analyst/Worker, Mike is the QA Reviewer/Critic. Reuse this cast (or extend it with the same naming convention) anywhere else in the curriculum a named agent is useful, including the capstone if it helps.
* A multi-agent setup is "a small team," not "a pipeline." A supervisor/worker pattern is "a manager and their report." Tools are "resources" or "systems" an employee has access to.
* Apply the metaphor concretely per chapter:
   * Ch1: frame the single agent as a new employee on their first day — it takes instructions, uses company resources (the calculator and search tools) to get things done, and reports back. Chapter 1 is effectively "training day."
   * Ch2: loop failures are an employee stuck on a task who never escalates or asks for help. The Jack/Mike cycle is two employees stuck bouncing the same decision back and forth without resolving it (think "per my last email"). The redundant hop is an unnecessary middle-manager role added on top that contributes no value.
   * Ch4: stale cache is an employee working from an outdated printout instead of checking the latest version.
   * Ch5: cost is headcount cost; latency is time-to-complete-a-task; model routing is matching task complexity to the right seniority level of employee, so you're not paying senior rates for junior work.
   * Ch6: prompt injection is social engineering — a stranger manipulating an employee into handing over confidential documents; least-privilege scoping is not giving every employee a master key.
   * Ch7: a flaky tool is a broken piece of equipment or an unreliable vendor the employee has to work around — deciding whether to retry, use a different resource, or escalate to their manager (the user).
   * Ch8: system design is org design. "When would you not use an agent" becomes "when would you not hire someone for this role at all, versus building a simpler repeatable process instead."
   * Ch9: canary deployment is a new hire's trial period with limited responsibilities before full ramp-up; rollback is reverting a bad decision or performance-managing the employee back to a known-good state.
* Keep this consistent, but don't force it where it becomes awkward or unclear. The real technical vocabulary (ReAct, context window, tool calling, etc.) must still be taught explicitly and accurately in every concept section — the employee framing is an intuition-building layer on top of the real content, not a replacement for the terms the learner actually needs in a real interview.

Repository Structure

```
ai-agent-interview-prep/
├── README.md
├── LICENSE                      # MIT (see Legitimacy and Trust for what else applies to which parts)
├── CONTRIBUTING.md              # how to submit real interview questions, PR process
├── SECURITY.md                  # responsible disclosure for the repo's own code
├── REFERENCES.md                # citations for datasets, techniques, and libraries — see Citations and References
├── PROGRESS.md                  # build checklist, read/updated once per session — see Build Process
├── requirements.txt             # pinned versions
├── .env.example
├── .gitignore
├── curriculum/
│   ├── 01_fundamentals.ipynb
│   ├── 02_control_flow.ipynb
│   ├── 03_rag_evaluation.ipynb
│   ├── 04_production_reliability.ipynb
│   ├── 05_cost_performance_model_selection.ipynb
│   ├── 06_security_safeguards.ipynb
│   ├── 07_tool_integration.ipynb
│   ├── 08_system_design_judgment.ipynb
│   └── 09_llmops_deployment.ipynb
├── interview_prep/
│   ├── question_bank.json
│   ├── mock_interview.ipynb
│   └── per_chapter_drills.ipynb
├── solutions/
│   ├── ch01_fundamentals_answers.md
│   ├── ch02_control_flow_answers.md
│   ├── ch03_rag_evaluation_answers.md
│   ├── ch04_production_reliability_answers.md
│   ├── ch05_cost_performance_model_selection_answers.md
│   ├── ch06_security_safeguards_answers.md
│   ├── ch07_tool_integration_answers.md
│   ├── ch08_system_design_judgment_answers.md
│   ├── ch09_llmops_deployment_answers.md
│   └── question_bank_answers.json
├── agentlib/
│   ├── __init__.py
│   ├── tools.py                 # shared mock tools (calculator, search, etc.)
│   ├── loop_guards.py           # max-iteration, duplicate-hash, semantic cycle detection
│   ├── tracing.py               # lightweight span/trace logger, no external account needed
│   ├── synthetic_data.py        # shared generators (docs, tickets, request logs)
│   ├── eval_metrics.py          # precision@k, recall@k, MRR, faithfulness scorer
│   └── llm_client.py            # provider-agnostic real-API wrapper (Anthropic/OpenAI) + HAS_KEY toggle, reused from Ch2 onward
├── data/
│   ├── rag_corpus/               # generated synthetic docs + ground truth Q&A
│   ├── request_logs/             # generated synthetic traffic logs
│   └── schemas/                  # tool JSON schemas for Chapter 7
├── capstone/
│   ├── README.md
│   └── capstone_agent.ipynb
├── tests/
│   ├── test_notebooks.py         # runs every notebook headlessly via nbmake/pytest
│   └── test_agentlib.py          # unit tests for shared library functions
└── .github/
    └── workflows/
        └── ci.yml                 # runs tests on every push/PR
```

Design rationale to follow

* `agentlib/` exists so notebooks don't each reimplement the same mock tools and loop guards. In Chapter 1 and Chapter 2, implement the tool/guard code inline in the notebook for teaching clarity (the learner should see it built from scratch once). From Chapter 3 onward, import from `agentlib` instead of reimplementing — this also teaches the realistic practice of building a shared internal library, which is itself worth calling out in a short markdown cell the first time it happens. `agentlib/llm_client.py` is a deliberate exception to this progression — it's built directly in `agentlib` starting in Chapter 1, since it's the one piece every real-API section from Chapter 2 onward needs immediately, and reimplementing a provider client per-notebook would be unrealistic.
* `interview_prep/` is a separate track from `curriculum/` on purpose — it's meant to be revisited repeatedly (e.g. the week before an actual interview) independent of working through the notebooks linearly.
* `solutions/` holds full written model answers for every cold-answer / interview-drill question across all chapters, plus model answers for `question_bank.json`, kept in files entirely separate from the notebooks and the question bank itself so nothing spoils the self-check exercise while it's being attempted. No notebook, and no entry in `question_bank.json`, may contain an inline model answer — answers live exclusively in `solutions/`.
* `capstone/` is intentionally not numbered as a 10th chapter — it's a different format (one built project, not concept→build→break→drill) and should be framed in its own README as a portfolio piece.

Chapter-by-Chapter Specification

For every chapter, follow this notebook template unless a chapter's spec below says otherwise:

1. Markdown — title cell: chapter title, time estimate, prerequisites, one-sentence framing of what interview category this chapter maps to.
2. Markdown — concept section: explain the core ideas in plain language, assuming the reader is learning this for the first time. Use a comparison table where it helps (this pattern worked well in Chapter 1's chatbot/workflow/agent table — reuse it wherever a chapter has 2-4 comparable concepts).
3. Code — imports and setup.
4. Markdown + Code, interleaved — Build section: working starter code the learner can run immediately, building up the chapter's core artifact (e.g. a retrieval pipeline, a cache layer, a schema validator) piece by piece with a markdown cell of explanation before each code cell.
5. Markdown + Code, interleaved — Break It section(s): one or more deliberate, runnable bugs matching the specific failure mode(s) listed below for that chapter, each followed by a working fix with visible before/after output.
6. Markdown — Interview Preparation section: a short recap framework, then a set of "cold-answer" questions the learner should attempt to answer from memory, referencing the actual interview scenario/follow-up pairs this chapter maps to. Do not include model answers in this cell or anywhere else in the notebook. End the section with a one-line pointer to the matching file, e.g. "check your answers against `solutions/ch03_rag_evaluation_answers.md`." The corresponding solutions file must contain a full written model answer for every cold-answer question in that chapter.
7. Markdown — closing cell: one or two sentences pointing to the next chapter and how it builds on this one.

Chapter 1 — Fundamentals of AI Agents (~6 hrs: roughly 30-45 min on account/API setup — longer than usual on purpose, since it's written for a limited-Python-background reader — with the remaining ~5+ hrs on concept, build, break-it, and the interview drill)

* Concept: introduce the running metaphor for the whole course here — think of the agent as a new employee on their first day. It takes instructions, uses company resources (tools) to get things done, and reports back; a bad one loops forever on a task instead of escalating, and a good one knows when to ask for help. Then cover: chatbot vs. workflow vs. agent, the ReAct pattern (Thought → Action → Observation), when not to use an agent (i.e. when you wouldn't hire someone for this at all), core vocabulary (context window/tokens, tool/function calling, grounding and hallucination).
* Build: two mock tools (a restricted-eval calculator, a canned-fact `mock_search`); a rule-based "fake LLM brain" function that stands in for a real model call via keyword matching, explicitly labeled as a stand-in so the learner understands what it's approximating; assemble these into a minimal ReAct loop; a memory-on vs. memory-off comparison showing how conversation history would be threaded through a real prompt.
* Break it: remove the loop's stop condition using a "bait tool" that always signals `{"status": "partial"}` — demonstrate the resulting infinite loop (capped at a high iteration count purely so the notebook doesn't hang, with a note that a real system has no such cap), then fix it with duplicate-observation detection.
* Account, budget, and API setup — this is the primary path for the whole course, not an optional add-on (build this as its own clearly-labeled section; it's the one-time setup point that Chapters 2, 3, 4, 6, 7, and the capstone will all reuse). Write this section for someone with limited Python background — this matches the prerequisites self-check in Appendix B, which already flags environment management (terminal use, `.env` files, package installs) as a plausible gap even for a strong data-science background. Don't assume familiarity with a terminal, `pip`, or environment variables; briefly say what each one is and why the step matters, not just the command to run. Do not compress this section for brevity — thoroughness here is the point, not a flaw to trim:
   * A markdown cell walking through setup step by step, in this order, before any code: (1) choose a provider — Anthropic (console.anthropic.com) or OpenAI (platform.openai.com); either works throughout the course, and the choice is stored in one environment variable so nothing else in the curriculum needs to know which one was picked; (2) create an account with the chosen provider — note that new accounts may receive a small trial credit; (3) before generating an API key or writing any code, set a spend limit — for Anthropic, under Settings → Billing → Usage limits in the console; for OpenAI, under Settings → Limits in the platform dashboard — both verified as of this document's construction but console UIs change often, so confirm the exact current menu path against the live dashboard before writing final instructions, and alternatively note that disabling auto-reload on prepaid credits is a simpler hard cap on either platform if the settings page has moved — recommend a $15–20 ceiling for the entire course as a comfortable margin (see the cost note below), explicitly framed as a guardrail against a runaway loop or bug, which is a fitting safeguard given that's exactly what Chapters 1–2 teach you to detect; (4) generate an API key; (5) create a `.env` file (never committed) with `LLM_PROVIDER=anthropic` (or `openai`) plus `ANTHROPIC_API_KEY=` or `OPENAI_API_KEY=` as appropriate; (6) add `.env` to `.gitignore`; (7) `pip install anthropic openai python-dotenv` — install both SDKs regardless of which provider is chosen, so switching later doesn't require a fresh install.
   * Include a short, honest cost note in this same cell rather than a hard number: real-API calls are now the default across most of the course — Chapters 1, 2, 3, 4, 6, 7, and the capstone all call a real model by default, with the mock path only as a fallback. A full pass through the course on either provider's cheapest current-generation model, including reasonable re-running of cells while learning, is realistically in the $5–15 range — but state plainly that per-token pricing on both platforms changes often, so the learner should check the provider's live pricing page before trusting any number written into a notebook months or years after it was built.
   * A code cell that loads `.env` via `python-dotenv`, reads `LLM_PROVIDER`, and checks for the corresponding key's presence without erroring if it's absent, setting a `HAS_KEY` boolean.
   * Build the shared wrapper in `agentlib/llm_client.py` now, not inline — this is the first thing that goes in `agentlib` rather than being reimplemented per-notebook, since every later real-API section reuses it. Make it provider-agnostic: a `call_model()` function that reads `LLM_PROVIDER` and dispatches to either `anthropic.Anthropic().messages.create(...)` or the equivalent current OpenAI chat/completions call, normalizing both providers' responses and tool-call formats into one common return shape so the rest of the curriculum never has to branch on provider. Default to each provider's cheapest current general-purpose model for cost reasons — for Anthropic this is `claude-haiku-4-5-20251001` ($1/$5 per million input/output tokens, confirmed current); for OpenAI, as of this document's construction verify the current cheapest general-purpose model and its pricing directly against `developers.openai.com/api/docs/pricing` (or the current equivalent URL) at build time rather than hardcoding a specific price in code, comments, or markdown, since reported pricing for newer models is often inconsistent across sources — have the notebook print a line directing the learner to the live pricing page instead of asserting a number that will likely be stale. Accept an optional `model=` override for the chapters that want higher-quality reasoning (Chapter 6 and the capstone default to a stronger tier on whichever provider is active — verify the current recommended mid/high-tier model and its pricing on both providers at build time rather than trusting a hardcoded figure). Include basic retry-on-rate-limit handling for both providers. Call out in a markdown cell that this provider-abstraction layer is itself a real, teachable AI-engineering skill — building directly against one vendor's SDK everywhere is a common early mistake that creates painful lock-in later.
   * In this notebook, a `real_llm_brain()` function built on top of `agentlib.llm_client.call_model()`, matching the same input/output shape as `fake_llm_brain()`, performing real tool-calling against the two mock tools with a proper tool-use schema for whichever provider is active.
   * A toggle: `brain = real_llm_brain if HAS_KEY else fake_llm_brain` — keep `fake_llm_brain()` in the notebook as the CI/no-budget fallback, but write the surrounding markdown so the real-API path reads as the intended way to run this chapter, not a bonus extra.
   * A no-key alternative for learners who want real model behavior with zero spend: a markdown cell explaining how to instead run this against a local model via Ollama (free, no account, no key, no spend limit needed at all).
* Interview drill: vocabulary flashcard quiz (interactive, using `input()`, skippable), a "explain agents to a non-technical PM" written-answer prompt cell, and 4+ cold-answer questions mapped to real interview phrasings (e.g. "your AI agent keeps looping forever — how would you detect and stop it?").

Chapter 2 — Agent Control Flow (~8 hrs, expanded to cover subagents properly)

* Concept: ReAct vs. plan-and-execute, state machines for agents, supervisor/worker multi-agent patterns — introduced here with a consistent named cast reused through the rest of the chapter: Jack (the planner), Bob (the worker), and Mike (the critic). Naming them is deliberate — it makes multi-agent traces easier to read and discuss than generic role labels, which matters once you're staring at a real log with several agents in it.
* Subagents — what actually makes something a "subagent," not just another agent in a pipeline: the defining mechanic is context isolation — a subagent gets a fresh, bounded context, executes its task independently, and returns a compressed synthesis to the orchestrator, not its full transcript. That's what keeps the orchestrator's own context from getting polluted by every worker's intermediate reasoning. Teach the four current management patterns, ordered by how much lifecycle control the orchestrator keeps: inline tool-call spawn (simplest — calling a subagent looks identical to calling any other tool, blocks until it returns), fan-out (multiple independent subagents dispatched in parallel), persistent agent pools (long-lived, stateful workers reused across tasks), and peer-to-peer teams (agents message each other directly, no central dispatcher). Note that supervisor-worker — which is what Jack/Bob/Mike already is — is the current production default, so the existing pipeline is the right foundation, not something to throw out. Also introduce skills as the companion concept, distinct from subagents: a skill is a small, self-contained instruction/tool package the orchestrator loads per task to stay capable without bloating its own context ("if it needs more than a paragraph of documentation, it's probably two skills") — subagents isolate execution, skills isolate capability, and production systems typically compose both.
* Build: a 3-agent pipeline — Jack (planner, breaks the task down), Bob (worker, executes and calls tools), Mike (critic, reviews Bob's output before it's returned) — using `agentlib/llm_client.py` and the `HAS_KEY` toggle from Chapter 1 so each of the three runs on a real model call by default, falling back to a rule-based stand-in only when no key is present; with artificial per-hop latency (`time.sleep` or simulated delay values, not real sleeps that slow down CI — use a simulated latency value that's logged, not actually slept, or keep real sleeps under 0.1s each); a lightweight tracer from `agentlib.tracing` logging each named agent's hop duration so the learner reads a trace instead of print statements. Extend Bob specifically to dispatch a real subagent using the inline tool-call spawn pattern above: Bob hands off a bounded subtask to a fresh-context subagent, which does its work in isolation and returns a compressed synthesis (a few sentences, not its full reasoning trace) back into Bob's context — implement both the isolated-context mechanic and the compression step for real, not just described in markdown, so the learner can inspect what does and doesn't cross back into the orchestrator's context.
* Break it — four distinct simulations, not three:
   1. A bait tool causing a straight-line infinite loop (same failure class as Chapter 1, but now fixed with a proper max-iteration guard built as reusable code).
   2. Jack and Mike ping-ponging — the planner and the critic defer the same decision back to each other indefinitely (Mike: "ask Jack to clarify scope"; Jack: "ask Mike what's unclear") — a genuine cycle, distinct from a straight loop, which a naive duplicate-action hash check will not catch (demonstrate this explicitly — show the hash-based guard failing on this case). Fix with a semantic-similarity-based cycle detector (can use simple string similarity / a small local embedding comparison rather than requiring an API).
   3. A redundant hop bolted onto Jack/Bob/Mike's pipeline — a second reviewer step duplicating Mike's job — adds latency with no functional value; build a latency profiler that identifies which hop contributed the most time with no corresponding value-add, and a cost/latency calculator comparing single-agent vs. multi-agent across varying task complexity.
   4. A leaky subagent — Bob's subagent from the build section returns its full raw transcript instead of a compressed synthesis; show concretely how this pollutes Bob's context (token count spike, relevant signal buried in irrelevant intermediate reasoning) and degrades Bob's next decision. Fix by enforcing a compression step the subagent must pass through before its result re-enters the orchestrator's context — this is the context-isolation mechanic from the concept section, broken and then fixed hands-on.
* Bridge: a short markdown cell showing what Jack/Bob/Mike's pipeline would look like expressed as LangGraph nodes/edges (code sketch, doesn't need to actually run LangGraph, just needs to accurately map the concepts). Add a second, real-world comparison alongside it: OpenClaw (the viral open-source, self-hosted AI agent that runs continuously and connects through WhatsApp/Telegram/Slack/etc.) uses a documented three-layer architecture — channel, brain, body — plus a seven-stage loop (normalize, route, assemble context, infer, ReAct, load skills, persist memory) that maps closely onto Jack/Bob/Mike's planner/worker/critic split. Point out explicitly which of OpenClaw's stages correspond to which of the three agents, and note that its "load skills" stage is a real, shipped instance of the skills concept just introduced, not just a course abstraction.
* Interview drill: cold diagnosis exercise — given only a symptom description, the learner must classify it as loop vs. cycle vs. unnecessary-hop vs. leaky-subagent (i.e., work out which of Jack, Bob, or Mike's interactions is at fault) before revealing which simulation it was; plus architectural tradeoff questions ("when is adding more agents actually a bad decision?", "what's the actual difference between a subagent and just calling another agent?", "when would you reach for fan-out instead of a persistent agent pool?").

Chapter 3 — RAG and Retrieval Evaluation (~8 hrs, the longest chapter — including a ~15-20 min concept review at the start)

* Quick review before diving in: a short, skippable markdown refresher on three specific concepts this chapter leans on, for anyone whose background didn't happen to cover them — this is a safety net, not an assumption of a gap, since a DS background likely already has some or all of it. A paragraph each, not a full lesson:
   * TF-IDF — weighting a word by how often it appears in a document versus how rare it is across all documents, the simplest way to turn text into comparable vectors.
   * Embeddings as semantic space — why distance between embedding vectors captures meaning rather than raw word overlap, unlike TF-IDF.
   * MRR (Mean Reciprocal Rank) — 1 divided by the rank of the first correct result, averaged across queries; a standard information-retrieval metric, less universal than precision/recall, so easy to have missed outside a search/recsys course.
* Concept: retrieval vs. ranking vs. generation as separate failure surfaces; precision@k, recall@k, MRR; faithfulness/groundedness; why RAG does not eliminate hallucination.
* Build:
   * Base corpus: pull 25-30 real passages from SQuAD 1.1 (Rajpurkar et al., 2016 — full citation in `REFERENCES.md`) via Hugging Face `datasets` (`load_dataset("rajpurkar/squad")` — use the canonical repo path, not the bare `"squad"` alias, since mirrors sometimes mislabel the license), which already includes human-annotated ground-truth Q&A mapped to each passage — use these directly instead of hand-writing synthetic Q&A. Default to 1.1 specifically (every question answerable, unambiguous for teaching precision/recall@k); note SQuAD 2.0's ~50,000 adversarial unanswerable questions as an optional follow-on extension for teaching abstention/"I don't know" behavior, not the default. Layer in 4-6 near-duplicate "confusable" documents synthetically, since real SQuAD passages won't reliably contain the specific near-duplicate pairs the break-it section needs — these stay generated on top of the real base. Cache the pulled subset locally after first download so re-runs need no network access. Note SQuAD's license (CC BY-SA 4.0, confirmed on the canonical dataset card) in the markdown cell that loads it, with a citation. Put the loader/cache logic in `agentlib/synthetic_data.py` alongside the still-synthetic confusable-document generator.
   * Optional complementary corpora, for a learner who wants more than one domain to practice on: PubMedQA (`qiaojin/PubMedQA`, MIT license) for a domain-specific medical RAG variant with yes/no/maybe + long-form answers grounded in real PubMed abstracts, and BEIR (specifically the FiQA subset) as a standardized heterogeneous retrieval benchmark, useful for showing how retrieval metrics behave across a genuinely different domain than SQuAD's Wikipedia passages. Neither is required — SQuAD 1.1 alone is sufficient to complete the chapter — but both are free, well-documented, and a natural "if you want more practice" pointer in the chapter's closing cell.
   * Document ingestion subsection (comes before indexing): pull a small batch of real SEC EDGAR 10-K/10-Q filings (U.S. Securities and Exchange Commission, public domain, no API key — full citation in `REFERENCES.md`; use the per-company `submissions` JSON endpoint at `data.sec.gov` to list recent filings rather than scraping the full-text search UI, and respect the 10-requests-per-second limit with a descriptive `User-Agent` header) — genuinely messy (real broken tables, inconsistent headers, long unstructured sections) without needing to fake it. As an alternative or complementary messy-document source, `bigcode/the-stack-github-issues` (nearly 31 million real GitHub issue/PR threads, inconsistent formatting, embedded code blocks, bot noise) is another good option if a learner wants messiness from a software-engineering domain instead of financial filings. Layer a few synthetic corruptions on top only where the real source doesn't naturally provide a needed case (e.g. near-duplicate-but-not-quite paragraphs for the dedup exercise). Have the learner build a small ingestion pipeline that normalizes this mess: handling broken formatting, choosing and justifying a chunking strategy (fixed-size vs. semantic/sentence-boundary chunking, with a worked side-by-side comparison of both against the same messy input), and deduplicating near-identical chunks before they enter the index. Frame this explicitly as RAG ingestion, not general data cleaning — retrieval quality is only as good as what gets indexed, and "how would you chunk a messy real-world corpus?" is a genuine, commonly-asked interview question.
   * Two retrieval implementations: TF-IDF (via scikit-learn, no download) and local embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`, one-time local model download, fully offline afterward) — let the learner compare both, run against the real SQuAD-based corpus.
   * A short section introducing Chroma (or FAISS) as what a real local vector store looks like, with a small working example indexing the same corpus, framed as "this is what you'd actually use in production instead of hand-rolled cosine similarity."
   * An eval harness computing precision@k, recall@k, and MRR (in `agentlib/eval_metrics.py`), plus a simple faithfulness scorer (does the generated answer's content actually appear in/derive from the retrieved chunks).
   * A short section mapping the hand-built metrics to what RAGAS and/or DeepEval actually compute, so the learner can name-drop and use the real tooling, not just the from-scratch version.
   * Real-model generation, reusing `agentlib/llm_client.py` and the `HAS_KEY` toggle from Chapter 1 (no new account/key steps here — just import and check): the generation step calls a real model by default instead of the template-based generator, so the learner sees a real model's actual behavior when it ignores or misuses retrieved context, rather than only a canned mock version. Falls back to the template-based generator only if no key is present.
* Break it — five distinct simulations:
   1. Corrupted retriever for a subset of docs → confident but wrong answers.
   2. Correct retrieval, but the generator ignores the retrieved context and answers from parametric knowledge instead (demonstrate this is possible even when retrieval succeeded).
   3. An answer whose supporting facts are split across two separate chunks, neither of which alone is sufficient — show naive top-k retrieval failing here.
   4. A query that matches a near-duplicate confusable document instead of the correct one.
   5. A simulated case where the offline eval metrics (precision/recall/MRR) improve after a change, while a simulated "user satisfaction" signal on a held-out sample of realistic queries drops — this is the online-vs-offline divergence case.
* Interview drill: for each break-it scenario, a cold-diagnosis exercise ("is this a retrieval problem or a generation problem, and which metric proves it?"), plus "how would you chunk a messy real-world corpus, and how would you catch near-duplicate chunks before they hurt retrieval?", plus a written exercise explaining hallucination-despite-RAG to a non-technical CEO in plain language.

Chapter 4 — Production Reliability (~7 hrs)

* Concept: what changes between demo and production; staleness/TTL/cache invalidation; retries with backoff; circuit breakers; graceful degradation.
* Build: a fake mini-codebase (4-5 Python files with realistic docstrings) with a version history (timestamp, content tuples) simulating edits over time; a caching layer with TTL.
* Break it:
   1. Stale cache — a file gets "edited" but the cache still serves the old version, causing an AI coding assistant to give an answer based on outdated code. Fix: invalidate on write, and log context age on every served response so staleness is detectable, not silent.
   2. A flaky tool that fails intermittently — build a retry decorator with exponential backoff and jitter.
   3. A cascading-failure scenario — build and demonstrate a circuit breaker that stops hammering a failing dependency.
* Real rate-limit handling: reusing `agentlib/llm_client.py` from Chapter 1, deliberately trigger a real rate-limit response (e.g. by firing a burst of concurrent calls) to see an actual `429`/overloaded error and real retry-timing behavior from whichever provider is active, then apply the same backoff decorator built above against the real API. Falls back to a simulated flaky-tool exercise only if no key is present.
* Interview drill: "users complain the AI coding assistant ignores recent code changes — walk through how you'd debug context freshness in production," answered using the actual logs generated in this chapter, not from memory; plus a reliability-pattern recall drill (retry vs. circuit breaker vs. cache invalidation — when does each apply).

Chapter 5 — Cost, Performance, and Model Selection (~8 hrs)

* Concept: token economics, latency decomposition (queueing vs. network vs. inference vs. generation), prompt caching, model routing.
* Build: a synthetic request log generator (timestamp, model, input/output tokens, latency, queue depth) using log-normal/Poisson distributions for realism, seeded; optionally ground the arrival-time and burstiness patterns in a real public trace instead of pure synthetic distributions — Microsoft's `AzurePublicDataset` (published LLM inference traces on GitHub) or the BurstGPT public LLM-serving workload trace both provide real request-arrival patterns and token counts that can replace or calibrate the synthetic log-normal/Poisson generator; this is optional (the exercise works fully synthetic too) but produces more defensible "this is what real traffic looks like" framing if included. Real tokenization using `tiktoken` (or a comparable local tokenizer) shown against the synthetic prompts so the learner sees real tokenization quirks (numbers, code, whitespace) rather than approximated counts; a latency profiler that decomposes each logged request into its component stages.
* Break it — inject each of these into slices of the same request log, and require the learner to diagnose from the raw log data alone before revealing which it was:
   1. A silent duplicate-call bug doubling token volume.
   2. Unbounded context growth (context length regression).
   3. A concurrency/queueing spike causing latency to jump from ~2s to ~12s.
* Optimization section: prompt caching, and a model-routing decision function that right-sizes model choice to query complexity.
* Fine-tuning subsection (not a full chapter — keep this to ~2-2.5 hrs): when fine-tuning is worth it vs. RAG vs. better prompting, framed explicitly as a cost/build tradeoff decision; LoRA/QLoRA explained conceptually (no actual training — this notebook must not require GPU access or paid compute); dataset curation and catastrophic forgetting explained conceptually with a small illustrative (non-trained) example. Add RLHF and RL's role in agent development here too, conceptual only, same treatment as LoRA/QLoRA — explain RLHF as how a base model becomes an assistant (ranking/preference data shaping behavior, not just next-token prediction), then explain the agent-specific framing that actually comes up in interviews: RL isn't used to build an agent from scratch, it's applied after initial prompting/prototyping to refine tool-selection policy and align planning/communication behavior with human preference — a fine-tuning and refinement layer on top of an already-functioning agent, not a starting point. No implementation, no training loop; this is explain-it-correctly knowledge, not build-it knowledge.
* Interview drill: "GPU costs doubled after your latest release — what would you try before adding more GPUs?" and "latency jumped from 2s to 12s — what's the first thing you investigate?", both answered via triage on the raw synthetic log, not from memorized talking points; plus "what role does RL play in developing an AI agent?" as a cold-answer conceptual question.

Chapter 6 — Security and Safeguards (~7 hrs)

* Responsible-use note, first cell in the notebook, before anything else: this chapter's injection payloads run against a real model, not a mock — a short, clearly-flagged markdown cell stating this is for learning against your own systems only, and these techniques should not be pointed at systems you don't own or have authorization to test (full wording in the Legitimacy and Trust section above).
* Concept: direct vs. indirect prompt injection, least privilege, output filtering, human-in-the-loop gating, why "just tell the model not to reveal X" isn't a safeguard. Ground this in two real, current examples rather than only the hypothetical: OpenClaw — a real, widely-deployed agent with shell/browser/email access — has its own documented security guidance (bind to localhost, enable token auth, lock file permissions, defend against prompt injection in its operating instructions) precisely because that level of access makes it a real target, not a hypothetical one. Snowflake's official MCP server documentation separately warns that "using multiple MCP servers without verifying tools and descriptions could lead to vulnerabilities such as tool poisoning or tool shadowing" and recommends verifying third-party MCP servers before use — a real vendor naming the exact class of risk this chapter teaches. Cite both in the concept markdown.
* Build: a fake internal document containing a clearly-marked-fake confidential field (e.g. `"internal_note": "FAKE-DO-NOT-USE-1234"` — make sure any fake secret is obviously fake and clearly labeled as synthetic, never resembling a real credential format); a naive agent with unrestricted access to it, using `agentlib/llm_client.py` from Chapter 1 with the stronger-tier `model=` override on whichever provider is active (this chapter treats the real API as the primary path, not optional, since prompt injection against the rule-based mock brain isn't really injection — there's no actual reasoning to hijack; fall back to a clearly-labeled simplified mock version only if no key is present, with a note that the lesson is meaningfully weaker without a real model).
* Break it: 3-5 injection payloads embedded inside otherwise-normal tool output, demonstrating the naive agent leaking the confidential field when queried by an unrelated request. This is real, working injection against your own mock system — not a description of the concept.
* Fix, layered (each as its own code cell with before/after): least-privilege scoping so the confidential field never enters context in the first place; output-side filtering as a second layer; treating all tool output as untrusted input structurally; re-test all original payloads against the hardened version and show they now fail to exfiltrate anything.
* Interview drill: "a prompt causes your AI agent to expose confidential data — what production safeguards should have prevented this?" plus a written exercise explaining defense-in-depth to a non-technical executive.

Chapter 7 — Tool Integration (~7 hrs, now built on a real MCP server, not generic mock functions)

* Concept: the Model Context Protocol (MCP) architecture — host, client, and server, communicating over JSON-RPC 2.0, with three core primitives (tools, resources, prompts). Explain that MCP standardizes tool access rather than replacing function calling — the model still makes structured tool calls, MCP just makes those calls interoperable across hosts and servers instead of one-off per integration. Note the spec's current version — verify at build time, as MCP has revised multiple times — and its governance (donated by Anthropic to the Agentic AI Foundation (AAIF), a directed fund under the Linux Foundation, co-founded by Anthropic, Block, and OpenAI — verify current governance status at build time and cite it as AAIF/Linux Foundation, not "Linux Foundation" alone). Then: schema contracts, idempotency, a failure taxonomy — transient vs. schema-invalid vs. semantically-wrong-but-valid.
* Build: an actual minimal MCP server, using the real MCP Python SDK, run as a local subprocess over stdio transport (no HTTP server, no ports, no account — MCP itself needs nothing beyond the SDK, regardless of whether a real LLM key is configured). Expose 2-3 tools modeled on real, well-known MCP servers rather than generic unnamed ones, so the schema/failure work feels like real enterprise integration: a Snowflake-style data tool (modeled on Snowflake's actual official MCP server — natural-language-to-SQL query and RBAC-style role-scoped access, mocked locally rather than requiring a real Snowflake account) and a GitHub-style repo tool, backed by real data rather than fabricated responses — pull a small, filtered slice from the `open-index/open-github` dataset on Hugging Face, a structured Parquet mirror of the public GH Archive/GitHub Events API, actively maintained and updated on a live edge. Its historical backfill is partial, not a gapless mirror to the present — check the dataset card for the current backfill extent before choosing a specific, verified date range to pin the exercise to. License is ODC-By v1.0 (attribution required, inherited from GH Archive) — cite it as such, not as unqualified "public" data. Because the dataset spans 16 differently-schemad tables partitioned by `data/TABLE/YYYY/MM/DD.parquet`, load a specific table/date range via `data_files` globbing or DuckDB predicate pushdown against the `hf://` path rather than a bare `load_dataset(..., streaming=True)` call, which the dataset's own card recommends over naive full-dataset streaming. Cache the filtered slice locally after first pull, same pattern as Chapter 3's SQuAD/SEC EDGAR loaders. The tool then answers "list recent issues/PRs for repo X" from real historical GitHub activity, not invented data. Each tool gets a Pydantic-validated schema (not hand-rolled dict checks — this should reflect real practice). Build a real MCP client in the notebook that connects to this server and lists/calls its tools, so the learner sees an actual client-server handshake, not a bare function dict.
* Break it — the same four failure types as before, now injected at the MCP server so they're tested through the real protocol layer, not a shortcut mock function:
   1. A transient, network-style intermittent failure.
   2. A malformed-type response (schema validation catches this one easily — show that).
   3. A valid-type-but-semantically-wrong-value response (harder — naive validation misses it; tighten validation to catch it, e.g. range/business-rule checks on top of type checks).
   4. A tool schema version change mid-session, and how the client should detect and handle it.
* Build a decision router matching failure type to response strategy (retry / switch tools / ask the user for clarification), and integration tests exercising all three paths against the real MCP server.
* Real tool-calling: reusing `agentlib/llm_client.py` from Chapter 1, have a real model (not the rule-based brain) select and call the MCP server's tools through the client built above, so schema-validation failures are tested against the actual, sometimes-inconsistent tool-call output a real model produces, not just a hand-crafted bad payload. Falls back to hand-crafted malformed payloads against the same MCP server if no key is present — the mock/real split is about which brain is choosing the tool calls, not about whether MCP itself is real.
* A short note distinguishing this local stdio setup from production MCP deployments, which increasingly use Streamable HTTP transport and connect to one of the hundreds of public MCP servers now available (GitHub, Slack, Postgres, and similar) — stdio is the right choice for a self-contained notebook, but the learner should know it's not the only transport.
* Interview drill: "an MCP tool suddenly starts returning invalid data — should the agent retry, switch tools, or ask the user for clarification?" as a cold-classification drill across several symptom descriptions — now answerable from having actually built and broken a real MCP server, not just discussed the concept.

Chapter 8 — System Design and Engineering Judgment (~5 hrs, mostly markdown/design-doc driven, minimal code)

This chapter is structurally different from the others — it is about design reasoning, not debugging code. Keep it light on code.

* Concept: a repeatable system-design framework (clarify requirements → identify constraints → propose architecture → identify failure modes → state what you'd measure).
* Design studio: blank, fillable design-doc templates (as markdown cells with a fixed structure: requirements / architecture / failure modes table / metrics / explicit tradeoffs) for two prompts: "design a customer support agent for 1M users" and "design a coding assistant with full codebase context." Leave these blank in the notebook — build fully worked model versions of both in `solutions/ch08_system_design_judgment_answers.md` instead.
* Judgment prompts (no bug to find, pure reasoning, each as a markdown prompt + blank answer cell): "the agent works in testing but fails 15% of the time in production — walk through your triage," "a stakeholder wants the agent to auto-approve refunds — what do you push back on," and critically, "when would you NOT use an agent or LLM here at all" — the filter question that should include cases like deterministic logic, strict latency/cost budgets, high-stakes irreversible actions, or a simple rules engine outperforming an LLM.
* Self-critique exercise: have the learner take their own design doc from one of the two worked prompts and argue against their own architecture, identifying its weakest assumption.
* Interview drill: timed cold-design drills (~10 min per prompt, no notes — instruct the learner to actually time themselves), plus the standard behavioral pair every AI engineering interview includes: "walk me through something you built that broke" and build-vs-buy reasoning for a tool/service choice.
* As with every other chapter, none of Chapter 8's design docs, judgment prompts, or drills may contain inline model answers. `solutions/ch08_system_design_judgment_answers.md` must contain full worked answers for the design studio prompts, both judgment prompts, the "when would you not use an agent" filter question, and the behavioral pair.

Chapter 9 — LLMOps and Deployment (~6 hrs)

* Concept: canary releases, shadow deployment, prompt versioning, feature-flagging prompts, drift detection, rollback strategy. Explicitly reference back to Chapter 4's reliability patterns (retries/circuit breakers) rather than re-teaching them — note in a markdown cell that this chapter is the operational/deployment half of what Chapter 4 covered at the request level.
* Build: a simple prompt-versioning scheme (versioned prompt templates with a changelog), a feature-flag toggle simulating a canary rollout (X% of simulated traffic routed to a new prompt/model version), and a drift monitor comparing a rolling window of simulated output-quality scores against a baseline.
* Containerization subsection: a short, concrete Dockerfile for the agent built across this curriculum — base image, installing `requirements.txt`, copying `agentlib/`, entrypoint — with a one-paragraph explanation of why containers matter for deployment (runs identically regardless of host machine, which is what makes the canary/rollback logic above actually deployable rather than notebook-only). Use OpenClaw as the concrete real-world reference point: its own documentation lists containerized deployment as a first-class install path for running the agent persistently on a VPS, which is the same real problem — a long-running background agent — that this chapter's canary/rollback logic is designed for. Building and running the Dockerfile locally (`docker build`, `docker run`) is enough; no real hosting/VPS required to complete the exercise.
* Break it: simulate a "bad model update" — inject a quality regression into the canary-routed traffic slice, have the learner detect it via the drift monitor before it reaches 100% rollout, then execute a rollback.
* Interview drill: revisit "your evaluation score improved but user satisfaction dropped" (this time from a deployment/rollout lens rather than Chapter 3's RAG-metrics lens — note explicitly that this is the same underlying interview question showing up in two different contexts), plus a deployment-strategy tradeoff drill (canary vs. shadow vs. blue-green, when each applies).

`interview_prep/` Specification

`question_bank.json`

A structured, tagged question bank — not prose. Every entry follows this schema:

```json
{
  "id": "rag-002",
  "chapter": 3,
  "category": "RAG evaluation",
  "difficulty": "mid",
  "format": "scenario_first",
  "scenario": "Your RAG system returns confident but wrong answers.",
  "follow_up": "Which metric tells you whether retrieval or generation is failing?",
  "key_concepts": ["faithfulness", "recall@k", "groundedness"],
  "grounded_in_real_incident": false,
  "source_note": null
}
```

Seed questions — use these verbatim, plus many variants of each

The 10 scenario/follow-up pairs below are user-provided seed material (supplied directly in this spec, not scraped by Claude Code from any interview-question site — the "no scraped questions" constraint above governs autonomous scraping during the build, not this). Each one must appear word-for-word as its own literal entry in `question_bank.json`, tagged to the chapter noted. For each seed, also generate at least 5 additional variant entries in that same chapter — same underlying failure pattern and `key_concepts`, different scenario wording, different `format`, different specific numbers/details — so a learner doesn't just memorize one fixed phrasing.

1. (Ch1) "Your AI agent keeps looping forever." → "How would you detect and stop infinite reasoning loops?"
2. (Ch3) "Your RAG system returns confident but wrong answers." → "Which metric tells you whether retrieval or generation is failing?"
3. (Ch7) "An MCP tool suddenly starts returning invalid data." → "Should the agent retry, switch tools, or ask the user for clarification?"
4. (Ch2) "Your multi-agent workflow is slower than a single agent." → "When is adding more agents actually a bad architectural decision?"
5. (Ch4) "Users complain your AI coding assistant ignores recent code changes." → "How would you debug context freshness in production?"
6. (Ch5) "GPU costs doubled after your latest release." → "What optimizations would you try before adding more GPUs?"
7. (Ch5) "Your LLM latency jumps from 2s to 12s." → "What is the first thing you investigate?"
8. (Ch3) "The CEO asks why your AI hallucinates despite using RAG." → "How would you explain hallucinations to a non-technical stakeholder?"
9. (Ch6) "A prompt causes your AI agent to expose confidential data." → "What production safeguards should have prevented this?"
10. (Ch3 and Ch9 — deliberately duplicated in both, since it's the same real question showing up in two different contexts) "Your evaluation score improved, but user satisfaction dropped." → "Which online metrics matter more than offline benchmarks?"

These verbatim entries and their variant clusters count toward each chapter's 8-12 entry minimum below, not on top of it. Chapters with no seed question here (5's second slot aside, and Chapter 8 entirely) still need their own originally-generated entries to hit the minimum.

Populate with at least 8-12 entries per chapter (so 70+ total) — the seed clusters above plus additional originally-generated entries for full coverage. Vary the `format` field across entries and actually write the entries differently depending on format — do not use one template for all of them (see Humanization section below for what this means concretely).

`question_bank.json` itself must not contain a full written answer for any entry — only the `key_concepts` tag, used solely for the mock interview's lightweight keyword check. Build a companion file, `solutions/question_bank_answers.json`, mapping each entry's `id` to a full written model answer covering its `key_concepts`. Keep this file entirely separate so `mock_interview.ipynb` and `per_chapter_drills.ipynb` never load or print a model answer during a live quiz session.

`mock_interview.ipynb`

An interactive, timed, randomized cross-chapter mock interview:

* Randomly samples N questions from `question_bank.json` (default 5, configurable), optionally filtered by chapter/difficulty.
* Presents each scenario, gives the learner a timer (soft — just prints elapsed time, doesn't hard-cut) to answer via `input()` or a blank markdown-style response cell, then reveals the follow-up.
* Where an entry's `key_concepts` are available, do a lightweight keyword-presence check against the learner's typed answer to give directional feedback ("you mentioned: faithfulness, recall@k — you didn't mention: groundedness"), explicitly framed as a rough signal, not a grade.
* Include at least one branching example: an interviewer follow-up that changes based on what the candidate said (e.g. if the answer mentions "add more GPUs," branch into a pushback follow-up; if it mentions "profile first," branch into a different, easier follow-up) — implement this as real conditional logic on keyword matches in the typed answer, to model how real interviews actually branch rather than presenting a clean, static Q&A pair.
* At the end of a session, print the list of question `id`s that were asked plus a pointer to `solutions/question_bank_answers.json` for full review. Do not load or display any model answer within the notebook itself, before or after the session.

`per_chapter_drills.ipynb`

A simpler, non-randomized, chapter-filtered version of the same question bank for focused review of one chapter at a time.

Humanization Requirements

Apply all of these — this is not optional polish, it materially affects whether the repository reads as a real, carefully-built resource versus obviously templated AI output:

1. Vary the question format. Do not let every entry in the question bank follow an identical "Your X does Y. Follow-up: Z?" structure — mix scenario-first, question-first, a Slack-message-style snippet, and a stakeholder-quote framing across different entries.
2. Ground some scenarios in real public incidents. Where genuinely relevant, base a scenario's failure pattern on a real public postmortem (e.g. well-known incident write-ups from companies that publish these), paraphrased into your own words and describing the general shape of the failure — never quote or closely mirror the original text, and include a `source_note` link in the question bank entry when you do this.
3. Write explanations with an actual point of view. Where the curriculum explains a tradeoff, state what you'd actually pick and why, rather than presenting a neutral, exhaustive pro/con list every time — this is what makes technical writing read as authored rather than generated.
4. Let the mock interview be messy. Use the branching logic described above rather than clean, static one-shot Q&A.
5. Disclose AI assistance and invite human review. In the README, state plainly that this content was built with AI assistance, and add a short section inviting practitioners to open a PR adding real interview questions they've actually been asked (with the same JSON schema), explicitly as a way to ground the question bank in real, current interview experience over time rather than relying solely on generated scenarios.

Citations and References

For this to be a legitimate, citable resource rather than an uncredited repackaging of others' work, every dataset, every named technique/pattern/algorithm the curriculum teaches, and every external library with a canonical paper needs a real citation — both a lightweight inline reference where it's first introduced, and a full entry in a repo-root `REFERENCES.md`.

Format: each `REFERENCES.md` entry follows `Author(s) (Year). "Title." Venue. URL or DOI/arXiv ID.` Organize the file with a "Datasets" section up top (license noted per dataset) followed by one section per chapter, matching the curriculum's own structure.

Inline citations: where a concept or technique is introduced in a chapter's concept markdown, add a short parenthetical citation the first time it's named — e.g. "...the ReAct pattern (Yao et al., 2022)..." — not on every subsequent mention, linking to the full entry in `REFERENCES.md`.

Critical — verify every citation before publishing, don't trust memory or this list. Citation accuracy is the entire point of doing this; a wrong author, year, or venue undermines the legitimacy it's meant to establish. Web-search and confirm every entry below (exact author list, year, venue, arXiv ID/DOI, and current URL, plus current license terms for datasets) before writing it into `REFERENCES.md` or any notebook. Treat the list below as "check this," not "trust this" — the same caution already applied to model names and pricing elsewhere in this document, for the same reason: guessed specifics are worse than an extra search.

Seed list, by chapter — verify each before use:

Datasets: SQuAD — Rajpurkar, Zhang, Lopyrev, Liang (2016), "SQuAD: 100,000+ Questions for Machine Comprehension of Text," EMNLP 2016, arXiv:1606.05250, license CC BY-SA 4.0 (confirmed on the canonical `rajpurkar/squad` Hugging Face dataset card — cite that specific repo, since mirrors sometimes mislabel the license; default to SQuAD 1.1, note 2.0's ~50,000 adversarial unanswerable questions as an optional abstention-teaching extension, not the default). SEC EDGAR filings — U.S. Securities and Exchange Commission, EDGAR full-text search and `data.sec.gov` submissions API, U.S. government work, public domain, no API key required, rate-limited to 10 requests/second with a descriptive `User-Agent` header required. GH Archive / `open-index/open-github` — GH Archive project (gharchive.org), public GitHub Events API data, structured Parquet mirror hosted as `open-index/open-github` on Hugging Face, license ODC-By v1.0 (attribution required — not unqualified "public," verify exact terms at build time). Its historical backfill is partial (not a gapless mirror to the present) — confirm the current backfill extent on the dataset card and pin a specific, verified date range before building exercises around it. PubMedQA — Jin et al. (2019), "PubMedQA: A Dataset for Biomedical Research Question Answering," arXiv:1909.06146, MIT license — optional complementary RAG corpus for Chapter 3. BEIR — Thakur et al. (2021), "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models" (verify exact arXiv ID/venue at build time) — optional, specifically the FiQA subset, for a second retrieval domain in Chapter 3. `bigcode/the-stack-github-issues` — BigCode Project, Hugging Face dataset card (verify current license at build time), real GitHub issue/PR threads — optional alternative messy-document source for Chapter 3's ingestion subsection.

Chapter 1: ReAct — Yao et al. (2022), "ReAct: Synergizing Reasoning and Acting in Language Models," arXiv:2210.03629.

Chapter 2: LangGraph — LangChain, Inc., LangGraph documentation (cite the live docs URL, not a paper). OpenClaw — official OpenClaw documentation (cite live URL; the project has been renamed before, so verify current name/URL at build time). Subagent management patterns (inline tool-call spawn, fan-out, persistent pools, peer-to-peer teams) — verify the current best citable source at build time (this space moves fast; prefer a live, still-accurate source over a stale one). Supervisor-worker as production default, and skills/subagents composition — practitioner consensus from multiple industry sources rather than one canonical/peer-reviewed paper; label as such in `REFERENCES.md` rather than presenting as academic fact, and confirm which specific source(s) are still live and citable before finalizing.

Chapter 3: RAG — Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 2020, arXiv:2005.11401. TF-IDF — Spärck Jones (1972), "A Statistical Interpretation of Term Specificity and Its Application in Retrieval," Journal of Documentation, 28(1), pp. 11–21, DOI 10.1108/eb026526. Embeddings — Mikolov et al. (2013), "Efficient Estimation of Word Representations in Vector Space," arXiv:1301.3781. FAISS — Johnson, Douze, Jégou (2017), "Billion-Scale Similarity Search with GPUs," arXiv:1702.08734. RAGAS — Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation," EACL 2024 (demo track), DOI 10.18653/v1/2024.eacl-demo.16 — prefer this peer-reviewed venue over the arXiv preprint (arXiv:2309.15217, 2023) for `REFERENCES.md`. Precision/recall/MRR — Manning, Raghavan, Schütze, Introduction to Information Retrieval, Cambridge University Press, 2008 (textbook reference for the metric definitions, not a single paper). Chroma and DeepEval — cite each project's live documentation/GitHub, no canonical paper. (SQuAD, PubMedQA, and BEIR are cited in the Datasets entry above, not repeated here.)

Chapter 4: Circuit breaker pattern — Michael T. Nygard, Release It!: Design and Deploy Production-Ready Software, Pragmatic Bookshelf, 2007 (2nd ed. 2018). Exponential backoff and jitter — Marc Brooker, "Exponential Backoff and Jitter," AWS Architecture Blog, 2015 (cite live URL).

Chapter 5: tiktoken — OpenAI, tiktoken documentation/GitHub (cite live URL). LoRA — Hu et al. (2021), "LoRA: Low-Rank Adaptation of Large Language Models," arXiv:2106.09685. QLoRA — Dettmers et al. (2023), "QLoRA: Efficient Finetuning of Quantized LLMs," arXiv:2305.14314. RLHF — Christiano, Leike, Brown, Martic, Legg, Amodei (2017), "Deep Reinforcement Learning from Human Preferences," NeurIPS 2017, arXiv:1706.03741, and Ouyang et al. (2022), "Training Language Models to Follow Instructions with Human Feedback," arXiv:2203.02155. Real traffic traces (optional) — Microsoft, `AzurePublicDataset` LLM inference traces, GitHub (cite live URL, verify current terms), or BurstGPT public LLM-serving workload trace (verify current citation/paper at build time).

Chapter 6: OpenClaw security guidance — official OpenClaw documentation, security/deployment section (cite live URL). Snowflake-managed MCP server governance guidance — Snowflake Documentation, "Snowflake-managed MCP server" (cite live URL; verify current wording, as this is an actively updated product page). Prompt injection — Greshake et al. (2023), "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," arXiv:2302.12173.

Chapter 7: Model Context Protocol — Anthropic, "Introducing the Model Context Protocol," November 2024, original announcement; current specification version at modelcontextprotocol.io (the spec has revised multiple times since — verify the current version number at build time). Governance: donated by Anthropic to the Agentic AI Foundation (AAIF), a directed fund under the Linux Foundation, co-founded by Anthropic, Block, and OpenAI (cite as AAIF/Linux Foundation, not "Linux Foundation" alone, and verify current status at build time). Snowflake MCP server — Snowflake-Labs, official GitHub repository and Snowflake Documentation (cite live URLs; verify current status). GitHub MCP server — GitHub, official `github/github-mcp-server` repository (cite live URL, verify current status). Pydantic — Pydantic documentation/GitHub, current major version 2.x (cite live URL).

Chapter 9: Canary releases / progressive delivery — Beyer, Jones, Petoff, Murphy (eds.), Site Reliability Engineering, O'Reilly, 2016, or Martin Fowler, "CanaryRelease," martinfowler.com (cite live URL). Docker — Docker, Inc., official documentation (cite live URL). OpenClaw containerized deployment — official OpenClaw documentation, install/hosting section (cite live URL).

Also applies to: the capstone README (cite LangGraph or the Claude Agent SDK the same way, plus OpenClaw as the real-world comparison), and Appendix B's prerequisite concepts (async I/O, testing, Docker — official docs are fine, no paper needed). Appendix C's question bank does not need citations — it's original scenario content per the "no scraped questions" constraint, not derived from a specific source.

Legitimacy and Trust

Beyond citations, these six things are required for the repo to be a credible, honest public resource rather than just a working one.

1. Accuracy review / errata process. Add a GitHub issue template specifically for "this explanation is technically wrong or outdated," separate from bug reports (which are about code not running, not about content being incorrect). In the README, explicitly invite practitioner review before treating the repo as a stable v1.0.
2. An honest Limitations section in the README, stated plainly, not implied. Cover: this prepares someone for AI-agent-engineering interviews and gives strong foundational skills, but finishing it does not make someone a senior engineer — that requires real production stakes, real scale, and organizational judgment no curriculum can simulate. It also does not fully prepare someone for a Forward Deployed Engineer or Solutions Engineer role by itself — those add a customer-facing, on-site dimension this repo can't replicate. Also state plainly: the "one follow-up question eliminates 9 of 10 candidates" framing that originally inspired this project's question set is an anecdotal claim from a social media post, not verified hiring data, and shouldn't be repeated as fact anywhere in the repo's own marketing/description.
3. A License section spelling out what governs what, since the repo mixes sources: MIT license for all original code and written content; Chapter 3's SQuAD-derived material carries SQuAD's own CC BY-SA 4.0 terms; Chapter 3's SEC EDGAR-derived material and Chapter 7's GH Archive-derived material are U.S. government/public-domain-sourced and carry no additional restriction beyond their own terms. State this explicitly rather than letting a single root `LICENSE` file imply everything in the repo is uniformly MIT.
4. A responsible-use note in Chapter 6, since its injection payloads work against a real model, not a mock: a short, clearly-flagged markdown cell near the top of the chapter stating this is for learning against your own systems only, and these techniques should not be pointed at systems you don't own or have authorization to test.
5. A staleness disclaimer with a "last verified" date. Add a short note near the top of `REFERENCES.md` (and echo it briefly in the README): the model names, pricing, and product specifics referenced throughout this repo reflect the state of the field as of the date the repo was built, are verified as of that date, and move fast — check the provider's current documentation directly rather than trusting a hardcoded figure written months or years earlier. Stamp `REFERENCES.md` with the actual build/verification date once building starts.
6. Standard governance files, both currently absent: `CONTRIBUTING.md`, formalizing the Humanization section's "submit real interview questions you've actually been asked" invitation into an actual PR process (schema, where to add entries, what a good submission looks like); `SECURITY.md`, a responsible-disclosure path for vulnerabilities in the repo's own code (its scripts, its CI, its dependencies) — distinct from Chapter 6's pedagogical content, which is a teaching exercise, not a real system to disclose against.

Add both new files to the repo root in the Repository Structure above.

Capstone (`capstone/`)

One combined, built project — not another concept→build→break→drill notebook. Build a single agent that combines: retrieval over the Chapter 3 synthetic corpus, tool use with the Chapter 7 schema-validated tools, memory across turns, and at least one safeguard from Chapter 6 — implemented using an actual framework rather than the from-scratch loop used in the early chapters (use LangGraph or the Claude Agent SDK; if using the Claude Agent SDK, note it's Anthropic-specific, so also confirm the capstone still works end-to-end if the learner set up OpenAI instead — LangGraph is the safer default for staying provider-agnostic). Reuse `agentlib/llm_client.py` and the account/key/spend-limit setup already done in Chapter 1 rather than asking the learner to set anything up again — default to the stronger-tier `model=` override on whichever provider is active, given this is the capstone quality bar, with a clear mock-mode fallback if no key is present. Include a `capstone/README.md` framing this explicitly as a portfolio piece: what it does, what it demonstrates, and how to run it on either provider or with no key at all. In that README, add a short "how this compares to a real system" note pointing to OpenClaw as a real, viral, production example combining the same pieces — retrieval/context, tool use, memory, and (per its own security docs) the exact injection risk Chapter 6 covers — so the capstone reads as a small version of something that actually exists at scale, not just a course exercise.

Packaging Requirements

* `README.md` at repo root: what this is (state the "ML to AI engineer transition" framing explicitly, including the scope boundary — no classical MLE/model training/MLOps infra), a Prerequisites section using the exact content below (don't reinvent this — it's already been refined), setup instructions, full chapter list with time estimates and one-line descriptions, a clear note that the course is meant to be run with a real Anthropic or OpenAI API key (with the recommended $15–20 spend-limit setup from Chapter 1) and that a mock/offline fallback exists purely for accessibility and CI, a note explaining that `solutions/` holds answers separately and is meant to be opened only after attempting each chapter's cold-answer questions, a pointer to `REFERENCES.md` for citations, a Limitations section (see below), a License section (see below), note on AI-assisted content per the Humanization section, and a CI status badge once the workflow below is in place.

Prerequisites section content — use this verbatim, adapting only formatting:

A quick gut-check before Chapter 1, not a mandatory review. This course assumes a data-science-level background — if that's you, most of this is already covered.

Already covered by a DS background — skip these: Python fundamentals, numpy/pandas, cosine similarity and vector math, core statistics, working in Jupyter.

Worth a 1–2 hour gut-check. If you can answer confidently without looking it up, skip it: (1) Async Python — `async def` vs. a regular function, when you need `await`, what happens if you don't (comes up in Chapter 1's multi-agent work and Chapter 2's subagent dispatch). (2) Testing — writing a `pytest` test with `assert`, unit vs. integration tests (Chapter 7's integration tests). (3) Environment management — virtual environments, what a `.env` file is for and why it's never committed (Chapter 1 walks through this fully regardless, written for a limited-Python-background reader — don't worry if this is new). (4) Transformer/LLM internals, conceptually — what a token roughly is, what a context window means (if your program predates ~2022 or was stats-heavy rather than NLP-heavy, this may be genuinely new — Chapter 1 introduces it properly). (5) Docker basics — only matters for Chapter 9's containerization subsection.

Not needed: deep software architecture experience, prior agent-framework exposure (that's what this course teaches), calculus/linear algebra beyond a DS background.

A few things get their own built-in review, so don't pre-study them: TF-IDF, embeddings-as-semantic-space, and MRR each get a short refresher at the start of Chapter 3. LoRA/QLoRA, catastrophic forgetting, RLHF, and RL's role in agent development are taught conceptually in Chapter 5.

If none of the five gut-check items raise a flag, start Chapter 1 with zero additional prep.

* `LICENSE`: MIT.
* `requirements.txt`: pin every dependency version. Expected dependencies include at minimum: `jupyter`, `numpy`, `scikit-learn`, `sentence-transformers`, `chromadb` (or `faiss-cpu`), `tiktoken`, `pydantic`, `python-dotenv`, `anthropic`, `openai`, plus `pytest` and `nbmake` as dev/test dependencies. Add anything else you determine is genuinely needed.
* `.env.example`: shows `LLM_PROVIDER=anthropic` (or `openai`) plus both `ANTHROPIC_API_KEY=` and `OPENAI_API_KEY=` with no real values, and a comment explaining the account/key/spend-limit setup happens once in Chapter 1 (including the recommended $15–20 spend-limit step) and is reused as the primary path in Chapters 2, 3, 4, 6, 7, and the capstone.
* `.gitignore`: must include `.env`, `__pycache__/`, `.ipynb_checkpoints/`, standard Python/venv entries, and any local model-cache directories created by `sentence-transformers`.

Testing and CI

* `tests/test_notebooks.py`: uses `pytest` with `nbmake` (or an equivalent headless-execution approach) to actually execute every notebook in `curriculum/`, `interview_prep/`, and `capstone/` and assert zero errors. Even though the real API is the primary path for a human learner, CI itself must run with no API key present, so verify the mock/fallback paths are exercised and pass cleanly on their own, without secrets.
* `tests/test_agentlib.py`: standard unit tests for the shared functions in `agentlib/` (loop guards, eval metrics, synthetic data generators — assert determinism given a fixed seed).
* `.github/workflows/ci.yml`: a GitHub Actions workflow that installs `requirements.txt` and runs the full test suite on every push and pull request, with no secrets required. Add the resulting status badge to the README.

Build Process

This build is intentionally split across many separate sessions — one unit of work per session — to stay within usage limits. Do not build more than one unit in a single invocation, even if there's budget left over after finishing one.

The units, in order

1. Scaffold the full repository structure and every packaging file (`README.md`, `LICENSE`, `requirements.txt`, `.env.example`, `.gitignore`, the full empty directory structure, stub/placeholder notebooks). Also create `PROGRESS.md` at the repo root with all 13 units below listed as an unchecked checklist.
2. Chapter 1 notebook + its `solutions/ch01_fundamentals_answers.md`.
3. Chapter 2 notebook + its solutions file — loop guards and tools stay inline per the design rationale above, but this is where `agentlib/tracing.py` gets built (new this chapter) and `agentlib/llm_client.py` from Chapter 1 gets its first reuse.
4. Chapter 3 notebook + its solutions file — also the point where `agentlib/synthetic_data.py` and `eval_metrics.py` get built.
5. Chapter 4 notebook + its solutions file.
6. Chapter 5 notebook + its solutions file.
7. Chapter 6 notebook + its solutions file.
8. Chapter 7 notebook + its solutions file.
9. Chapter 8 notebook + its solutions file.
10. Chapter 9 notebook + its solutions file.
11. `interview_prep/` in full — `question_bank.json`, `solutions/question_bank_answers.json`, `mock_interview.ipynb`, `per_chapter_drills.ipynb`.
12. `capstone/` in full.
13. CI setup (`tests/`, `.github/workflows/ci.yml`) plus one full clean-environment run (fresh venv, `requirements.txt` only, no `.env`) to confirm everything CI will check actually passes.

Within each session

* Do the work for that unit only — nothing from the next unit, even opportunistically.
* Actually execute whichever notebook(s) you touched, headlessly, and confirm zero errors before considering the unit done.
* Make one meaningful, scoped git commit for the unit (e.g. `feat(ch3): add RAG evaluation notebook with 5 break-it scenarios`).
* Update `PROGRESS.md`: check off the completed unit, note anything the next session needs to know (assumptions made, anything left partially done, anything that deviated from this spec and why), and name the next unit explicitly.
* Stop there. Do not start the next unit in the same session.

`PROGRESS.md`

A build log at the repo root — not part of the published curriculum itself, but fine to leave in the repo afterward as a record of the build, or delete once everything's done. At the start of every session: read this file first, sanity-check that the repo's actual state matches what it claims (the files it says are done actually exist and still pass), then do exactly the next unchecked unit and nothing more.

To resume between sessions, the human only needs to say something like "continue the build" — read `PROGRESS.md` and pick up from there without needing this whole document repeated.

Final Acceptance Checklist

Before considering this complete, confirm all of the following are true:

* [ ] Every notebook in `curriculum/`, `interview_prep/`, and `capstone/` executes top-to-bottom with zero errors using only `requirements.txt`, with no `.env` file present.
* [ ] Every "break it" section demonstrates a real failure and a real fix with visible before/after output.
* [ ] All synthetic data generation is seeded and reproducible.
* [ ] The real-API path (Chapters 1, 2, 3, 4, 6, 7, and the capstone) works correctly on both Anthropic and OpenAI via the `LLM_PROVIDER` toggle, and every one of those notebooks also still passes with no key present, using the mock fallback.
* [ ] Chapter 1's setup section includes account creation, the spend-limit step (before key generation) for both providers, and a $15–20 recommended ceiling, and Chapters 2, 3, 4, 6, 7, and the capstone all reuse `agentlib/llm_client.py` rather than reimplementing their own provider-specific API calls.
* [ ] `question_bank.json` has 70+ entries across varied formats, none of them scraped from real interview-question sites.
* [ ] All 10 seed scenario/follow-up pairs appear verbatim in `question_bank.json`, each with at least 5 variant entries in the same chapter.
* [ ] The README accurately scopes the course (transition course, not full "become an AI engineer," not classical MLE/MLOps) and discloses AI-assisted content.
* [ ] `.env` is git-ignored and no real credentials of any kind appear anywhere in the repo, including in git history.
* [ ] CI passes on a clean run.
* [ ] `PROGRESS.md` shows all 13 units checked off, and its state matches the actual repo — nothing marked done that doesn't exist or doesn't pass.
* [ ] `REFERENCES.md` exists, is organized by chapter plus a datasets section, and every citation (dataset, technique, library) was verified via search at build time rather than copied from the seed list unchecked — no fabricated authors, years, or URLs.
* [ ] Every cold-answer / interview-drill question across all 9 chapters, and every entry in `question_bank.json`, has a corresponding full written model answer in `solutions/` — and no notebook, and no entry in `question_bank.json` itself, contains an inline model answer.
* [ ] README includes the verbatim Prerequisites section, a Limitations section (including the "9 of 10 candidates" anecdote disclaimer), and a License section clarifying MIT vs. CC BY-SA 4.0 (SQuAD) vs. public domain (SEC EDGAR, GH Archive) per part of the repo.
* [ ] `CONTRIBUTING.md` and `SECURITY.md` exist at the repo root.
* [ ] Chapter 6's notebook opens with the responsible-use note before any other content.
* [ ] `REFERENCES.md` is stamped with the actual date it was verified/built, and the README echoes the staleness disclaimer.
