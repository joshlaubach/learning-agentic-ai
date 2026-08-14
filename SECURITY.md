# Security Policy

This policy covers vulnerabilities in this repository's own code, CI configuration, and
dependencies: its build scripts, `agentlib/` library code, test suite, and GitHub Actions
workflow. It does not cover Chapter 6's prompt-injection content, which is a pedagogical
exercise run against a mock system the learner controls, not a real system to disclose
against (see the responsible-use note at the top of `curriculum/06_security_safeguards.ipynb`).

## Reporting a vulnerability

If you find a genuine security issue in this repo's own code, for example a dependency with
a known CVE pinned in `requirements.txt`, a CI workflow that could leak secrets, or a code
path in `agentlib/` that executes untrusted input unsafely, please report it privately
rather than opening a public issue:

- Email **joshuaglaubach@gmail.com** with a description of the issue, steps to reproduce if
  applicable, and its potential impact.
- Please allow a reasonable window to investigate and address the issue before any public
  disclosure.

This is a personal/educational project maintained on a best-effort basis, not a funded
security program; there's no bug bounty and no guaranteed SLA, but reports are taken
seriously and will be acknowledged.

## What's in scope

- Vulnerable or malicious dependencies pinned in `requirements.txt`.
- Command injection, path traversal, or unsafe deserialization in `agentlib/` or `tests/`.
- Secrets handling issues (e.g. `.env` values being logged, committed, or leaked in CI).
- GitHub Actions workflow issues (e.g. a workflow that would expose repository secrets to a
  fork's PR).

## What's out of scope

- The intentional, clearly-labeled prompt-injection payloads and "confidential" fake data in
  Chapter 6; those are teaching content, not a real vulnerability, and they only ever run
  against a mock in-notebook system with obviously-fake secrets (e.g.
  `"internal_note": "FAKE-DO-NOT-USE-1234"`).
- The deliberate "break it" bugs throughout the curriculum (infinite loops, stale caches,
  flaky tools, etc.); those are the point of the exercise, not accidental defects.
- Findings about third-party services (Anthropic's or OpenAI's APIs, Hugging Face, SEC EDGAR,
  GH Archive); please report those to the relevant vendor directly.
