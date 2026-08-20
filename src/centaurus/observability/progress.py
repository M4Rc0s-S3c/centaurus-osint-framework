"""Ephemeral runtime-progress contract for user-facing execution feedback.

Runtime progress is operational presentation metadata.  It never enters the
Investigation aggregate, the knowledge pipeline, or persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RuntimeProgressEvent:
    """One immutable, ephemeral runtime-progress update."""

    message: str
    kind: str = "phase"
    task_index: int | None = None
    task_total: int | None = None
    plugin_id: str | None = None
    task_variant: str | None = None
    failure_category: str | None = None


class RuntimeProgressReporter(Protocol):
    """Minimal presentation-agnostic progress boundary."""

    def start(self) -> None:
        """Start one user-visible progress session."""

    def publish(self, event: RuntimeProgressEvent) -> None:
        """Publish one ephemeral runtime-progress event."""

    def stop(self) -> None:
        """Stop the current progress session."""


class NullRuntimeProgressReporter:
    """No-op reporter used outside interactive presentation adapters."""

    def start(self) -> None:
        return None

    def publish(self, event: RuntimeProgressEvent) -> None:
        return None

    def stop(self) -> None:
        return None
