"""Capstone reference answer — Ava, a combined agent project.

The module capstone/ava.py is the learner's version of this file. Everything here already
exists somewhere in Chapters 1-9: the retriever is Chapter 3's, the MCP call is Chapter 7's,
the sanitizer is Chapter 6's, and the loop shape is Chapter 1's. What is new is that they are
composed into one graph, and that the graph has to satisfy a written specification
(capstone/README.md) rather than just run.
"""

from __future__ import annotations

import json
import operator
import os
import re
import sys
from typing import Annotated, TypedDict

from agentlib import llm_client, synthetic_data

_REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent.parent
MCP_SERVER_PATH = str(_REPO_ROOT / "curriculum" / "_ch07_mcp_server.py")
STRONG_MODEL = llm_client.STRONG_MODELS[llm_client.LLM_PROVIDER]

# The five questions the agent is measured on. Two need retrieval, one needs the package
# tool, one is a memory follow-up, one is unanswerable from the corpus.
EVAL_QUESTIONS = [
    "What feature of the Shah's army enabled the Mongol forces easy early victories?",
    "Who was the Norman leader that conquered England?",
    "Tell me about the package called requests",
    "What was my first question?",
    "What is the airspeed velocity of an unladen swallow?",
]


# --- Tool 1: retrieval over Chapter 3's corpus ---


class TfidfRetriever:
    """Identical shape to Chapter 3's retriever -- reused here, not redesigned."""

    def __init__(self, docs: list):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.docs = {d["doc_id"]: d for d in docs}
        self.doc_ids = [d["doc_id"] for d in docs]
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform([d["text"] for d in docs])

    def retrieve(self, query: str, k: int = 2) -> list:
        from sklearn.metrics.pairwise import cosine_similarity

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.doc_vectors)[0]
        top_indices = sims.argsort()[::-1][:k]
        return [self.docs[self.doc_ids[i]] for i in top_indices]


CORPUS = synthetic_data.load_squad_sample()
CORPUS_DOC_IDS = {d["doc_id"] for d in CORPUS["docs"]}
_retriever = TfidfRetriever(CORPUS["docs"])


def search_knowledge_base(query: str, k: int = 2) -> list:
    return [
        {"doc_id": d["doc_id"], "title": d["title"], "text": d["text"]}
        for d in _retriever.retrieve(query, k=k)
    ]


# --- Tool 2: Chapter 7's real MCP server ---


async def lookup_package_info(package_name: str) -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from pydantic import BaseModel

    class PackageInfo(BaseModel):
        name: str
        version: str
        summary: str
        license: str | None = None
        home_page: str | None = None
        project_urls: dict | None = None

    params = StdioServerParameters(command=sys.executable, args=[MCP_SERVER_PATH])
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "get_package_info", {"package_name": package_name}
                )
                raw = json.loads(result.content[0].text)
                return PackageInfo.model_validate(raw).model_dump()


# --- Safeguard: Chapter 6's instruction/data separation ---

_DIRECTIVE_RE = re.compile(
    r"(?im)^\s*(?:system|admin|override|developer)\s*[:>]\s*.+$"
)
_BRACKETED_RE = re.compile(
    r"(?is)[\[<(]\s*(?:system|admin|override|developer)\s*[\]>)]\s*:?\s*.*?(?:\n|$)"
)
_IGNORE_RE = re.compile(
    r"(?is)\bignore\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions?\b.*?(?:\n|$)"
)
REDACTION = "[removed: a line here impersonated a system directive]"


def sanitize_retrieved_text(text: str) -> str:
    """Neutralize anything shaped like an embedded directive before it reaches the model.

    Retrieved documents are exactly the untrusted content Chapter 6 warned about -- a corpus
    document can carry a directive as easily as a support ticket can."""
    cleaned = text
    for pattern in (_DIRECTIVE_RE, _BRACKETED_RE, _IGNORE_RE):
        cleaned = pattern.sub(REDACTION, cleaned)
    return cleaned


# --- The graph ---


class AvaState(TypedDict):
    messages: Annotated[list, operator.add]


_PACKAGE_QUERY_RE = re.compile(
    r"\bpackage\s+(?:called\s+|named\s+)?['\"]?([a-zA-Z0-9_-]+)['\"]?", re.IGNORECASE
)


def fake_decide(messages: list) -> dict:
    """Deterministic stand-in for the model's decision: which tool (if any) to call next."""
    if messages and messages[-1]["role"] == "tool":
        return {
            "tool": None,
            "args": {},
            "response": f"Based on what I found: {messages[-1]['content']}",
        }

    last_user = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    if "first" in last_user.lower() and (
        "question" in last_user.lower() or "ask" in last_user.lower()
    ):
        all_user_messages = [m["content"] for m in messages if m["role"] == "user"]
        first_question = all_user_messages[0] if all_user_messages else "(none)"
        return {"tool": None, "args": {}, "response": f"You first asked: {first_question!r}"}

    package_match = _PACKAGE_QUERY_RE.search(last_user)
    if package_match:
        return {
            "tool": "lookup_package_info",
            "args": {"package_name": package_match.group(1)},
        }
    if "?" in last_user or len(last_user.split()) > 3:
        return {"tool": "search_knowledge_base", "args": {"query": last_user}}
    return {
        "tool": None,
        "args": {},
        "response": "Could you say a bit more about what you're looking for?",
    }


async def real_decide(messages: list) -> dict:
    """Real-API path: an actual model, at the strong tier, deciding which tool to call."""
    tools = [
        {
            "name": "search_knowledge_base",
            "description": "Search the reference knowledge base.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "lookup_package_info",
            "description": "Look up real PyPI package metadata.",
            "input_schema": {
                "type": "object",
                "properties": {"package_name": {"type": "string"}},
                "required": ["package_name"],
            },
        },
    ]
    response = llm_client.call_model(messages=messages, tools=tools, model=STRONG_MODEL)
    if response.tool_calls:
        tc = response.tool_calls[0]
        return {"tool": tc.name, "args": tc.input}
    return {"tool": None, "args": {}, "response": response.text}


async def decide(messages: list) -> dict:
    """One model call: the single decision point the graph asks the model to make."""
    if llm_client.HAS_KEY:
        return await real_decide(messages)
    return fake_decide(messages)


TOOLS = {
    "search_knowledge_base": search_knowledge_base,
    "lookup_package_info": lookup_package_info,
}


async def agent_node(state: AvaState) -> dict:
    decision = await decide(state["messages"])
    if decision["tool"] is None:
        return {
            "messages": [
                {"role": "assistant", "content": decision["response"], "tool_call": None}
            ]
        }
    return {
        "messages": [
            {
                "role": "assistant",
                "content": None,
                "tool_call": {"name": decision["tool"], "args": decision["args"]},
            }
        ]
    }


async def tool_node(state: AvaState) -> dict:
    """Run the tool the agent asked for, sanitize anything it retrieved, and cite sources.

    A tool that raises is reported back into the conversation as a tool result, not allowed
    to escape: a dependency being down is a thing the agent has to handle, not a crash."""
    tool_call = state["messages"][-1]["tool_call"]
    name = tool_call["name"]
    tool_fn = TOOLS.get(name)
    if tool_fn is None:
        return {
            "messages": [
                {
                    "role": "tool",
                    "content": f"No such tool: {name!r}. Answering without it.",
                    "tool_call": None,
                }
            ]
        }

    try:
        if name == "lookup_package_info":
            result = await tool_fn(**tool_call["args"])
            summary = f"{result['name']} v{result['version']} -- {result['summary']}"
        else:
            docs = tool_fn(**tool_call["args"])
            if docs:
                # Sanitize before the text re-enters the conversation, and carry the doc_id
                # alongside it so the answer can be traced back to what it came from.
                summary = " ".join(
                    f"[{d['doc_id']}] {sanitize_retrieved_text(d['text'])}" for d in docs
                )
            else:
                summary = "No matching documents found."
    except Exception as exc:
        summary = (
            f"The {name} tool failed ({type(exc).__name__}: {exc}). "
            "Answering from what is already known instead."
        )

    return {"messages": [{"role": "tool", "content": summary, "tool_call": None}]}


def route_after_agent(state: AvaState) -> str:
    from langgraph.graph import END

    return "tools" if state["messages"][-1].get("tool_call") else END


def build_ava():
    """Compile the agent <-> tools graph with a checkpointer for cross-turn memory."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, StateGraph

    graph = StateGraph(AvaState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=MemorySaver())
