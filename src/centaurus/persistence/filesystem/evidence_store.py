"""Filesystem implementation of EvidenceStore."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from centaurus.config import resolve_workspace

from centaurus.evidence.evidence import Evidence
from centaurus.persistence.evidence_store import EvidenceStore
from centaurus.persistence.serialization import evidence_payload, json_default

_SEQUENCE_PATTERN = re.compile(r"^(?P<investigation>.+)_(?P<sequence>\d+)-.+\.json$")
_SAFE_SOURCE = re.compile(r"[^A-Za-z0-9_.-]+")


class FilesystemEvidenceStore(EvidenceStore):
    """Persist normalized Evidence below investigations/<id>/evidences/normalized/."""

    def __init__(self, workspace: str | Path | None = None) -> None:
        self._workspace = resolve_workspace(workspace)

    @property
    def workspace(self) -> Path:
        return self._workspace

    def persist_evidence(self, investigation_id: str, evidence: Evidence) -> Path:
        self._validate_investigation_id(investigation_id)
        if not isinstance(evidence, Evidence):
            raise TypeError("evidence must be an Evidence instance")
        directory = self._workspace / "investigations" / investigation_id / "evidences" / "normalized"
        directory.mkdir(parents=True, exist_ok=True)
        source = self._source_name(evidence)
        payload = (json.dumps(evidence_payload(evidence), ensure_ascii=False, indent=2, default=json_default) + "\n").encode("utf-8")
        sequence = self._next_sequence(directory, investigation_id)
        while True:
            destination = directory / f"{investigation_id}_{sequence:04d}-{source}.json"
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
    def _source_name(evidence: Evidence) -> str:
        value = getattr(evidence.source, "value", evidence.source)
        result = _SAFE_SOURCE.sub("_", str(value)).strip("._-")
        if not result:
            raise ValueError("Evidence source cannot produce a valid filename")
        return result

    @staticmethod
    def _write_no_replace(destination: Path, payload: bytes) -> Path:
        temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent, prefix=".evidence-", suffix=".tmp", delete=False) as fh:
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
                try: temp.unlink()
                except FileNotFoundError: pass

    @staticmethod
    def _validate_investigation_id(investigation_id: str) -> None:
        if not isinstance(investigation_id, str) or not investigation_id:
            raise ValueError("investigation_id must be a non-empty string")
        if investigation_id in {".", ".."} or Path(investigation_id).name != investigation_id:
            raise ValueError("investigation_id cannot contain path separators")
