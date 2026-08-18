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
