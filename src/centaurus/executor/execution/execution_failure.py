"""Operational failure record for one ExecutionTask."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import subprocess
from typing import Any, Iterator

import httpx

from centaurus.executor.execution.execution_task import ExecutionTask
from centaurus.exceptions import InvalidPluginOutputError


class ExecutionFailureCategory(str, Enum):
    """Small stable taxonomy for recoverable tool-execution failures."""

    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    UPSTREAM_ERROR = "upstream_error"
    INVALID_OUTPUT = "invalid_output"
    EXECUTION_ERROR = "execution_error"


@dataclass(frozen=True, slots=True)
class ExecutionFailure:
    """
    Immutable application-level trace of one failed ExecutionTask.

    ExecutionFailure is operational metadata. It is not RawObservation,
    Evidence, Finding or Report and therefore never enters the knowledge
    pipeline.
    """

    task_index: int
    plugin_id: str
    parameters: dict[str, Any]
    category: ExecutionFailureCategory
    error_type: str
    message: str
    occurred_at: datetime

    @classmethod
    def from_exception(
        cls,
        task_index: int,
        task: ExecutionTask,
        exc: Exception,
    ) -> "ExecutionFailure":
        """Translate one plugin-boundary exception into a stable failure record."""

        chain = tuple(cls._exception_chain(exc))
        root = chain[-1]
        message = next(
            (str(item).strip() for item in reversed(chain) if str(item).strip()),
            type(root).__name__,
        )

        return cls(
            task_index=task_index,
            plugin_id=task.plugin_id,
            parameters=dict(task.parameters),
            category=cls._classify(exc),
            error_type=type(root).__name__,
            message=message,
            occurred_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _exception_chain(exc: Exception) -> Iterator[BaseException]:
        """Yield an exception and its explicit/implicit causes without looping."""

        current: BaseException | None = exc
        seen: set[int] = set()

        while current is not None and id(current) not in seen:
            seen.add(id(current))
            yield current
            current = current.__cause__ or current.__context__

    @classmethod
    def _classify(cls, exc: Exception) -> ExecutionFailureCategory:
        """Classify known operational failure families without tool-specific logic."""

        chain = tuple(cls._exception_chain(exc))

        if any(
            isinstance(item, (TimeoutError, subprocess.TimeoutExpired, httpx.TimeoutException))
            for item in chain
        ):
            return ExecutionFailureCategory.TIMEOUT

        if any(
            isinstance(item, (FileNotFoundError, ModuleNotFoundError, httpx.ConnectError))
            for item in chain
        ):
            return ExecutionFailureCategory.UNAVAILABLE

        if any(isinstance(item, httpx.HTTPStatusError) for item in chain):
            return ExecutionFailureCategory.UPSTREAM_ERROR

        if any(
            isinstance(
                item,
                (
                    InvalidPluginOutputError,
                    json.JSONDecodeError,
                    UnicodeDecodeError,
                ),
            )
            for item in chain
        ):
            return ExecutionFailureCategory.INVALID_OUTPUT

        return ExecutionFailureCategory.EXECUTION_ERROR
