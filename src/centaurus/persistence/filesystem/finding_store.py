"""Filesystem implementation of FindingStore."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from centaurus.finding.finding import Finding
from centaurus.persistence.finding_store import FindingStore
from centaurus.persistence.serialization import finding_payload, json_default

_SEQUENCE_PATTERN = re.compile(r"^(?P<investigation>.+)_(?P<sequence>\d+)-.+\.json$")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")


class FilesystemFindingStore(FindingStore):
    """Persist immutable Findings below investigations/<id>/findings/."""

    def __init__(self, workspace: str | Path | None = None) -> None:
        configured = os.environ.get("CENTAURUS_WORKSPACE")
        self._workspace = Path(workspace if workspace is not None else configured or "/workspace")

    @property
    def workspace(self) -> Path:
        return self._workspace

    def persist_finding(self, investigation_id: str, finding: Finding) -> Path:
        self._validate_investigation_id(investigation_id)
        if not isinstance(finding, Finding):
            raise TypeError("finding must be a Finding instance")

        directory = self._workspace / "investigations" / investigation_id / "findings"
        directory.mkdir(parents=True, exist_ok=True)
        rule_id = self._safe_name(finding.rule.id)
        payload = (
            json.dumps(finding_payload(finding), ensure_ascii=False, indent=2, default=json_default)
            + "\n"
        ).encode("utf-8")
        sequence = self._next_sequence(directory, investigation_id)
        while True:
            destination = directory / f"{investigation_id}_{sequence:04d}-{rule_id}.json"
            try:
                return self._write_no_replace(destination, payload)
            except FileExistsError:
                sequence += 1

    @staticmethod
    def _next_sequence(directory: Path, investigation_id: str) -> int:
        maximum = 0
        for path in directory.glob(f"{investigation_id}_*.json"):
            match = _SEQUENCE_PATTERN.match(path.name)
            if match and match.group("investigation") == investigation_id:
                maximum = max(maximum, int(match.group("sequence")))
        return maximum + 1

    @staticmethod
    def _safe_name(value: object) -> str:
        result = _SAFE_NAME.sub("_", str(value)).strip("._-")
        if not result:
            raise ValueError("Finding rule id cannot produce a valid filename")
        return result

    @staticmethod
    def _write_no_replace(destination: Path, payload: bytes) -> Path:
        temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent, prefix=".finding-", suffix=".tmp", delete=False
            ) as fh:
                temp = Path(fh.name)
                fh.write(payload)
                fh.flush()
                os.fsync(fh.fileno())
            os.link(temp, destination)
            if os.name != "nt":
                fd = os.open(destination.parent, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            return destination
        finally:
            if temp is not None:
                try:
                    temp.unlink()
                except FileNotFoundError:
                    pass

    @staticmethod
    def _validate_investigation_id(investigation_id: str) -> None:
        if not isinstance(investigation_id, str) or not investigation_id:
            raise ValueError("investigation_id must be a non-empty string")
        if investigation_id in {".", ".."} or Path(investigation_id).name != investigation_id:
            raise ValueError("investigation_id cannot contain path separators")
