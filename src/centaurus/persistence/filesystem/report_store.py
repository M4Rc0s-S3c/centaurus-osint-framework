"""Filesystem implementation of ReportStore."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from centaurus.config import resolve_workspace

from centaurus.report.report import Report
from centaurus.persistence.report_markdown import render_report_markdown
from centaurus.persistence.report_store import ReportStore
from centaurus.persistence.serialization import finding_payload, json_default


class FilesystemReportStore(ReportStore):
    """Persist the final Report as authoritative JSON plus Markdown projection."""

    def __init__(self, workspace: str | Path | None = None) -> None:
        self._workspace = resolve_workspace(workspace)

    @property
    def workspace(self) -> Path:
        return self._workspace

    def persist_report(self, investigation_id: str, report: Report) -> Path:
        """Persist ``report.json`` and its deterministic ``report.md`` projection.

        The returned path always identifies ``report.json``, which remains the
        authoritative persisted Report representation. Neither file contains
        LLM-generated narrative.
        """

        self._validate_investigation_id(investigation_id)
        if not isinstance(report, Report):
            raise TypeError("report must be a Report instance")
        if report.investigation_id != investigation_id:
            raise ValueError("Report belongs to a different Investigation")

        directory = self._workspace / "investigations" / investigation_id / "reports"
        directory.mkdir(parents=True, exist_ok=True)

        json_destination = directory / "report.json"
        markdown_destination = directory / "report.md"
        if json_destination.exists() or markdown_destination.exists():
            raise FileExistsError(
                f"Report already persisted for Investigation {investigation_id}"
            )

        payload = {
            "investigation_id": report.investigation_id,
            "generated_at": report.generated_at,
            "target": report.target,
            "target_type": report.target_type,
            "intent": report.intent,
            "analyst_question": report.analyst_question,
            "findings": [
                {
                    "finding_ref": f"F-{index:03d}",
                    **finding_payload(finding),
                }
                for index, finding in enumerate(report.findings, start=1)
            ],
        }
        json_encoded = (
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                default=json_default,
            )
            + "\n"
        ).encode("utf-8")
        markdown_encoded = render_report_markdown(report).encode("utf-8")

        created: list[Path] = []
        try:
            self._persist_exclusive(json_destination, json_encoded)
            created.append(json_destination)
            self._persist_exclusive(markdown_destination, markdown_encoded)
            created.append(markdown_destination)
            return json_destination
        except Exception:
            for destination in reversed(created):
                try:
                    destination.unlink()
                except FileNotFoundError:
                    pass
            raise

    @staticmethod
    def _persist_exclusive(destination: Path, encoded: bytes) -> None:
        """Atomically create one artifact without replacing an existing file."""

        directory = destination.parent
        temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=directory,
                prefix=f".{destination.stem}-",
                suffix=".tmp",
                delete=False,
            ) as file_handle:
                temp = Path(file_handle.name)
                file_handle.write(encoded)
                file_handle.flush()
                os.fsync(file_handle.fileno())

            os.link(temp, destination)
            if os.name != "nt":
                descriptor = os.open(directory, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
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
        if (
            investigation_id in {".", ".."}
            or Path(investigation_id).name != investigation_id
        ):
            raise ValueError("investigation_id cannot contain path separators")
