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

    def add_result(
        self,
        result: dict,
    ) -> None:
        """
        Store one execution result.
        """

        self.results.append(result)