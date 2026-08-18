#!/usr/bin/env python3
"""Progress dashboard for the graded tasks in this course.

    python grade.py                 per-chapter table of every graded task and its status
    python grade.py --by-chapter    task counts per chapter
    python grade.py --count-cases   how many assertion cases back the whole course

Status comes from .progress.json, which agentlib.grading.check() rewrites every time you run
a graded cell. A task you have never run shows as "not attempted"; that file is gitignored, so
a fresh clone starts everyone at zero.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from agentlib.grading import load_all_tasks  # noqa: E402

PROGRESS_PATH = REPO_ROOT / ".progress.json"

CHAPTER_TITLES = {
    "ch01": "Fundamentals",
    "ch02": "Agent Control Flow",
    "ch03": "RAG and Retrieval Evaluation",
    "ch04": "Production Reliability",
    "ch05": "Cost, Performance, Model Selection",
    "ch06": "Security and Safeguards",
    "ch07": "Tool Integration",
    "ch08": "System Design Judgment",
    "ch09": "LLMOps and Deployment",
}


def _load_progress() -> dict:
    try:
        data = json.loads(PROGRESS_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _grouped(registry: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for task_id, spec in registry.items():
        groups.setdefault(spec["chapter"], []).append(task_id)
    return {ch: sorted(ids) for ch, ids in sorted(groups.items())}


def show_table(registry: dict) -> None:
    progress = _load_progress()
    groups = _grouped(registry)
    done = 0

    for chapter, task_ids in groups.items():
        title = CHAPTER_TITLES.get(chapter, chapter)
        print(f"\n{chapter} — {title}")
        for task_id in task_ids:
            entry = progress.get(task_id)
            n_cases = len(registry[task_id]["cases"])
            if entry is None:
                status, detail = "· not attempted", f"{n_cases} cases"
            elif entry.get("passed"):
                status, detail = "✓ passed", f"{entry.get('cases', '')} cases"
                done += 1
            else:
                status, detail = "✗ failing", f"{entry.get('cases', '')} cases"
            print(f"  {status:16s} {task_id:24s} {detail}")

    total = len(registry)
    print(f"\n{total} graded tasks registered across {len(groups)} chapters.")
    print(f"{done}/{total} passed.")


def show_by_chapter(registry: dict) -> None:
    groups = _grouped(registry)
    print(f"{'chapter':8s} {'tasks':>6s} {'cases':>6s}  title")
    for chapter, task_ids in groups.items():
        cases = sum(len(registry[t]["cases"]) for t in task_ids)
        print(
            f"{chapter:8s} {len(task_ids):>6d} {cases:>6d}  "
            f"{CHAPTER_TITLES.get(chapter, chapter)}"
        )
    print(f"\n{len(registry)} graded tasks across {len(groups)} chapters.")


def show_case_count(registry: dict) -> None:
    total = sum(len(spec["cases"]) for spec in registry.values())
    print(f"{total} assertion cases across {len(registry)} graded tasks.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--by-chapter", action="store_true", help="task counts per chapter")
    parser.add_argument("--count-cases", action="store_true", help="total assertion cases")
    args = parser.parse_args()

    registry = load_all_tasks()
    if args.by_chapter:
        show_by_chapter(registry)
    elif args.count_cases:
        show_case_count(registry)
    else:
        show_table(registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
