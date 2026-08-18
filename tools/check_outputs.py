#!/usr/bin/env python3
"""Output hygiene check for notebooks under curriculum/ and capstone/.

One rule, in two halves:

- A cell tagged `graded` must ship with EMPTY outputs. Those cells contain the exercise, and
  a committed output is the answer's printed result sitting right underneath the
  NotImplementedError the learner is supposed to replace.
- Every other code cell keeps its outputs. Committed DEMO output is what makes this repo
  readable straight from GitHub without running anything, and this script must never be
  turned into a reason to strip it.

Run it yourself with `python tools/check_outputs.py`; CI runs it on every push. To fix a
flagged cell: `pip install -r requirements-dev.txt && nbstripout <notebook>` then re-run the
notebook to restore the DEMO outputs, or just clear that one cell in Jupyter.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# solutions/ is deliberately absent: nothing there is tagged `graded` (it IS the answer
# key), so committed output is exactly what those notebooks are for.
CHECKED_DIRS = ["curriculum", "capstone"]
GRADED_TAG = "graded"


def _notebooks():
    for dirname in CHECKED_DIRS:
        yield from sorted((REPO_ROOT / dirname).glob("*.ipynb"))


def main() -> int:
    violations: list[str] = []
    graded_cells = 0

    for path in _notebooks():
        nb = json.loads(path.read_text())
        for index, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            if GRADED_TAG not in cell.get("metadata", {}).get("tags", []):
                continue
            graded_cells += 1
            rel = path.relative_to(REPO_ROOT)
            if cell.get("outputs"):
                violations.append(
                    f"{rel}: cell {index} is tagged '{GRADED_TAG}' but ships "
                    f"{len(cell['outputs'])} committed output(s)"
                )
            if cell.get("execution_count") is not None:
                violations.append(
                    f"{rel}: cell {index} is tagged '{GRADED_TAG}' but has "
                    f"execution_count={cell['execution_count']}; it should be null"
                )

    if violations:
        print(f"{len(violations)} graded cell(s) ship committed output:\n")
        for v in violations:
            print(f"  {v}")
        print(
            "\nClear those cells' outputs before committing "
            "(see tools/check_outputs.py's docstring)."
        )
        return 1

    print(f"OK: all {graded_cells} graded cell(s) ship with cleared outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
