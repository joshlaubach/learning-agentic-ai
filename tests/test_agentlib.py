"""Unit tests for shared functions in agentlib/.

Real tests get added chapter by chapter as each agentlib module is implemented (see
PROGRESS.md): llm_client's pure-logic pieces as of Unit 2 (Chapter 1); tracing in Unit 3;
tools, loop_guards, synthetic_data, and eval_metrics in Unit 4. This file also asserts
determinism given a fixed seed wherever a module generates data.
"""

import json
from pathlib import Path

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


# --- agentlib.injection_lab ---
#
# The Chapter 6 lab's core invariant, asserted here so it can't drift: the sanitizer the
# chapter specifies catches five of the eight shipped payloads and misses three. If a change
# ever closes that gap, ch06-write-a-payload silently stops being an exercise -- the learner
# would be asked to defeat a filter with no known gap in it.


def test_injection_lab_every_shipped_payload_is_obeyed_by_the_naive_brain():
    from agentlib.injection_lab import PAYLOADS, obeys_directive, vulnerable_brain

    for payload in PAYLOADS:
        assert obeys_directive(payload["text"]) is not None, payload["id"]
        decision = vulnerable_brain(payload["text"])
        assert decision["tool"] == "issue_refund", payload["id"]


def test_injection_lab_sanitizer_catches_exactly_five_of_eight():
    from agentlib.injection_lab import PAYLOADS, obeys_directive
    from solutions.reference.ch06 import sanitize_ticket_text

    caught = {
        p["id"] for p in PAYLOADS if obeys_directive(sanitize_ticket_text(p["text"])) is None
    }
    expected = {p["id"] for p in PAYLOADS if p["caught"]}
    assert caught == expected, f"expected {sorted(expected)}, caught {sorted(caught)}"
    assert len(caught) == 5


def test_injection_lab_sanitizer_leaves_benign_tickets_untouched():
    from agentlib.injection_lab import BENIGN_TICKETS
    from solutions.reference.ch06 import sanitize_ticket_text

    for ticket in BENIGN_TICKETS:
        assert sanitize_ticket_text(ticket) == ticket, ticket


def test_injection_lab_reference_payload_bypasses_layer_one_and_is_stopped_by_layer_two():
    from agentlib.injection_lab import ORDERS, obeys_directive, vulnerable_brain
    from solutions.reference.ch06 import (
        LEARNER_PAYLOAD,
        check_refund_policy,
        sanitize_ticket_text,
    )

    sanitized = sanitize_ticket_text(LEARNER_PAYLOAD)
    assert obeys_directive(sanitized) is not None, "layer 1 should not neutralize it"

    decision = vulnerable_brain(sanitized)
    allowed, _ = check_refund_policy(
        decision["args"]["order_id"], decision["args"]["amount"], ORDERS
    )
    assert allowed is False, "layer 2 must still refuse the refund"


# --- interview_prep/question_bank.json and its answer key ---
#
# key_concepts moved out of the question bank and into solutions/question_bank_answers.json:
# browsing the questions should not hand you the answer skeleton for all 93 of them. These
# tests keep the two files in sync and keep the answers out of the question file, which
# CONTRIBUTING.md now tells contributors to rely on.

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTION_BANK = REPO_ROOT / "interview_prep" / "question_bank.json"
ANSWER_KEY = REPO_ROOT / "solutions" / "question_bank_answers.json"


def _bank():
    return json.loads(QUESTION_BANK.read_text())


def _answers():
    return json.loads(ANSWER_KEY.read_text())


def test_question_bank_carries_no_answers():
    for question in _bank():
        assert "key_concepts" not in question, (
            f"{question['id']} still ships key_concepts in the question bank; it belongs in "
            "solutions/question_bank_answers.json"
        )


def test_every_question_has_an_answer_entry():
    answers = _answers()
    orphans = [q["id"] for q in _bank() if q["id"] not in answers]
    assert not orphans, f"questions with no answer entry: {orphans}"


def test_every_answer_entry_has_a_question():
    ids = {q["id"] for q in _bank()}
    orphans = [qid for qid in _answers() if qid not in ids]
    assert not orphans, f"answer entries with no question: {orphans}"


def test_every_answer_entry_has_both_halves():
    for qid, entry in _answers().items():
        assert isinstance(entry, dict), f"{qid}: expected {{key_concepts, answer}}, got {type(entry).__name__}"
        assert entry.get("answer", "").strip(), f"{qid}: empty answer"
        concepts = entry.get("key_concepts")
        assert isinstance(concepts, list) and concepts, f"{qid}: key_concepts must be a non-empty list"


# --- parallel tool calls: the invariant the per-helper shape tests missed -----------------


def _tool_use_ids(messages: list) -> list:
    """Every tool_use id the assistant turns claim, in order (Anthropic shape)."""
    out = []
    for m in messages:
        if m.get("role") != "assistant":
            continue
        for block in m.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                out.append(block["id"])
    return out


def _tool_result_ids(messages: list) -> list:
    """Every tool_use_id the user turns answer, in order (Anthropic shape)."""
    out = []
    for m in messages:
        if m.get("role") != "user":
            continue
        for block in m.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                out.append(block["tool_use_id"])
    return out


def test_format_tool_results_batches_into_one_user_turn_for_anthropic(monkeypatch):
    """Anthropic wants every tool_result for one assistant turn in a single user message."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "2+2"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})

    msgs = llm_client.format_tool_results([(a, "4"), (b, "1998")])

    assert len(msgs) == 1, f"expected one batched user turn, got {len(msgs)}"
    assert msgs[0]["role"] == "user"
    assert [blk["tool_use_id"] for blk in msgs[0]["content"]] == ["tc_1", "tc_2"]


def test_format_tool_results_emits_one_message_per_call_for_openai(monkeypatch):
    """OpenAI wants the opposite: a separate role='tool' message per tool_call_id."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "openai")
    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "2+2"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})

    msgs = llm_client.format_tool_results([(a, "4"), (b, "1998")])

    assert len(msgs) == 2, f"expected one message per call, got {len(msgs)}"
    assert [m["role"] for m in msgs] == ["tool", "tool"]
    assert [m["tool_call_id"] for m in msgs] == ["tc_1", "tc_2"]


def test_format_tool_results_handles_no_calls(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    assert llm_client.format_tool_results([]) == []


def test_parallel_tool_calls_leave_no_tool_use_unanswered(monkeypatch):
    """Replay a conversation where the model emits TWO tool calls in one turn.

    This is the case that shipped broken in Chapter 1 and that the per-helper shape tests
    could not catch, because each helper was correct in isolation. The bug only appears when
    they are composed across a turn: an assistant message carrying two `tool_use` blocks
    answered by a single `tool_result` is an invalid request to Anthropic, and the failure is
    intermittent because it depends on whether the model chose to parallelise.

    The invariant is the whole contract: every tool_use id is answered exactly once.
    """
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")

    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "12*7"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})
    parallel = llm_client.ModelResponse(text="", tool_calls=[a, b])

    messages = [{"role": "user", "content": "How many days in 12 weeks, and when was it founded?"}]
    messages.append(llm_client.format_assistant_tool_call(parallel))
    messages.extend(llm_client.format_tool_results([(a, "84"), (b, "1998")]))

    used, answered = _tool_use_ids(messages), _tool_result_ids(messages)
    assert used == ["tc_1", "tc_2"], f"both calls should be on the assistant turn; got {used}"
    assert sorted(answered) == sorted(used), (
        f"every tool_use block must have a matching tool_result. Claimed {used}, answered "
        f"{answered} -- an unanswered tool_use is rejected by the API, not merely ignored."
    )


def test_answering_only_the_first_parallel_call_is_detectably_broken(monkeypatch):
    """The exact shape that shipped: two tool_use blocks, one tool_result.

    Pinned as a test so the invariant above is known to have teeth rather than being
    trivially satisfiable.
    """
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")

    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "12*7"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})
    parallel = llm_client.ModelResponse(text="", tool_calls=[a, b])

    broken = [{"role": "user", "content": "..."}]
    broken.append(llm_client.format_assistant_tool_call(parallel))
    broken.append(llm_client.format_tool_result(a, "84"))  # only the first -- the bug

    assert _tool_use_ids(broken) == ["tc_1", "tc_2"]
    assert _tool_result_ids(broken) == ["tc_1"], "the shipped bug answered only the first call"
    assert sorted(_tool_result_ids(broken)) != sorted(_tool_use_ids(broken)), (
        "if this ever passes, the invariant check above has stopped detecting the bug"
    )


# --- Chapter 1's RealLLMBrain, driven without an API key ---------------------------------


def _load_real_llm_brain():
    """Exec Chapter 1's RealLLMBrain cell and return the class.

    Loaded out of the notebook rather than copied here on purpose: a copy drifts, and the
    point of these tests is to exercise the code the learner actually runs. This class is
    otherwise untested by anything, because it only executes when HAS_KEY is true and CI
    deliberately runs with no key -- which is exactly how a parallel-tool-call bug shipped
    in it unnoticed.
    """
    import json as _json
    from pathlib import Path

    nb_path = Path(__file__).resolve().parent.parent / "curriculum" / "01_fundamentals.ipynb"
    nb = _json.loads(nb_path.read_text())
    source = next(
        "".join(c["source"]) for c in nb["cells"] if "class RealLLMBrain" in "".join(c["source"])
    )
    namespace = {"llm_client": llm_client, "json": _json}
    exec(compile(source, str(nb_path), "exec"), namespace)
    return namespace["RealLLMBrain"]


def _drive_brain(brain, script, monkeypatch, max_steps: int = 8):
    """Run `brain` through a run_agent-shaped loop against a scripted sequence of responses."""
    state = {"i": 0}

    def stub_call_model(**kwargs):
        response = script[min(state["i"], len(script) - 1)]
        state["i"] += 1
        return response

    monkeypatch.setattr(llm_client, "call_model", stub_call_model)

    messages = [{"role": "user", "content": "How many days in 12 weeks, and when was it founded?"}]
    actions = []
    for _ in range(max_steps):
        action = brain(messages)
        actions.append(action)
        if action["action"] == "final_answer":
            break
        messages.append({"role": "user", "content": f"observation for {action['action']}"})
    return actions, state["i"]


def _parallel_script():
    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "12*7"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})
    return a, b, [
        llm_client.ModelResponse(text="", tool_calls=[a, b]),
        llm_client.ModelResponse(text="84 days, founded 1998.", tool_calls=[]),
    ]


def test_real_llm_brain_answers_every_parallel_tool_call(monkeypatch):
    """A model turn with two tool calls must end up with two tool results."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    brain = _load_real_llm_brain()(model="stub")
    _, _, script = _parallel_script()

    _drive_brain(brain, script, monkeypatch)
    messages = brain.provider_messages

    assert sorted(_tool_use_ids(messages)) == sorted(_tool_result_ids(messages)), (
        f"tool_use {_tool_use_ids(messages)} vs tool_result {_tool_result_ids(messages)}: an "
        "unanswered tool_use block makes the whole request invalid, which is why this failed "
        "intermittently -- only when the model chose to parallelise."
    )


def test_real_llm_brain_batches_parallel_results_into_one_turn(monkeypatch):
    """Anthropic wants both results in a single user turn, not two consecutive ones."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    brain = _load_real_llm_brain()(model="stub")
    _, _, script = _parallel_script()

    _drive_brain(brain, script, monkeypatch)

    result_turns = [
        m
        for m in brain.provider_messages
        if m.get("role") == "user"
        and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in (m.get("content") or []))
    ]
    assert len(result_turns) == 1, (
        f"expected one batched user turn carrying both tool_result blocks, got {len(result_turns)}"
    )
    # Both halves matter. Counting turns alone is satisfied by a brain that answers only the
    # first call -- it also produces exactly one result turn, just an incomplete one.
    blocks = [b for b in result_turns[0]["content"] if b.get("type") == "tool_result"]
    assert [b["tool_use_id"] for b in blocks] == ["tc_1", "tc_2"], (
        f"the single turn has to carry BOTH results, in call order; got {blocks}"
    )


def test_real_llm_brain_serves_parallel_calls_without_extra_model_calls(monkeypatch):
    """The second queued call is served from the first response, not by re-prompting."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    brain = _load_real_llm_brain()(model="stub")
    _, _, script = _parallel_script()

    actions, model_calls = _drive_brain(brain, script, monkeypatch)

    assert [a["action"] for a in actions] == ["calculator", "mock_search", "final_answer"], (
        f"both tool calls should reach the sequential loop, in order; got {actions}"
    )
    assert model_calls == 2, (
        f"two tool calls came from ONE model turn, so this run needs two model calls total "
        f"(the parallel turn and the final answer), not {model_calls}"
    )


def test_real_llm_brain_still_handles_one_call_at_a_time(monkeypatch):
    """The sequential path is the common case and must not regress."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    brain = _load_real_llm_brain()(model="stub")
    a = llm_client.ToolCall(id="tc_1", name="calculator", input={"expression": "12*7"})
    b = llm_client.ToolCall(id="tc_2", name="mock_search", input={"query": "founded"})
    script = [
        llm_client.ModelResponse(text="", tool_calls=[a]),
        llm_client.ModelResponse(text="", tool_calls=[b]),
        llm_client.ModelResponse(text="84 days, founded 1998.", tool_calls=[]),
    ]

    actions, model_calls = _drive_brain(brain, script, monkeypatch)
    messages = brain.provider_messages

    assert [x["action"] for x in actions] == ["calculator", "mock_search", "final_answer"]
    assert model_calls == 3, f"one call per turn means three model calls, got {model_calls}"
    assert sorted(_tool_use_ids(messages)) == sorted(_tool_result_ids(messages))


def test_real_llm_brain_parallel_results_on_openai(monkeypatch):
    """OpenAI needs the opposite batching: a separate tool message per call."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "openai")
    brain = _load_real_llm_brain()(model="stub")
    _, _, script = _parallel_script()

    _drive_brain(brain, script, monkeypatch)

    tool_messages = [m for m in brain.provider_messages if m.get("role") == "tool"]
    assert [m["tool_call_id"] for m in tool_messages] == ["tc_1", "tc_2"], (
        f"expected one tool message per call; got {tool_messages}"
    )


def test_real_llm_brain_final_answer_without_tools(monkeypatch):
    """A question needing no tool at all still terminates cleanly."""
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    brain = _load_real_llm_brain()(model="stub")
    script = [llm_client.ModelResponse(text="Paris.", tool_calls=[])]

    actions, model_calls = _drive_brain(brain, script, monkeypatch)

    assert actions == [{"action": "final_answer", "action_input": "Paris."}]
    assert model_calls == 1


# --- self_check: the written drills ------------------------------------------------------


def test_self_check_parses_every_chapter():
    """All nine answer files yield numbered questions, whether headed at ## or ###."""
    from agentlib import self_check

    for chapter in range(1, 10):
        d = self_check.drill(chapter)
        assert d._bank, f"chapter {chapter} parsed no questions"
        for number, (question, answer) in d._bank.items():
            assert question.strip(), f"ch{chapter} q{number} has no question text"
            assert len(answer.split()) > 20, f"ch{chapter} q{number} has a suspiciously short answer"


def test_self_check_rejects_placeholder_and_stub_answers(capsys):
    from agentlib import self_check

    d = self_check.drill(1)
    for bad in ("", "   ", "(Write your answer here.)", "TODO", "cap the iterations"):
        d.attempt(1, bad)
    assert 1 not in d._attempts, "placeholder and too-short answers must not be recorded"

    real = " ".join(["word"] * 30)
    d.attempt(1, real)
    assert d._attempts[1] == real


def test_self_check_withholds_the_answer_until_you_attempt(capsys):
    """The reveal is the whole value; handing it over unprompted removes the exercise."""
    from agentlib import self_check

    d = self_check.drill(1)
    d.check(2)
    out = capsys.readouterr().out
    assert "MODEL ANSWER" not in out, "check() leaked the model answer before any attempt"
    assert "attempt() first" in out

    d.attempt(2, " ".join(["word"] * 30))
    d.check(2)
    out = capsys.readouterr().out
    assert "MODEL ANSWER" in out and "YOUR ANSWER" in out


def test_self_check_reveal_is_an_explicit_escape_hatch(capsys):
    from agentlib import self_check

    self_check.drill(1).reveal(3)
    out = capsys.readouterr().out
    assert "MODEL ANSWER" in out, "reveal() is the deliberate way to see it without attempting"


def test_self_check_rejects_an_unknown_question_number():
    from agentlib import self_check

    d = self_check.drill(1)
    for call in (lambda: d.attempt(99, "x" * 200), lambda: d.check(99), lambda: d.reveal(99)):
        try:
            call()
        except KeyError:
            continue
        raise AssertionError("an out-of-range question number should raise KeyError")


def test_no_notebook_contains_a_model_answer():
    """The drills read answers from solutions/ at runtime; none may be pasted into a notebook."""
    import json as _json
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    from agentlib import self_check

    for chapter in range(1, 10):
        d = self_check.drill(chapter)
        nb_matches = sorted((root / "curriculum").glob(f"{chapter:02d}_*.ipynb"))
        if not nb_matches:
            continue
        text = nb_matches[0].read_text()
        for number, (_, answer) in d._bank.items():
            # A distinctive run of the model answer, long enough not to collide by chance.
            probe = " ".join(answer.split()[:12])
            assert probe not in text, (
                f"ch{chapter} q{number}'s model answer appears inside "
                f"{nb_matches[0].name} -- it must only live in solutions/"
            )
