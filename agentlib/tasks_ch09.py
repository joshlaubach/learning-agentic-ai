"""Graded task suites for Chapter 9 — LLMOps and Deployment.

The registry suite leans on the rollback scenario rather than on the immutability rule
directly, because a mutable store passes every test that only ever reads back what it just
wrote. It fails the moment you try to roll back to something you edited.
"""

from __future__ import annotations

from agentlib.grading import task
from agentlib.prose_checks import is_written_answer, matched, mentions

_V1 = "You are a helpful support assistant. Answer the customer's question directly."
_V2 = "You are a helpful support assistant. Answer directly and concisely."
_V3 = "You are a cautious support assistant. When in doubt, decline to answer."


# --- ch09-prompt-version ---


def _ref_registry():
    from solutions.reference.ch09 import PromptRegistry

    return PromptRegistry


def _r1(f):
    """publishing then reading back"""
    r = f()
    r.publish("v1", _V1)
    assert r.get("v1").text == _V1, f"get() returns what publish() stored; got {r.get('v1')!r}"
    assert r.get("v1").version_id == "v1", "each version knows its own id"


def _r2(f):
    """republishing an existing id"""
    r = f()
    r.publish("v1", _V1)
    try:
        r.publish("v1", "something else entirely")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "publishing over an existing id must raise. Allowing it is how 'we rolled back' "
            "becomes a sentence people say about a system that did not roll back."
        )


def _r3(f):
    """a published version cannot be edited afterwards"""
    r = f()
    published = r.publish("v1", _V1)
    try:
        published.text = "quietly rewritten"
    except Exception:
        pass
    else:
        raise AssertionError(
            "a PromptVersion has to be immutable once published -- frozen=True on the "
            "dataclass. If the object can be edited in place, every audit trail in this "
            f"registry is describing an id, not a prompt. It now reads {published.text!r}."
        )


def _r4(f):
    """rollback returns the ORIGINAL text, not an edited one"""
    r = f()
    r.publish("v1", _V1)
    r.promote("v1")
    r.publish("v2", _V2)
    r.promote("v2")
    r.promote("v1")  # the rollback
    assert r.current_version == "v1", f"promote() moves the pointer; got {r.current_version!r}"
    assert r.get("v1").text == _V1, (
        "this is the whole point of the registry. Rolling back has to give you back exactly "
        "the prompt that was running before, byte for byte. If publishing a new version "
        "edited the stored text in place, the pointer moves and nothing else does -- the "
        f"rollback is a no-op that reports success. Got {r.get('v1').text!r}"
    )


def _r5(f):
    """publishing v2 leaves v1 alone"""
    r = f()
    r.publish("v1", _V1)
    r.publish("v2", _V2)
    r.publish("v3", _V3)
    assert r.get("v1").text == _V1 and r.get("v2").text == _V2, (
        "versions are independent records, not a single slot that gets overwritten"
    )


def _r6(f):
    """promoting a version that was never published"""
    r = f()
    r.publish("v1", _V1)
    try:
        r.promote("v99")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "promoting an id that does not exist must raise -- silently pointing production "
            "at nothing is worse than failing the deploy"
        )


def _r7(f):
    """the pointer starts empty"""
    r = f()
    assert r.current_version is None, (
        f"a fresh registry has nothing promoted yet; got {r.current_version!r}"
    )
    assert r.history == [], f"and no history; got {r.history!r}"


def _r8(f):
    """history records every promote, in order"""
    r = f()
    for vid, text in (("v1", _V1), ("v2", _V2), ("v3", _V3)):
        r.publish(vid, text)
    r.promote("v1")
    r.promote("v2")
    r.promote("v3")
    assert r.history == ["v1", "v2", "v3"], (
        f"history is the audit trail -- append on every promote; got {r.history!r}"
    )


def _r9(f):
    """a rollback is itself an event in the history"""
    r = f()
    r.publish("v1", _V1)
    r.publish("v2", _V2)
    r.promote("v1")
    r.promote("v2")
    r.promote("v1")
    assert r.history == ["v1", "v2", "v1"], (
        "the rollback is a deploy and belongs in the trail. Deduplicating it away loses the "
        f"one entry an incident review is looking for. Got {r.history!r}"
    )


def _r10(f):
    """publishing does not promote"""
    r = f()
    r.publish("v1", _V1)
    r.promote("v1")
    r.publish("v2", _V2)
    assert r.current_version == "v1", (
        "publishing puts a version on the shelf; promoting is what points traffic at it. "
        f"Conflating them means every publish is a deploy. Got {r.current_version!r}"
    )


task(
    "ch09-prompt-version",
    _ref_registry,
    [_r1, _r2, _r3, _r4, _r5, _r6, _r7, _r8, _r9, _r10],
)


# --- ch09-canary-split ---


def _ref_route():
    from solutions.reference.ch09 import route_request

    return route_request


_IDS = [f"req-{i:05d}" for i in range(1000)]


def _c1(f):
    """ten percent of traffic reaches the canary"""
    routed = [f(rid, "v1", "v2", 10) for rid in _IDS]
    share = routed.count("v2") / len(routed) * 100
    assert 7 <= share <= 13, f"canary_pct=10 should route about 10% of 1000 ids; got {share:.1f}%"


def _c2(f):
    """the same request always lands on the same side"""
    for rid in _IDS[:50]:
        first = f(rid, "v1", "v2", 10)
        for _ in range(5):
            assert f(rid, "v1", "v2", 10) == first, (
                "routing must be a pure function of the request id. An unseeded random() "
                "gives the right SHARE of traffic and re-rolls per call, so one user flips "
                f"between versions mid-conversation and no bug report is ever reproducible. "
                f"{rid!r} routed to {first!r} and then somewhere else."
            )


def _c3(f):
    """nobody is on the canary at zero percent"""
    routed = {f(rid, "v1", "v2", 0) for rid in _IDS}
    assert routed == {"v1"}, f"canary_pct=0 means no canary traffic at all; got {routed}"


def _c4(f):
    """everybody is on the canary at a hundred percent"""
    routed = {f(rid, "v1", "v2", 100) for rid in _IDS}
    assert routed == {"v2"}, f"canary_pct=100 means all of it; got {routed}"


def _c5(f):
    """ramping up never moves anyone back to stable"""
    at_10 = {rid for rid in _IDS if f(rid, "v1", "v2", 10) == "v2"}
    at_25 = {rid for rid in _IDS if f(rid, "v1", "v2", 25) == "v2"}
    assert at_10 <= at_25, (
        "a progressive rollout widens the cohort; it does not reshuffle it. Everyone on the "
        "canary at 10% must still be on it at 25%, or users bounce between prompt versions "
        f"as you ramp. {len(at_10 - at_25)} request(s) were moved back to stable."
    )


def _c6(f):
    """the split scales with the percentage"""
    share_5 = sum(f(rid, "v1", "v2", 5) == "v2" for rid in _IDS) / 10
    share_50 = sum(f(rid, "v1", "v2", 50) == "v2" for rid in _IDS) / 10
    assert share_5 < share_50, (
        f"a bigger canary_pct means more canary traffic; got {share_5:.1f}% at 5 and "
        f"{share_50:.1f}% at 50"
    )


def _c7(f):
    """only the two given versions come back"""
    routed = {f(rid, "stable-a", "canary-b", 30) for rid in _IDS}
    assert routed <= {"stable-a", "canary-b"}, (
        f"return one of the two version ids you were handed; got {routed}"
    )


def _c8(f):
    """the assignment does not depend on which versions are named"""
    a = [f(rid, "v1", "v2", 20) == "v2" for rid in _IDS[:200]]
    b = [f(rid, "x", "y", 20) == "y" for rid in _IDS[:200]]
    assert a == b, (
        "the cohort is decided by the request id, not by the version strings, so renaming "
        "the versions must not reshuffle who sees what"
    )


task(
    "ch09-canary-split",
    _ref_route,
    [_c1, _c2, _c3, _c4, _c5, _c6, _c7, _c8],
)


# --- ch09-drift-detect ---


def _ref_health():
    from solutions.reference.ch09 import check_canary_health

    return check_canary_health


def _h1(f):
    """the two versions behave identically"""
    assert f(0.10, 0.10) is True, "no difference at all is healthy"


def _h2(f):
    """ordinary sampling noise"""
    got = f(0.100, 0.108)
    assert got is True, (
        "less than a percentage point of movement between two 500-request samples is noise, "
        f"not a regression. Got {got!r}. A check with no threshold -- one that fires on any "
        "difference at all -- pages someone on every single rollout, and a rollback signal "
        "that cries wolf gets muted within a week, which leaves you with no signal at all."
    )


def _h3(f):
    """the chapter's actual regression"""
    got = f(0.08, 0.40)
    assert got is False, (
        f"a 32-point jump in refusal rate is a severe, obvious regression and has to trip "
        f"the check. Got {got!r} -- this is the exact swing that sailed through the buggy "
        "0.5 threshold and shipped to 100% of traffic."
    )


def _h4(f):
    """the default threshold is calibrated, not just round"""
    assert f(0.08, 0.20) is False, (
        "a 12-point move is well past noise and must be caught by the DEFAULT threshold, "
        "without the caller having to pass one. 0.5 is a round number, not a calibrated one: "
        "it only trips above a fifty-point swing, which no real regression ever reaches."
    )


def _h5(f):
    """an explicit threshold is honoured"""
    assert f(0.10, 0.13, threshold=0.05) is True, "3 points is inside a 5-point threshold"
    assert f(0.10, 0.13, threshold=0.01) is False, "and outside a 1-point one"


def _h6(f):
    """drift in the other direction counts too"""
    assert f(0.40, 0.08) is False, (
        "compare the absolute difference. A canary that refuses thirty points LESS often has "
        "also changed behaviour sharply, and an unexplained improvement is worth stopping "
        "the rollout for just as much as an unexplained regression."
    )


def _h7(f):
    """right at the threshold"""
    # 0.25 and 0.5 are exact in binary, so this boundary is actually reachable -- 0.10 vs
    # 0.15 against 0.05 is not, since the subtraction lands on 0.04999999999999999.
    assert f(0.25, 0.50, threshold=0.25) is False, (
        "a difference of exactly the threshold is not inside it -- use a strict <"
    )


def _h8(f):
    """the verdict is a real bool"""
    got = f(0.10, 0.10)
    assert isinstance(got, bool), (
        f"the rollout branches on this directly; return True or False. Got "
        f"{type(got).__name__}: {got!r}"
    )


task(
    "ch09-drift-detect",
    _ref_health,
    [_h1, _h2, _h3, _h4, _h5, _h6, _h7, _h8],
)


# --- The two written diagnoses ---
#
# Same shape as Chapter 5's: the case that matters in each rejects the confident wrong
# answer, which for both of these is a PROCESS answer to a STRUCTURAL problem. "Be more
# careful during deploys" and "the rollout process is broken" are what a competent engineer
# says when they have not yet looked at the thing that is actually wrong.

_MIN_WORDS = 60


def _needs(answer, family, what, hint, wrong=None, wrong_hint=""):
    if mentions(answer, family):
        return
    if wrong is not None and mentions(answer, wrong):
        raise AssertionError(
            f"this settles on {', '.join(matched(answer, wrong))!r}, which is a process "
            f"answer to a structural problem. {wrong_hint} {hint}"
        )
    raise AssertionError(f"the answer never names {what}. {hint}")


# ch09-diagnose-mutable-prompt

_MUT_CAUSE = ("mutable", "overwrit", "over-writ", "in place", "in-place", "no history",
              "no version", "same key", "edited", "replaced", "no record", "lost the")
_MUT_WRONG = ("be more careful", "more careful", "review process", "code review",
              "training", "discipline", "double-check", "human error", "process")
_MUT_FIX = ("immutable", "append-only", "append only", "never overwrite", "new version",
            "pointer", "current_version", "current version", "version per publish",
            "history")


def _ref_mutable():
    from solutions.reference.ch09 import DIAGNOSE_MUTABLE_PROMPT

    return DIAGNOSE_MUTABLE_PROMPT


def _m1(f):
    """the answer is written out at length"""
    is_written_answer(f, _MIN_WORDS)


def _m2(f):
    """it names why the rollback did nothing"""
    _needs(f, _MUT_CAUSE, "the cause",
           "The pointer moved and the text behind it did not, because the text had already "
           "been overwritten.",
           wrong=_MUT_WRONG,
           wrong_hint="Care is not a control. A store that allows the edit will eventually "
                      "have the edit made, by someone tired, at the wrong hour.")


def _m3(f):
    """it says how it would be confirmed"""
    _needs(f, ("history", "record", "prior", "previous", "original", "audit", "check "),
           "how you would confirm it",
           "What would you look for in the store to prove the old text is gone?")


def _m4(f):
    """it proposes a structural fix"""
    _needs(f, _MUT_FIX, "a fix",
           "The fix is a data structure that makes the mistake impossible: immutable "
           "versions and a pointer that is the only movable thing.")


def _m5(f):
    """it does not settle for a process fix"""
    assert mentions(f, _MUT_FIX), (
        "'be more careful' is the answer that leaves the system exactly as breakable as it "
        "was. Name the structural change -- that is the difference between an incident "
        "review that fixes something and one that produces a resolution."
    )


task("ch09-diagnose-mutable-prompt", _ref_mutable, [_m1, _m2, _m3, _m4, _m5])


# ch09-diagnose-loose-threshold

_THR_CAUSE = ("threshold", "0.5", "50 point", "50-point", "fifty", "too loose", "too large",
              "too high", "uncalibrated", "not calibrated", "never checked", "round number")
_THR_WRONG = ("rollout process", "the process", "should have rolled back",
              "canary process", "more stages", "slower rollout", "manual review")
_THR_FIX = ("calibrat", "0.05", "5 point", "5-point", "five point", "tighter", "smaller",
            "against what", "observed", "real regression", "magnitude")
_THR_NOISE = ("noise", "sampling", "false", "fire on every", "cry wolf", "too tight",
              "flaky", "variance")


def _ref_threshold():
    from solutions.reference.ch09 import DIAGNOSE_LOOSE_THRESHOLD

    return DIAGNOSE_LOOSE_THRESHOLD


def _t1(f):
    """the answer is written out at length"""
    is_written_answer(f, _MIN_WORDS)


def _t2(f):
    """it identifies the threshold itself as the bug"""
    _needs(f, _THR_CAUSE, "the threshold",
           "The question asked what is wrong with the FUNCTION, not with the rollout.",
           wrong=_THR_WRONG,
           wrong_hint="The rollout did exactly what it was told to do. It was told the "
                      "canary was healthy.")


def _t3(f):
    """it relates the threshold to the size of the actual regression"""
    _needs(f, ("32", "thirty", "regression", "swing", "magnitude", "point"),
           "the size of the regression it missed",
           "A threshold is only wrong relative to something. Say what the real regression "
           "measured and why the threshold could not see it.")


def _t4(f):
    """it proposes a calibrated replacement"""
    _needs(f, _THR_FIX, "a fix",
           "Calibrate the threshold against what a real regression actually looks like "
           "rather than against a round number.")


def _t5(f):
    """it recognises that a threshold can also be too tight"""
    _needs(f, _THR_NOISE, "the other failure direction",
           "A threshold set at zero catches every regression and fires on every rollout, "
           "because two finite samples never agree exactly. A rollback signal that cries "
           "wolf gets muted, which leaves you with no signal at all.")


task("ch09-diagnose-loose-threshold", _ref_threshold, [_t1, _t2, _t3, _t4, _t5])
