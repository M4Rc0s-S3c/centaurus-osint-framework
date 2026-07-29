"""
Investigation aggregate.
"""

from uuid import uuid4

from centaurus.investigation.investigation_status import (
    InvestigationStatus,
)


class Investigation:
    """
    Aggregate root representing an investigation.
    """

    def __init__(
        self,
        objective: str,
    ) -> None:
        """
        Create a new investigation.
        """

        self.id = str(uuid4())

        self.objective = objective

        self.status = InvestigationStatus.CREATED

        #
        # Results produced during execution.
        #

        self.results = []

    def mark_planned(self) -> None:
        """
        Mark the investigation as planned.
        """

        self.status = InvestigationStatus.PLANNED

    def mark_running(self) -> None:
        """
        Mark the investigation as running.
        """

        self.status = InvestigationStatus.RUNNING

    def mark_completed(self) -> None:
        """
        Mark the investigation as completed.
        """

        self.status = InvestigationStatus.COMPLETED

    def mark_failed(self) -> None:
        """
        Mark the investigation as failed.
        """

        self.status = InvestigationStatus.FAILED

    def register_results(
        self,
        results: list,
    ) -> None:
        """
        Register execution results produced during the investigation.
        """

        self.results.extend(results)