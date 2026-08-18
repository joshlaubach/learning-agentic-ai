"""Chapter 7 reference answers — Tool Integration.

An MCP stdio client, schema validation that surfaces its failures, and the four-way failure
taxonomy this chapter is built around.
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
