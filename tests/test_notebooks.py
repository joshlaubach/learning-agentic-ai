"""Structural checks for every notebook in curriculum/, interview_prep/, capstone/, and
solutions/.

Execution is covered by pytest-nbmake, wired into CI's single pytest invocation (see
.github/workflows/ci.yml): every notebook runs end to end with no API key present, under
GRADER_MODE=reference so the graded cells are scored against solutions/reference/ rather
than the learner's empty stubs. `test_every_notebook_executes_under_nbmake` below asserts
that wiring is actually in place, so removing --nbmake from CI fails a test rather than
silently reducing the suite to the JSON checks here.

What this file adds on top of execution is the structural invariants nbmake cannot see:
well-formed nbformat 4, and one graded-cell hygiene rule that mirrors tools/check_outputs.py.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NOTEBOOK_DIRS = ["curriculum", "interview_prep", "capstone", "solutions"]


def _all_notebooks():
    for dirname in NOTEBOOK_DIRS:
        yield from sorted((REPO_ROOT / dirname).glob("*.ipynb"))


def test_at_least_one_notebook_found():
    notebooks = list(_all_notebooks())
    assert notebooks, f"expected at least one .ipynb file under {NOTEBOOK_DIRS}"


def test_every_notebook_is_well_formed_json():
    for notebook_path in _all_notebooks():
        with open(notebook_path) as f:
            nb = json.load(f)
        assert nb.get("nbformat") == 4, f"{notebook_path} is not nbformat 4"
        assert "cells" in nb, f"{notebook_path} has no cells"
        assert len(nb["cells"]) > 0, f"{notebook_path} has zero cells"


def test_every_notebook_executes_under_nbmake():
    """CI must actually execute the notebooks, not just parse them.

    This file used to be a placeholder standing in for real execution. It no longer is --
    but the execution lives in CI's pytest invocation, so this asserts the invocation still
    carries --nbmake and the reference grading mode. Without it, dropping one flag would
    quietly turn the whole notebook suite back into a JSON well-formedness check."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "--nbmake" in workflow, "CI no longer executes notebooks: --nbmake is gone"
    assert "GRADER_MODE: reference" in workflow, (
        "CI no longer sets GRADER_MODE=reference, so graded cells would raise "
        "NotImplementedError and every notebook would fail"
    )
    for dirname in NOTEBOOK_DIRS:
        assert f"{dirname}/*.ipynb" in workflow, (
            f"{dirname}/ notebooks are not in CI's pytest invocation"
        )


def test_graded_cells_ship_without_outputs():
    """The same rule tools/check_outputs.py enforces, asserted here so a plain `pytest` run
    catches it too -- a graded cell with committed output shows the answer's printed result
    underneath the NotImplementedError the learner is meant to replace."""
    offenders = []
    for notebook_path in _all_notebooks():
        if notebook_path.parent.name not in ("curriculum", "capstone"):
            continue
        nb = json.loads(notebook_path.read_text())
        for index, cell in enumerate(nb["cells"]):
            if cell.get("cell_type") != "code":
                continue
            if "graded" not in cell.get("metadata", {}).get("tags", []):
                continue
            if cell.get("outputs") or cell.get("execution_count") is not None:
                offenders.append(f"{notebook_path.name} cell {index}")
    assert not offenders, f"graded cells shipping output: {offenders}"
