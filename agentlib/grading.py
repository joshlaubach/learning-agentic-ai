"""Autograder core. One public function: check().

Every graded cell in the curriculum ends with a `check("<task-id>", your_function)` call.
That call runs a suite of assertion cases against what the learner wrote and either prints a
pass line or raises an AssertionError listing exactly which cases failed and why.

Two modes, selected by the GRADER_MODE environment variable:

- learner   (default) — grade the function the learner passed in. On a fresh clone the
                        notebook cells raise NotImplementedError, so this path fails loudly.
- reference           — ignore the passed-in function entirely, import the model answer from
                        solutions/reference/ and grade that instead. CI runs in this mode, so
                        every notebook still executes end-to-end with no API key, and CI
                        additionally proves that every case suite is passable and every
                        reference implementation is correct.

Task suites live in agentlib/tasks_chNN.py, one module per chapter, and are auto-discovered
the first time check() runs.
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import pkgutil
import time
from pathlib import Path

MODE = os.environ.get("GRADER_MODE", "learner").lower()  # learner | reference

_PROGRESS = Path(__file__).resolve().parent.parent / ".progress.json"
_REGISTRY: dict[str, dict] = {}
_LOADED = False


def task(task_id: str, reference, cases) -> None:
    """Register a graded task.

    `reference` is a zero-argument callable returning the model answer (imported lazily so a
    learner-mode run never touches solutions/). `cases` is a list of callables, each taking
    the function under test and asserting one specific behaviour.
    """
    if task_id in _REGISTRY:
        raise ValueError(
            f"duplicate task id {task_id!r}: already registered by "
            f"{_REGISTRY[task_id]['module']}. Task ids must be unique across all chapters."
        )
    if not cases:
        raise ValueError(f"{task_id}: a task needs at least one case")
    caller = inspect.stack()[1]
    _REGISTRY[task_id] = {
        "reference": reference,
        "cases": list(cases),
        "module": Path(caller.filename).name,
        "chapter": task_id.split("-")[0],
    }


def load_all_tasks() -> dict[str, dict]:
    """Import every agentlib/tasks_ch*.py so the registry is complete. Idempotent."""
    global _LOADED
    if not _LOADED:
        package_dir = Path(__file__).resolve().parent
        for module in sorted(m.name for m in pkgutil.iter_modules([str(package_dir)])):
            if module.startswith("tasks_"):
                importlib.import_module(f"{__package__}.{module}")
        _LOADED = True
    return _REGISTRY


class _Probe:
    """Transparent wrapper that remembers how the function under test was called, so a failed
    case can report the inputs that produced the failure without every case message having to
    repeat them by hand."""

    def __init__(self, fn):
        self._fn = fn
        self.calls: list[str] = []

    def __call__(self, *args, **kwargs):
        rendered = ", ".join(
            [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        )
        name = getattr(self._fn, "__name__", "your function")
        self.calls.append(f"{name}({rendered})")
        return self._fn(*args, **kwargs)

    def __getattr__(self, name):  # forward __name__, __doc__, attributes, everything else
        return getattr(self._fn, name)

    def __repr__(self):
        return repr(self._fn)


def _record(task_id: str, passed: bool, n_pass: int, n_total: int) -> None:
    try:
        data = json.loads(_PROGRESS.read_text()) if _PROGRESS.exists() else {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    data[task_id] = {
        "passed": passed,
        "cases": f"{n_pass}/{n_total}",
        "ts": time.strftime("%Y-%m-%d %H:%M"),
    }
    try:
        _PROGRESS.write_text(json.dumps(data, indent=2, sort_keys=True))
    except OSError:
        pass  # a read-only checkout should not break grading


def check(task_id: str, fn=None):
    """Grade `fn` against the case suite registered for `task_id`.

    Prints a one-line pass summary, or raises AssertionError naming every failed case, the
    call that failed, and what went wrong.

    Returns whatever was graded, so a graded cell can rebind its own name to the result:

        my_function = check("chNN-task-id", my_function)

    In learner mode that returns `fn` unchanged and the rebinding is a no-op. In reference
    mode it returns the model answer, which is how the rest of a notebook keeps running
    under CI even though its graded cells are still empty stubs.
    """
    registry = load_all_tasks()
    if task_id not in registry:
        raise KeyError(
            f"unknown task id {task_id!r}. Registered ids: {', '.join(sorted(registry))}"
        )
    spec = registry[task_id]
    target = spec["reference"]() if MODE == "reference" else fn
    if target is None:
        raise ValueError(f"{task_id}: pass your function to check()")

    failures, n = [], len(spec["cases"])
    for i, case in enumerate(spec["cases"], 1):
        # A class is passed through so isinstance/construction still work, and so is a
        # non-callable -- ch06-write-a-payload grades a payload string, not a function.
        wrappable = callable(target) and not inspect.isclass(target)
        probe = _Probe(target) if wrappable else target
        detail = getattr(case, "__doc__", None)
        label = f"[{i}/{n}]" + (f" {detail.strip()}" if detail else "")
        try:
            case(probe)
        except AssertionError as e:
            failures.append(f"  {label}\n      {e}{_last_call(probe)}")
        except NotImplementedError:
            failures.append(f"  {label}\n      not implemented yet")
        except Exception as e:
            failures.append(
                f"  {label}\n      raised {type(e).__name__}: {e}{_last_call(probe)}"
            )

    n_pass = n - len(failures)
    _record(task_id, not failures, n_pass, n)
    if failures:
        raise AssertionError(
            f"\n{task_id}: {n_pass}/{n} checks passed.\n"
            + "\n".join(failures)
            + "\n\nFix the function above and re-run this cell."
        )
    print(f"{task_id}: {n}/{n} checks passed.")
    return target


def _last_call(probe) -> str:
    calls = getattr(probe, "calls", None)
    if not calls:
        return ""
    return f"\n      failing call: {calls[-1]}"
