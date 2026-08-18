"""Graded task suites for Chapter 7 — Tool Integration.

The MCP suite runs against the chapter's real companion server over a real stdio transport,
so a client that skips the handshake fails the way it would in production rather than the
way a mock would let it.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
from pathlib import Path

from pydantic import BaseModel

from agentlib import structured_outputs as so
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


# --- ch07-json-repair ---


def _ref_repair():
    from solutions.reference.ch07 import repair_json

    return repair_json


def _wrapped(record, quirks):
    """The raw text a model with `quirks` produces for `record`."""
    return so.MockModel(record, quirks=quirks).generate()


def _r1(f):
    """clean JSON, nothing to repair"""
    got = f(json.dumps(so.RECORDS[0]))
    assert got == so.RECORDS[0], f"already-valid JSON should pass straight through; got {got!r}"


def _r2(f):
    """markdown fences"""
    got = f(_wrapped(so.RECORDS[0], ["fence"]))
    assert got == so.RECORDS[0], (
        f"```json fences are the single most common wrapper; strip them. Got {got!r}"
    )


def _r3(f):
    """prose on both sides of the fence"""
    got = f(_wrapped(so.RECORDS[1], ["fence", "preamble", "epilogue"]))
    assert got == so.RECORDS[1], (
        f"a helpful sentence before and after the block is still just wrapping; got {got!r}"
    )


def _r4(f):
    """a brace inside a string value is not the end of the object"""
    record = dict(so.RECORDS[0], summary="use {} to build an empty dict")
    got = f("```json\n" + json.dumps(record) + "\n```")
    assert got == record, (
        "matching braces with a non-greedy regex stops at the first '}' it sees, which here "
        f"is inside a string value. Scan to the LAST '}}' instead. Got {got!r}"
    )


def _r5(f):
    """an unquoted key is not repairable by stripping wrappers"""
    got = f(_wrapped(so.RECORDS[0], ["unquoted_key"]))
    assert got is None, (
        "this is the honest ceiling of the repair approach, and the reason the chapter does "
        "not stop here. `{name: \"numpy\"}` is not JSON, and no amount of trimming the "
        "outside makes the inside parse. Report the failure by returning None rather than "
        f"papering over it. Got {got!r}"
    )


def _r6(f):
    """a trailing comma, likewise"""
    got = f(_wrapped(so.RECORDS[2], ["trailing_comma"]))
    assert got is None, f"`,}}` is a syntax error, not a wrapper; got {got!r}"


def _r7(f):
    """no JSON in the response at all"""
    for raw in ("I'm sorry, I can't help with that.", "", "```\n\n```"):
        got = f(raw)
        assert got is None, f"nothing to parse in {raw!r}, so report nothing; got {got!r}"


def _r8(f):
    """failure is None, not an empty dict"""
    got = f(_wrapped(so.RECORDS[0], ["unquoted_key"]))
    assert got != {}, (
        "an empty dict reads downstream as 'the model returned a record with no fields', "
        "which is a different and much more confusing claim than 'parsing failed'. Same "
        "mistake as returning None from a validator: it destroys the caller's ability to "
        "tell one failure from another."
    )


task("ch07-json-repair", _ref_repair, [_r1, _r2, _r3, _r4, _r5, _r6, _r7, _r8])


# --- ch07-retry-budget ---


def _ref_retry():
    from solutions.reference.ch07 import retry_until_valid

    return retry_until_valid


def _t1(f):
    """a transiently broken model: retrying genuinely works"""
    model = so.MockModel(so.RECORDS[1], quirks=so.QUIRKS, flaky_until=2)
    record, attempts = f(model, 4)
    assert record == so.RECORDS[1], f"the third generation is clean; got {record!r}"
    assert attempts == 3, f"it took three attempts to get there; reported {attempts}"


def _t2(f):
    """a systematically broken model: retrying does not"""
    model = so.MockModel(so.RECORDS[1], quirks=so.QUIRKS)
    record, attempts = f(model, 4)
    assert record is None, (
        "this model malforms its output the same way every single time, so re-prompting it "
        "four times produces four identically broken responses. This is why 'add a retry "
        f"loop' is a mitigation for flakiness, not a fix for format. Got {record!r}"
    )
    assert attempts == 4, f"and it spent the whole budget finding that out; got {attempts}"


def _t3(f):
    """a clean model costs exactly one call"""
    model = so.MockModel(so.RECORDS[0], quirks=[])
    record, attempts = f(model, 4)
    assert record == so.RECORDS[0] and attempts == 1, (
        f"nothing to retry here; got ({record!r}, {attempts})"
    )
    assert model.generations == 1, (
        f"and no speculative extra generations after success; model ran {model.generations}"
    )


def _t4(f):
    """the budget is a real ceiling"""
    model = so.MockModel(so.RECORDS[2], quirks=so.QUIRKS, flaky_until=99)
    record, _ = f(model, 2)
    assert record is None, f"still broken after two tries; got {record!r}"
    assert model.generations == 2, (
        "max_attempts has to bound the loop. An unbounded retry against a model that is "
        "systematically wrong is how a $30 support ticket happens -- the same failure "
        f"Chapter 1 caps with max_iterations. The model ran {model.generations} times."
    )


def _t5(f):
    """the result is always a (record_or_None, attempts) pair"""
    for quirks in ([], so.QUIRKS):
        got = f(so.MockModel(so.RECORDS[0], quirks=quirks), 3)
        assert isinstance(got, tuple) and len(got) == 2, (
            f"return (record_or_None, attempts_used); got {got!r}"
        )
        assert isinstance(got[1], int) and got[1] >= 1, (
            f"attempts is a 1-based count of generations made; got {got[1]!r}"
        )


def _t6(f):
    """the reported attempt count matches what the model actually did"""
    model = so.MockModel(so.RECORDS[1], quirks=so.QUIRKS, flaky_until=3)
    _, attempts = f(model, 5)
    assert attempts == model.generations, (
        f"reported {attempts} attempts but the model ran {model.generations} times -- the "
        "number a caller uses for cost accounting has to be the real one"
    )


def _t7(f):
    """a parse is not enough: the record has to carry every field"""
    model = so.MockModel({"name": "numpy", "version": "2.4.6", "summary": "arrays"}, quirks=[])
    record, _ = f(model, 3)
    assert record is not None and set(record) == set(so.FIELDS), (
        f"accept only a record with all of {so.FIELDS}; got {record!r}"
    )


def _t8(f):
    """valid JSON with a field missing is still a failure"""
    model = so.MockModel(so.RECORDS[0], quirks=[so.DROP_FIELD])
    record, _ = f(model, 3)
    assert record is None, (
        "this model emits perfectly well-formed JSON every single time -- it just leaves out "
        "`summary`, the way a real model does when it cannot find a field in the source and "
        "moves on. `json.loads` is delighted. That is why 'did it parse?' is the wrong "
        "success condition: the contract is the SCHEMA, and a retry loop that stops at the "
        f"first clean parse hands a half-filled record downstream. Got {record!r}"
    )


task("ch07-retry-budget", _ref_retry, [_t1, _t2, _t3, _t4, _t5, _t6, _t7, _t8])


# --- ch07-constrained-decode ---


def _ref_constrained():
    from solutions.reference.ch07 import constrained_decode

    return constrained_decode


def _c1(f):
    """the same systematically broken model the retry loop could not save"""
    model = so.MockModel(so.RECORDS[1], quirks=so.QUIRKS)
    got = f(model, so.FIELDS)
    assert got == so.RECORDS[1], (
        "this is the model that defeated both repair and retry. Masking the invalid tokens "
        f"before they are emitted is what changes the outcome. Got {got!r}"
    )


def _c2(f):
    """every record, every quirk"""
    for record in so.RECORDS:
        got = f(so.MockModel(record, quirks=so.QUIRKS), so.FIELDS)
        assert got == record, f"expected {record!r}; got {got!r}"


def _c3(f):
    """one generation, not several"""
    model = so.MockModel(so.RECORDS[0], quirks=so.QUIRKS)
    f(model, so.FIELDS)
    assert model.generations == 1, (
        "constrained decoding is not retrying-with-extra-steps. It never emits an invalid "
        "token, so there is nothing to re-prompt for and the correct answer costs one "
        f"generation. This one ran {model.generations}."
    )


def _c4(f):
    """the mask is applied, not just the parse"""
    model = so.MockModel(so.RECORDS[2], quirks=["unquoted_key", "trailing_comma"])
    got = f(model, so.FIELDS)
    assert got == so.RECORDS[2], f"expected {so.RECORDS[2]!r}; got {got!r}"
    assert "```" not in model.text and ", }" not in model.text, (
        f"no invalid token should ever have been emitted; raw output was {model.text!r}"
    )


def _c5(f):
    """the BEST legal token, not the first one offered"""
    model = so.MockModel(so.RECORDS[0], quirks=so.QUIRKS)
    got = f(model, so.FIELDS)
    assert got["summary"] == so.RECORDS[0]["summary"], (
        "candidates() hands back a distribution in no particular order, so the first entry "
        "that survives the mask is not the likeliest one -- here it is a truncated value. "
        "Filter first, then take the highest-scoring survivor. Note what this case is "
        "really showing: the mask guarantees the output is well-formed and on-schema, and "
        f"guarantees nothing about it being right. Got {got!r}"
    )


def _c6(f):
    """decoding stops at the closing brace"""
    model = so.MockModel(so.RECORDS[1], quirks=so.QUIRKS)
    f(model, so.FIELDS)
    assert model.text.endswith("}"), (
        "stop as soon as the object is complete. Keep asking for tokens past that point and "
        "the model happily starts on its closing pleasantry, which is how a 'valid JSON' "
        f"path ends up with prose glued to it. Raw output was {model.text!r}"
    )


def _c7(f):
    """the returned value is a parsed dict, not the raw string"""
    got = f(so.MockModel(so.RECORDS[0], quirks=so.QUIRKS), so.FIELDS)
    assert isinstance(got, dict), f"return the parsed object; got {type(got).__name__}"


task("ch07-constrained-decode", _ref_constrained, [_c1, _c2, _c3, _c4, _c5, _c6, _c7])
