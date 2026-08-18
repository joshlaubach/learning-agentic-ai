"""Reference implementations for every graded task, one module per chapter.

Kept out of the notebooks on purpose: a learner working through curriculum/ never has to
scroll past the answer to the exercise they are on. This mirrors the existing convention of
solutions/chNN_*_answers.md holding the written answers.

These are also what CI grades. `GRADER_MODE=reference` makes agentlib.grading.check() import
from here instead of grading the learner's function, so every CI run doubles as proof that
each case suite is passable and each reference below is correct.
"""
