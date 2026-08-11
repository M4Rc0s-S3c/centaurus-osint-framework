"""Persistence contract for RawObservation artifacts."""

from pathlib import Path
from typing import Protocol

from centaurus.evidence.raw_observation import RawObservation


class RawObservationStore(Protocol):
    """
    Infrastructure contract for persisting RawObservation objects.

    The store receives the Investigation identity explicitly. It does not
    create or modify Investigation and it exposes no update/delete operation.
    """

    def persist_raw(
        self,
        investigation_id: str,
        observation: RawObservation,
    ) -> Path:
        """Persist one RawObservation and return its filesystem path."""

        ...
