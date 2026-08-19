# Chapter 7: Tool Integration — Model Answers

Open this file only after you've attempted `curriculum/07_tool_integration.ipynb`'s
interview drill from memory.

---

## 1. Definitional: why MCP standardizes the client-server interface, not a shared library

A shared library only solves the problem for whoever's willing to write code against that
specific library, in that specific language, imported into that specific process. It's
still one-to-one glue, just glue that happens to live in a package registry instead of a
hand-rolled adapter. It doesn't help a Python agent framework talk to a tool server someone
wrote in TypeScript, and it doesn't help a brand-new agent framework released next year talk
to a tool server that already exists today, since both sides would need to adopt the same
library.

A protocol (a wire format and a set of rules for the messages that cross it) solves this
differently: it doesn't matter what language either side is written in, or whether the two
sides were ever built with each other in mind, as long as both speak the protocol. That's
what turns M×N (every agent framework needing custom glue for every tool) into M+N (each
side implements MCP once, and everything on one side can talk to everything on the other).
It's the same shape of leverage HTTP gives web clients and servers, or that a common file
format gives applications that need to read and write files. The concrete payoff in this
chapter's build: the notebook's client and `_ch07_mcp_server.py` were built independently,
one consuming `mcp.client`, the other `mcp.server.fastmcp`, and they interoperate correctly
without either having any special knowledge of the other's internals. That's the protocol
doing its job, not a shared library doing it.

---

## 2. Cold diagnosis: schema-valid data, confidently wrong answer

Start from the fact that schema validation already passed. That rules out malformed data
(a type error) and version mismatch (a missing/renamed field) immediately, since both of
those would have failed validation before the answer was ever generated. What's left,
matching this chapter's taxonomy, is either a transient issue that somehow didn't surface as
an error (worth briefly checking, but unusual; transient failures are typically visible as
exceptions, not silent wrong answers) or, much more likely, semantically wrong data: a
well-formed, schema-valid response that simply isn't the right answer to what was asked.

The investigation should work outward from the response itself. First, check whether the
returned entity actually matches what was requested. This is this chapter's break-it #3
exactly: a tool that returns data about the wrong thing (wrong package, wrong order, wrong
document, whatever the tool's domain is) passes every type check while being completely
wrong in substance. Compare the identifying field in the response (a name, an ID) against
what was actually asked for.

If the identifying field does match, the wrongness is one level deeper: either the tool's
own data source is stale or wrong (a caching or freshness issue, Chapter 4's territory) or
the agent's interpretation of a correct response was wrong (a prompting/reasoning issue, not
a tool-integration issue at all). It's worth explicitly separating these, since the fix is
completely different depending on which layer the bug is actually in.

The reason schema validation alone can't have caught this is worth stating explicitly in an
interview: schema validation checks shape, not truth. A response can be perfectly well-typed
and still be an answer to a different question than the one asked. That's exactly why this
chapter's taxonomy treats "malformed" and "semantically wrong" as two separate failure types
needing two separate detection mechanisms, not one.

---

## 3. Design judgment: "retry three times with backoff" as a universal policy

This policy is exactly right for transient failures, and actively wrong, or at best
useless, for the other three.

For malformed data, if a response failed schema validation because a field's data is corrupt
at the source (this chapter's `version: 2.5` float-instead-of-string example), retrying the
identical call against the identical source will very likely reproduce the identical
corruption three times in a row, burning latency for zero benefit. What actually helps is
switching to an alternate path (a fresh, uncached read; a different endpoint), which "retry
the same call" doesn't do.

For semantically wrong data, retrying can't fix this at all, because nothing about the call
was wrong; the response was well-formed and the call succeeded. Retrying the same call with
the same arguments will very plausibly return the same wrong-but-valid data every time. This
needs a different kind of check entirely (validating content against what was requested,
this chapter's break-it #3's fix), not more attempts at the same call.

For version mismatch, retrying is actively pointless: the upstream shape has genuinely
changed, so every retry will fail the exact same schema check the first one did. Worse,
"retry three times then give up silently" turns a signal that a developer needs to see (the
integration needs a code update) into three wasted round-trips and then silence. The actual
bug (an outdated field-name assumption) never surfaces to anyone who could fix it.

The general critique to lead with: a universal "retry N times" policy treats every failure
as if it has the same cause (something glitched, try again), when this chapter's whole point
is that tool failures don't share one cause. Retry-everything either wastes time on failures
retrying can't fix, or worse, silently hides failures (malformed data, semantic wrongness,
schema drift) that a developer specifically needed to be told about.

---

## 4. Judgment call: catching schema drift automatically

Since the third-party API's own version number didn't change even though the response shape
did, an integration can't rely on checking a version number at all. It needs to detect the
actual shape changing, independent of whatever the provider claims about versioning.

Strict schema validation belongs on every response, not just at integration time. This
chapter's `PackageInfo` model, applied on every call rather than only in a one-off test, is
exactly this: a field silently renamed or restructured shows up immediately as a validation
failure (the "missing" error type this chapter's version-mismatch scenario demonstrates)
instead of silently propagating bad data downstream until a user notices.

New validation-failure patterns deserve their own alert, distinct from ordinary error
monitoring. A spike in "missing field" errors starting at a specific timestamp, across many
or all calls rather than a random scattering, is the signature of a real upstream schema
change, as opposed to isolated data-quality issues in individual responses, and is worth its
own alert rather than being buried in generic error-rate monitoring.

A canary or smoke-test call against the real API on a schedule, independent of production
traffic, catches a schema change on its own timeline rather than waiting for whichever real
user request happens to hit it first.

Finally, log the raw, unvalidated response (or at least its top-level keys) alongside any
validation failure. When schema drift does get caught, having the actual new shape on hand,
not just "validation failed," is what lets a developer update the integration in one pass
instead of needing to reproduce the failure first to see what actually changed.

The throughline: since the provider's own version number can't be trusted to signal a
breaking change, the integration has to treat its own schema validation as the detector, and
report failures in it as urgently as it would any other observability signal about a system
that changed without warning.

---

## 5. Rapid-fire: malformed JSON from the model

**One sentence:** turn on schema-constrained output at the API level — JSON mode,
`response_format`, or a grammar — so an invalid token cannot be generated in the first place.

That is the right first answer, and it is right for a specific reason worth being able to
state: it removes the failure mode rather than responding to it. The three alternatives people
reach for all respond to it. A retry loop assumes the failure is transient. A repair pass
assumes the damage is outside the JSON rather than inside it. A larger model assumes the
failure is a capability problem, and buys you a lower rate rather than a guarantee — which is
arguably worse, because a 0.5% malformation rate is one that no longer shows up in staging.

**What I'd want to know before trusting it:** whether the provider actually offers constrained
decoding for this schema, and whether the failures are transient or systematic. Those are
different problems. If the same prompt and schema produce the same broken shape every time, no
retry budget helps — the loop just multiplies the bill by the budget. If the failures are
scattered and rare, a retry is a legitimate stopgap while you wire up the real fix. And if
constrained decoding isn't available at all, the honest answer is a repair pass *plus*
validation *plus* a bounded retry, in that order, and knowing that this stack has a ceiling.

Raising temperature, for completeness, is the opposite of a fix. Lower it if anything —
though determinism in format is not what temperature primarily controls, and reaching for it
first suggests the mechanism isn't clear.

---

## 6. Cold diagnosis: the retry loop that helps everyone except one customer

The distinguishing property is that this customer's failures are **systematic**, not
transient, and a retry loop can only ever fix the second kind.

For everyone else, malformation is a sampling accident: the same request would mostly have
succeeded, so a fresh generation is a genuinely fresh roll and the error rate falls
geometrically with attempts. For this customer, something about their input makes the model
produce the same malformed output every time — and re-prompting reproduces it exactly. Four
attempts means four identical failures and four times the cost.

What to look for in their traffic, roughly in order of likelihood:

- **Content that collides with the JSON encoding.** Unescaped quotes, backslashes, or newlines
  in the source text — a company name with a `"` in it, a Windows file path, a snippet of code.
  The model reproduces the character verbatim and breaks its own string literal.
- **Non-ASCII or RTL text**, which shifts tokenization enough to change what the model emits
  around the structural characters.
- **A field that is genuinely absent from their documents**, so the model improvises: emits
  `null` unquoted, or omits the key, or writes a prose apology where a value belongs.
- **Length.** If their inputs are longer than everyone else's, the response may be hitting the
  output token limit and truncating mid-object. Truncation is 100% reproducible and looks
  exactly like malformation.

That last one is worth calling out separately because the fix is different: truncation is not
a format problem and constrained decoding will not save you from it either — the grammar
happily produces a valid prefix and then runs out of budget. Check `finish_reason` before
concluding anything about format.

The general lesson: before adding retries to anything, ask whether a second attempt is
actually an independent trial. If it isn't, a retry budget is just a spend cap on a failure.

---

## 7. Judgment call: does constrained output let you delete validation?

No, and the distinction is one interviewers push on deliberately, because it separates people
who have used the feature from people who have read about it.

**What the guarantee covers:** the output parses, and it conforms to the schema. Required
fields are present, types match, and no key outside the schema appears. That is real, and it
genuinely does replace your *parser* — the fence-stripping, brace-scanning, try/except layer
can go.

**What it does not cover** is everything about whether the content is right:

- **Values can be wrong.** The chapter's `_c5` case is exactly this: a decoder that masks
  correctly but picks carelessly returns `{"name": "nump", "summary": "Fund"}` — perfect JSON,
  correct keys, truncated garbage in the values. The grammar has no opinion about which legal
  string is the true one.
- **Values can be hallucinated.** Constraining the shape gives the model *no* option to say
  "this field isn't in the document." If `version` is required and there is no version in the
  source, it must emit some string, so it invents one. Constrained decoding can actively
  *increase* fabrication on fields the source doesn't support — make genuinely optional fields
  nullable in the schema, or the constraint becomes a fabrication requirement.
- **Cross-field consistency is unchecked.** `start_date` after `end_date`, a total that isn't
  the sum of the line items, a currency that doesn't match the country. No grammar catches
  these.
- **Business rules are unchecked.** An amount within schema but outside any plausible range, an
  ID matching the type but referring to nothing.

So the layers do different jobs and both stay: constrained decoding is a **syntactic and
structural** guarantee, and validation is a **semantic** one. The teammate is right that one
specific piece of code can go — the JSON repair path — and wrong that the validation can.

---

## 8. Design judgment: six fields, two frequently absent

The core move is to make "absent" a **representable value in the schema** rather than a
failure of extraction, and then keep the two apart at every layer.

**Schema.** The four reliable fields are required and non-null. The two frequently-absent
fields are declared nullable — `str | None`, with `None` an explicitly legal value the model
is told to use when the document doesn't contain the field. This is the load-bearing decision.
If those fields are required and non-nullable, constrained decoding forces the model to emit
*something* for a field that isn't there, and it will oblige with a plausible invention. The
schema would be converting a missing value into a fabricated one, silently, on exactly the
fields where you can least afford it.

**Success condition.** Three outcomes, not two:

- `ok` — parsed, on-schema, all four required fields populated. The optional two may be null.
- `incomplete` — parsed and on-schema, but a required field is null or empty. This is a
  *document* problem: retrying will not help, and the record should route to human review.
- `failed` — did not parse, or did not conform. This is a *pipeline* problem: worth a retry,
  and worth alerting on if the rate moves.

Collapsing `incomplete` into `failed` is what generates the phantom retry storms — the loop
burns its budget re-asking for something that was never in the document. Collapsing it into
`ok` is worse, because a half-filled invoice flows downstream looking complete. The chapter's
`_t8` case is this exact mistake in miniature: a model that emits flawless JSON with a field
quietly missing, accepted by any success condition built on "did it parse".

**Instrumentation.** Track the null rate per field, not just the overall failure rate. A field
that is null 30% of the time is a documented property of your corpus; the same field jumping
to 80% overnight is an upstream change — a new document template, a different scanner, a
prompt edit — and it is invisible in an aggregate success metric that counts those records as
successes.
