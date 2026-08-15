"""Persistence contract for Report artifacts."""

from pathlib import Path
from typing import Protocol

from centaurus.report.report import Report


class ReportStore(Protocol):
    """Infrastructure contract for persisting the final Report."""

    def persist_report(self, investigation_id: str, report: Report) -> Path:
        """Persist one Report artifact and return its path."""
        ...
