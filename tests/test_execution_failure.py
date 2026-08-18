"""Tests for the framework-level ExecutionFailure contract."""

from datetime import timezone
import json
import subprocess

import httpx
import pytest

from centaurus.executor.execution import (
    ExecutionFailure,
    ExecutionFailureCategory,
    ExecutionTask,
)
from centaurus.exceptions import (
    InvalidPluginOutputError,
    PluginExecutionError,
)


def _wrapped(root: Exception) -> PluginExecutionError:
    try:
        raise root
    except Exception as exc:
        try:
            raise PluginExecutionError("tool", str(exc) or type(exc).__name__) from exc
        except PluginExecutionError as wrapped:
            return wrapped


@pytest.mark.parametrize(
    ("root", "expected"),
    [
        (TimeoutError("slow"), ExecutionFailureCategory.TIMEOUT),
        (
            subprocess.TimeoutExpired(cmd=["tool"], timeout=5),
            ExecutionFailureCategory.TIMEOUT,
        ),
        (FileNotFoundError("missing"), ExecutionFailureCategory.UNAVAILABLE),
        (
            httpx.ConnectError("connect failed"),
            ExecutionFailureCategory.UNAVAILABLE,
        ),
        (
            httpx.HTTPStatusError(
                "bad status",
                request=httpx.Request("GET", "https://example.invalid"),
                response=httpx.Response(
                    503,
                    request=httpx.Request("GET", "https://example.invalid"),
                ),
            ),
            ExecutionFailureCategory.UPSTREAM_ERROR,
        ),
        (
            json.JSONDecodeError("bad json", "{", 0),
            ExecutionFailureCategory.INVALID_OUTPUT,
        ),
        (
            InvalidPluginOutputError("wrong type"),
            ExecutionFailureCategory.INVALID_OUTPUT,
        ),
        (RuntimeError("generic"), ExecutionFailureCategory.EXECUTION_ERROR),
    ],
)
def test_execution_failure_classifies_root_cause(root, expected) -> None:
    task = ExecutionTask("tool", {"domain": "example.com"})

    failure = ExecutionFailure.from_exception(3, task, _wrapped(root))

    assert failure.task_index == 3
    assert failure.plugin_id == "tool"
    assert failure.parameters == {"domain": "example.com"}
    assert failure.category is expected
    assert failure.error_type == type(root).__name__
    assert failure.occurred_at.tzinfo == timezone.utc


def test_execution_failure_copies_task_parameters() -> None:
    task = ExecutionTask("dnsrecon", {"domain": "example.com", "mode": "dmarc"})
    failure = ExecutionFailure.from_exception(
        4,
        task,
        _wrapped(RuntimeError("failed")),
    )

    task.parameters["mode"] = "standard"

    assert failure.parameters == {"domain": "example.com", "mode": "dmarc"}
