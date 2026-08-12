"""Provider-agnostic real-API wrapper for Anthropic and OpenAI.

Placeholder — implemented in Unit 2 (Chapter 1). Will expose a `call_model()` function that
reads the `LLM_PROVIDER` environment variable and dispatches to either
`anthropic.Anthropic().messages.create(...)` or the equivalent OpenAI chat-completions call,
normalizing both providers' responses and tool-call formats into one common return shape, plus
an `HAS_KEY` toggle and basic retry-on-rate-limit handling. See curriculum/01_fundamentals.ipynb
once Unit 2 lands.
"""
