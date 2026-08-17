"""Filesystem implementation of RawObservationStore."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from centaurus.evidence.raw_observation import RawObservation
from centaurus.persistence.raw_observation_store import RawObservationStore


_SEQUENCE_PATTERN = re.compile(r"^(?P<investigation>.+)_(?P<sequence>\d+)-.+\.json$")
_SAFE_SOURCE = re.compile(r"[^A-Za-z0-9_.-]+")


class FilesystemRawObservationStore(RawObservationStore):
    """
    Persist RawObservation artifacts below the configured workspace.

    Physical layout::

        <workspace>/investigations/<investigation-id>/evidences/raw/

    Files use the contract-defined naming convention::

        <investigation-id>_<sequence>-<source>.json
    """

    def __init__(self, workspace: str | Path | None = None) -> None:
        """
        Create a filesystem-backed RAW store.

        If no workspace is supplied, CENTAURUS_WORKSPACE is used when set;
        otherwise /workspace is the runtime default defined by STORAGE.md.
        """

        configured_workspace = os.environ.get("CENTAURUS_WORKSPACE")
        self._workspace = Path(
            workspace if workspace is not None else configured_workspace or "/workspace"
        )

    @property
    def workspace(self) -> Path:
        """Return the configured workspace root."""

        return self._workspace

    def persist_raw(
        self,
        investigation_id: str,
        observation: RawObservation,
    ) -> Path:
        """Persist one RAW observation without overwriting an existing artifact."""

        self._validate_investigation_id(investigation_id)
        if not isinstance(observation, RawObservation):
            raise TypeError("observation must be a RawObservation instance")

        raw_directory = (
            self._workspace
            / "investigations"
            / investigation_id
            / "evidences"
            / "raw"
        )
        raw_directory.mkdir(parents=True, exist_ok=True)

        source = self._source_name(observation)
        payload = self._serialize(observation)

        sequence = self._next_sequence(raw_directory, investigation_id)

        while True:
            destination = raw_directory / (
                f"{investigation_id}_{sequence:04d}-{source}.json"
            )
            try:
                return self._write_atomically_without_overwrite(
                    destination,
                    payload,
                )
            except FileExistsError:
                sequence += 1

    def _next_sequence(
        self,
        raw_directory: Path,
        investigation_id: str,
    ) -> int:
        """Return the next sequence number for an Investigation."""

        maximum = 0
        for path in raw_directory.glob(f"{investigation_id}_*.json"):
            match = _SEQUENCE_PATTERN.match(path.name)
            if match is None or match.group("investigation") != investigation_id:
                continue
            try:
                maximum = max(maximum, int(match.group("sequence")))
            except ValueError:
                continue

        return maximum + 1

    @staticmethod
    def _source_name(observation: RawObservation) -> str:
        """Return a filesystem-safe source name from the observation."""

        source = getattr(observation.source, "value", observation.source)
        source_name = _SAFE_SOURCE.sub("_", str(source)).strip("._-")
        if not source_name:
            raise ValueError("RawObservation source cannot produce a valid filename")
        return source_name

    @staticmethod
    def _serialize(observation: RawObservation) -> bytes:
        """Serialize a RawObservation as UTF-8 JSON."""

        payload = {
            "source": getattr(observation.source, "value", observation.source),
            "collected_at": observation.collected_at,
            "data": observation.data,
        }

        return (
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                default=FilesystemRawObservationStore._json_default,
            )
            + "\n"
        ).encode("utf-8")

    @staticmethod
    def _json_default(value: Any) -> str:
        """Encode values not natively supported by JSON."""

        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

    @staticmethod
    def _write_atomically_without_overwrite(
        destination: Path,
        payload: bytes,
    ) -> Path:
        """
        Write a payload atomically and fail if the destination already exists.

        The temporary file is created in the destination directory. A hard-link
        creation is then used as the atomic, no-replace publication step on the
        same filesystem. This prevents a concurrent writer from being able to
        replace an existing RAW artifact.
        """

        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=destination.parent,
                prefix=".raw-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temp_path = Path(temporary.name)
                temporary.write(payload)
                temporary.flush()
                os.fsync(temporary.fileno())

            os.link(temp_path, destination)

            # POSIX filesystems allow fsync() on the containing directory to
            # strengthen rename/link durability. Windows does not expose
            # directory handles through os.open() in the same way, so attempting
            # the POSIX durability step raises PermissionError on Windows.
            # The no-replace publication itself is provided by os.link(), and
            # the temporary file contents are already flushed before publication.
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
        """Reject empty or path-like Investigation identifiers."""

        if not isinstance(investigation_id, str) or not investigation_id:
            raise ValueError("investigation_id must be a non-empty string")
        if investigation_id in {".", ".."}:
            raise ValueError("investigation_id cannot be a path traversal component")
        if Path(investigation_id).name != investigation_id:
            raise ValueError("investigation_id cannot contain path separators")
