"""
Investigation lifecycle states.
"""

from enum import Enum


class InvestigationStatus(Enum):
    """
    Lifecycle states of an Investigation aggregate.
    """

    CREATED = "created"

    PLANNED = "planned"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"