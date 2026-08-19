# ai-agent-interview-prep

[![CI](https://github.com/joshlaubach/learning-agentic-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/joshlaubach/learning-agentic-ai/actions/workflows/ci.yml)

*A 9-chapter, hands-on Jupyter curriculum plus a separate interview-drilling layer, built to
take a data scientist or ML engineer with no prior agentic-AI experience through a realistic
transition into AI agent engineering, and to prepare them for real technical interviews on
the topic.*

> **Status:** this repository is being built incrementally across many sessions. See
> [`PROGRESS.md`](PROGRESS.md) for exactly what's done and what's next. Chapters and
> interview-prep content are added one unit at a time; don't expect everything below to be
> live yet.

## What this is

This is explicitly an "ML engineer → AI agent engineer" transition course. It assumes you
already have statistics, core Python, and ML/embeddings fundamentals (the kind of background
a data science role gives you), and it spends 100% of its time on the layer most DS/MLE
backgrounds haven't touched yet: agent control flow, tool use, retrieval-augmented
generation, production reliability, cost/latency, security, and system design for
LLM-based applications.

One scope boundary is worth reading before starting. This course does not teach classical MLE
(model training, hyperparameter tuning, evaluation of traditional ML models) as a primary
skill; that's assumed background, not something built here. It also doesn't teach fine-tuning
or model training as a hands-on skill: Chapter 5 covers LoRA/QLoRA/RLHF *conceptually* (what
they are, when they matter, how they come up in interviews), with no training loop, no GPU
requirement, and no implementation. Nor does it cover MLOps infrastructure (feature stores,
training pipelines, GPU cluster management); Chapter 9 covers *LLMOps* instead (prompt
versioning, canary rollout, drift detection), which is a different, narrower problem than
classical MLOps.

If you're looking for a course on training or fine-tuning models, or on classical MLOps, this
isn't it. If you're looking for the orchestration/integration layer that sits on top of a
model API (the actual day-to-day of an AI agent engineer), that's exactly what's here.

## Prerequisites

A quick gut-check before Chapter 1, not a mandatory review. This course assumes a
data-science-level background; if that's you, most of this is already covered.

Already covered by a DS background, so skip these: Python fundamentals, numpy/pandas, cosine
similarity and vector math, core statistics, working in Jupyter.

Five areas are worth a 1-2 hour gut-check if you can't already answer confidently. Async
Python: `async def` vs. a regular function, when you need `await`, and what happens if you
don't (this comes up in Chapter 7's MCP client and again in the capstone; Chapters 1-6 are
entirely synchronous).
Testing: writing a `pytest` test with `assert`, and unit vs. integration tests, which
Chapter 7's integration tests build on. Environment management: virtual environments, and
what a `.env` file is for and why it's never committed (Chapter 1 walks through this fully
regardless, written for a limited-Python-background reader, so don't worry if this is new).
Transformer and LLM internals at a conceptual level: what a token roughly is and what a
context window means (if your program predates ~2022 or was stats-heavy rather than
NLP-heavy, this may be genuinely new; Chapter 1 introduces it properly). Docker basics, which
only matters for Chapter 9's containerization subsection.

Not needed: deep software architecture experience, prior agent-framework exposure (that's
what this course teaches), or calculus/linear algebra beyond a DS background.

A few things get their own built-in review, so don't pre-study them: TF-IDF,
embeddings-as-semantic-space, and MRR each get a short refresher at the start of Chapter 3.
LoRA/QLoRA, catastrophic forgetting, RLHF, and RL's role in agent development are taught
conceptually in Chapter 5.

If none of the five gut-check items raise a flag, start Chapter 1 with zero additional prep.

## Setup

This project targets Python 3.11 and uses `pip` plus a standard virtual environment, not
`uv` or `poetry`, deliberately, since it's written for learners who may not have a Python
environment set up yet (see Prerequisites above). `pip install -r requirements.txt` is the
whole story.

```bash
git clone https://github.com/joshlaubach/learning-agentic-ai.git
cd learning-agentic-ai
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your API key — see Chapter 1
jupyter notebook curriculum/01_fundamentals.ipynb
```

Chapter 1's own first section walks through account creation, spend limits, and API keys in
much more detail than this README. Start there if any of the above is unfamiliar.

### Real API key vs. mock mode

This course is meant to be run with a real Anthropic or OpenAI API key. That's the primary,
intended experience: every notebook in Chapters 1, 2, 3, 4, 6, and the capstone calls a
real model by default once you've completed Chapter 1's one-time setup (provider account,
spend limit, API key, `.env`). A deterministic mock/offline fallback exists in every notebook
too, but only for two reasons: accessibility for learners without budget, and so CI can run
with no secrets. It is not the headline path; markdown cells throughout present the real-API
path as the default and the mock path as the fallback, not the reverse.

Chapter 1 walks through setting a **spend limit before generating any API key**: a $15–20
ceiling is recommended for the entire course as a comfortable margin. A full pass through the
course, including reasonable re-running of cells while learning, realistically costs $5–15 on
either provider's cheapest current-generation model. Per-token pricing changes often. Check
the provider's live pricing page rather than trusting a number written into a notebook months
or years after it was built.

## How this course works

This is a build-it course, not a read-it one. Most of what you learn here, you learn by
writing code that doesn't work yet and then making it work.

Every chapter contains **graded cells**: a function with a docstring describing what it has to
do, a `raise NotImplementedError` where the body should be, and a `check(...)` call underneath
that grades whatever you write against a suite of assertions.

```python
def retry_with_backoff(fn, max_retries: int = 6, base_delay: float = 1.0, jitter: float = 0.5,
                       seed: int = 1, sleep_fn=None, retry_predicate=None):
    '''Reusable exponential backoff + jitter wrapper.

    The delay before retry number `attempt` (1-based) is:

        base_delay * 2 ** (attempt - 1) + rng.uniform(0, jitter)

    Exponential, not linear. Linear growth looks almost identical over three attempts and
    then stops helping precisely when it matters [...]

    Back off AFTER a failure. A call that succeeds first time must not sleep at all.
    '''
    raise NotImplementedError("Implement me, then re-run this cell")


retry_with_backoff = check("ch04-backoff", retry_with_backoff)
```

That docstring is the spec — it is longer than most, and deliberately so. The reasoning it
gives you (*why* exponential rather than linear, *when* not to sleep) is the part worth
keeping; the code is just how you prove you took it in.

**If you clone this repo and run Chapter 1, the notebook will fail. That is the design, not a
bug.** Delete the `raise`, write the function, re-run the cell.

### What failure looks like

The checks are meant to teach, not just to reject. You get partial credit, the exact call that
broke, and an explanation of why it's wrong:

````
ch07-json-repair: 5/8 checks passed.
  [4/8] a brace inside a string value is not the end of the object
      matching braces with a non-greedy regex stops at the first '}' it sees, which here
      is inside a string value. Scan to the LAST '}' instead. Got None
      failing call: repair_json('```json\n{"name": "numpy", "version": "2.4.6", "summary":
      "use {} to build an empty dict"}\n```')

Fix the function above and re-run this cell.
````

There are **36 graded tasks and 304 assertion cases** across the nine chapters, distributed
roughly two to six per chapter. They are adversarially tested: for every task, a plausible
wrong answer is implemented in `tests/test_grader_catches_wrong_answers.py` and asserted to
fail. A suite that any reasonable attempt passes teaches nothing, so each one has at least one
case aimed at a specific mistake — not a typo or an empty function, but a version that looks
right, runs cleanly, and returns a value of the correct type.

### Tracking progress

```bash
python grade.py                 # every task, with pass/fail and case counts
python grade.py --by-chapter    # one line per chapter
python grade.py --count-cases   # total assertion cases
```

Results are cached in `.progress.json` as you go. It's gitignored, so a fresh clone always
starts empty.

### The two modes

`GRADER_MODE` controls what gets graded:

| mode | what it grades | when to use it |
|---|---|---|
| `learner` (default) | the function you wrote in the notebook | always, while working through the course |
| `reference` | the model answer in `solutions/reference/` | CI only |

`reference` exists so continuous integration can execute every notebook end to end without
shipping the answers inside them. **Don't set it while learning** — it makes every graded cell
pass without you writing anything, which feels like progress and isn't. If a chapter suddenly
stops failing, check whether `GRADER_MODE` is still exported in your shell.

### Where the answers are

Two kinds, both outside the notebooks:

- **Code** — `solutions/reference/ch01.py` … `ch09.py`, one model implementation per graded
  task.
- **Prose** — `solutions/ch0N_*_answers.md`, full written answers to every chapter's interview
  drill, plus `solutions/question_bank_answers.json` for all 99 question-bank entries.

Nothing in `curriculum/` or `interview_prep/` contains an inline answer, which is deliberate:
the reveal is a file you have to open on purpose, not a cell you scroll past by accident. The
intended workflow is to attempt from memory first, then check.

### Running the whole suite

```bash
# the nine chapters plus the agentlib unit tests -- the quick version
GRADER_MODE=reference pytest --nbmake curriculum/*.ipynb tests/

# everything, exactly as CI runs it
GRADER_MODE=reference pytest --nbmake curriculum/*.ipynb interview_prep/*.ipynb \
  capstone/*.ipynb solutions/*.ipynb tests/ capstone/test_capstone.py
```

Both execute the notebooks against the reference answers and need **no API key** — CI runs
with no provider secrets at all, deliberately, so every mock fallback stays honest. If this
passes on your machine, your environment is set up correctly, which is worth confirming
before concluding that a failing chapter is your fault.

## Curriculum

| # | Chapter | Time | What it covers |
|---|---------|------|-----------------|
| 1 | [Fundamentals of AI Agents](curriculum/01_fundamentals.ipynb) | ~6 hrs | Chatbot vs. workflow vs. agent, ReAct, a minimal agent loop built from scratch, and the one-time provider/API-key/spend-limit setup reused for the rest of the course |
| 2 | [Agent Control Flow](curriculum/02_control_flow.ipynb) | ~8 hrs | ReAct vs. plan-and-execute, a 3-agent Jack/Bob/Mike pipeline, subagents and context isolation, loops vs. cycles vs. unnecessary hops vs. leaky subagents |
| 3 | [RAG and Retrieval Evaluation](curriculum/03_rag_evaluation.ipynb) | ~8 hrs | TF-IDF vs. embeddings, precision/recall/MRR, a real SQuAD-based retrieval pipeline, chunking a messy real-world corpus, five retrieval/generation failure modes |
| 4 | [Production Reliability](curriculum/04_production_reliability.ipynb) | ~7 hrs | Stale caches, retries with backoff and jitter, circuit breakers, real rate-limit handling against a live API |
| 5 | [Cost, Performance, and Model Selection](curriculum/05_cost_performance_model_selection.ipynb) | ~8 hrs | Token economics, latency decomposition, model routing, and a conceptual (no-GPU) tour of fine-tuning, LoRA/QLoRA, and RLHF's role in agent development |
| 6 | [Security and Safeguards](curriculum/06_security_safeguards.ipynb) | ~7 hrs | Real, working prompt-injection payloads against your own mock system, least-privilege scoping, output filtering, defense in depth |
| 7 | [Tool Integration](curriculum/07_tool_integration.ipynb) | ~7 hrs | A real local MCP server (stdio transport), schema validation, a failure taxonomy (transient / malformed / semantically-wrong / version-mismatch), a retry/switch/ask-user decision router |
| 8 | [System Design and Engineering Judgment](curriculum/08_system_design_judgment.ipynb) | ~5 hrs | A repeatable system-design framework, blank design-doc studios, judgment prompts, "when would you NOT use an agent at all" |
| 9 | [LLMOps and Deployment](curriculum/09_llmops_deployment.ipynb) | ~6 hrs | Canary releases, shadow deployment, prompt versioning, drift detection, rollback, containerizing the curriculum's agent |

The chapter times above sum to about 62 hours. Add roughly 8-12 hours for the capstone
(it is a specification with an acceptance suite, not a walkthrough) and however much you
spend in `interview_prep/`, which is designed to be revisited rather than completed once.
Call it **70-75 hours** for a full pass.

These are working estimates, not measurements. Every chapter now ships graded exercises
that fail until you implement them, so how long a chapter takes depends far more on how
much you fight the exercises than on how fast you read.

### Interview prep (separate track)

Unlike the numbered chapters, [`interview_prep/`](interview_prep/) is meant to be revisited
repeatedly (for example, the week before an actual interview), independent of working through
the notebooks in order:

- `question_bank.json`: a tagged bank of 99 scenario/follow-up interview questions across
  all 9 chapters, none scraped from any interview-question site.
- `mock_interview.ipynb`: a randomized, timed, cross-chapter mock interview with branching
  follow-ups based on your typed answers.
- `per_chapter_drills.ipynb`: a simpler, chapter-filtered version for focused review.

### Capstone

[`capstone/`](capstone/) is intentionally not a 10th chapter: it's a single built project
(retrieval + tool use + memory + a security safeguard, in an actual agent framework) framed
as a portfolio piece. See `capstone/README.md`.

## Solutions

Every chapter's "cold-answer" interview questions, and every `question_bank.json` entry, have
a full written model answer, but only in [`solutions/`](solutions/), kept entirely separate
from the notebooks and the question bank itself. No notebook and no question-bank entry
contains an inline answer. The intended workflow: attempt the cold-answer questions from
memory first, *then* open the matching file in `solutions/` to check yourself.

The same directory also holds `solutions/reference/`, one model implementation per graded
exercise — the code half of the same bargain, and what CI grades against in `reference` mode.
See [How this course works](#how-this-course-works) above.

## Citations

Every dataset, technique, and library with a canonical source is cited: a short inline
citation where it's first introduced in a chapter, and a full entry in
[`REFERENCES.md`](REFERENCES.md). `REFERENCES.md` is also stamped with a "last verified"
date; see the staleness note there and below.

## Limitations

Stated plainly, not implied.

This is interview prep and foundational skill-building, not seniority. Finishing this course
prepares you to talk credibly about agent architecture, RAG evaluation, reliability patterns,
and security tradeoffs in an interview, and gives you real hands-on reps with the tools. It
does not make you a senior engineer; that requires real production stakes, real scale, and
organizational judgment no curriculum can simulate.

This also does not prepare you for a Forward Deployed Engineer or Solutions Engineer role by
itself. Those roles add a customer-facing, on-site dimension this repo has no way to
replicate; it's an engineering curriculum, not a client-facing-skills one.

The "one follow-up question eliminates 9 of 10 candidates" framing that originally inspired
this project's question set is an anecdotal claim from a social media post, not verified
hiring data. It shouldn't be repeated as fact anywhere in this repo, including here. It's
noted only to disclose where the idea came from and to explicitly disclaim it.

## License

This repository mixes sources, so a single root `LICENSE` file does not uniformly cover
everything in it:

- All original code and written content (notebooks, `agentlib/`, solutions, question bank,
  prose) is MIT licensed. See [`LICENSE`](LICENSE).
- Chapter 3's SQuAD-derived material (`data/rag_corpus/squad_sample.json`) carries SQuAD's
  own CC BY-SA 4.0 terms (see the `rajpurkar/squad` dataset card, cited in `REFERENCES.md`).
- Chapter 3's messy-corpus source (`data/rag_corpus/messy_source_changelog.md`, a real
  excerpt of `anthropic-sdk-python`'s own `CHANGELOG.md`) is MIT licensed, per that project's
  own license.
- Chapter 5's vendored `tiktoken` vocabulary file (`data/tiktoken_cache/`) is distributed
  by OpenAI as part of the `tiktoken` library for use with it; this repo's copy is a
  hash-verified, byte-identical mirror, not independently re-licensed content.
- Chapter 7's cached PyPI package metadata (`data/pypi_cache/`) is factual package
  metadata (name, version, summary, license, URLs) pulled from PyPI's own public JSON API,
  not independently copyrightable creative content.

Note: the original build specification for this course anticipated SEC EDGAR and GH Archive
as data sources for Chapters 3 and 7 respectively; both are unreachable from this repo's
build environment (see `PROGRESS.md`'s Unit 4 and Unit 8 notes), so neither actually appears
in this repo. The license breakdown above reflects what's genuinely bundled here, not the
original plan.

Check `REFERENCES.md` before reusing any dataset-derived content outside this repo.

## AI-assisted content and human review

This repository's notebooks, prose, and question bank were built with AI assistance
(Claude Code), following a detailed human-written specification. It has not yet been
reviewed end-to-end by a working AI agent engineer. Before treating any of this as a stable
v1.0 resource:

- If something reads as technically wrong or outdated, please open an issue using the
  "Content accuracy / errata" issue template. This is different from a bug report (which is
  about code not running).
- If you've been asked a real interview question this repo doesn't cover, or a real
  postmortem/incident this repo's scenarios should be grounded in, see
  [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to submit it.

## Build log

[`PROGRESS.md`](PROGRESS.md) is the running build log for this repository, not part of the
published curriculum, but left in place as a record of how it was built and what's still
outstanding.
