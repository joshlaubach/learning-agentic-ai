# Chapter 6: Security and Safeguards (Model Answers)

Open this file only after you've attempted `curriculum/06_security_safeguards.ipynb`'s
interview drill from memory.

---

## 1. Definitional: direct vs. indirect prompt injection

*Direct* prompt injection is a user typing a malicious instruction straight into their own
conversation with the agent: "ignore your previous instructions and do X." It's the easiest
case to reason about, because the untrusted content and "the conversation" are the same
thing; anything a user types is, by definition, something you should already be treating
with some suspicion.

*Indirect* prompt injection is different in a way that matters much more once an agent has
tools: the malicious instruction arrives inside content the agent *retrieves or processes on
someone's behalf* (a support ticket, a web page, a document, a retrieved search result, an
email), content that was never flagged as "user input" at all, because from the system's
point of view it's just data the agent is supposed to read. This chapter's break-it #1 is
exactly this: the attacker never talks to the agent directly, they just get their words into
a ticket the agent will eventually read.

An agent with tools is the case where this actually bites, because reading untrusted content
used to be low-stakes (a chatbot that only ever talks back to you can't do much damage by
being fooled). The moment an agent can *act* on what it reads (issue a refund, send an
email, run a query), an indirect injection stops being "the agent said something wrong" and
becomes "the agent did something wrong," with real consequences downstream. That's the
distinction worth leading with in an interview: direct injection is a prompting problem,
indirect injection against a tool-using agent is a security problem with a real blast
radius.

---

## 2. Cold diagnosis: an outsized refund with no normal request behind it

Start from the fact that there's no legitimate request to trace; that rules out "a customer
made a normal but confusing ask" and points straight at the agent having acted on something
it shouldn't have treated as an instruction at all. The investigation:

- Pull whatever raw content the agent was processing right before the refund was issued:
  the actual ticket, email, or document text, not a summary of it. This chapter's break-it #1
  is exactly this shape: the "request" was never a request, it was a directive-shaped line
  buried in otherwise ordinary text. Look specifically for anything that reads like an
  authoritative directive (a line starting with `SYSTEM:`, `ADMIN:`, "ignore previous
  instructions," or similar) sitting inside content that should have been pure data.
- Check whether the refund amount matches anything real: the actual order total, a
  policy-defined maximum, anything grounded in the system's own data. If the amount has no
  connection to the order it's attached to, that's strong evidence the amount came from
  content the agent trusted that it shouldn't have, exactly this chapter's break-it #1
  pattern, not a miscalculation.
- Check what validated the tool call before it executed. If there was no independent
  policy check on the refund amount (nothing verifying `amount <= order_total` regardless of
  how the amount was decided), that's the actual gap, and it's the fix regardless of how the
  injected content got in. This is the chapter's "layer 2" argument: even a good instruction/
  data separation can have a gap, which is exactly why a policy check on the tool call itself,
  independent of how the decision was reached, is the layer that actually stops the damage.
- Only after confirming this is an injection would it be worth separately checking
  whether the tool itself was over-scoped (break-it #2's lesson). If the same bug could have
  reached something worse than a refund (a database wipe, an unrestricted email send), that's
  a second, independent finding about blast radius, not the same bug restated.

---

## 3. Design judgment: "just tell it not to follow instructions in user content"

Would not rely on this alone, and the reasoning is the same "mixed channel" problem this
chapter's concept section names directly: the instruction *not* to follow embedded
instructions lives in the exact same channel as the embedded instructions themselves; there
is nothing structurally separating "things the model should treat as authoritative" from
"things it should treat as data," so a strongly-worded system-prompt instruction is
competing with the attack on equal footing, not overriding it from a privileged position.
This chapter's break-it #3 makes the identical point about secrets: telling a model "never
reveal this" inside the same prompt that contains the thing not to reveal is the same
category of fragile defense.

What to add instead, layered rather than as a replacement:

- Explicit content-boundary framing: wrap untrusted content in clear delimiters and
  instruct the model that content inside those delimiters is data to summarize/answer
  questions about, never instructions to follow (what this chapter's `sanitize_ticket_text`
  does at the pattern level; a real system would do this more robustly, e.g. with a
  dedicated data-tagging convention the model was specifically trained to respect).
- A policy check on the resulting tool call, independent of how the decision was reached:
  this chapter's break-it #1 fix, layer 2. This is the one that actually stops the damage
  even if the prompt-level defense has a gap, which it likely will, since prompt-level
  instruction-following isn't a hard guarantee.
- Least-privilege tool scoping: break-it #2's lesson. Even a successfully-tricked model
  can only do as much damage as its tools allow; this doesn't stop the trick, but it bounds
  the consequence.

The honest framing for an interview: a stronger system-prompt instruction is worth having
(it's cheap and it helps at the margin), but presenting it as *the* fix, rather than one
layer among several, is the actual red flag an interviewer is likely listening for here.

---

## 4. Judgment call: least-privileged "can send emails"

Working from most to least privileged, and what an attacker loses at each step:

1. Unrestricted `send_email(to, subject, body)`. The agent can email anyone, anything.
   An attacker who tricks the agent (via a summarized email's content, e.g.) can exfiltrate
   data to an arbitrary address or impersonate the user to anyone.
2. Restrict `to` to a fixed allowlist (e.g., only the user's own saved contacts). An
   attacker can no longer exfiltrate to an address of their choosing. This is the most
   damaging single restriction, since it closes off exfiltration as a goal entirely, even if
   the agent can still be tricked into *sending* something.
3. Require the body to be a reply in an existing thread, not an arbitrary new message.
   An attacker embedding an instruction in an email the agent reads can no longer get the
   agent to originate new outbound content on their behalf, only respond within a context a
   human already started.
4. Draft-and-hold instead of send: the agent composes a reply but a human confirms
   before it actually sends. This is the strongest version and the one this chapter's
   concept section gestures at with "human approval gates for sensitive actions." It doesn't
   prevent the agent from being tricked into drafting something bad, but it puts a human in
   the loop before anything leaves the system, which is the actual backstop once every other
   layer has a gap.

The general shape worth naming explicitly: each restriction above doesn't make the agent
harder to trick; it removes one more thing a successful trick can accomplish. That's the
least-privilege argument from this chapter's build section, applied to a different tool.
