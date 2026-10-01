"""Shared plumbing for Chapter 4's multi-step reliability section.

Chapter 4's second half argues that a multi-step agent's headline number (pass@1) hides how
often it actually finishes: at 95% per step, twenty steps succeed 0.95**20 = 35.8% of the
time. This module is the measurement side of that argument. The *policies* the chapter teaches
-- the pass^k estimator, the fail-closed gate chain, the refine loop, the harness fingerprint --
are graded builds the learner writes in the notebook (task ids ch04-pass-hat-k, ch04-gate-chain,
ch04-refine-loop, ch04-harness-fingerprint), so `reliability_report` takes the learner's
`pass_hat_k` and `fingerprint` as arguments rather than importing them, the same split
`eval_metrics.evaluate_retrieval` makes.

Three design choices worth knowing about, because each one is a way a reliability number quietly
becomes optimistic:

- A trial that crashes is a failed trial. `run_trials` records it as success=False with the
  error; dropping it would be survivorship bias, and a crash on step 14 of 20 is exactly the
  failure the metric exists to count.
- Trials must be independent. A cache or counter that survives from one trial to the next makes
  pass^k look better than it is, so `run_trials` takes a `reset` hook that runs before every
  trial.
- A report carries the harness it measured. A number with no manifest cannot be reproduced or
  compared; `reliability_report` embeds the manifest's fingerprint and lists what the manifest
  fails to disclose.
"""

from __future__ import annotations

import math

# What a reliability number should disclose about the harness that produced it: change any of
# these and the number is about a different system.
MANIFEST_FIELDS = (
    "harness_version",
    "model",
    "prompt_version",
    "context_policy",
    "tools",
    "retry_policy",
    "budgets",
    "verifications",
    "sampling",
)

# llm_client.call_model forwards no temperature or seed, and the Messages API has no seed, so
# the honest disclosure is "not controlled" rather than a number we do not set.
_DEFAULT_SAMPLING = {
    "temperature": "provider default (not set by call_model)",
    "seed": None,
    "seed_supported": False,
}

_ABSENT = "<absent>"


def default_manifest(**overrides) -> dict:
    """A harness manifest with every disclosed field present: None means "not yet disclosed".

    An unknown keyword raises KeyError instead of being added, so a typo like `budget=` cannot
    quietly leave the real `budgets` field undisclosed while the manifest looks complete."""
    manifest = {field: None for field in MANIFEST_FIELDS}
    manifest["sampling"] = dict(_DEFAULT_SAMPLING)
    for key, value in overrides.items():
        if key not in manifest:
            raise KeyError(f"{key!r} is not a manifest field; fields are {MANIFEST_FIELDS}")
        manifest[key] = value
    return manifest


def missing_disclosures(manifest: dict) -> list[str]:
    """The manifest fields that are absent or None, in MANIFEST_FIELDS order."""
    return [f for f in MANIFEST_FIELDS if manifest.get(f) is None]


def manifest_diff(a: dict, b: dict) -> dict[str, tuple]:
    """{dotted.path: (a_value, b_value)} for every leaf where two manifests differ.

    Dicts are walked; lists are compared whole, because a retry schedule or a tool order is one
    value whose order is behaviour. A key present on only one side shows the other as
    "<absent>"."""
    diff: dict[str, tuple] = {}

    def walk(x, y, path):
        if isinstance(x, dict) and isinstance(y, dict):
            for key in sorted(set(x) | set(y)):
                walk(x.get(key, _ABSENT), y.get(key, _ABSENT), f"{path}.{key}" if path else key)
        elif x != y:
            diff[path] = (x, y)

    walk(a, b, "")
    return diff


def run_trials(agent, tasks, n: int, *, reset=None) -> dict[str, list[dict]]:
    """Run `agent(task)` n times per task and return {task: [outcome, ...]}.

    `agent` returns {"success": bool, "cost": float = 0, "steps": int = 0, "harm": bool =
    False}. An agent that raises is recorded as {"success": False, ..., "error": "..."} and
    still counted. `reset()` runs before every trial so no state leaks between them."""
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    results: dict[str, list[dict]] = {}
    for task in tasks:
        outcomes = []
        for _ in range(n):
            if reset is not None:
                reset()
            try:
                out = agent(task)
            except Exception as e:  # a crash is a failed trial, not a missing one
                outcomes.append(
                    {"success": False, "cost": 0.0, "steps": 0, "harm": False,
                     "error": f"{type(e).__name__}: {e}"}
                )
                continue
            if not isinstance(out, dict) or "success" not in out:
                raise TypeError(
                    f"agent({task!r}) must return a dict with a 'success' key, got {out!r}"
                )
            outcomes.append(
                {
                    "success": bool(out["success"]),
                    "cost": float(out.get("cost", 0.0)),
                    "steps": int(out.get("steps", 0)),
                    "harm": bool(out.get("harm", False)),
                }
            )
        results[task] = outcomes
    return results


def _successes(runs: dict[str, list[dict]]) -> dict[str, list[bool]]:
    return {task: [o["success"] for o in outcomes] for task, outcomes in runs.items()}


def pass_at_k(results: dict[str, list[bool]], k: int) -> float:
    """Chen et al. (2021) unbiased pass@k: the chance that at least one of k trials drawn from
    the n you ran succeeds, averaged over tasks. Given here so the chapter can set it beside
    pass^k; the two answer opposite questions ("can it ever?" vs "will it every time?")."""
    if not results:
        raise ValueError("results is empty")
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    total = 0.0
    for task, trials in results.items():
        n, c = len(trials), sum(trials)
        if n < k:
            raise ValueError(f"task {task!r} has {n} trials, fewer than k={k}")
        total += 1 - math.comb(n - c, k) / math.comb(n, k)
    return total / len(results)


def reliability_report(runs, manifest, ks, *, pass_hat_k, fingerprint) -> dict:
    """Summarise run_trials output: pass@k and pass^k side by side, cost, harm, and the harness.

    A k larger than the number of trials cannot be estimated, so it lands in `ks_skipped`
    rather than being clamped to something the data cannot support. Cost is whatever the agent
    reported -- count model calls, as llm_client does, rather than hard-coding a price."""
    if not runs:
        raise ValueError("runs is empty")
    results = _successes(runs)
    n_trials = min(len(trials) for trials in results.values())
    usable = [k for k in ks if k <= n_trials]
    outcomes = [o for trials in runs.values() for o in trials]
    successes = sum(o["success"] for o in outcomes)
    total_cost = sum(o["cost"] for o in outcomes)
    return {
        "n_tasks": len(runs),
        "n_trials": n_trials,
        "pass@k": {k: pass_at_k(results, k) for k in usable},
        "pass^k": {k: pass_hat_k(results, k) for k in usable},
        "ks_skipped": [k for k in ks if k > n_trials],
        "cost": {
            "per_trial": total_cost / len(outcomes),
            "per_success": total_cost / successes if successes else None,
        },
        "crashed_trials": sum(1 for o in outcomes if "error" in o),
        "harmful_trials": sum(o["harm"] for o in outcomes),
        "manifest_fingerprint": fingerprint(manifest),
        "undisclosed": missing_disclosures(manifest),
    }


def render_report(report: dict) -> str:
    """The report as plain text, one line per k, for printing under a notebook cell."""
    lines = [
        f"harness {report['manifest_fingerprint']}  "
        f"({report['n_tasks']} tasks x {report['n_trials']} trials)",
        f"{'k':>3}  {'pass@k':>8}  {'pass^k':>8}",
    ]
    for k in sorted(report["pass^k"]):
        lines.append(f"{k:>3}  {report['pass@k'][k]:>8.3f}  {report['pass^k'][k]:>8.3f}")
    if report["ks_skipped"]:
        lines.append(f"skipped k={report['ks_skipped']}: more than {report['n_trials']} trials")
    per_success = report["cost"]["per_success"]
    lines.append(
        f"cost/trial {report['cost']['per_trial']:.2f}, cost/success "
        f"{'n/a' if per_success is None else f'{per_success:.2f}'}, "
        f"crashed {report['crashed_trials']}, harmful {report['harmful_trials']}"
    )
    if report["undisclosed"]:
        lines.append(f"undisclosed: {', '.join(report['undisclosed'])}")
    return "\n".join(lines)


def quorum_gate(votes: list, required: int | None = None) -> tuple[bool, str]:
    """Consensus gate: pass only if enough voters approve. votes are True / False / None.

    `required` defaults to a strict majority of ALL voters, not of those who answered, so
    abstentions (None) count against approval and a tie denies. Three copies of one biased
    judge are one vote that happens to be counted three times; consensus buys safety only when
    the voters' mistakes are independent."""
    n = len(votes)
    if n == 0:
        return False, "no voters"
    if required is None:
        required = n // 2 + 1
    if not 1 <= required <= n:
        raise ValueError(f"required must be between 1 and {n}, got {required}")
    approvals = sum(1 for v in votes if v is True)
    abstained = sum(1 for v in votes if v is None)
    ok = approvals >= required
    return ok, f"{approvals}/{n} approved ({abstained} abstained), needed {required}"


def audit_gate(gate, known_good: list, known_bad: list) -> dict:
    """Test a gate against cases whose right answer you already know.

    Verification is both an origin of failures and the downstream gate, so a gate is itself
    code that needs a test suite. `gate(case)` must return (True, reason) to accept; anything
    else -- False, None, a bare truthy value, an exception -- counts as a reject, the same
    fail-closed reading run_gated uses. Returns the offending cases, not just counts: a
    rubber-stamp verifier shows up as every known-bad case in `false_accepts`."""

    def accepts(case) -> bool:
        try:
            result = gate(case)
        except Exception:
            return False
        return isinstance(result, tuple) and len(result) == 2 and result[0] is True

    false_accepts = [c for c in known_bad if accepts(c)]
    false_rejects = [c for c in known_good if not accepts(c)]
    return {
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
        "n_good": len(known_good),
        "n_bad": len(known_bad),
    }
