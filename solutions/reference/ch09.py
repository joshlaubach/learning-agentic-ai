"""Chapter 9 reference answers — LLMOps and Deployment.

An immutable prompt registry, a deterministic canary split, and a drift check whose threshold
is calibrated against what a real regression actually looks like.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptVersion:
    """frozen=True is the whole point: a published version cannot be edited afterwards."""

    version_id: str
    text: str


class PromptRegistry:
    def __init__(self):
        self._versions: dict[str, PromptVersion] = {}
        self.current_version: str | None = None
        self.history: list[str] = []  # every promote(), in order -- the actual audit trail

    def publish(self, version_id: str, text: str) -> PromptVersion:
        if version_id in self._versions:
            raise ValueError(
                f"version {version_id!r} already exists -- versions are immutable, "
                "publish a new id"
            )
        pv = PromptVersion(version_id, text)
        self._versions[version_id] = pv
        return pv

    def promote(self, version_id: str) -> None:
        if version_id not in self._versions:
            raise ValueError(f"no such version: {version_id!r}")
        self.current_version = version_id
        self.history.append(version_id)

    def get(self, version_id: str) -> PromptVersion:
        return self._versions[version_id]


def route_request(
    request_id: str, stable_version: str, canary_version: str, canary_pct: float
) -> str:
    """Hash the request id and split on the hash, so the assignment is a pure function of the
    id: the same request lands on the same side every time, in every process, forever."""
    h = int(hashlib.sha256(request_id.encode()).hexdigest(), 16)
    return canary_version if (h % 100) < canary_pct else stable_version


def check_canary_health(
    stable_rate: float, canary_rate: float, threshold: float = 0.05
) -> bool:
    """Is the canary's behaviour close enough to the stable version's to keep rolling?

    The threshold is the entire content of this function, and 0.05 is calibrated against what
    a real regression looks like -- five percentage points, not fifty."""
    return abs(canary_rate - stable_rate) < threshold


# --- Written diagnoses (the two "diagnose before reading on" scenarios) ---

DIAGNOSE_MUTABLE_PROMPT = (
    "There is no version history here at all. 'v1' is just a mutable key in a dictionary, so "
    "publishing over it edits the stored text in place, and 'rolling back to v1' then reads "
    "whatever v1 currently points to -- which is the edited text, not the original. I would "
    "confirm it by checking whether the store has any record of the prior text: if the only "
    "thing that changed on rollback was a pointer, and the text behind it was overwritten "
    "weeks ago, the rollback is a structural no-op that reports success. The fix is not 'be "
    "more careful during deploys'. It is a data structure that makes the mistake impossible: "
    "an immutable version per publish, an append-only history, and a current_version pointer "
    "that is the only thing a rollback is allowed to move."
)

DIAGNOSE_LOOSE_THRESHOLD = (
    "The threshold itself is the bug. 0.5 was picked as a round, conservative-sounding "
    "number without ever being checked against what a real regression's magnitude actually "
    "looks like, so it only trips above a fifty-percentage-point swing. The regression here "
    "is about 32 points -- severe and obvious to anyone reading the numbers -- and it sailed "
    "straight through. Nothing crashed and no infrastructure alert fired, so the rollout "
    "'succeeded' by every signal except the one that mattered, which is the quiet-failure "
    "problem this chapter opened with. The fix is to calibrate the threshold against observed "
    "regression sizes rather than round numbers: something nearer 5 points, tight enough to "
    "catch a real regression and loose enough not to fire on ordinary sampling noise between "
    "two finite samples."
)
