"""Chapter 7 reference answers — Tool Integration.

An MCP stdio client, schema validation that surfaces its failures, the four-way failure
taxonomy this chapter is built around, and the three strategies for getting JSON out of a
model that does not reliably produce it.
"""

from __future__ import annotations

import json
import os
import sys


async def call_mcp_tool(server_path: str, tool_name: str, arguments: dict) -> dict:
    """Spawn the MCP server over stdio, complete the handshake, call one tool."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable, args=[server_path])
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return json.loads(result.content[0].text)


def validate_tool_output(response: dict, model):
    """Validate a raw tool response against its schema.

    Returns (validated_or_None, error_or_None). A validation failure is a RESULT, reported
    back to the caller -- never a None that a happy path can mistake for "nothing found"."""
    from pydantic import ValidationError

    try:
        return model.model_validate(response), None
    except ValidationError as exc:
        return None, exc


def classify_failure(package_name: str, response: dict, model) -> dict:
    """Sort a raw tool response into this chapter's four categories.

    The distinction that carries the weight is malformed vs. semantically wrong. Malformed
    means the response failed to type-check, which a retry against a fresh source can fix.
    Semantically wrong means it type-checked perfectly and describes the wrong thing, which
    no retry will ever fix and no schema will ever catch."""
    validated, error = validate_tool_output(response, model)

    if error is not None:
        missing = [e["loc"][0] for e in error.errors() if e["type"] == "missing"]
        if missing:
            return {
                "category": "version_mismatch",
                "action": "ask-user",
                "detail": f"field(s) {missing} missing entirely -- the upstream shape changed",
            }
        bad = [e["loc"][0] for e in error.errors()]
        return {
            "category": "malformed",
            "action": "switch",
            "detail": f"field(s) {bad} failed type validation",
        }

    if validated.name != package_name:
        return {
            "category": "semantically_wrong",
            "action": "ask-user",
            "detail": f"asked for {package_name!r}, got data for {validated.name!r}",
        }

    return {
        "category": "ok",
        "action": "proceed",
        "detail": f"{validated.name} v{validated.version}",
    }


def repair_json(raw: str):
    """Strip markdown fences and surrounding prose, then parse. None if it will not parse.

    The ceiling of this approach is worth being precise about, because it is the answer most
    people reach for first: it fixes everything WRAPPED around the JSON and nothing wrong
    INSIDE it. An unquoted key or a trailing comma survives every trim you can write, which
    is the argument for constraining generation instead of cleaning up after it.
    """
    text = raw.strip()

    if "```" in text:
        body = text[text.find("```") + 3 :]
        if body.lstrip().startswith("json"):
            body = body.lstrip()[4:]
        end = body.find("```")
        text = (body if end == -1 else body[:end]).strip()

    # Scan to the LAST closing brace, not the first: a '}' can legitimately appear inside a
    # string value, and a non-greedy match would stop there and truncate the object.
    first, last = text.find("{"), text.rfind("}")
    if first == -1 or last == -1 or last < first:
        return None

    try:
        parsed = json.loads(text[first : last + 1])
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def retry_until_valid(model, max_attempts: int = 4):
    """Re-prompt until the output parses with every field present, or the budget runs out.

    Returns (record_or_None, attempts_used). The budget is not optional: against a model that
    malforms its output the same way every time, an unbounded loop is a bill, not a fix.
    """
    from agentlib.structured_outputs import FIELDS

    for attempt in range(1, max_attempts + 1):
        parsed = repair_json(model.generate())
        if parsed is not None and set(parsed) == set(FIELDS):
            return parsed, attempt
    return None, max_attempts


def constrained_decode(model, fields) -> dict:
    """Decode under a grammar mask: filter to legal tokens, then take the best survivor.

    Two lines carry the whole idea. The filter is what makes an invalid token unemittable
    rather than merely regrettable, so the output is well-formed by construction and one
    generation is always enough. The max() is what keeps the result *likely* as well as
    legal -- the candidate list arrives in no particular order, so taking the first survivor
    would hand back a well-formed, on-schema, wrong answer.

    Worth stating plainly, since interviewers push on it: the mask guarantees syntax and
    schema. It does not guarantee the content is correct, and nothing about constrained
    decoding removes the need to validate what the fields actually say.
    """
    from agentlib.structured_outputs import is_allowed, is_complete

    model.reset()
    emitted: list[str] = []
    while not is_complete(emitted, fields):
        legal = [(t, s) for t, s in model.candidates() if is_allowed(emitted, t, fields)]
        if not legal:
            raise ValueError(f"no legal continuation after {''.join(emitted)!r}")
        token, _ = max(legal, key=lambda pair: pair[1])
        model.accept(token)
        emitted.append(token)
    return json.loads("".join(emitted))
