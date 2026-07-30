"""
RawObservation application object.

Represents the structured output produced by a plugin before it is
transformed into domain knowledge by the EvidenceManager.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .evidence_source import EvidenceSource


@dataclass(frozen=True, slots=True)
class RawObservation:
    """
    Immutable application object representing the output of a plugin.

    RawObservation is not part of the domain.

    It exists only as an intermediate representation between plugins
    and the EvidenceManager.
    """

    source: EvidenceSource
    data: dict[str, Any]
    collected_at: datetime