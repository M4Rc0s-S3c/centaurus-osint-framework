"""Filesystem implementation of ExecutionFailureStore."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from centaurus.config import resolve_workspace

from centaurus.executor.execution import ExecutionFailure
from centaurus.persistence.execution_failure_store import ExecutionFailureStore
from centaurus.persistence.serialization import json_default


_SEQUENCE_PATTERN = re.compile(r"^(?P<investigation>.+)_(?P<sequence>\d+)-.+\.json$")
_SAFE_PLUGIN = re.compile(r"[^A-Za-z0-9_.-]+")


class FilesystemExecutionFailureStore(ExecutionFailureStore):
    """
    Persist operational task failures outside the knowledge pipeline.

    Physical layout::

        <workspace>/investigations/<investigation-id>/execution/failures/

    Files use::

        <investigation-id>_<sequence>-<plugin-id>.json
    """

    def __init__(self, workspace: str | Path | None = None) -> None:
        self._workspace = resolve_workspace(workspace)

    @property
    def workspace(self) -> Path:
        """Return the configured workspace root."""

        return self._workspace

    def persist_failure(
        self,
        investigation_id: str,
        failure: ExecutionFailure,
    ) -> Path:
        """Append one failure trace without creating domain knowledge."""

        self._validate_investigation_id(investigation_id)
        if not isinstance(failure, ExecutionFailure):
            raise TypeError("failure must be an ExecutionFailure instance")

        directory = (
            self._workspace
            / "investigations"
            / investigation_id
            / "execution"
            / "failures"
        )
        directory.mkdir(parents=True, exist_ok=True)

        plugin_id = _SAFE_PLUGIN.sub("_", failure.plugin_id).strip("._-")
        if not plugin_id:
            raise ValueError("ExecutionFailure plugin_id cannot produce a valid filename")

        payload = self._serialize(failure)
        sequence = self._next_sequence(directory, investigation_id)

        while True:
            destination = directory / (
                f"{investigation_id}_{sequence:04d}-{plugin_id}.json"
            )
            try:
                return self._write_atomically_without_overwrite(destination, payload)
            except FileExistsError:
                sequence += 1

    @staticmethod
    def _serialize(failure: ExecutionFailure) -> bytes:
        payload = {
            "task_index": failure.task_index,
            "plugin_id": failure.plugin_id,
            "parameters": failure.parameters,
            "category": failure.category.value,
            "error_type": failure.error_type,
            "message": failure.message,
            "occurred_at": failure.occurred_at,
        }
        return (
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                default=json_default,
            )
            + "\n"
        ).encode("utf-8")

    @staticmethod
    def _next_sequence(directory: Path, investigation_id: str) -> int:
        maximum = 0
        for path in directory.glob(f"{investigation_id}_*.json"):
            match = _SEQUENCE_PATTERN.match(path.name)
            if match is None or match.group("investigation") != investigation_id:
                continue
            try:
                maximum = max(maximum, int(match.group("sequence")))
            except ValueError:
                continue
        return maximum + 1

    @staticmethod
    def _write_atomically_without_overwrite(destination: Path, payload: bytes) -> Path:
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=destination.parent,
                prefix=".execution-failure-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temp_path = Path(temporary.name)
                temporary.write(payload)
                temporary.flush()
                os.fsync(temporary.fileno())

            os.link(temp_path, destination)

            if os.name != "nt":
                directory_fd = os.open(destination.parent, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)

            return destination
        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass

    @staticmethod
    def _validate_investigation_id(investigation_id: str) -> None:
        if not isinstance(investigation_id, str) or not investigation_id:
            raise ValueError("investigation_id must be a non-empty string")
        if investigation_id in {".", ".."}:
            raise ValueError("investigation_id cannot be a path traversal component")
        if Path(investigation_id).name != investigation_id:
            raise ValueError("investigation_id cannot contain path separators")
