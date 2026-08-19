"""Provider-agnostic real-API wrapper for Anthropic and OpenAI.

Built in Chapter 1 (curriculum/01_fundamentals.ipynb) and reused, unmodified, by every later
real-API chapter (2, 3, 4, 6, 7) and the capstone. This is the one module in `agentlib` that
is NOT built inline-first in a notebook — every real-API section from Chapter 2 onward needs
it immediately, and reimplementing a provider client per-notebook would be unrealistic.

The point of this module, pedagogically: building directly against one vendor's SDK
everywhere is a common early mistake that creates painful lock-in later. `call_model()` reads
`LLM_PROVIDER` once and normalizes both providers' responses and tool-call formats into one
common shape, so the rest of the curriculum never has to branch on which provider a learner
picked.

Model choices (verified against live pricing pages at build time — see REFERENCES.md's
staleness disclaimer, since these move fast):
  - Default (cheapest current-gen) model: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`,
    $1/$5 per million input/output tokens) on Anthropic, GPT-5.6 Luna (`gpt-5.6-luna`,
    OpenAI's fastest/lowest-cost current tier) on OpenAI. Do not use the bare `"gpt-5.6"`
    alias if you specifically want Luna — it currently routes to the flagship "Sol" tier
    instead, which is easy to do by accident and a good reason to pin exact model IDs, not
    aliases, in production.
  - Stronger tier (`model=` override, used by Chapter 6 and the capstone): Claude Sonnet 5
    (`claude-sonnet-5`, $2/$10 per million tokens — Anthropic made this permanent on
    2026-08-11 rather than the price increase originally planned for September) on
    Anthropic, GPT-5.6 Terra (`gpt-5.6-terra`, OpenAI's balanced everyday-work tier) on
    OpenAI.
  - OpenAI pricing specifically has been reported inconsistently across sources during this
    repo's construction (figures from ~$0.20/$1.20 to $1/$6 per million tokens depending on
    source and date) — this module deliberately does not hardcode an OpenAI price anywhere.
    Check https://developers.openai.com/api/docs/pricing for the live number.
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").strip().lower()

_KEY_ENV_VAR = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}

DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "openai": "gpt-5.6-luna",
}

STRONG_MODELS = {
    "anthropic": "claude-sonnet-5",
    "openai": "gpt-5.6-terra",
}

HAS_KEY = bool(os.environ.get(_KEY_ENV_VAR.get(LLM_PROVIDER, ""), "").strip())


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict[str, Any]


@dataclass
class ModelResponse:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str | None = None
    raw: Any = None


class RetryExhaustedError(RuntimeError):
    """Raised when call_model() exhausts its retry budget on rate-limit errors."""


def _is_rate_limit_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 429:
        return True
    return exc.__class__.__name__ in {"RateLimitError", "APIStatusError"} and "429" in str(exc)


def _with_retry(fn, max_retries: int = 5, base_delay: float = 1.0):
    """Exponential backoff with jitter, retrying only on rate-limit-shaped errors.

    Used for real API calls only — never exercised when HAS_KEY is False, since the
    notebooks fall back to a mock brain in that case rather than calling this at all.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - deliberately broad, re-raised on last attempt
            if not _is_rate_limit_error(exc) or attempt == max_retries - 1:
                raise
            delay = base_delay * (2**attempt) + random.uniform(0, base_delay)
            time.sleep(delay)
    raise RetryExhaustedError(f"exhausted {max_retries} retries")


def _to_anthropic_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            "input_schema": t["input_schema"],
        }
        for t in tools
    ]


def _to_openai_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


def _call_anthropic(
    messages: list[dict],
    system: str | None,
    tools: list[dict] | None,
    model: str,
    max_tokens: int,
) -> ModelResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = _to_anthropic_tools(tools)

    response = _with_retry(lambda: client.messages.create(**kwargs))

    text_parts = [block.text for block in response.content if block.type == "text"]
    tool_calls = [
        ToolCall(id=block.id, name=block.name, input=block.input)
        for block in response.content
        if block.type == "tool_use"
    ]
    return ModelResponse(
        text="".join(text_parts),
        tool_calls=tool_calls,
        stop_reason=response.stop_reason,
        raw=response,
    )


def _call_openai(
    messages: list[dict],
    system: str | None,
    tools: list[dict] | None,
    model: str,
    max_tokens: int,
) -> ModelResponse:
    import json

    import openai

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    full_messages = list(messages)
    if system:
        full_messages = [{"role": "system", "content": system}] + full_messages

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": full_messages,
        "max_completion_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = _to_openai_tools(tools)

    response = _with_retry(lambda: client.chat.completions.create(**kwargs))

    choice = response.choices[0]
    tool_calls = [
        ToolCall(
            id=tc.id,
            name=tc.function.name,
            input=json.loads(tc.function.arguments or "{}"),
        )
        for tc in (choice.message.tool_calls or [])
    ]
    return ModelResponse(
        text=choice.message.content or "",
        tool_calls=tool_calls,
        stop_reason=choice.finish_reason,
        raw=response,
    )


def call_model(
    messages: list[dict],
    system: str | None = None,
    tools: list[dict] | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
) -> ModelResponse:
    """Call whichever provider LLM_PROVIDER points to, returning a normalized ModelResponse.

    `tools`, if given, uses one common schema regardless of provider:
        [{"name": str, "description": str, "input_schema": <JSON schema dict>}, ...]

    `model` defaults to DEFAULT_MODELS[LLM_PROVIDER] (each provider's cheapest current
    general-purpose model). Pass model=STRONG_MODELS[LLM_PROVIDER] for chapters that want a
    higher-quality-reasoning tier instead.
    """
    if not HAS_KEY:
        raise RuntimeError(
            f"No API key found for LLM_PROVIDER={LLM_PROVIDER!r}. "
            f"Set {_KEY_ENV_VAR.get(LLM_PROVIDER, 'the matching API key')} in .env, "
            "or use the mock/offline path instead (see HAS_KEY in this module)."
        )

    resolved_model = model or DEFAULT_MODELS[LLM_PROVIDER]

    if LLM_PROVIDER == "anthropic":
        return _call_anthropic(messages, system, tools, resolved_model, max_tokens)
    elif LLM_PROVIDER == "openai":
        return _call_openai(messages, system, tools, resolved_model, max_tokens)
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. Set LLM_PROVIDER to "
            "'anthropic' or 'openai' in .env."
        )


def format_tool_result(tool_call: ToolCall, result_content: str) -> dict:
    """Build the follow-up message for a tool result, in whichever shape the active
    provider expects, so callers never have to branch on LLM_PROVIDER themselves.
    """
    if LLM_PROVIDER == "anthropic":
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result_content,
                }
            ],
        }
    elif LLM_PROVIDER == "openai":
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result_content,
        }
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}")


def format_tool_results(pairs: list) -> list[dict]:
    """Build the follow-up message(s) for one or more tool results, correctly batched.

    Takes [(ToolCall, result_string), ...] and returns a LIST of messages, because the right
    batching differs by provider and getting it wrong is an invalid request rather than a
    degraded answer:

    - Anthropic wants every `tool_result` block for a given assistant turn inside ONE user
      message. An assistant turn carrying two `tool_use` blocks must be answered by a single
      user turn carrying two `tool_result` blocks.
    - OpenAI wants one separate `role: "tool"` message per `tool_call_id`.

    Prefer this over calling format_tool_result() in a loop. A model that emits parallel tool
    calls produces one assistant turn with several `tool_use` blocks, and replying with a
    single result -- or with several separate user turns -- leaves those blocks unanswered.
    Anthropic rejects that outright: every `tool_use` block must have a matching `tool_result`.
    """
    if not pairs:
        return []

    if LLM_PROVIDER == "anthropic":
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result_content,
                    }
                    for tool_call, result_content in pairs
                ],
            }
        ]
    elif LLM_PROVIDER == "openai":
        return [format_tool_result(tc, content) for tc, content in pairs]
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}")


def format_assistant_tool_call(response: ModelResponse) -> dict:
    """Build the assistant-turn message representing a model's tool call(s), in whichever
    shape the active provider expects, so it can be appended to `messages` before the
    matching format_tool_result() messages.
    """
    if LLM_PROVIDER == "anthropic":
        content: list[dict] = []
        if response.text:
            content.append({"type": "text", "text": response.text})
        for tc in response.tool_calls:
            content.append(
                {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input}
            )
        return {"role": "assistant", "content": content}
    elif LLM_PROVIDER == "openai":
        import json

        return {
            "role": "assistant",
            "content": response.text or None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": json.dumps(tc.input)},
                }
                for tc in response.tool_calls
            ]
            or None,
        }
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}")
