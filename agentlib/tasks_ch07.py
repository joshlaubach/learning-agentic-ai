"""Graded task suites for Chapter 7 — Tool Integration.

The MCP suite runs against the chapter's real companion server over a real stdio transport,
so a client that skips the handshake fails the way it would in production rather than the
way a mock would let it.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from pathlib import Path

from pydantic import BaseModel

from agentlib.grading import task

_SERVER = str(Path(__file__).resolve().parent.parent / "curriculum" / "_ch07_mcp_server.py")


class PackageInfo(BaseModel):
    name: str
    version: str
    summary: str
    license: str | None = None
    home_page: str | None = None
    project_urls: dict | None = None


_REAL = {
    "name": "numpy",
    "version": "2.4.6",
    "summary": "Fundamental package for array computing in Python",
    "license": "BSD-3-Clause",
    "home_page": "https://numpy.org",
    "project_urls": {"Homepage": "https://numpy.org"},
}


def _run(coro):
    """Drive a coroutine to completion from either a sync or an async caller.

    The notebook grades these cells from inside a Jupyter kernel, which already has a
    running event loop, so asyncio.run() cannot be used directly. Running it on its own
    thread works from both there and from pytest."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


# --- ch07-mcp-client ---


def _ref_client():
    from solutions.reference.ch07 import call_mcp_tool

    return call_mcp_tool


def _m1(f):
    """calling the server's one real tool"""
    got = _run(f(_SERVER, "get_package_info", {"package_name": "numpy"}))
    assert isinstance(got, dict), f"return the tool's parsed JSON payload as a dict; got {got!r}"
    assert got.get("name") == "numpy", f"expected numpy's record back; got {got!r}"


def _m2(f):
    """the handshake happens before the call"""
    got = _run(f(_SERVER, "get_package_info", {"package_name": "requests"}))
    assert got.get("name") == "requests", (
        "await session.initialize() BEFORE call_tool. MCP is a stateful protocol: the "
        "session negotiates capabilities on connect, and a call issued before that "
        "completes has nothing to route. Skipping it is the classic first MCP bug, and it "
        f"shows up as a hang or a protocol error rather than a clear message. Got {got!r}"
    )


def _m3(f):
    """arguments reach the tool"""
    for package in ("numpy", "requests", "anthropic"):
        got = _run(f(_SERVER, "get_package_info", {"package_name": package}))
        assert got.get("name") == package, (
            f"the arguments dict has to be forwarded to call_tool; asked for {package!r} "
            f"and got {got.get('name')!r}"
        )


def _m4(f):
    """the payload is parsed, not returned raw"""
    got = _run(f(_SERVER, "get_package_info", {"package_name": "numpy"}))
    assert not isinstance(got, str), (
        "MCP hands back content blocks whose text is a JSON string; parse it so callers get "
        f"a dict rather than having to json.loads() it themselves. Got {got!r}"
    )
    assert "version" in got, f"the full record should come through; got {sorted(got)}"


def _m5(f):
    """the subprocess is cleaned up between calls"""
    for _ in range(3):
        got = _run(f(_SERVER, "get_package_info", {"package_name": "numpy"}))
        assert got.get("name") == "numpy", "repeated connects must each work"


task("ch07-mcp-client", _ref_client, [_m1, _m2, _m3, _m4, _m5])


# --- ch07-schema-validate ---


def _ref_validate():
    from solutions.reference.ch07 import validate_tool_output

    return validate_tool_output


def _v1(f):
    """a clean response"""
    validated, error = f(dict(_REAL), PackageInfo)
    assert error is None, f"a valid response produces no error; got {error!r}"
    assert validated.name == "numpy", f"and the parsed model; got {validated!r}"


def _v2(f):
    """a field with the wrong type"""
    bad = dict(_REAL, version=["2", "4", "6"])
    validated, error = f(bad, PackageInfo)
    assert validated is None, f"nothing validated, so nothing to hand back; got {validated!r}"
    assert error is not None, (
        "a validation failure has to come back as a RESULT the caller can see. Catching "
        "ValidationError and returning a bare None is the single most damaging line in this "
        "chapter: the caller cannot tell 'the tool returned garbage' from 'the package "
        "doesn't exist', so a broken integration reads as an empty search and the agent "
        "confidently reports nothing found."
    )


def _v3(f):
    """a missing required field"""
    bad = {k: v for k, v in _REAL.items() if k != "summary"}
    validated, error = f(bad, PackageInfo)
    assert validated is None and error is not None, (
        f"a missing required field is still a failure to report; got ({validated!r}, {error!r})"
    )


def _v4(f):
    """the error carries enough to act on"""
    bad = dict(_REAL, version=123.4)
    _, error = f(bad, PackageInfo)
    errors = error.errors()
    assert any(e["loc"][0] == "version" for e in errors), (
        f"return the ValidationError itself, not a flattened string -- the caller needs "
        f"errors() to tell a missing field from a mistyped one. Got {error!r}"
    )


def _v5(f):
    """optional fields really are optional"""
    minimal = {"name": "numpy", "version": "2.4.6", "summary": "arrays"}
    validated, error = f(minimal, PackageInfo)
    assert error is None, (
        f"license/home_page/project_urls are genuinely absent from plenty of real PyPI "
        f"records; that is not a failure. Got {error!r}"
    )


def _v6(f):
    """the result is always a two-tuple"""
    for response in (dict(_REAL), dict(_REAL, version=None)):
        got = f(response, PackageInfo)
        assert isinstance(got, tuple) and len(got) == 2, (
            f"return (validated_or_None, error_or_None); got {got!r}"
        )


def _v7(f):
    """exactly one of the two is populated"""
    ok, ok_err = f(dict(_REAL), PackageInfo)
    bad, bad_err = f(dict(_REAL, name=None), PackageInfo)
    assert (ok is not None) != (ok_err is not None), "a success is (model, None)"
    assert (bad is not None) != (bad_err is not None), "a failure is (None, error)"


task("ch07-schema-validate", _ref_validate, [_v1, _v2, _v3, _v4, _v5, _v6, _v7])


# --- ch07-failure-classifier ---


def _ref_classifier():
    from solutions.reference.ch07 import classify_failure

    return classify_failure


def _f1(f):
    """a clean response"""
    got = f("numpy", dict(_REAL), PackageInfo)
    assert got["category"] == "ok", f"nothing wrong with this one; got {got!r}"
    assert got["action"] == "proceed", f"and nothing to do about it; got {got!r}"


def _f2(f):
    """a field that fails to type-check"""
    got = f("numpy", dict(_REAL, version=["2", "4", "6"]), PackageInfo)
    assert got["category"] == "malformed", (
        f"the shape is right but a field's type is wrong -- that is malformed; got {got!r}"
    )
    assert got["action"] == "switch", (
        f"malformed data may well be a bad cache entry, so retry against a fresh source; "
        f"got {got['action']!r}"
    )


def _f3(f):
    """valid data describing the wrong thing"""
    got = f("numpy", dict(_REAL, name="scipy", summary="Scientific library"), PackageInfo)
    assert got["category"] == "semantically_wrong", (
        "this response type-checks perfectly. Every field is the right type, nothing is "
        "missing, and it describes a different package than the one that was asked for. "
        "Lumping it in with 'malformed' is the mistake that matters here, because the two "
        "call for opposite responses: malformed data is worth retrying, and semantically "
        "wrong data will come back identical every time. A schema can never catch this -- "
        f"which is exactly why it needs its own category. Got {got['category']!r}."
    )
    assert got["action"] == "ask-user", (
        f"schema-valid but untrustworthy is not something to resolve automatically; got "
        f"{got['action']!r}"
    )


def _f4(f):
    """a required field that vanished"""
    got = f("numpy", {k: v for k, v in _REAL.items() if k != "summary"}, PackageInfo)
    assert got["category"] == "version_mismatch", (
        "a field missing ENTIRELY means the upstream contract changed, which is different "
        f"from a field being present with a bad value; got {got!r}"
    )
    assert got["action"] == "ask-user", (
        f"a changed contract needs a developer, not a retry; got {got['action']!r}"
    )


def _f5(f):
    """malformed and semantically wrong are not the same verdict"""
    malformed = f("numpy", dict(_REAL, version=[1, 2]), PackageInfo)
    wrong = f("numpy", dict(_REAL, name="scipy"), PackageInfo)
    assert malformed["category"] != wrong["category"], (
        f"these two need different handling, so they need different categories; both came "
        f"back as {malformed['category']!r}"
    )
    assert malformed["action"] != wrong["action"], (
        f"one is worth retrying and the other never will be; both said "
        f"{malformed['action']!r}"
    )


def _f6(f):
    """a missing field and a mistyped field are not the same verdict"""
    missing = f("numpy", {k: v for k, v in _REAL.items() if k != "version"}, PackageInfo)
    mistyped = f("numpy", dict(_REAL, version=[1, 2]), PackageInfo)
    assert missing["category"] != mistyped["category"], (
        f"absent means the shape changed; wrong-typed means this response is bad. Both came "
        f"back as {missing['category']!r}"
    )


def _f7(f):
    """the verdict names all three things"""
    got = f("numpy", dict(_REAL), PackageInfo)
    for key in ("category", "action", "detail"):
        assert key in got, f"the router needs {key!r} to act on; got {sorted(got)}"


def _f8(f):
    """the four categories are the four in the taxonomy"""
    seen = {
        f("numpy", dict(_REAL), PackageInfo)["category"],
        f("numpy", dict(_REAL, version=[1]), PackageInfo)["category"],
        f("numpy", dict(_REAL, name="scipy"), PackageInfo)["category"],
        f("numpy", {k: v for k, v in _REAL.items() if k != "name"}, PackageInfo)["category"],
    }
    assert seen == {"ok", "malformed", "semantically_wrong", "version_mismatch"}, (
        f"use exactly these four category names so the router can branch on them; got {seen}"
    )


def _f9(f):
    """the detail says something specific"""
    got = f("numpy", dict(_REAL, name="scipy"), PackageInfo)
    assert "scipy" in got["detail"], (
        f"name what was actually wrong -- a generic message means whoever reads the log "
        f"still has to go and look. Got {got['detail']!r}"
    )


task(
    "ch07-failure-classifier",
    _ref_classifier,
    [_f1, _f2, _f3, _f4, _f5, _f6, _f7, _f8, _f9],
)
