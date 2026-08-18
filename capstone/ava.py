"""Ava — the capstone agent. This is the file you implement.

The specification is capstone/README.md and the acceptance suite is
capstone/test_capstone.py. Read the README first; it states five requirements, and meeting
four of them is a fail.

Nothing here is new material. The retriever below is Chapter 3's, the MCP call is Chapter
7's, and both are given to you already working. What is yours is the safeguard, the decision
step, the three graph nodes, and the wiring — the parts that turn four separate techniques
into one agent.

Run `pytest capstone/test_capstone.py` as you go. No API key needed.
"""

from __future__ import annotations

import json
import operator
import os
import re
import sys
from pathlib import Path
from typing import Annotated, TypedDict

from agentlib import llm_client, synthetic_data

_REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_PATH = str(_REPO_ROOT / "curriculum" / "_ch07_mcp_server.py")
STRONG_MODEL = llm_client.STRONG_MODELS[llm_client.LLM_PROVIDER]

# The five questions the agent is measured on (requirement 5). Two need retrieval, one needs
# the package tool, one is a memory follow-up, one is unanswerable from the corpus.
EVAL_QUESTIONS = [
    "What feature of the Shah's army enabled the Mongol forces easy early victories?",
    "Who was the Norman leader that conquered England?",
    "Tell me about the package called requests",
    "What was my first question?",
    "What is the airspeed velocity of an unladen swallow?",
]


# --- Tool 1: retrieval over Chapter 3's corpus. GIVEN -- this is Chapter 3's retriever. ---


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
    """Returns [{"doc_id": ..., "title": ..., "text": ...}, ...] -- note the doc_id, which
    requirement 1 needs you to carry all the way into the answer."""
    return [
        {"doc_id": d["doc_id"], "title": d["title"], "text": d["text"]}
        for d in _retriever.retrieve(query, k=k)
    ]


# --- Tool 2: Chapter 7's real MCP server. GIVEN -- a real stdio connection. ---


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


# --- Safeguard: requirement 4. YOURS. ---


def sanitize_retrieved_text(text: str) -> str:
    """Neutralize anything shaped like an embedded directive, before it reaches the model.

    Retrieved documents are exactly the untrusted content Chapter 6 warned about: a corpus
    document can carry a directive as easily as a support ticket can, and the corpus is not
    "yours" in any sense that matters -- it is text from somewhere else that your agent reads
    on a user's behalf.

    Cover at least the shapes Chapter 6 covered: a line opening with an authority word and a
    colon, the same wrapped in brackets, and plain English asking for prior instructions to
    be ignored.

    Strip the directive and KEEP the document. Discarding the whole thing is a denial of
    service an attacker can trigger with one line (requirement 4's second test).
    """
    raise NotImplementedError("Implement me -- see capstone/README.md requirement 4")


# --- The graph. YOURS, apart from the state shape. ---


class AvaState(TypedDict):
    """One channel: the conversation. `operator.add` makes each node's returned messages
    append to it rather than replace it, which is what lets the checkpointer accumulate."""

    messages: Annotated[list, operator.add]


async def decide(messages: list) -> dict:
    """One model call: the single decision point the graph asks the model to make.

    Return either a tool call or a final answer:

        {"tool": "search_knowledge_base", "args": {"query": ...}}
        {"tool": "lookup_package_info",   "args": {"package_name": ...}}
        {"tool": None, "args": {}, "response": "<the answer>"}

    Same real/mock split as every chapter since Chapter 1: call the real model through
    llm_client.call_model (at STRONG_MODEL, this being the capstone) when llm_client.HAS_KEY,
    and fall back to deterministic logic when it is False. The mock path is what CI runs and
    what the tests grade, so it has to make a real decision from the real conversation --
    not follow a script.

    Two things the mock path has to get right, and both are requirement 5:
      - if the last message is a tool result, answer from it rather than calling another tool
      - a question about the conversation itself ("what was my first question?") is answered
        from `messages`, which is where the checkpointer's state arrives
    """
    raise NotImplementedError("Implement me -- see capstone/README.md")


TOOLS = {
    "search_knowledge_base": search_knowledge_base,
    "lookup_package_info": lookup_package_info,
}


async def agent_node(state: AvaState) -> dict:
    """Ask `decide` what to do, and record it as an assistant message.

    Return {"messages": [{"role": "assistant", "content": ..., "tool_call": ...}]} --
    `content` carries the answer and `tool_call` is None when the agent is done; when it
    wants a tool, `tool_call` is {"name": ..., "args": {...}} and content is None.
    """
    raise NotImplementedError("Implement me -- see capstone/README.md")


async def tool_node(state: AvaState) -> dict:
    """Run the tool the agent just asked for and return its result as a tool message.

    Three requirements land in this one function:

      1. Sources. Carry each retrieved document's doc_id into the text you return, so the
         final answer can be traced back to what it came from.
      2. Failures. A tool that raises gets reported back into the conversation as a tool
         result. It must not escape the graph -- and it must not be silently swallowed
         either, or the user gets a confident answer built on a tool that never ran.
      4. The safeguard. Sanitize retrieved text HERE, on the path the graph actually
         executes. A sanitizer that exists but is not wired in protects nothing.

    Return {"messages": [{"role": "tool", "content": <summary>, "tool_call": None}]}.
    """
    raise NotImplementedError("Implement me -- see capstone/README.md")


def route_after_agent(state: AvaState) -> str:
    """After the agent node: go to "tools" if it asked for one, otherwise END."""
    raise NotImplementedError("Implement me -- see capstone/README.md")


def build_ava():
    """Compile the graph: agent <-> tools, entry point at agent, with a checkpointer.

    The checkpointer is requirement 3. Without one, every invocation starts from nothing and
    the second turn of a conversation cannot see the first.
    """
    raise NotImplementedError("Implement me -- see capstone/README.md requirement 3")
