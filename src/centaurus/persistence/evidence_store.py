"""Persistence contract for normalized Evidence artifacts."""

from pathlib import Path
from typing import Protocol

from centaurus.evidence.evidence import Evidence


class EvidenceStore(Protocol):
    """Infrastructure contract for persisting normalized Evidence."""

    def persist_evidence(self, investigation_id: str, evidence: Evidence) -> Path:
        """Persist one Evidence artifact and return its path."""
        ...
