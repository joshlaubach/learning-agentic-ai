"""Headless execution tests for every notebook in curriculum/, interview_prep/, and
capstone/.

Placeholder — wired up for real in Unit 13, using pytest-nbmake (or an equivalent headless
execution approach) to run every notebook end-to-end with no API key present, asserting zero
errors. See PROGRESS.md.

For now, this just sanity-checks that every notebook currently in the repo is at least
well-formed JSON with the expected notebook structure — a much weaker check than actual
execution, kept here so `pytest` has something real to run against the Unit 1 scaffold.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

NOTEBOOK_DIRS = ["curriculum", "interview_prep", "capstone"]


def _all_notebooks():
    for dirname in NOTEBOOK_DIRS:
        yield from sorted((REPO_ROOT / dirname).glob("*.ipynb"))


def test_at_least_one_notebook_found():
    notebooks = list(_all_notebooks())
    assert notebooks, "expected at least one .ipynb file under curriculum/, interview_prep/, or capstone/"


def test_every_notebook_is_well_formed_json():
    for notebook_path in _all_notebooks():
        with open(notebook_path) as f:
            nb = json.load(f)
        assert nb.get("nbformat") == 4, f"{notebook_path} is not nbformat 4"
        assert "cells" in nb, f"{notebook_path} has no cells"
        assert len(nb["cells"]) > 0, f"{notebook_path} has zero cells"
