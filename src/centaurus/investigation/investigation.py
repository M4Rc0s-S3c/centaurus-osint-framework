"""
Investigation aggregate.
"""

from uuid import uuid4

from centaurus.investigation.exceptions import (
    InvalidInvestigationState,
)

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

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def mark_planned(self) -> None:
        """
        Mark the investigation as planned.
        """

        self._change_status(
            expected=InvestigationStatus.CREATED,
            new=InvestigationStatus.PLANNED,
        )

    def mark_running(self) -> None:
        """
        Mark the investigation as running.
        """

        self._change_status(
            expected=InvestigationStatus.PLANNED,
            new=InvestigationStatus.RUNNING,
        )

    def mark_completed(self) -> None:
        """
        Mark the investigation as completed.
        """

        self._change_status(
            expected=InvestigationStatus.RUNNING,
            new=InvestigationStatus.COMPLETED,
        )

    def mark_failed(self) -> None:
        """
        Mark the investigation as failed.
        """

        self._change_status(
            expected=InvestigationStatus.RUNNING,
            new=InvestigationStatus.FAILED,
        )

    # ==========================================================
    # Results
    # ==========================================================

    def register_results(
        self,
        results: list,
    ) -> None:
        """
        Register execution results produced during the investigation.
        """

        self.results.extend(results)

    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _change_status(
        self,
        expected: InvestigationStatus,
        new: InvestigationStatus,
    ) -> None:
        """
        Change the investigation status if the current state
        matches the expected lifecycle stage.
        """

        if self.status != expected:
            raise InvalidInvestigationState(
                f"Cannot transition from "
                f"{self.status.value!r} "
                f"to {new.value!r}."
            )

        self.status = new