"""Unit tests for shared functions in agentlib/.

Placeholder — real tests (loop guards, eval metrics, synthetic data generators — asserting
determinism given a fixed seed) get added chapter by chapter as each agentlib module is
implemented (see PROGRESS.md). For now this just confirms the package scaffold itself
imports cleanly.
"""

import agentlib
import agentlib.llm_client
import agentlib.tracing
import agentlib.tools
import agentlib.loop_guards
import agentlib.synthetic_data
import agentlib.eval_metrics


def test_agentlib_package_imports():
    assert agentlib.__doc__ is not None
