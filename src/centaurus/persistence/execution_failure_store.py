"""Persistence contract for operational ExecutionFailure artifacts."""

from pathlib import Path
from typing import Protocol

from centaurus.executor.execution import ExecutionFailure


class ExecutionFailureStore(Protocol):
    """Infrastructure contract for appending task-failure traces."""

    def persist_failure(
        self,
        investigation_id: str,
        failure: ExecutionFailure,
    ) -> Path:
        """Persist one ExecutionFailure and return its filesystem path."""

        ...
