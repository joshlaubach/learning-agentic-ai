"""Unit tests for shared functions in agentlib/.

Real tests get added chapter by chapter as each agentlib module is implemented (see
PROGRESS.md): llm_client's pure-logic pieces as of Unit 2 (Chapter 1); tracing in Unit 3;
tools, loop_guards, synthetic_data, and eval_metrics in Unit 4. This file also asserts
determinism given a fixed seed wherever a module generates data.
"""

import pytest

import agentlib
import agentlib.eval_metrics as eval_metrics
import agentlib.llm_client as llm_client
import agentlib.loop_guards
import agentlib.synthetic_data as synthetic_data
import agentlib.tools
import agentlib.tracing
from solutions.reference import ch03 as ref_ch03


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


# --- agentlib.tracing ---

from agentlib.tracing import Tracer


def test_tracer_span_context_manager_measures_real_time():
    tracer = Tracer()
    with tracer.span("Jack", role="planner"):
        pass
    assert len(tracer.spans) == 1
    assert tracer.spans[0].name == "Jack"
    assert tracer.spans[0].metadata == {"role": "planner"}
    assert tracer.spans[0].duration_ms >= 0


def test_tracer_record_uses_simulated_duration_not_real_time():
    tracer = Tracer()
    tracer.record("Bob", duration_ms=450.0, role="worker")
    assert tracer.spans[0].duration_ms == 450.0


def test_tracer_summary_and_slowest():
    tracer = Tracer()
    tracer.record("Jack", duration_ms=100.0)
    tracer.record("Bob", duration_ms=500.0)
    tracer.record("Mike", duration_ms=200.0)

    assert tracer.slowest().name == "Bob"
    assert tracer.total_ms() == 800.0
    summary = tracer.summary()
    assert [s["name"] for s in summary] == ["Jack", "Bob", "Mike"]
    assert summary[1]["duration_ms"] == 500.0


def test_tracer_reset_clears_spans():
    tracer = Tracer()
    tracer.record("Jack", duration_ms=100.0)
    tracer.reset()
    assert tracer.spans == []
    assert tracer.slowest() is None


# --- agentlib.eval_metrics ---


# precision@k / recall@k / MRR are graded builds as of the autograder conversion: the
# learner writes them in Chapter 3 and the model answers live in solutions/reference/ch03.py,
# so these tests point there. The full case suites are in agentlib/tasks_ch03.py.


def test_precision_recall_at_k():
    retrieved = ["a", "b", "c", "d"]
    relevant = {"b", "d", "z"}
    assert ref_ch03.precision_at_k(retrieved, relevant, k=2) == 0.5  # b in top 2
    assert ref_ch03.precision_at_k(retrieved, relevant, k=4) == 0.5  # b, d in top 4
    assert ref_ch03.recall_at_k(retrieved, relevant, k=4) == pytest.approx(2 / 3)


def test_precision_at_k_empty_top_k_is_zero():
    assert ref_ch03.precision_at_k([], {"a"}, k=3) == 0.0


def test_mean_reciprocal_rank():
    assert ref_ch03.mean_reciprocal_rank(["a", "b", "c"], {"b"}) == 0.5
    assert ref_ch03.mean_reciprocal_rank(["a", "b", "c"], {"a"}) == 1.0
    assert ref_ch03.mean_reciprocal_rank(["a", "b", "c"], {"z"}) == 0.0


def test_evaluate_retrieval_aggregates_across_queries():
    queries = [
        {"query": "q1", "relevant_doc_ids": {"a"}},
        {"query": "q2", "relevant_doc_ids": {"z"}},
    ]

    def retrieve_fn(query, k):
        return {"q1": ["a", "b"], "q2": ["x", "y"]}[query]

    result = eval_metrics.evaluate_retrieval(
        queries,
        retrieve_fn,
        k=2,
        precision_fn=ref_ch03.precision_at_k,
        recall_fn=ref_ch03.recall_at_k,
        mrr_fn=ref_ch03.mean_reciprocal_rank,
    )
    assert result["n_queries"] == 2
    assert result["mrr"] == 0.5  # q1 hits at rank 1 (mrr=1.0), q2 never hits (mrr=0.0)


def test_faithfulness_score_full_and_zero_support():
    context = ["Anthropic was founded in 2021 by Dario Amodei and Daniela Amodei."]
    grounded_answer = "Anthropic was founded in 2021."
    ungrounded_answer = "Bananas are a great source of potassium."

    assert eval_metrics.faithfulness_score(grounded_answer, context) == 1.0
    assert eval_metrics.faithfulness_score(ungrounded_answer, context) < 0.5


# --- agentlib.synthetic_data ---


def test_load_squad_sample_from_cache_has_expected_shape():
    sample = synthetic_data.load_squad_sample()
    assert len(sample["docs"]) > 0
    assert len(sample["qa_pairs"]) > 0
    doc_ids = {d["doc_id"] for d in sample["docs"]}
    for qa in sample["qa_pairs"]:
        assert qa["gold_doc_id"] in doc_ids


def test_generate_confusable_documents_is_deterministic():
    sample = synthetic_data.load_squad_sample()
    run_1 = synthetic_data.generate_confusable_documents(sample["docs"], n=5, seed=42)
    run_2 = synthetic_data.generate_confusable_documents(sample["docs"], n=5, seed=42)
    assert run_1 == run_2
    assert len(run_1) > 0
    for confusable in run_1:
        assert confusable["synthetic_change"] is not None
        assert confusable["confusable_of"] in {d["doc_id"] for d in sample["docs"]}


def test_load_messy_corpus_from_cache_is_nonempty_text():
    text = synthetic_data.load_messy_corpus()
    assert isinstance(text, str)
    assert len(text) > 500


def test_generate_request_log_is_deterministic_and_well_formed():
    log_1 = synthetic_data.generate_request_log(n_requests=50, seed=42)
    log_2 = synthetic_data.generate_request_log(n_requests=50, seed=42)
    assert log_1 == log_2
    assert len(log_1) == 50

    required_fields = {
        "request_id", "timestamp", "model", "input_tokens", "output_tokens",
        "queue_depth", "queue_time_ms", "network_time_ms", "inference_time_ms",
        "generation_time_ms", "total_latency_ms",
    }
    for row in log_1:
        assert required_fields.issubset(row.keys())
        assert row["input_tokens"] > 0
        assert row["output_tokens"] > 0
        stage_sum = (
            row["queue_time_ms"] + row["network_time_ms"]
            + row["inference_time_ms"] + row["generation_time_ms"]
        )
        assert abs(stage_sum - row["total_latency_ms"]) < 0.3  # 4 independently-rounded components

    timestamps = [row["timestamp"] for row in log_1]
    assert timestamps == sorted(timestamps)
