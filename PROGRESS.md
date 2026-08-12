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
- [x] **Unit 3 — Chapter 2: Agent Control Flow.** Notebook + solutions file. Loop guards and
      tools stay inline per the design rationale, but `agentlib/tracing.py` gets built here,
      and `agentlib/llm_client.py` gets its first reuse.
- [x] **Unit 4 — Chapter 3: RAG and Retrieval Evaluation.** Notebook + solutions file.
      Builds `agentlib/synthetic_data.py` and `agentlib/eval_metrics.py`. Pulls and caches
      SQuAD 1.1 and a real messy-document source; fills in the Datasets + Chapter 3 sections
      of `REFERENCES.md`.
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

## Notes from Unit 3

- **`agentlib/tracing.py` built for real.** A `Tracer`/`Span` pair with two ways to log a
  hop: `tracer.span(name, **meta)` as a context manager (measures real wall-clock time) and
  `tracer.record(name, duration_ms, **meta)` (logs an explicit, possibly-simulated duration
  without actually sleeping) — the notebook uses `record()` throughout so the multi-agent
  demo stays fast in CI while still teaching realistic per-hop latency numbers.
- **`agentlib/llm_client.py` reused for the first time**, exactly as planned — Jack's
  planner, Bob's subagent calls, and Mike's critic each get a real-vs-mock toggle via
  `HAS_KEY`, same pattern as Chapter 1.
- **Dropped `tiktoken` from this chapter's leaky-subagent demo.** `tiktoken.get_encoding()`
  downloads its BPE vocab file from `openaipublic.blob.core.windows.net` on first use, and
  this build session's sandboxed egress policy blocks that host outright (confirmed via the
  proxy's own diagnostics — a permanent policy block, not a transient network error, so not
  something to retry around). Beyond just blocking verification in this specific
  environment, requiring a live external download inside a notebook that must "execute with
  zero errors" under Hard Constraint #3 is fragile on its own merits regardless of network
  policy. Chapter 2's break-it #4 (leaky subagent) now measures a dependency-free word-count
  proxy instead of exact token counts, explicitly labeled as an approximation, with a note
  that Chapter 5 is where the spec calls for real tiktoken-based tokenization to be
  introduced properly. **Unit 6 (Chapter 5) will need to solve this network-robustness
  problem for real** (likely a try/except fallback from real tiktoken to an approximate
  counter, so the notebook stays robust to network variability in any environment) — flagged
  here so that session doesn't hit the same wall unprepared.
- **Caught and fixed a spec-compliance bug before finishing:** the cold-diagnosis exercise
  in the interview-prep section originally included inline "Answer: ..." reveals directly in
  the notebook markdown, violating the hard constraint that no notebook may contain an
  inline model answer. Fixed by moving all four diagnoses into
  `solutions/ch02_control_flow_answers.md` and leaving only the bare symptom prompts in the
  notebook, with a pointer to the solutions file. Re-verified Chapter 1 doesn't have the same
  issue (it doesn't — its cold-answer questions were pointer-only from the start).
- **Verification:** `pytest --nbmake` across all 12 notebooks + `tests/` with no `.env`
  present — 28/28 pass. The notebook was executed in place afterward
  (`jupyter nbconvert --execute --inplace`) so its committed version shows real example
  output — including, notably, the hash-based cycle guard visibly failing to catch the
  Jack/Mike cycle (running the full 8 rounds) right next to the semantic guard catching it
  in 2, which is the clearest before/after in the chapter.
- `REFERENCES.md`'s Chapter 2 section is now filled in (LangGraph docs, OpenClaw docs,
  Schmid's subagent-patterns article, and a labeled practitioner-consensus note for the
  supervisor-worker/skills claims that aren't from one canonical source).

## Notes from Unit 4

**Environment reachability check (done first, per Unit 3's own advice) — three of Chapter
3's planned real-data sources are unreachable from this build environment, one substitute
found per source:**

- `huggingface.co`, `hf.co`, and every `*.huggingface.co` CDN host (including
  `cdn-lfs.huggingface.co`) are blocked by this session's egress policy — same permanent,
  non-retryable 403 pattern as Unit 3's tiktoken finding. This rules out the Hugging Face
  `datasets` library for SQuAD, `sentence-transformers`' model download, and (later, Unit 8's
  problem) the GH Archive slice.
- `data.sec.gov` **and** `www.sec.gov` are both blocked the same way — SEC EDGAR is entirely
  unreachable from this environment, not just its API host.
- `raw.githubusercontent.com`, `api.github.com`, `release-assets.githubusercontent.com`, and
  `pypi.org` are all reachable. This unlocked three substitutions, each real data from an
  official/canonical source, just fetched through a different (allowed) channel than the
  spec suggested:
  1. **SQuAD 1.1** — fetched directly from `rajpurkar/SQuAD-explorer`'s `dev-v1.1.json` on
     `raw.githubusercontent.com` (the dataset author's own canonical repo) instead of
     `datasets.load_dataset("rajpurkar/squad")`. Same real data, same license (CC BY-SA
     4.0), different access mechanism. Extracted a seeded, deterministic sample (28
     passages, 55 QA pairs) and cached it at `data/rag_corpus/squad_sample.json` — committed
     to the repo, so no notebook run (including CI) ever needs network access for it.
  2. **Messy real-world document source** — the spec's two suggested options (SEC EDGAR;
     `bigcode/the-stack-github-issues` on Hugging Face) are both unreachable here. Live
     GitHub Issues API access for an arbitrary third-party repo also isn't available without
     escalating this session's repo-scoped GitHub access beyond what this task actually
     needs (attempted against `anthropics/anthropic-sdk-python`'s issues endpoint; got a
     scoping error, not a network block — see `add_repo`'s own guidance not to attach a repo
     the task doesn't genuinely need, and requesting push/API access for a read-only content
     pull would violate least-privilege for no reason). Substituted a real, messy, genuinely
     un-fabricated document instead: `anthropics/anthropic-sdk-python`'s actual
     `CHANGELOG.md` (900 lines / ~2,575 words, fetched anonymously via
     `raw.githubusercontent.com`, no repo attachment needed), which has exactly the
     properties the ingestion exercise needs — real inconsistent formatting, embedded
     commit/PR links, and (usefully) many genuinely near-duplicate release-note sections,
     which turns out to be a *better* fit for the deduplication exercise specifically than a
     generic issues dump would have been. Cached at
     `data/rag_corpus/messy_source_changelog.md`.
  3. **Local embeddings** — swapped `sentence-transformers` (needs a `huggingface.co` model
     download at runtime) for **spaCy's `en_core_web_md`**, whose model ships as one
     self-contained wheel hosted on a GitHub release
     (`github.com/explosion/spacy-models/releases/...`, confirmed reachable and installable
     via `pip install -r requirements.txt` directly — no separate download step for anyone,
     regardless of their own network's access to Hugging Face). Verified end-to-end: real
     300-dim GloVe-style vectors load and produce sensible similarity ordering. This is a
     `requirements.txt` change from Unit 1's original pins, documented here as a deliberate,
     verified substitution — not a silent scope cut.
- **Chroma vs. FAISS:** Unit 1 already chose `faiss-cpu` over `chromadb` for CI reliability
  reasons unrelated to network access; that decision stands and turned out to be additionally
  correct here since FAISS needs no runtime download at all (indexes are built from your own
  embeddings).
- **PubMedQA / BEIR (optional complementary corpora):** both Hugging-Face-hosted and
  therefore unreachable here too. Per spec these are optional "if you want more practice"
  pointers, not required content — kept as a closing-cell markdown pointer only, no runnable
  code cell, so this doesn't block the chapter.
- **Caught one real bug via output inspection, not just green tests:** the first version of
  break-it #3 (answer split across two chunks) used a mock `template_generate` that only
  ever extracted one single best-matching sentence globally, so its "fix" cell (retrieving
  both chunks) produced the exact same one-sentence answer as the "bug" cell — the before/
  after showed no visible difference, which fails the hard constraint that a fix must
  visibly resolve the bug even though nothing raised an exception. Fixed by having
  `template_generate` pull the best sentence from *each* retrieved doc instead of one global
  best; re-verified the fix cell now genuinely shows both facts appearing together.
- **break-it #5 (offline/online divergence) needed a redesign for the same "looks right but
  isn't" reason:** the first version wrapped a retriever to "return more results," but
  `eval_metrics.precision_at_k`/`recall_at_k` truncate to `k` internally regardless of how
  many results a retriever function returns, so v1 and v2 would have scored identically —
  caught this by re-reading the code before running it, not empirically. Redesigned v2 as a
  bigram-augmented TF-IDF retriever (a real, mechanistic ranking difference) — which then, in
  the actual run, won on *both* the offline and simulated-online metrics rather than
  diverging as hoped. Per spec this scenario is explicitly meant to be simulated, so rather
  than keep searching for a real mechanistic change that happens to diverge the "right" way,
  the online-satisfaction signal was rebuilt as a transparently hand-constructed, clearly
  -labeled simulation (see the notebook's docstring for that function) — honest about being
  illustrative rather than dressing up an empirical result that didn't cooperate.
- **Verification:** `pytest --nbmake` across all 12 notebooks + `tests/` with no `.env`
  present — 36/36 pass (22 `agentlib` unit tests now, up from 14, covering
  `eval_metrics`/`synthetic_data`). Notebook executed in place afterward so its committed
  version shows real output throughout, including the actual (not hypothetical) TF-IDF-
  beats-embeddings result on this corpus — left as-is rather than tuned to fit a preferred
  narrative, since it's a real, honestly-obtained measurement.
- `REFERENCES.md`'s Datasets and Chapter 3 sections are filled in — all citations
  (SQuAD, RAG, TF-IDF, embeddings, FAISS, RAGAS, the IR-metrics textbook, spaCy, PubMedQA,
  BEIR) verified via live search at build time.

**Next unit:** Unit 5 — Chapter 4 notebook (`curriculum/04_production_reliability.ipynb`) and
`solutions/ch04_production_reliability_answers.md`.
