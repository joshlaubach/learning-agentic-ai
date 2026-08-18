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
- [x] **Unit 5 — Chapter 4: Production Reliability.** Notebook + solutions file.
- [x] **Unit 6 — Chapter 5: Cost, Performance, and Model Selection.** Notebook + solutions
      file.
- [x] **Unit 7 — Chapter 6: Security and Safeguards.** Notebook + solutions file.
      Responsible-use note must be the first cell.
- [x] **Unit 8 — Chapter 7: Tool Integration.** Notebook + solutions file. Builds a real
      local MCP server over stdio; pulls and caches a filtered GH Archive slice
      (`open-index/open-github`) — pin the exact date range used, verified against the
      dataset card at build time.
      > **Partially delivered.** The MCP half shipped and is real: `curriculum/_ch07_mcp_server.py`
      > is a genuine stdio server, and Chapter 7 connects to it over a real transport. The GH
      > Archive slice was never built. The chapter's tool reads from a small committed cache of
      > real PyPI metadata (`data/pypi_cache/`, three packages) instead, which serves the same
      > teaching purpose — a real external tool with a real schema — without the Hugging Face
      > reachability problem this environment has (see Unit 4's notes). This box stayed checked
      > with the unbuilt half unmarked; it is annotated here rather than unchecked because the
      > chapter itself is complete and shipped. `datasets`, `huggingface_hub` and `duckdb`
      > were all dropped from `requirements.txt` in the same pass: all three were pinned for
      > this feature and nothing in the repo imports any of them.
- [x] **Unit 9 — Chapter 8: System Design and Engineering Judgment.** Notebook + solutions
      file. Mostly markdown; blank design-doc templates in the notebook, fully worked model
      versions only in `solutions/ch08_system_design_judgment_answers.md`.
- [x] **Unit 10 — Chapter 9: LLMOps and Deployment.** Notebook + solutions file. Includes a
      working `Dockerfile` for the curriculum's agent.
- [x] **Unit 11 — `interview_prep/` in full.** `question_bank.json` (70+ entries, all 10
      seed scenario/follow-up pairs verbatim plus 5+ variants each),
      `solutions/question_bank_answers.json`, `mock_interview.ipynb`,
      `per_chapter_drills.ipynb`.
- [x] **Unit 12 — `capstone/` in full.** `capstone/README.md` + `capstone_agent.ipynb`, built
      on LangGraph or the Claude Agent SDK, reusing `agentlib/llm_client.py` and Chapter 1's
      account setup. Fills in the capstone section of `REFERENCES.md`.
- [x] **Unit 13 — CI.** `tests/test_notebooks.py` and `tests/test_agentlib.py` made real
      (not stubs), `.github/workflows/ci.yml`, README CI badge wired up, plus one full clean
      -environment run (fresh venv, `requirements.txt` only, no `.env`) confirming everything
      CI checks actually passes.

## Notes from Unit 1

Assumptions made (documented here per the build spec's instruction to log deviations):

- Repo layout: the spec's repository-structure diagram shows `ai-agent-interview-prep/`
  as if it were its own repo root. This repo (`joshlaubach/learning-agentic-ai`) was empty
  except for `.claude/skills/` and had no existing content or conventions, and the working
  branch (`claude/interview-prep-repo-build-*`) is clearly dedicated to this build, so
  everything was scaffolded at the repository root, not nested under an
  `ai-agent-interview-prep/` subfolder. If this repo turns out to be intended as a
  multi-project monorepo, this would need to move.
- Package manager: `pip` + a plain venv, not `uv`/`poetry` (both available in the build
  environment but not chosen), because the spec hard-requires a root `requirements.txt` and
  the course's own stated audience has a limited Python background, for whom
  `pip install -r requirements.txt` is the simplest thing to teach and debug.
- Vector store: the spec allows "Chroma (or FAISS)" for Chapter 3's local-vector-store
  section. Chose **`faiss-cpu`** over `chromadb` for `requirements.txt`, lighter dependency
  footprint (no bundled ONNX runtime), more reliable to install headlessly in CI. Chapter 3's
  notebook (Unit 4) should still *describe* Chroma as an alternative real vector-store option
  per spec, even though the installed/runnable example uses FAISS.
- SDK version pins: `anthropic==0.121.0` and `openai==1.109.1` were pinned to the latest
  *stable, well-documented API-shape* versions available at build time. Note that `openai`
  and `mcp` both had newer major versions on PyPI (`openai` 2.x/3.x, `mcp` 2.x) at pin time
  that were deliberately not used, since their API surface is unverified against this
  build's knowledge and picking a version whose `client.chat.completions.create(...)` /
  `client.messages.create(...)` shape is well-understood was judged safer for the chapters
  that write code against these SDKs. Unit 2 (Anthropic) and Unit 8 (MCP) should
  re-verify these pins still match the SDK calls being written and bump if there's a good
  reason to; this was a deliberate, documented judgment call, not an oversight.
- `REFERENCES.md` is intentionally incremental: Unit 1 only laid down section headers
  and the staleness disclaimer. Each chapter unit fills in its own section as that chapter's
  real content (and therefore its real citations) gets built and verified.
- PR strategy: no PR existed yet for this branch at the start of Unit 1. Opened a draft
  PR after this unit's push; later units should just push additional commits to the same
  branch/PR rather than opening new ones, per the standing instruction to open a PR only if
  one doesn't already exist.
- Verification scope for Unit 1: since there's no real chapter content yet, "notebooks
  execute cleanly" for this unit means the *stub* notebooks (title cell + an
  "under construction" note) parse and execute with zero errors, and `agentlib` imports
  cleanly as a package, confirming the toolchain the next 12 units depend on actually works,
  not that any real curriculum content is correct yet (there isn't any).

## Notes from Unit 2

- **`agentlib/llm_client.py` built for real.** Provider-agnostic `call_model()`, `ToolCall`/
  `ModelResponse` dataclasses, `format_tool_result()` / `format_assistant_tool_call()`
  helpers so callers never branch on `LLM_PROVIDER` themselves, and retry-on-429 with
  exponential backoff + jitter. `HAS_KEY` is derived from whichever key env var matches
  `LLM_PROVIDER`.
- Model pricing/names were re-verified via live web search at Unit 2 build time, not
  copied from the original spec unchecked (per the spec's own instruction). One correction
  worth flagging: the spec assumed Claude Sonnet 5's introductory $2/$10 pricing would revert
  to $3/$15 on 2026-09-01 — search confirmed Anthropic instead made $2/$10 **permanent** on
  2026-08-11. The notebook and `agentlib/llm_client.py` reflect the corrected, verified
  figure, not the spec's original assumption. OpenAI's GPT-5.6 Luna pricing was reported
  inconsistently across sources at verification time, so neither the notebook nor the code
  hardcodes a number for it — both point to the live OpenAI pricing page instead, per spec.
- `real_llm_brain` is a class (`RealLLMBrain`), not a plain function, despite the spec
  describing a `real_llm_brain()` function. It's still a drop-in callable matching
  `fake_llm_brain`'s exact `brain(messages) -> {"action": ..., "action_input": ...}`
  interface — the class form was needed to correctly maintain provider-native multi-turn
  tool-call state (proper Anthropic `tool_use`/`tool_result` pairing, proper OpenAI
  `tool_calls`/`role: tool` pairing) across a run, which a stateless function couldn't do
  without either re-deriving state each call or losing protocol correctness. Documented here
  since it's a deliberate deviation from the letter of the spec, not an oversight.
- Verification: `pytest --nbmake` run against all 12 notebooks + `tests/` with no `.env`
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
- `agentlib/llm_client.py` reused for the first time, exactly as planned — Jack's
  planner, Bob's subagent calls, and Mike's critic each get a real-vs-mock toggle via
  `HAS_KEY`, same pattern as Chapter 1.
- Dropped `tiktoken` from this chapter's leaky-subagent demo. `tiktoken.get_encoding()`
  downloads its BPE vocab file from `openaipublic.blob.core.windows.net` on first use, and
  this build session's sandboxed egress policy blocks that host outright (confirmed via the
  proxy's own diagnostics — a permanent policy block, not a transient network error, so not
  something to retry around). Beyond just blocking verification in this specific
  environment, requiring a live external download inside a notebook that must "execute with
  zero errors" under Hard Constraint #3 is fragile on its own merits regardless of network
  policy. Chapter 2's break-it #4 (leaky subagent) now measures a dependency-free word-count
  proxy instead of exact token counts, explicitly labeled as an approximation, with a note
  that Chapter 5 is where the spec calls for real tiktoken-based tokenization to be
  introduced properly. Unit 6 (Chapter 5) will need to solve this network-robustness
  problem for real (likely a try/except fallback from real tiktoken to an approximate
  counter, so the notebook stays robust to network variability in any environment) — flagged
  here so that session doesn't hit the same wall unprepared.
- Caught and fixed a spec-compliance bug before finishing: the cold-diagnosis exercise
  in the interview-prep section originally included inline "Answer: ..." reveals directly in
  the notebook markdown, violating the hard constraint that no notebook may contain an
  inline model answer. Fixed by moving all four diagnoses into
  `solutions/ch02_control_flow_answers.md` and leaving only the bare symptom prompts in the
  notebook, with a pointer to the solutions file. Re-verified Chapter 1 doesn't have the same
  issue (it doesn't; its cold-answer questions were pointer-only from the start).
- Verification: `pytest --nbmake` across all 12 notebooks + `tests/` with no `.env`
  present — 28/28 pass. The notebook was executed in place afterward
  (`jupyter nbconvert --execute --inplace`) so its committed version shows real example
  output — including, notably, the hash-based cycle guard visibly failing to catch the
  Jack/Mike cycle (running the full 8 rounds) right next to the semantic guard catching it
  in 2, which is the clearest before/after in the chapter.
- `REFERENCES.md`'s Chapter 2 section is now filled in (LangGraph docs, OpenClaw docs,
  Schmid's subagent-patterns article, and a labeled practitioner-consensus note for the
  supervisor-worker/skills claims that aren't from one canonical source).

## Notes from Unit 4

Environment reachability check (done first, per Unit 3's own advice): three of Chapter
3's planned real-data sources are unreachable from this build environment, one substitute
found per source.

- `huggingface.co`, `hf.co`, and every `*.huggingface.co` CDN host (including
  `cdn-lfs.huggingface.co`) are blocked by this session's egress policy, same permanent,
  non-retryable 403 pattern as Unit 3's tiktoken finding. This rules out the Hugging Face
  `datasets` library for SQuAD, `sentence-transformers`' model download, and (later, Unit 8's
  problem) the GH Archive slice.
- `data.sec.gov` and `www.sec.gov` are both blocked the same way; SEC EDGAR is entirely
  unreachable from this environment, not just its API host.
- `raw.githubusercontent.com`, `api.github.com`, `release-assets.githubusercontent.com`, and
  `pypi.org` are all reachable. This unlocked three substitutions, each real data from an
  official/canonical source, just fetched through a different (allowed) channel than the
  spec suggested:
  1. **SQuAD 1.1** — fetched directly from `rajpurkar/SQuAD-explorer`'s `dev-v1.1.json` on
     `raw.githubusercontent.com` (the dataset author's own canonical repo) instead of
     `datasets.load_dataset("rajpurkar/squad")`. Same real data, same license (CC BY-SA
     4.0), different access mechanism. Extracted a seeded, deterministic sample (28
     passages, 55 QA pairs) and cached it at `data/rag_corpus/squad_sample.json`, committed
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
     properties the ingestion exercise needs: real inconsistent formatting, embedded
     commit/PR links, and (usefully) many genuinely near-duplicate release-note sections,
     which turns out to be a *better* fit for the deduplication exercise specifically than a
     generic issues dump would have been. Cached at
     `data/rag_corpus/messy_source_changelog.md`.
  3. **Local embeddings** — swapped `sentence-transformers` (needs a `huggingface.co` model
     download at runtime) for **spaCy's `en_core_web_md`**, whose model ships as one
     self-contained wheel hosted on a GitHub release
     (`github.com/explosion/spacy-models/releases/...`, confirmed reachable and installable
     via `pip install -r requirements.txt` directly, no separate download step for anyone,
     regardless of their own network's access to Hugging Face). Verified end-to-end: real
     300-dim GloVe-style vectors load and produce sensible similarity ordering. This is a
     `requirements.txt` change from Unit 1's original pins, documented here as a deliberate,
     verified substitution, not a silent scope cut.
- Chroma vs. FAISS: Unit 1 already chose `faiss-cpu` over `chromadb` for CI reliability
  reasons unrelated to network access; that decision stands and turned out to be additionally
  correct here since FAISS needs no runtime download at all (indexes are built from your own
  embeddings).
- PubMedQA / BEIR (optional complementary corpora): both Hugging-Face-hosted and
  therefore unreachable here too. Per spec these are optional "if you want more practice"
  pointers, not required content; kept as a closing-cell markdown pointer only, no runnable
  code cell, so this doesn't block the chapter.
- Caught one real bug via output inspection, not just green tests: the first version of
  break-it #3 (answer split across two chunks) used a mock `template_generate` that only
  ever extracted one single best-matching sentence globally, so its "fix" cell (retrieving
  both chunks) produced the exact same one-sentence answer as the "bug" cell — the before/
  after showed no visible difference, which fails the hard constraint that a fix must
  visibly resolve the bug even though nothing raised an exception. Fixed by having
  `template_generate` pull the best sentence from *each* retrieved doc instead of one global
  best; re-verified the fix cell now genuinely shows both facts appearing together.
- break-it #5 (offline/online divergence) needed a redesign for the same "looks right but
  isn't" reason: the first version wrapped a retriever to "return more results," but
  `eval_metrics.precision_at_k`/`recall_at_k` truncate to `k` internally regardless of how
  many results a retriever function returns, so v1 and v2 would have scored identically —
  caught this by re-reading the code before running it, not empirically. Redesigned v2 as a
  bigram-augmented TF-IDF retriever (a real, mechanistic ranking difference) — which then, in
  the actual run, won on *both* the offline and simulated-online metrics rather than
  diverging as hoped. Per spec this scenario is explicitly meant to be simulated, so rather
  than keep searching for a real mechanistic change that happens to diverge the "right" way,
  the online-satisfaction signal was rebuilt as a transparently hand-constructed, clearly
  -labeled simulation (see the notebook's docstring for that function), honest about being
  illustrative rather than dressing up an empirical result that didn't cooperate.
- Verification: `pytest --nbmake` across all 12 notebooks + `tests/` with no `.env`
  present — 36/36 pass (22 `agentlib` unit tests now, up from 14, covering
  `eval_metrics`/`synthetic_data`). Notebook executed in place afterward so its committed
  version shows real output throughout, including the actual (not hypothetical) TF-IDF-
  beats-embeddings result on this corpus — left as-is rather than tuned to fit a preferred
  narrative, since it's a real, honestly-obtained measurement.
- `REFERENCES.md`'s Datasets and Chapter 3 sections are filled in — all citations
  (SQuAD, RAG, TF-IDF, embeddings, FAISS, RAGAS, the IR-metrics textbook, spaCy, PubMedQA,
  BEIR) verified via live search at build time.

## Notes from Unit 5

- No new `agentlib` module: per the repo structure spec, `agentlib/` has exactly six
  files (`tools.py`, `loop_guards.py`, `tracing.py`, `synthetic_data.py`, `eval_metrics.py`,
  `llm_client.py`), and none of them is a reliability/caching module, so this chapter's
  `TTLCache`, `retry_with_backoff()`, and `CircuitBreaker` are built inline in the notebook
  by design, not extracted — consistent with the spec's exact file inventory rather than an
  oversight.
- Hit the same nested-quoting bug class as Chapters 1-3, in a new shape: the fake
  mini-codebase's file contents needed realistic Python docstrings (using `"""`), nested
  inside Python string literals (using `'''`), nested inside this build's own generator
  script's string wrapper (also `"""`, three levels deep) — the innermost `"""` prematurely
  closed the outermost one. Fixed by writing that one cell's source to a plain, unwrapped
  `.py` file and reading it back as text rather than embedding it as a nested string literal,
  which avoids the whole class of bug rather than patching this one instance. Worth
  remembering for any future chapter whose example content itself contains Python code with
  docstrings.
- Real rate-limit section falls back cleanly (verified in this no-key build): reuses the
  exact same `retry_with_backoff()` built earlier in the chapter against a simulated flaky
  tool when `HAS_KEY` is False, rather than a separate/simplified mock path. The real-key
  branch (untested here, no key present) fires a 20-way concurrent burst via
  `agentlib.llm_client.call_model()` and applies the same decorator against genuine 429s.
- Verification: `pytest --nbmake` across all 12 notebooks + `tests/` with no `.env`
  present — 36/36 pass (no new agentlib tests needed this unit, per the point above).
  Notebook executed in place; break-it #1's before/after is the clearest in the chapter (same
  question, wrong answer with no explanation vs. correct answer with a visible context-age
  log), and break-it #3's circuit breaker demo shows a nice true-to-life detail: it
  auto-retries once per cooldown window and correctly reopens when that trial still fails,
  not just a scripted open-then-closed sequence.
- `REFERENCES.md`'s Chapter 4 section is filled in (Nygard's *Release It!* for circuit
  breakers, Brooker's *Exponential Backoff and Jitter* for the retry jitter component), both
  verified via live search.

## Notes from Unit 6

- Solved the `tiktoken` network block properly, not just with a fallback. As flagged at
  the end of Unit 5, `tiktoken.get_encoding("cl100k_base")` needs
  `openaipublic.blob.core.windows.net`, which this build environment cannot reach, the same
  class of block as Hugging Face and SEC EDGAR. Rather than fall back to an approximate
  word-count proxy (the plan sketched at the end of Unit 5), found a strictly better fix: a
  community-mirrored copy of the exact canonical `cl100k_base` vocabulary file is reachable
  on GitHub. Fetched it, verified it byte-for-byte via SHA-256 against the hash `tiktoken`'s
  own source code checks for at load time (match confirmed), and vendored it into
  `data/tiktoken_cache/` under the filename `tiktoken` itself expects
  (`hashlib.sha1(url.encode()).hexdigest()` of the real blob URL), then set
  `TIKTOKEN_CACHE_DIR` to that directory before calling `tiktoken.get_encoding()`. The result
  is genuine, real `cl100k_base` tokenization with zero network calls and zero approximation —
  `tiktoken` cannot tell the difference between this and a live fetch. Full verification
  steps are in `curriculum/05_cost_performance_model_selection.ipynb`'s setup section.
- `agentlib/synthetic_data.py` extended with `generate_request_log()`: Poisson arrivals
  (`expovariate`), log-normal token counts, a four-stage latency breakdown (queue/network/
  inference/generation), seeded and deterministic. Tuned the model-mix weights (70% haiku /
  30% sonnet) and per-token latency rates so the unmodified log's average total latency lands
  around ~1.7s, close enough to the spec's "~2s" framing that the break-it scenarios read
  naturally against it without needing to be tuned separately.
- Caught two real bugs via actual output inspection, not just green tests:
  1. A floating-point tolerance bug in the new `test_generate_request_log_...` test:
     asserting `abs(stage_sum - total_latency_ms) < 0.1` fails intermittently because four
     independently-rounded-to-1-decimal stage values can accumulate up to ~0.2 of rounding
     error; loosened to `< 0.3` with an inline comment explaining why, rather than rounding
     differently and changing the log's realistic-looking precision.
  2. A markdown claim in the tokenization-quirks section asserted "long runs of whitespace
     still cost real tokens," written before checking real output. The actual baked-in
     `tiktoken` output shows a whitespace-only test string collapsing into exactly **one**
     token. Corrected the markdown to describe this accurately as a genuine `cl100k_base`
     property (efficient whitespace merges, useful for indented code), contrasted with GPT-2's
     older, per-space tokenization — a more interesting and more correct fact than the
     original assumption.
  3. Break-it #3 (queueing spike)'s first pass used a queue-time-per-depth-unit multiplier
     that only reached ~3.9s peak latency against a ~1.7s baseline: real, working code, but
     it didn't match the chapter's own "2s → 12s" interview-question framing quoted right next
     to it. Recomputed the needed multiplier from the actual per-request generation-time
     values in the log (rather than guessing again) and retuned it; the baked-in output now
     shows baseline ~1.7s and peak ~12.4s, genuinely matching the framing instead of just
     being in the right direction.
- Verified the duplicate-call scenario's diagnostic signal at the aggregate level, not just
  by eyeballing the printed slice: individual doubled requests can still land inside the
  normal log-normal token range purely by chance (real variance, not a scenario flaw), so
  confirmed separately that the injected slice's *mean* input token count is ~2.01x the
  surrounding baseline's mean, matching the 2x bug by construction and giving a clean signal
  even though a few individual printed rows don't visually pop out on their own.
- Verification: `pytest --nbmake` on the finished notebook alone passed at each of the
  six build stages (setup; request log + tokenization + latency profiler; break-it #1/#2;
  break-it #3; optimization + fine-tuning concept; interview drill + recap) before moving to
  the next; full-suite `pytest --nbmake` across all 13 notebooks plus `tests/` also passed.
  25 `agentlib` unit tests total (up from 23, the two new `generate_request_log` tests from
  Unit 5's tail end are included in that count, not added again here). Notebook executed in
  place after every stage so the committed version shows real output throughout, including
  the corrected ~1.7s → ~12.4s latency numbers and the real `cl100k_base` tokenization quirks.
- `REFERENCES.md`'s Chapter 5 section is filled in: `tiktoken` (with the offline-cache
  access note), Hu et al. 2021 (LoRA), Dettmers et al. 2023 (QLoRA), Christiano et al. 2017
  (the foundational RLHF paper), and Ouyang et al. 2022 (InstructGPT, RLHF at instruction-
  following scale), all verified via live search at build time.

## Notes from Unit 7

- No new `agentlib` module: same reasoning as Unit 5: `agentlib/` has exactly six files
  per the repo-structure spec, none of them security-specific, so this chapter's mock support
  -ticket agent, its tools, and its three defenses are built inline in the notebook by
  design, not extracted.
- **No environment-reachability issues this unit**: every citation (Willison's blog,
  Greshake et al.'s arXiv paper, OWASP's own site, OpenClaw's docs, Snowflake's blog) is
  reachable and was only needed for `REFERENCES.md`, not for any runnable notebook content.
  The chapter's mock system is entirely local and needed no external data source at all — the
  first chapter since Unit 4 with zero access-workaround story to tell.
- Responsible-use note placed as the very first cell, combined with the title (a
  blockquote directly under the "Estimated time" line) rather than as a separate cell after
  it, so it's genuinely the first thing anyone opening the notebook sees, satisfying the
  spec's requirement literally.
- Caught and fixed three real bugs via output inspection, not just green tests, all in
  the same "the demo silently didn't demonstrate what it claimed to" shape:
  1. Break-it #1's first draft split the injected directive ("SYSTEM: ... refund of $5000 to
     order ORD-1002 ...") across two lines in the ticket text; the directive-matching regex
     is intentionally single-line (so it can't be tricked into swallowing unrelated
     surrounding text), so it only captured the first line and missed the order ID/amount
     on the second, and the "attack" silently failed and issued the correct $118 refund
     instead of the intended $5,000 one. Fixed by keeping the directive on one line, which is
     also more realistic (a real injected directive embedded in otherwise-normal text is more
     likely to read as one dense sentence than as an artificially-line-broken paragraph).
  2. Break-it #2's malicious ticket phrased the destructive instruction as "Run scheduled
     maintenance now. WIPE all stale records..."; the destructive tool's own dispatch logic
     checks `command.strip().upper().startswith("WIPE")`, but the captured directive text
     started with "Run scheduled maintenance," not "WIPE," so the attack silently no-opped
     into the read-only branch instead of wiping anything. Fixed by rephrasing so the
     directive itself opens with the WIPE command, which is also the more realistic attack
     shape (an attacker crafting the payload controls its exact wording, and would put the
     actual command first).
  3. A benign demo ticket ("How long does shipping usually take?") in the normal-operation
     build section didn't share any exact substring with the `"shipping time"` knowledge-base
     key, so it fell through to human-routing instead of a KB answer, not a security bug,
     but a distracting one right next to the security content. Reworded to `"What's your
     shipping time?"` so the normal-operation demo cleanly shows all three tool paths
     working before the break-it sections start subverting them.
- Verified break-it #1's fix has two genuinely independent layers, not one dressed up as
  two: confirmed empirically that layer 2 (the policy check) still catches an inflated
  refund amount when tested directly against `issue_refund_with_policy_check`, independent
  of whether layer 1's sanitization ran at all, which is the actual point of calling it
  "defense in depth" rather than just chaining two similar checks.
- Verification: `pytest --nbmake` on the finished notebook passed at each of the six
  build stages (title/concept/setup; mock system + brains + normal-operation demo; break-it
  #1; break-it #2; break-it #3; interview drill + recap) before moving to the next; full-suite
  `pytest --nbmake` across all 14 notebooks plus `tests/` also passed, 25/25 `agentlib` unit
  tests unchanged (no new agentlib module this unit, per the point above). Notebook executed
  in place after every stage; the committed version shows real before/after output for all
  three attacks — a $118 legitimate refund vs. a $5,000 injected one, a 3-record database
  wiped to 0 vs. untouched, and a leaked internal key vs. a redacted/never-exposed one.
- `REFERENCES.md`'s Chapter 6 section is filled in: Willison's 2022 post (coining "prompt
  injection"), Greshake et al. 2023 (indirect prompt injection), the OWASP Top 10 for LLM
  Applications 2025 (LLM01), OpenClaw's security documentation, and Snowflake's 2026
  agentic-governance blog post for its least-privilege framing, all verified via live search
  at build time.

## Notes from Unit 8

- Confirmed the GH Archive block before writing anything, per Unit 7's own advice:
  `huggingface.co`, `data.gharchive.org`, `www.gharchive.org`, and `api.github.com` (the API
  root, distinct from `raw.githubusercontent.com`, which stays reachable) are all blocked
  with the same permanent 403-via-proxy pattern documented since Unit 4. Also confirmed, per
  this session's own repo-scope restrictions, that this session's attached GitHub MCP tools
  (scoped to `joshlaubach/learning-agentic-ai` only) are not a legitimate workaround:
  reaching outside that scope to pull real GitHub event data from other repos via those tools
  would violate the session's own access-scope policy, not just be technically awkward, so
  that path was correctly ruled out rather than attempted.
- **Substituted PyPI's live JSON API for GH Archive**: see `REFERENCES.md`'s new access
  note for the full reasoning. Unlike every prior HF-blocking substitution (SQuAD, the
  Chapter 3 messy-corpus source, `tiktoken`), this one needed no vendoring/caching
  workaround at all: `pypi.org` is directly reachable from this build environment, so
  `curriculum/_ch07_mcp_server.py`'s tool genuinely calls a live, real external API on an
  uncached request. Three packages' metadata (`requests`, `numpy`, `anthropic`) are cached at
  `data/pypi_cache/` purely so the notebook's own verification runs need no network access,
  not because live access doesn't work.
- Solved a real nbmake/asyncio compatibility issue, not previously hit in this build:
  `asyncio.run()` fails inside a notebook kernel's already-running event loop
  (`RuntimeError: asyncio.run() cannot be called from a running event loop`) — the fix is
  top-level `await` in the cell instead, which both `jupyter nbconvert --execute` and
  `pytest --nbmake` support natively. Separately, and less obviously: under `pytest
  --nbmake` specifically (not under plain `nbconvert`), spawning the MCP server subprocess
  failed with `io.UnsupportedOperation: fileno` — the `mcp` SDK's `stdio_client()` defaults
  to redirecting the child process's stderr to `sys.stderr`, but nbmake's kernel I/O capture
  wraps `sys.stderr` in an object with no real file descriptor, which the subprocess-spawning
  code needs. Fixed by passing `stdio_client(params, errlog=open(os.devnull, "w"))`, a real
  file object with a real fd. Verified this fix in an isolated probe notebook under both
  `nbconvert` and `nbmake` before writing it into the real chapter content, given how easy
  this class of bug is to miss if only one runner is tested.
- No new `agentlib` module: same reasoning as Units 5 and 7: the six-file inventory is
  fixed, and none of the six is an MCP-specific file, so the server, client-calling code, and
  decision router are all inline in the notebook. `curriculum/_ch07_mcp_server.py` is the one
  exception to "everything lives in the notebook" for this chapter specifically, and
  necessarily so: MCP's stdio transport spawns the server as a genuine separate OS process,
  which requires it to exist as a real, independently-executable script, not inline cell code.
- **`data/schemas/`** (scaffolded empty since Unit 1) gets its first real content this unit:
  `package_info.schema.json`, generated live by the notebook itself
  (`PackageInfo.model_json_schema()`) rather than hand-written, so the committed schema file
  is guaranteed to match the actual Pydantic model rather than drifting from it over time.
- Verification: `pytest --nbmake` on the finished notebook passed at each of the six
  build stages (title/concept/setup; client connection + schema + normal-operation demo;
  transient-failure demo; malformed/semantic/version-mismatch demos; decision router;
  interview drill + recap) before moving to the next; full-suite `pytest --nbmake` across all
  15 notebooks plus `tests/` also passed (34/34, unchanged agentlib test count, no new
  module this unit). Notebook executed in place after every stage; the committed version
  shows real output throughout, including a real PyPI response for `numpy`/`requests`/
  `anthropic`, a real subprocess-spawned server recovering from two simulated timeouts on the
  third attempt, and the router correctly classifying all four injected failure shapes.
- `REFERENCES.md`'s Chapter 7 section is filled in: the MCP specification, PyPI's JSON API
  docs, Pydantic's own docs, and a full access note documenting the GH Archive → PyPI
  substitution, all verified via live search at build time.

## Notes from Unit 9

- No new `agentlib` module and no citations: both expected per spec and per this file's
  own forward note; confirmed rather than assumed. `REFERENCES.md`'s Chapter 8 section
  already correctly stated "no citations expected" from Unit 1 and needed no edit this unit.
- Genuinely mostly markdown, as spec anticipated: the notebook has 12 cells total, of
  which only 2 are code (a small `DesignDoc` dataclass mirroring the nine-question framework,
  and nothing else, no break-it section, since there's no runnable bug to inject in a
  judgment/framework chapter). This is a deliberate departure from every prior chapter's
  concept/build/break-it/interview-drill structure, not an oversight: a system-design
  judgment chapter doesn't have a "break it" in the same sense Chapters 1-7 do, since there's
  no single piece of code whose failure mode is the teaching point.
- The nine-question framework was designed to explicitly cite back to Chapters 1-7
  (a table mapping each question to the chapter that built the underlying technique) rather
  than introducing new judgment criteria from scratch. The goal was synthesis, not new
  content, matching the spec's framing of this chapter as consolidating prior material into a
  repeatable interview process rather than teaching something new.
- Three design-doc studios were deliberately built with different risk/latency/reliability
  profiles (a high-stakes financial-action agent, a low-stakes human-reviewed assistant, and
  a correctness-critical grounded-QA system) specifically so the solutions file's answers
  can't just repeat the same generic reasoning three times: each studio's answer to "what's
  the reliability story" or "what's the security surface" genuinely differs based on that
  studio's actual stakes, which is itself the point the chapter is trying to teach (judgment
  that's sensitive to context, not a fixed checklist applied identically everywhere).
- Verification: `pytest --nbmake` on the finished notebook passed at each of the four
  build stages (title/concept/"when not to use an agent"; the `DesignDoc` framework cell;
  the three blank studios; interview drill + recap) before moving to the next; full-suite
  `pytest --nbmake` across all 16 notebooks plus `tests/` also passed (34/34, unchanged
  agentlib test count, no new module this unit, consistent with this chapter having no
  runnable technique to add tests for). Notebook executed in place; grepped for "Answer:" and
  bold/italic "Answer" patterns across all markdown cells to confirm zero inline-answer
  violations, same check applied to every prior chapter.

## Notes from Unit 10

- Confirmed the Docker base-image reachability risk flagged at the end of Unit 9 was real,
  and characterized it precisely before writing any content that assumed otherwise:
  `docker` CLI and `dockerd` are both installed in this build environment (no systemd, so
  `dockerd` needed to be started manually, works fine once started). `docker pull
  python:3.11-slim` and a GHCR image both fail specifically at the blob-download step
  (`production.cloudfront.docker.com` / `pkg-containers.githubusercontent.com`, both
  `Forbidden`) — the registry API/manifest resolution itself succeeds first, only the actual
  layer data is blocked. Confirmed this is a targeted network-policy block, not a broader
  Docker malfunction, by running a `FROM scratch` build (no external base image) to
  completion successfully in the same session. `docker build --check` (buildx's lint-only
  mode) also fails the same way, since it still needs to resolve base-image metadata.
- **No substitute exists for this one, unlike every prior HF/SEC-driven substitution**: SQuAD
  had a GitHub-hosted equivalent, `tiktoken` had a hash-verifiable mirrored vocab file, GH
  Archive had PyPI's live API as a legitimate alternative real-data source. A container base
  image has no equivalent "differently-hosted, still-real" substitute: it's not a dataset
  that can be fetched from an alternate reachable host, it's specifically Docker Hub/GHCR's
  own layer storage. Rather than fabricate a fake "build succeeded" result or silently skip
  the deliverable, wrote a real, carefully-reviewed root `Dockerfile` (non-root user,
  dependency-layer-before-code-layer caching order, no secrets baked in, a `HEALTHCHECK`) and
  documented transparently, in both `REFERENCES.md` and this file, exactly what could and
  couldn't be verified. This is a genuine limitation of this specific build session's sandbox,
  not a claim that the Dockerfile is untested in principle; a normal network environment
  should build it successfully.
- **Kept all Docker interaction out of the notebook's own executed cells entirely**: Hard
  Constraint #3 requires every notebook to execute with zero errors, in any environment, and
  invoking `docker build` from inside a notebook cell would make that constraint
  environment-dependent (working in a normal network environment, failing in this build's
  own sandbox, and potentially in other sandboxed CI environments too). The notebook instead
  reads and prints the real `Dockerfile`'s actual content (a real file read, not a string
  copy embedded in the notebook) and explains the verification limitation in markdown;
  everything the notebook itself executes remains genuinely network-independent.
- No new `agentlib` module: same reasoning as Units 5, 6, 8: the file inventory is
  fixed, and none of the six files is deployment-specific, so `PromptRegistry`, the canary
  router, and the drift-detection functions are all inline in the notebook.
- Caught the same "silent no-op" bug class break-it sections have hit before, twice, before
  running anything: the first draft of break-it 1's malicious-directive-style demo (a
  regressed prompt) and break-it 2's rollout demo both needed the *same* underlying
  regression (v3-regressed's ~35% refusal rate vs. v1's ~3%) to actually register as
  "unhealthy" against whatever threshold was in place. Designed `check_canary_health`'s
  buggy version (`threshold=0.5`) and its fix (`threshold=0.05`) by first computing what the
  real simulated regression's magnitude actually is (~32 points), then picking a buggy
  threshold safely above it and a fixed threshold safely below it, rather than guessing
  round numbers and hoping they'd produce the right before/after — the same lesson break-it
  #2 itself is teaching, applied to writing the break-it section.
- Verification: `pytest --nbmake` on the finished notebook passed at each of the seven
  build stages (title/concept/setup; prompt registry; canary router + shadow deployment;
  break-it 1; break-it 2; containerization section; interview drill + recap) before moving to
  the next; full-suite `pytest --nbmake` across all 16 notebooks plus `tests/` also passed
  (34/34, unchanged agentlib test count, no new module this unit). Notebook executed in
  place after every stage; the committed version shows real output throughout, including the
  buggy threshold's rollout reaching "FULLY PROMOTED" at 100% and the fixed threshold's
  rollout correctly halting at the 5% stage with `ROLLED BACK`.
- `REFERENCES.md`'s Chapter 9 section is filled in: Fowler/Sato's canary-release bliki
  post, the Google SRE Workbook's canarying-releases chapter, Docker's own build-best-
  -practices docs, and OpenClaw's Docker deployment docs, plus the full Docker
  -verification-limitation note, all verified via live search at build time.

## Notes from Unit 11

- The exact text of the "10 seed scenario/follow-up pairs" this file's own Unit 10 note
  referred to was not preserved anywhere in the repo; only the meta-description
  ("verbatim") survived compaction, not the seed content itself. Rather than fabricate
  replacement seed questions or silently drop the "verbatim" requirement, recovered the
  original build specification text from this session's own pre-compaction transcript
  (`/root/.claude/projects/.../*.jsonl`, referenced in the compaction summary's own "if you
  need specific details" pointer) and extracted the real spec section verbatim from there.
  Worth remembering for any future session that finds a forward note referencing content it
  doesn't actually have: check the pre-compaction transcript before assuming the content is
  unrecoverable.
- **All 10 seeds are in `question_bank.json` verbatim**, each with exactly 5 additional
  variant entries in the same chapter (6 total per seed cluster), programmatically verified,
  not just visually checked (see the validation script's output below). Seed 10 ("Your
  evaluation score improved, but user satisfaction dropped.") is deliberately duplicated in
  both Chapter 3 (`evalgap-001`) and Chapter 9 (`deploy-001`) per the spec's own instruction,
  with independently-written variant clusters in each chapter's context (RAG-evaluation
  framing in Ch3, canary-rollout framing in Ch9) rather than the same six variants copy-pasted
  into two chapters.
- **93 total entries** (spec required 70+, ~8-12 per chapter as a general target). Chapter 3
  has 18 (three seed clusters: RAG confident-but-wrong, hallucination-explanation, and the
  Ch3 half of the duplicated eval-gap seed), Chapter 5 has 12 (two seed clusters: GPU cost,
  latency), every other chapter has 9. Chapter 8 has zero seed material (per spec, "Chapter 8
  entirely" has none) and is fully originally-generated.
- **Three entries are grounded in real, verified public incidents**, per the Humanization
  Requirements: `hallu-004` (Moffatt v. Air Canada, the chatbot bereavement-fare tribunal
  ruling), `hallu-005` (Mata v. Avianca, the fabricated-case-citations sanctions case), and
  `security-002` (the Chevrolet dealership chatbot prompt-injection incident), each verified
  via live search before writing (not trusted from memory), paraphrased into original wording
  rather than quoting source coverage, and carrying a real `source_note` URL.
- **Format variety enforced, not just claimed**: final distribution across all 93 entries:
  33 `scenario_first`, 29 `question_first`, 17 `slack_message`, 14 `stakeholder_quote`; no
  chapter uses only one format.
- Validated programmatically before moving on, not just by inspection: valid JSON: unique
  IDs; every `question_bank.json` schema field present on every entry; zero inline-answer
  fields in `question_bank.json` itself; exact 1:1 id match between `question_bank.json` and
  `solutions/question_bank_answers.json` (93 entries, 93 answers, no orphans on either side);
  per-chapter counts; and a direct check that every one of the 10 seed scenario/follow-up
  pairs (11 instances, counting the Ch3/Ch9 duplicate) appears character-for-character.
- `mock_interview.ipynb` and `per_chapter_drills.ipynb` both needed two layers of
  headless-safe `input()` handling, not one. Plain Python raises `EOFError` when `input()`
  is called with closed/empty stdin, which is what a script run outside a notebook would hit —
  but the ZMQ-based Jupyter kernel `nbconvert`/`pytest --nbmake` actually execute cells
  through raises IPython's `StdinNotImplementedError` instead, since the connected frontend
  doesn't implement stdin requests at all. Caught this by actually running `pytest --nbmake`
  against the first draft (which only caught `EOFError`) and seeing the real failure, not by
  reasoning about it in advance. Both exceptions are now caught, and both notebooks execute
  cleanly under nbmake while still behaving like a normal interactive prompt when run for
  real.
- The branching example (spec-required: "at least one branching example... implement as
  real conditional logic on keyword matches") is demonstrated deterministically in
  `mock_interview.ipynb` with three canned example answers run through the same
  `branching_follow_up()` function the live session uses: one triggering the "add more
  GPUs" pushback branch, one triggering the "profile first" easier-follow-up branch, one
  matching neither and falling back to the standard question, so the branching logic is
  genuinely exercised and its real output committed, not just described as possible.
- No new `agentlib` module: `interview_prep/`'s logic (sampling, keyword feedback,
  branching) is specific to this unit and inline in its own notebooks, consistent with the
  fixed six-file `agentlib/` inventory.
- README.md's AI-assistance disclosure and CONTRIBUTING.md's "submit a real interview
  question" section were already written in full during Unit 1 and needed no changes this
  unit, confirmed rather than assumed, since the spec's Humanization Requirement #5 (disclose
  AI assistance, invite real-question PRs) was correctly anticipated and built early.
- Verification: `pytest --nbmake` on both new notebooks passed individually before the
  full-suite run; `curriculum/*.ipynb interview_prep/*.ipynb tests/` together: 36/36 passed
  (9 curriculum + 2 interview_prep notebooks + 25 `tests/`, `capstone/`'s still-stub notebook
  intentionally excluded from this specific run, unaffected by this unit). Both new notebooks
  executed in place; committed output includes a real 5-question mock session (headless
  placeholder answers, but real sampling, real keyword checks, real follow-ups) and a real
  9-question Chapter 6 drill run in bank order.

## Notes from Unit 12

- **Recovered the exact capstone spec from the pre-compaction transcript**, same recovery
  method as Unit 11: the original build prompt's "Capstone" section (a single combined
  agent: retrieval + Ch7 tool use + memory + a Ch6 safeguard, LangGraph or the Claude Agent
  SDK, LangGraph recommended as the provider-agnostic default) was extracted verbatim rather
  than reconstructed from this file's own compressed forward notes.
- **LangGraph chosen over the Claude Agent SDK**, exactly as the spec itself recommends:
  the Agent SDK is Anthropic-specific, and this whole repo supports both Anthropic and OpenAI
  via `LLM_PROVIDER`. `langgraph==1.2.11` added to `requirements.txt` (pulls in
  `langchain-core`, `langgraph-checkpoint`, `langgraph-prebuilt` as real transitive deps, left
  unpinned like other transitive deps elsewhere in the file). Used purely for graph
  orchestration (`StateGraph`, nodes, conditional edges, `MemorySaver` for a real
  checkpointer); actual model calls still go through `agentlib.llm_client.call_model()`, not
  a LangChain-native model wrapper, so `LLM_PROVIDER` switching still works with zero
  capstone-specific code changes, preserving the whole repo's provider-agnostic design.
- Both real Chapter artifacts genuinely reused, not re-implemented: the exact
  `TfidfRetriever` class from Chapter 3 (same shape, over the same real `squad_sample.json`
  corpus), and a genuine stdio connection to Chapter 7's actual `curriculum/_ch07_mcp_server.py`
  process, calling its real `get_package_info` tool and validating the response with the same
  `PackageInfo` Pydantic model.
- Caught and fixed a real infinite-loop bug in the mock decision path before it ever ran:
  the first draft of `fake_decide` only looked at the latest *user* message to decide which
  tool to call, so after a tool result came back, it would re-derive the exact same tool call
  from the same original question and loop forever, since a tool result was never recognized
  as a signal to stop and answer. Fixed by adding an explicit termination branch: if the most
  recent message is a tool result, synthesize a final answer instead of deciding again. A
  real model with real reasoning would do this naturally, but the deterministic mock path
  needed the termination condition made explicit.
- The memory demo was redesigned once, for a real reason. The first draft's cross-turn
  follow-up ("Who led that army?") relied on pronoun resolution the mock decision function
  can't actually do; it only looks at the latest message, so the follow-up would have
  triggered a fresh, disconnected retrieval search rather than genuinely demonstrating memory
  working. Redesigned around a meta-question ("What was the first question I asked you?")
  that can *only* be answered correctly by scanning the full accumulated message history —
  an unambiguous, mechanistic proof that LangGraph's checkpointer is providing real state
  across `ainvoke()` calls, not something that looks like memory by coincidence.
- The Chapter 6 safeguard is proven wired into the live pipeline, not just demonstrated
  standalone: after the standalone `sanitize_retrieved_text` demo (same shape as Chapter
  6's own break-it demo), a second demo runs the real `tool_node` function itself (via a
  temporary tool swap, not a separate reimplementation) against a deliberately poisoned
  document, confirming the injected directive genuinely never reaches the conversation
  through the actual code path Ava's graph executes.
- No new `agentlib` module: the capstone's own logic (state schema, decision functions,
  graph wiring) is specific to this one project and lives in `capstone_agent.ipynb` itself,
  consistent with the fixed six-file `agentlib/` inventory used throughout this build.
- Verification: `pytest --nbmake` on the finished notebook passed at each of the eight
  build stages before moving to the next; full-suite `pytest --nbmake` across all 17
  notebooks (curriculum + interview_prep + capstone) plus `tests/` also passed (37/37,
  unchanged agentlib test count, no new module this unit). Notebook executed in place after
  every stage; the committed version shows real output throughout, including a real
  retrieved passage about Genghis Khan and the Shah's army, a real memory-proving answer to
  "what was the first question I asked you," a real PyPI package summary via the live MCP
  tool, and a real sanitized (directive-stripped) result from the poisoned-document safeguard
  proof.
- `capstone/README.md` rewritten in full from its Unit 1 placeholder: what it does, what it
  demonstrates, how to run it on either provider or with no key, and the OpenClaw
  comparison section the spec calls for. `REFERENCES.md`'s Capstone and Appendices section
  filled in (LangGraph's own docs, OpenClaw's docs cited for the real-system comparison),
  both verified via live search at build time.

## Notes from Unit 13 (final unit)

- **`.github/workflows/ci.yml` added**: installs `requirements.txt` on `ubuntu-latest` /
  Python 3.11, then runs the exact same command every prior unit used to self-verify:
  `pytest --nbmake curriculum/*.ipynb interview_prep/*.ipynb capstone/*.ipynb tests/`.
  Triggers on every `push` and `pull_request`, no secrets referenced anywhere in the
  workflow. CI runs entirely through each notebook's mock/`HAS_KEY=False` fallback path, by
  design, per Hard Constraint #1. `"on":` quoted explicitly in the YAML to avoid the
  well-known YAML 1.1 boolean-coercion gotcha (`on` → `True`) some generic parsers apply,
  even though GitHub Actions' own parser handles the bare key correctly regardless.
- README's CI badge needed no changes; it was already written correctly in Unit 1,
  pointing at exactly this workflow's real path
  (`joshlaubach/learning-agentic-ai/actions/workflows/ci.yml`), anticipating this unit
  correctly a dozen units in advance.
- **One full clean-environment run performed**, exactly as the spec's Unit 13 and Final
  Acceptance Checklist both require: a brand-new venv (not the incrementally-built one every
  prior unit's verification reused), `pip install -r requirements.txt` with no other install
  step, no `.env` present, no relevant API-key env vars set — `pytest --nbmake
  curriculum/*.ipynb interview_prep/*.ipynb capstone/*.ipynb tests/` → **37/37 passed**. This
  is the strongest verification this repo has had of `requirements.txt`'s completeness and
  correctness, since every earlier unit's local verification reused a venv that had
  accumulated installs incrementally (including one manual `pip install langgraph` in Unit 12
  before it was added to `requirements.txt` in the same session) rather than proving the pins
  file installs cleanly from nothing in one shot.
- **Went through the spec's full Final Acceptance Checklist item by item** (not just this
  unit's own narrower CI requirements), since this is genuinely the last unit and nothing
  else will re-check the whole repo afterward. Verified: no notebook or `question_bank.json`
  entry contains an inline answer (full grep sweep, zero hits beyond the disclosure text
  itself); `.env` is git-ignored and a full history grep found no real credentials anywhere
  (one placeholder `sk-ant-...` illustrative string in Chapter 1's setup instructions, not a
  real key); `agentlib.llm_client` is genuinely reused (not reimplemented) in Chapters 1, 2,
  3, 4, 6, 7, and the capstone; Chapter 1's setup section has the spend-limit-before-key-
  generation step and the $15–20 ceiling; Chapter 6 opens with the responsible-use note as
  its literal first cell; `REFERENCES.md`'s staleness date is stamped and echoed in the
  README; `CONTRIBUTING.md`/`SECURITY.md`/`LICENSE` all exist at the repo root; every
  `solutions/` file has real, substantial content (not a stub).
- Caught and fixed one real, previously-unnoticed inaccuracy during this pass: the
  README's License section described SEC EDGAR- and GH Archive-derived material as being
  present in the repo (carried over from the original build spec's plan), but neither
  source was ever actually reachable (documented in Units 4 and 8), so neither one's data
  ever made it into the repo at all. The README described a plan, not the repository's
  actual contents. Rewrote the License section to describe what's genuinely bundled instead
  — the real SQuAD sample (CC BY-SA 4.0), the real `anthropic-sdk-python` CHANGELOG.md
  excerpt (MIT), the vendored `tiktoken` vocabulary file (OpenAI-distributed, not
  independently re-licensed), and the cached PyPI package metadata (factual data, not
  independently copyrightable) — with an explicit note that the original SEC
  EDGAR/GH Archive plan never materialized and why, so a reader isn't misled about what's
  actually here. This is exactly the kind of drift a final acceptance pass exists to catch —
  accurate at the time each unit was written, stale by the time the whole repo was assembled.
- Verification: the clean-environment run above is this unit's primary verification
  (37/37, fresh venv, no `.env`); re-ran the full suite once more against the existing
  incremental `.venv` after the README License-section fix to confirm nothing regressed
  (37/37 again).

## Build complete

All 13 units are checked off above, and this file's own state matches the actual repository:
every file it claims exists does, and every notebook it claims passes does, verified fresh
in a clean environment in this same unit, not carried forward as an assumption from earlier
units. Per the Final Acceptance Checklist: real-API-path code is structurally correct and
consistently reuses `agentlib.llm_client` across every chapter that needs it, but, as every
unit's own notes have said throughout, was never executed against a live Anthropic or
OpenAI key in this build environment, since none was ever provided; that verification still
needs to happen against a real key before this repository is exercised end-to-end on the
real-API path a human learner is meant to use as the default. Everything else in the
checklist was verified directly against the repository's actual, current state during this
final unit, not assumed from earlier sessions' notes.

This file can stay in the repo as a build record, or be deleted; either is fine now that
the build itself is done.
