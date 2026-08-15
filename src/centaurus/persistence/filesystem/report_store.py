"""Filesystem implementation of ReportStore."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from centaurus.report.report import Report
from centaurus.persistence.report_store import ReportStore
from centaurus.persistence.serialization import finding_payload, json_default


class FilesystemReportStore(ReportStore):
    """Persist the single final Report of an Investigation as report.json."""

    def __init__(self, workspace: str | Path | None = None) -> None:
        configured = os.environ.get("CENTAURUS_WORKSPACE")
        self._workspace = Path(workspace if workspace is not None else configured or "/workspace")

    @property
    def workspace(self) -> Path:
        return self._workspace

    def persist_report(self, investigation_id: str, report: Report) -> Path:
        self._validate_investigation_id(investigation_id)
        if not isinstance(report, Report):
            raise TypeError("report must be a Report instance")
        if report.investigation_id != investigation_id:
            raise ValueError("Report belongs to a different Investigation")
        directory = self._workspace / "investigations" / investigation_id / "reports"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / "report.json"
        payload = {
            "investigation_id": report.investigation_id,
            "findings": [finding_payload(f) for f in report.findings],
        }
        encoded = (json.dumps(payload, ensure_ascii=False, indent=2, default=json_default) + "\n").encode("utf-8")
        if destination.exists():
            raise FileExistsError(f"Report already persisted for Investigation {investigation_id}")
        temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=directory, prefix=".report-", suffix=".tmp", delete=False) as fh:
                temp = Path(fh.name)
                fh.write(encoded)
                fh.flush()
                os.fsync(fh.fileno())
            os.link(temp, destination)
            if os.name != "nt":
                fd = os.open(directory, os.O_RDONLY)
                try: os.fsync(fd)
                finally: os.close(fd)
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
