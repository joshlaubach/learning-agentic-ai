"""agentlib — shared library code for ai-agent-interview-prep.

Built incrementally as the curriculum's own build progresses (see PROGRESS.md), not written
up front. Each module below is a placeholder until the unit that implements it lands:

- llm_client.py    — Unit 2  (Chapter 1). The one module built directly here from the start,
                      since every real-API chapter from Chapter 2 onward needs it immediately.
- tracing.py       — Unit 3  (Chapter 2). New that chapter.
- tools.py         — Unit 4  (Chapter 3). Built inline in Chapters 1-2 first for teaching
                      clarity, then promoted here for reuse from Chapter 3 onward.
- loop_guards.py   — Unit 4  (Chapter 3). Same inline-then-promoted pattern as tools.py.
- synthetic_data.py — Unit 4 (Chapter 3).
- eval_metrics.py  — Unit 4  (Chapter 3).
"""
