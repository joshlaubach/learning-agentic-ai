#!/usr/bin/env python3
"""Re-execute the notebooks and commit their DEMO outputs, leaving graded cells cleared.

Committed DEMO output is what makes this repo readable straight from GitHub without running
anything, so a cell that loses its outputs during editing is a real regression even though
nothing fails. Graded cells are the exception and must stay empty -- a committed output there
is the answer's printed result sitting under the NotImplementedError the learner is meant to
replace. tools/check_outputs.py enforces that half in CI; this script restores the other half.

Runs under GRADER_MODE=reference, since the graded cells raise NotImplementedError otherwise.

    python tools/refresh_outputs.py                 # every notebook
    python tools/refresh_outputs.py curriculum/03_rag_evaluation.ipynb
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIRS = ["curriculum", "capstone", "solutions"]
GRADED_TAG = "graded"


def _targets(argv):
    if argv:
        return [Path(a).resolve() for a in argv]
    return [p for d in NOTEBOOK_DIRS for p in sorted((REPO_ROOT / d).glob("*.ipynb"))]


def main(argv) -> int:
    import nbformat
    from nbclient import NotebookClient

    os.environ["GRADER_MODE"] = "reference"

    for path in _targets(argv):
        nb = nbformat.read(path, as_version=4)
        NotebookClient(
            nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": REPO_ROOT}}
        ).execute()

        cleared = 0
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            if GRADED_TAG in cell.get("metadata", {}).get("tags", []):
                cell["outputs"] = []
                cell["execution_count"] = None
                cleared += 1

        # nbformat's writer normalises differently from the repo's on-disk style; match the
        # existing indent=1 + trailing newline so diffs stay to the cells that changed.
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")

        with_out = sum(
            1
            for c in nb.cells
            if c.cell_type == "code"
            and GRADED_TAG not in c.get("metadata", {}).get("tags", [])
            and c.get("outputs")
        )
        total = sum(
            1
            for c in nb.cells
            if c.cell_type == "code"
            and GRADED_TAG not in c.get("metadata", {}).get("tags", [])
        )
        print(f"{path.relative_to(REPO_ROOT)}: {with_out}/{total} DEMO cells with output, "
              f"{cleared} graded cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
