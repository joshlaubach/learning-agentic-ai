# Contributing

Thanks for considering a contribution. This is a curriculum repo built from a detailed
specification, and the two most valuable kinds of contribution are (1) flagging things that
are technically wrong or outdated, and (2) submitting real interview questions you've
actually been asked, so the question bank stays grounded in current, real interview
experience rather than relying solely on generated scenarios.

## Submitting a real interview question

`interview_prep/question_bank.json` is a structured, tagged bank, not prose. If you've been
asked something in a real AI-agent-engineering interview that isn't already well covered,
please open a PR that adds it.

### Schema

Every entry follows this shape:

```json
{
  "id": "rag-013",
  "chapter": 3,
  "category": "RAG evaluation",
  "difficulty": "mid",
  "format": "scenario_first",
  "scenario": "Your RAG system returns confident but wrong answers.",
  "follow_up": "Which metric tells you whether retrieval or generation is failing?",
  "grounded_in_real_incident": false,
  "source_note": null
}
```

Field notes:

- `id`: a short kebab-case slug, prefixed with a category shorthand (e.g. `rag-`, `agent-`,
  `sec-`) and a zero-padded number that doesn't collide with an existing entry.
- `chapter`: the integer 1–9 this question maps to most closely. Chapter 8 (system design) or
  a cross-chapter question is fine too; use your judgment.
- `format`: one of `scenario_first`, `question_first`, `slack_snippet`, or
  `stakeholder_quote`. Please don't add a fifth `scenario_first` entry in a row; the bank is
  deliberately varied so it doesn't read as templated.
- `key_concepts` does NOT live in this file. A learner browsing `question_bank.json` should
  not be handed the answer skeleton to all 93 questions along with the questions, so the tags
  live in `solutions/question_bank_answers.json` alongside the written answer, keyed by the
  same `id`. Add both halves there when you add a question:

  ```json
  "rag-013": {
    "key_concepts": ["faithfulness", "recall@k", "groundedness"],
    "answer": "..."
  }
  ```

  2–4 short tags, used only for the drill notebooks' lightweight keyword-presence check,
  which runs after the learner has committed to an answer. Every question needs an entry;
  `tests/test_agentlib.py` asserts neither side has orphans.
- `grounded_in_real_incident` / `source_note`: set `true` and link a source only if the
  scenario is modeled on a real, publicly documented incident (a postmortem, a post-incident
  writeup). Paraphrase the failure pattern in your own words; never quote or closely mirror
  the original text. Leave `false`/`null` for original scenarios, including ones inspired by
  a real interview you personally experienced (don't link back to a specific employer's
  interview process; describe the technical scenario only).

### What we will not merge

- No scraped questions: don't submit anything pulled from Glassdoor, Blind, LeetCode
  discussion threads, or similar sites. This is both a terms-of-service problem and a quality
  problem (that content is often wrong or misremembered). If you were personally asked a
  question in an interview, describe it in your own words instead.
- No inline model answers: `question_bank.json` never contains a full answer, only
  `key_concepts`. If you're contributing a question, also contribute its answer as a PR to
  `solutions/question_bank_answers.json`, keyed by the same `id`, so the two stay in sync.
- No verbatim reproduction of copyrighted material (postmortems, articles, proprietary
  interview content) anywhere in the repo.

### PR process

1. Fork and branch.
2. Add your entry to `interview_prep/question_bank.json` (and its answer to
   `solutions/question_bank_answers.json`).
3. Open a PR briefly describing what prompted the addition (a real interview, a gap you
   noticed, a real incident you want it grounded in). This isn't published anywhere; it's
   just useful context for review.
4. A maintainer will check the entry against the schema and the constraints above before
   merging.

## Reporting content that's wrong or outdated

Please use the "Content accuracy / errata" issue template (separate from the standard bug
report template, which is for code that doesn't run) if an explanation, citation, price,
model name, or technical claim anywhere in this repo is wrong or has gone stale. See the
README's "AI-assisted content and human review" section for why this matters here in
particular. This repo has not yet had an end-to-end practitioner review, and that review is
exactly what this issue template is for.

## Reporting a bug (code doesn't run)

If a notebook throws an error, a test fails, or CI is red, please open a standard bug report
issue with: which notebook/file, the exact error/traceback, and your environment (Python
version, whether you had an API key set).

## Security issues

Do not open a public issue for a security vulnerability in this repo's own code, CI, or
dependencies; see [`SECURITY.md`](SECURITY.md) instead. (Chapter 6's prompt-injection
content is a teaching exercise against a mock system, not a real system to disclose against;
see the responsible-use note at the top of that notebook.)
