"""Tests for filesystem persistence of operational execution failures."""

from datetime import datetime, timezone
import json

import pytest

from centaurus.executor.execution import ExecutionFailure, ExecutionFailureCategory
from centaurus.persistence.filesystem import FilesystemExecutionFailureStore


def _failure(plugin_id="crtsh", task_index=6) -> ExecutionFailure:
    return ExecutionFailure(
        task_index=task_index,
        plugin_id=plugin_id,
        parameters={"domain": "example.com"},
        category=ExecutionFailureCategory.TIMEOUT,
        error_type="ReadTimeout",
        message="The read operation timed out",
        occurred_at=datetime(2026, 8, 18, 8, 30, tzinfo=timezone.utc),
    )


def test_execution_failure_store_persists_outside_knowledge_directories(tmp_path) -> None:
    store = FilesystemExecutionFailureStore(tmp_path)

    path = store.persist_failure("INV-1", _failure())

    assert path == (
        tmp_path
        / "investigations"
        / "INV-1"
        / "execution"
        / "failures"
        / "INV-1_0001-crtsh.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == {
        "task_index": 6,
        "plugin_id": "crtsh",
        "parameters": {"domain": "example.com"},
        "category": "timeout",
        "error_type": "ReadTimeout",
        "message": "The read operation timed out",
        "occurred_at": "2026-08-18T08:30:00+00:00",
    }
    root = tmp_path / "investigations" / "INV-1"
    assert not (root / "evidences").exists()
    assert not (root / "findings").exists()
    assert not (root / "reports").exists()


def test_execution_failure_store_appends_sequence(tmp_path) -> None:
    store = FilesystemExecutionFailureStore(tmp_path)

    first = store.persist_failure("INV-1", _failure("dnsrecon", 3))
    second = store.persist_failure("INV-1", _failure("dnsrecon", 4))

    assert first.name == "INV-1_0001-dnsrecon.json"
    assert second.name == "INV-1_0002-dnsrecon.json"


def test_execution_failure_store_rejects_wrong_type(tmp_path) -> None:
    store = FilesystemExecutionFailureStore(tmp_path)
    with pytest.raises(TypeError, match="ExecutionFailure"):
        store.persist_failure("INV-1", object())


@pytest.mark.parametrize("investigation_id", ["", ".", "..", "../INV", "a/b"])
def test_execution_failure_store_rejects_invalid_investigation_id(
    tmp_path,
    investigation_id,
) -> None:
    store = FilesystemExecutionFailureStore(tmp_path)
    with pytest.raises(ValueError):
        store.persist_failure(investigation_id, _failure())
