"""Persistence contract for Finding artifacts."""

from pathlib import Path
from typing import Protocol

from centaurus.finding.finding import Finding


class FindingStore(Protocol):
    """Infrastructure contract for persisting immutable Finding artifacts."""

    def persist_finding(self, investigation_id: str, finding: Finding) -> Path:
        """Persist one Finding artifact and return its path."""
        ...
