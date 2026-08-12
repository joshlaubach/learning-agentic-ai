"""Lightweight span/trace logger for multi-agent pipelines — no external account needed.

Built in Chapter 2 (curriculum/02_control_flow.ipynb), where it's first used to log each
named agent's (Jack/Bob/Mike) hop duration in the control-flow pipeline, and reused by any
later chapter that wants a readable trace instead of scattered print statements.

Two ways to record a hop:
  - `tracer.span(name, **metadata)` as a context manager, measuring real wall-clock time —
    for genuine work (e.g. an actual API call).
  - `tracer.record(name, duration_ms, **metadata)` for a hop whose duration is a simulated
    value you want logged rather than actually slept through — used for teaching realistic
    per-hop latency numbers without slowing down notebook execution or CI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Span:
    name: str
    start: float
    end: float | None = None
    duration_ms_override: float | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        if self.duration_ms_override is not None:
            return self.duration_ms_override
        end = self.end if self.end is not None else time.perf_counter()
        return (end - self.start) * 1000


class _SpanContext:
    def __init__(self, tracer: "Tracer", name: str, metadata: dict):
        self._tracer = tracer
        self._name = name
        self._metadata = metadata
        self.span: Span | None = None

    def __enter__(self) -> Span:
        self.span = self._tracer.start_span(self._name, **self._metadata)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._tracer.end_span(self.span)
        return False


class Tracer:
    """An in-memory, append-only list of spans -- no network calls, no external service."""

    def __init__(self):
        self.spans: list[Span] = []

    def start_span(self, name: str, **metadata) -> Span:
        span = Span(name=name, start=time.perf_counter(), metadata=metadata)
        self.spans.append(span)
        return span

    def end_span(self, span: Span) -> Span:
        span.end = time.perf_counter()
        return span

    def span(self, name: str, **metadata) -> _SpanContext:
        """Context manager form: `with tracer.span("Jack", role="planner"): ...`"""
        return _SpanContext(self, name, metadata)

    def record(self, name: str, duration_ms: float, **metadata) -> Span:
        """Log a hop with an explicit (possibly simulated) duration rather than measuring
        real wall-clock time."""
        now = time.perf_counter()
        span = Span(name=name, start=now, end=now, duration_ms_override=duration_ms, metadata=metadata)
        self.spans.append(span)
        return span

    def total_ms(self) -> float:
        return sum(s.duration_ms for s in self.spans)

    def slowest(self) -> Span | None:
        return max(self.spans, key=lambda s: s.duration_ms) if self.spans else None

    def summary(self) -> list[dict]:
        return [
            {"name": s.name, "duration_ms": round(s.duration_ms, 2), **s.metadata}
            for s in self.spans
        ]

    def print_trace(self) -> None:
        for s in self.spans:
            meta = f" {s.metadata}" if s.metadata else ""
            print(f"[{s.name}] {s.duration_ms:.1f}ms{meta}")

    def reset(self) -> None:
        self.spans.clear()
