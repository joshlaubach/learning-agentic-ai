# Containerizes this repository's Python environment so the curriculum's agent code (the
# capstone agent, or any individual chapter's notebook run headlessly) can run the same way
# regardless of the host machine. See curriculum/09_llmops_deployment.ipynb for the
# containerization concept section this file accompanies, and PROGRESS.md's Unit 10 notes
# for how this file was verified in this repo's own build environment.

FROM python:3.11-slim

# A non-root user to run the agent as -- least privilege inside the container too, not just
# in the agent's own tool scoping (Chapter 6's principle, applied one layer down).
RUN useradd --create-home --uid 1000 agent
WORKDIR /app

# Copy dependency manifests first so Docker's layer cache is only invalidated by a real
# dependency change, not by every source-code edit -- the single most common Dockerfile
# performance mistake, worth doing correctly even in a course example.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual code -- after dependencies, for the caching reason above. --chown
# hands ownership to the non-root user up front, so nothing needs a runtime chown step.
COPY --chown=agent:agent agentlib/ ./agentlib/
COPY --chown=agent:agent curriculum/ ./curriculum/
COPY --chown=agent:agent data/ ./data/
COPY --chown=agent:agent tests/ ./tests/
COPY --chown=agent:agent pytest.ini .

# No secrets are ever baked into the image -- LLM_PROVIDER and the API key env vars
# (see .env.example) are supplied at `docker run` time, not at build time. HAS_KEY inside
# agentlib.llm_client resolves to False if they're absent, so the container still starts
# cleanly and falls back to the mock path, exactly like this repo's own CI does.

USER agent

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
    CMD python -c "import agentlib; import sys; sys.exit(0)" || exit 1

# Default: run the full test suite as a smoke test, so `docker run <image>` alone proves the
# image is healthy without needing to know which specific script to invoke. Override with
# `docker run <image> python curriculum/some_script.py` (or `jupyter nbconvert --execute
# <notebook>`) to run something specific instead.
CMD ["python", "-m", "pytest", "tests/", "-q"]
