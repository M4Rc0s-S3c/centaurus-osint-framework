"""
Evidence Value Object.

Represents normalized observed knowledge obtained during an investigation.

Evidence is immutable and belongs conceptually to exactly one Investigation,
although it does not keep a reference to it.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .evidence_source import EvidenceSource


@dataclass(frozen=True, slots=True)
class Evidence:
    """
    Immutable Value Object representing normalized observed knowledge.

    An Evidence contains:

    - the logical origin of the observation;
    - the normalized knowledge;
    - the collection timestamp.

    Evidence never contains raw tool output.
    Evidence never performs interpretation.
    """

    source: EvidenceSource
    data: dict[str, Any]
    collected_at: datetime