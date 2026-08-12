# Build Progress

This is the build log for `ai-agent-interview-prep`, tracked against the original build
specification. It is not part of the published curriculum — it can stay as a build record or
be deleted once everything's done.

**How to resume:** at the start of every session, read this file first, sanity-check that the
repo's actual state matches what it claims (files marked done actually exist and still pass),
then do exactly the next unchecked unit and nothing more. Do not start a unit out of order,
and do not do more than one unit per session even with budget left over.

## Units

- [x] **Unit 1 — Scaffold.** Full repository structure, all packaging/governance files
      (`README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `REFERENCES.md` skeleton,
      `requirements.txt`, `.env.example`, `.gitignore`), this `PROGRESS.md`, and
      stub/placeholder notebooks and modules throughout.
- [x] **Unit 2 — Chapter 1: Fundamentals of AI Agents.** Notebook +
      `solutions/ch01_fundamentals_answers.md`. Builds `agentlib/llm_client.py` for real
      (the one exception to "build inline first" — every later real-API chapter needs it
      immediately).
- [ ] **Unit 3 — Chapter 2: Agent Control Flow.** Notebook + solutions file. Loop guards and
      tools stay inline per the design rationale, but `agentlib/tracing.py` gets built here,
      and `agentlib/llm_client.py` gets its first reuse.
- [ ] **Unit 4 — Chapter 3: RAG and Retrieval Evaluation.** Notebook + solutions file.
      Builds `agentlib/synthetic_data.py` and `agentlib/eval_metrics.py`. Pulls and caches
      SQuAD 1.1 and SEC EDGAR filings; fills in the Datasets + Chapter 3 sections of
      `REFERENCES.md`.
- [ ] **Unit 5 — Chapter 4: Production Reliability.** Notebook + solutions file.
- [ ] **Unit 6 — Chapter 5: Cost, Performance, and Model Selection.** Notebook + solutions
      file.
- [ ] **Unit 7 — Chapter 6: Security and Safeguards.** Notebook + solutions file.
      Responsible-use note must be the first cell.
- [ ] **Unit 8 — Chapter 7: Tool Integration.** Notebook + solutions file. Builds a real
      local MCP server over stdio; pulls and caches a filtered GH Archive slice
      (`open-index/open-github`) — pin the exact date range used, verified against the
      dataset card at build time.
- [ ] **Unit 9 — Chapter 8: System Design and Engineering Judgment.** Notebook + solutions
      file. Mostly markdown; blank design-doc templates in the notebook, fully worked model
      versions only in `solutions/ch08_system_design_judgment_answers.md`.
- [ ] **Unit 10 — Chapter 9: LLMOps and Deployment.** Notebook + solutions file. Includes a
      working `Dockerfile` for the curriculum's agent.
- [ ] **Unit 11 — `interview_prep/` in full.** `question_bank.json` (70+ entries, all 10
      seed scenario/follow-up pairs verbatim plus 5+ variants each),
      `solutions/question_bank_answers.json`, `mock_interview.ipynb`,
      `per_chapter_drills.ipynb`.
- [ ] **Unit 12 — `capstone/` in full.** `capstone/README.md` + `capstone_agent.ipynb`, built
      on LangGraph or the Claude Agent SDK, reusing `agentlib/llm_client.py` and Chapter 1's
      account setup. Fills in the capstone section of `REFERENCES.md`.
- [ ] **Unit 13 — CI.** `tests/test_notebooks.py` and `tests/test_agentlib.py` made real
      (not stubs), `.github/workflows/ci.yml`, README CI badge wired up, plus one full clean
      -environment run (fresh venv, `requirements.txt` only, no `.env`) confirming everything
      CI checks actually passes.

## Notes from Unit 1

**Assumptions made (documented here per the build spec's instruction to log deviations):**

- **Repo layout:** the spec's repository-structure diagram shows `ai-agent-interview-prep/`
  as if it were its own repo root. This repo (`joshlaubach/learning-agentic-ai`) was empty
  except for `.claude/skills/` and had no existing content or conventions, and the working
  branch (`claude/interview-prep-repo-build-*`) is clearly dedicated to this build — so
  everything was scaffolded at the **repository root**, not nested under an
  `ai-agent-interview-prep/` subfolder. If this repo turns out to be intended as a
  multi-project monorepo, this would need to move.
- **Package manager:** `pip` + a plain venv, not `uv`/`poetry` (both available in the build
  environment but not chosen) — because the spec hard-requires a root `requirements.txt` and
  the course's own stated audience has a limited Python background, for whom
  `pip install -r requirements.txt` is the simplest thing to teach and debug.
- **Vector store:** the spec allows "Chroma (or FAISS)" for Chapter 3's local-vector-store
  section. Chose **`faiss-cpu`** over `chromadb` for `requirements.txt` — lighter dependency
  footprint (no bundled ONNX runtime), more reliable to install headlessly in CI. Chapter 3's
  notebook (Unit 4) should still *describe* Chroma as an alternative real vector-store option
  per spec, even though the installed/runnable example uses FAISS.
- **SDK version pins:** `anthropic==0.121.0` and `openai==1.109.1` were pinned to the latest
  *stable, well-documented API-shape* versions available at build time — note that `openai`
  and `mcp` both had newer major versions on PyPI (`openai` 2.x/3.x, `mcp` 2.x) at pin time
  that were deliberately **not** used, since their API surface is unverified against this
  build's knowledge and picking a version whose `client.chat.completions.create(...)` /
  `client.messages.create(...)` shape is well-understood was judged safer for the chapters
  that write code against these SDKs. **Unit 2 (Anthropic) and Unit 8 (MCP) should
  re-verify these pins still match the SDK calls being written and bump if there's a good
  reason to** — this was a deliberate, documented judgment call, not an oversight.
- **`REFERENCES.md` is intentionally incremental** — Unit 1 only laid down section headers
  and the staleness disclaimer. Each chapter unit fills in its own section as that chapter's
  real content (and therefore its real citations) gets built and verified.
- **PR strategy:** no PR existed yet for this branch at the start of Unit 1. Opened a draft
  PR after this unit's push; later units should just push additional commits to the same
  branch/PR rather than opening new ones, per the standing instruction to open a PR only if
  one doesn't already exist.
- **Verification scope for Unit 1:** since there's no real chapter content yet, "notebooks
  execute cleanly" for this unit means the *stub* notebooks (title cell + an
  "under construction" note) parse and execute with zero errors, and `agentlib` imports
  cleanly as a package — confirming the toolchain the next 12 units depend on actually works,
  not that any real curriculum content is correct yet (there isn't any).

## Notes from Unit 2

- **`agentlib/llm_client.py` built for real.** Provider-agnostic `call_model()`, `ToolCall`/
  `ModelResponse` dataclasses, `format_tool_result()` / `format_assistant_tool_call()`
  helpers so callers never branch on `LLM_PROVIDER` themselves, and retry-on-429 with
  exponential backoff + jitter. `HAS_KEY` is derived from whichever key env var matches
  `LLM_PROVIDER`.
- **Model pricing/names were re-verified via live web search at Unit 2 build time**, not
  copied from the original spec unchecked (per the spec's own instruction). One correction
  worth flagging: the spec assumed Claude Sonnet 5's introductory $2/$10 pricing would revert
  to $3/$15 on 2026-09-01 — search confirmed Anthropic instead made $2/$10 **permanent** on
  2026-08-11. The notebook and `agentlib/llm_client.py` reflect the corrected, verified
  figure, not the spec's original assumption. OpenAI's GPT-5.6 Luna pricing was reported
  inconsistently across sources at verification time, so neither the notebook nor the code
  hardcodes a number for it — both point to the live OpenAI pricing page instead, per spec.
- **`real_llm_brain` is a class (`RealLLMBrain`), not a plain function**, despite the spec
  describing a `real_llm_brain()` function. It's still a drop-in callable matching
  `fake_llm_brain`'s exact `brain(messages) -> {"action": ..., "action_input": ...}`
  interface — the class form was needed to correctly maintain provider-native multi-turn
  tool-call state (proper Anthropic `tool_use`/`tool_result` pairing, proper OpenAI
  `tool_calls`/`role: tool` pairing) across a run, which a stateless function couldn't do
  without either re-deriving state each call or losing protocol correctness. Documented here
  since it's a deliberate deviation from the letter of the spec, not an oversight.
- **Verification:** `pytest --nbmake` run against all 12 notebooks + `tests/` with no `.env`
  present — 24/24 pass (12 notebooks execute cleanly via their mock-path fallback, 10 new
  `agentlib.llm_client` unit tests, 2 notebook-JSON sanity tests, plus the 1 pre-existing
  `agentlib` import test). The notebook was executed in place afterward
  (`jupyter nbconvert --execute --inplace`) so its committed version shows real example
  output from the mock path, not blank cells.
- `REFERENCES.md`'s Chapter 1 section is now filled in (ReAct citation, plus a note on the
  Sonnet 5 pricing correction above).

**Next unit:** Unit 3 — Chapter 2 notebook (`curriculum/02_control_flow.ipynb`) and
`solutions/ch02_control_flow_answers.md`. Builds `agentlib/tracing.py`; loop guards and tools
stay inline per the design rationale, reusing `agentlib/llm_client.py` from Unit 2 for the
first time.
