# Chapter 7: Tool Integration — Model Answers

Open this file only after you've attempted `curriculum/07_tool_integration.ipynb`'s
interview drill from memory.

---

## 1. Definitional: why MCP standardizes the client-server interface, not a shared library

A shared library only solves the problem for whoever's willing to write code against that
specific library, in that specific language, imported into that specific process — it's
still one-to-one glue, just glue that happens to live in a package registry instead of a
hand-rolled adapter. It doesn't help a Python agent framework talk to a tool server someone
wrote in TypeScript, and it doesn't help a brand-new agent framework released next year talk
to a tool server that already exists today, since both sides would need to adopt the same
library.

A **protocol** (a wire format and a set of rules for the messages that cross it) solves this
differently: it doesn't matter what language either side is written in, or whether the two
sides were ever built with each other in mind, as long as both speak the protocol. That's
what turns M×N (every agent framework needing custom glue for every tool) into M+N (each
side implements MCP once, and everything on one side can talk to everything on the other) —
the same shape of leverage HTTP gives web clients and servers, or that a common file format
gives applications that need to read and write files. The concrete payoff in this chapter's
build: the notebook's client and `_ch07_mcp_server.py` were built independently, one
consuming `mcp.client`, the other `mcp.server.fastmcp`, and they interoperate correctly
without either having any special knowledge of the other's internals — that's the protocol
doing its job, not a shared library doing it.

---

## 2. Cold diagnosis: schema-valid data, confidently wrong answer

Start from the fact that schema validation already passed — that rules out malformed data
(a type error) and version mismatch (a missing/renamed field) immediately, since both of
those would have failed validation before the answer was ever generated. What's left,
matching this chapter's taxonomy, is either a transient issue that somehow didn't surface as
an error (worth briefly checking, but unusual — transient failures are typically visible as
exceptions, not silent wrong answers) or, much more likely, **semantically wrong data**: a
well-formed, schema-valid response that simply isn't the right answer to what was asked.

The investigation:

- **Check whether the returned entity actually matches what was requested** — this chapter's
  break-it #3 exactly: a tool that returns data *about the wrong thing* (wrong package, wrong
  order, wrong document — whatever the tool's domain is) passes every type check while being
  completely wrong in substance. Compare the identifying field in the response (a name, an
  ID) against what was actually asked for.
- **If the identifying field does match**, the wrongness is one level deeper — either the
  tool's own data source is stale/wrong (a caching or freshness issue, Chapter 4's territory)
  or the agent's *interpretation* of a correct response was wrong (a prompting/reasoning
  issue, not a tool-integration issue at all). Worth explicitly separating these, since the
  fix is completely different depending on which layer the bug is actually in.
- **The reason schema validation alone can't have caught this** is worth stating explicitly
  in an interview: schema validation checks shape, not truth. A response can be perfectly
  well-typed and still be an answer to a different question than the one asked — that's
  exactly why this chapter's taxonomy treats "malformed" and "semantically wrong" as two
  separate failure types needing two separate detection mechanisms, not one.

---

## 3. Design judgment: "retry three times with backoff" as a universal policy

This policy is exactly right for **transient** failures and actively wrong, or at best
useless, for the other three:

- **Malformed** — if a response failed schema validation because a field's data is corrupt
  at the source (this chapter's `version: 2.5` float-instead-of-string example), retrying the
  identical call against the identical source will very likely reproduce the identical
  corruption three times in a row, burning latency for zero benefit. What actually helps is
  switching to an alternate path (a fresh, uncached read; a different endpoint), which "retry
  the same call" doesn't do.
- **Semantically wrong** — retrying can't fix this at all, because nothing about the *call*
  was wrong; the response was well-formed and the call succeeded. Retrying the same call with
  the same arguments will very plausibly return the same wrong-but-valid data every time.
  This needs a different kind of check entirely (validating content against what was
  requested, this chapter's break-it #3's fix), not more attempts at the same call.
- **Version mismatch** — retrying is actively pointless here: the upstream shape has
  genuinely changed, so every retry will fail the exact same schema check the first one did.
  Worse, "retry three times then give up silently" turns a signal that a developer needs to
  see (the integration needs a code update) into three wasted round-trips and then silence —
  the actual bug (an outdated field-name assumption) never surfaces to anyone who could fix
  it.

The general critique to lead with: a universal "retry N times" policy treats every failure as
if it has the same cause (something glitched, try again), when this chapter's whole point is
that tool failures don't share one cause — retry-everything either wastes time on failures
retrying can't fix, or worse, silently hides failures (malformed data, semantic wrongness,
schema drift) that a developer specifically needed to be told about.

---

## 4. Judgment call: catching schema drift automatically

Since the third-party API's own version number didn't change even though the response shape
did, an integration can't rely on checking a version number at all — it needs to detect the
*actual shape* changing, independent of whatever the provider claims about versioning:

- **Strict schema validation on every response, not just at integration time.** This
  chapter's `PackageInfo` model, applied on every call rather than only in a one-off test,
  is exactly this — a field silently renamed or restructured shows up immediately as a
  validation failure (the "missing" error type this chapter's version-mismatch scenario
  demonstrates) instead of silently propagating bad data downstream until a user notices.
- **Alert on new validation-failure patterns specifically, distinct from ordinary error
  monitoring.** A spike in "missing field" errors starting at a specific timestamp, across
  many/all calls rather than a random scattering, is the signature of a real upstream schema
  change (as opposed to isolated data-quality issues in individual responses) — worth its own
  alert rather than being buried in generic error-rate monitoring.
- **A canary/smoke-test call against the real API on a schedule**, independent of production
  traffic, so a schema change gets caught by a scheduled check rather than by whichever real
  user request happens to hit it first.
- **Log the raw, unvalidated response (or at least its top-level keys) alongside any
  validation failure.** When schema drift does get caught, having the actual new shape on
  hand — not just "validation failed" — is what lets a developer update the integration in
  one pass instead of needing to reproduce the failure first to see what actually changed.

The throughline: since the provider's own version number can't be trusted to signal a
breaking change, the integration has to treat its own schema validation as the detector — and
report failures in it as urgently as it would any other observability signal about a system
that changed without warning.
