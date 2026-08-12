"""Unit tests for shared functions in agentlib/.

Real tests get added chapter by chapter as each agentlib module is implemented (see
PROGRESS.md): llm_client's pure-logic pieces as of Unit 2 (Chapter 1); tracing in Unit 3;
tools, loop_guards, synthetic_data, and eval_metrics in Unit 4. This file also asserts
determinism given a fixed seed wherever a module generates data.
"""

import pytest

import agentlib
import agentlib.eval_metrics
import agentlib.llm_client as llm_client
import agentlib.loop_guards
import agentlib.synthetic_data
import agentlib.tools
import agentlib.tracing


def test_agentlib_package_imports():
    assert agentlib.__doc__ is not None


# --- agentlib.llm_client ---


def test_has_key_false_with_no_api_key_in_environment():
    # CI (and this test suite) runs with no .env / no API key present -- HAS_KEY must be
    # False so every real-API notebook falls back to its mock path with zero errors.
    assert llm_client.HAS_KEY is False


def test_default_and_strong_models_cover_both_providers():
    for provider in ("anthropic", "openai"):
        assert provider in llm_client.DEFAULT_MODELS
        assert provider in llm_client.STRONG_MODELS
        assert isinstance(llm_client.DEFAULT_MODELS[provider], str)
        assert isinstance(llm_client.STRONG_MODELS[provider], str)
        # Default and stronger tier should never be the same model -- that would defeat the
        # point of having a model= override at all.
        assert llm_client.DEFAULT_MODELS[provider] != llm_client.STRONG_MODELS[provider]


def test_call_model_raises_clear_error_without_a_key():
    with pytest.raises(RuntimeError, match="No API key found"):
        llm_client.call_model(messages=[{"role": "user", "content": "hi"}])


def test_tool_call_and_model_response_construct():
    tc = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "1+1"})
    assert tc.name == "calculator"

    resp = llm_client.ModelResponse(text="hello", tool_calls=[tc], stop_reason="end_turn")
    assert resp.text == "hello"
    assert resp.tool_calls == [tc]


def test_format_tool_result_anthropic_shape(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    tc = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "1+1"})
    msg = llm_client.format_tool_result(tc, "2")
    assert msg["role"] == "user"
    assert msg["content"][0]["type"] == "tool_result"
    assert msg["content"][0]["tool_use_id"] == "tc_1"
    assert msg["content"][0]["content"] == "2"


def test_format_tool_result_openai_shape(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "openai")
    tc = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "1+1"})
    msg = llm_client.format_tool_result(tc, "2")
    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == "tc_1"
    assert msg["content"] == "2"


def test_format_assistant_tool_call_anthropic_shape(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    tc = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "1+1"})
    resp = llm_client.ModelResponse(text="", tool_calls=[tc])
    msg = llm_client.format_assistant_tool_call(resp)
    assert msg["role"] == "assistant"
    tool_use_blocks = [b for b in msg["content"] if b["type"] == "tool_use"]
    assert tool_use_blocks[0]["id"] == "tc_1"
    assert tool_use_blocks[0]["name"] == "calculator"


def test_format_assistant_tool_call_openai_shape(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "openai")
    tc = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "1+1"})
    resp = llm_client.ModelResponse(text="", tool_calls=[tc])
    msg = llm_client.format_assistant_tool_call(resp)
    assert msg["role"] == "assistant"
    assert msg["tool_calls"][0]["id"] == "tc_1"
    assert msg["tool_calls"][0]["function"]["name"] == "calculator"


def test_is_rate_limit_error_detects_429_status_code():
    class FakeError(Exception):
        status_code = 429

    assert llm_client._is_rate_limit_error(FakeError()) is True
    assert llm_client._is_rate_limit_error(ValueError("unrelated")) is False
