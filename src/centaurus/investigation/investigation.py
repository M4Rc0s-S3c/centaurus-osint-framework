"""
Investigation aggregate.
"""

from uuid import uuid4

from centaurus.evidence.evidence import Evidence
from centaurus.finding.finding import Finding
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
        objective: str | None = None,
        *,
        target: str | None = None,
        intent: str | None = None,
    ) -> None:
        """
        Create a new Investigation.

        During the migration phase both constructors are accepted:

            Investigation(objective="example.org")

        and

            Investigation(
                target="example.org",
                intent="whois",
            )
        """

        self.id = str(uuid4())

        #
        # Transitional compatibility.
        #

        if objective is not None:

            self.objective = objective

            self.target = objective

            self.intent = "generic"

        else:

            if target is None or intent is None:
                raise ValueError(
                    "Either 'objective' or both "
                    "'target' and 'intent' must be provided."
                )

            self.target = target
            self.intent = intent
            self.objective = f"{intent}:{target}"

        self.status = InvestigationStatus.CREATED

        #
        # Investigation owns Evidence.
        #

        self._evidences: list[Evidence] = []

        #
        # Investigation owns Findings.
        #

        self._findings: list[Finding] = []

        #
        # Existing execution results.
        #

        self._results = []

    # ==========================================================
    # Public properties
    # ==========================================================

    @property
    def results(self) -> tuple:
        """
        Immutable execution results.
        """

        return tuple(self._results)

    @property
    def evidences(self) -> tuple[Evidence, ...]:
        """
        Immutable Evidence collection.
        """

        return tuple(self._evidences)

    @property
    def findings(self) -> tuple[Finding, ...]:
        """
        Immutable Finding collection.
        """

        return tuple(self._findings)

    #
    # Transitional compatibility.
    #

    @property
    def evidence(self) -> tuple[Evidence, ...]:
        """
        Backwards-compatible alias.
        """

        return self.evidences

    # ==========================================================
    # Domain operations
    # ==========================================================

    def add_evidence(
        self,
        evidence: Evidence,
    ) -> None:
        """
        Store one Evidence inside the Investigation.
        """

        if not isinstance(evidence, Evidence):
            raise TypeError(
                "Only Evidence instances can be added."
            )

        self._evidences.append(evidence)

    def add_finding(
        self,
        finding: Finding,
    ) -> None:
        """
        Store one Finding inside the Investigation.
        """

        if not isinstance(finding, Finding):
            raise TypeError(
                "Only Finding instances can be added."
            )

        self._findings.append(finding)

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def mark_planned(self) -> None:

        self._change_status(
            expected=InvestigationStatus.CREATED,
            new=InvestigationStatus.PLANNED,
        )

    def mark_running(self) -> None:

        self._change_status(
            expected=InvestigationStatus.PLANNED,
            new=InvestigationStatus.RUNNING,
        )

    def mark_completed(self) -> None:

        self._change_status(
            expected=InvestigationStatus.RUNNING,
            new=InvestigationStatus.COMPLETED,
        )

    def mark_failed(self) -> None:

        self._change_status(
            expected=InvestigationStatus.RUNNING,
            new=InvestigationStatus.FAILED,
        )

    # ==========================================================
    # Execution results
    # ==========================================================

    def register_results(
        self,
        results: list,
    ) -> None:

        self._results.extend(results)

    # ==========================================================
    # Internal helpers
    # ==========================================================

    def _change_status(
        self,
        expected: InvestigationStatus,
        new: InvestigationStatus,
    ) -> None:

        if self.status != expected:
            raise InvalidInvestigationState(
                f"Cannot transition from "
                f"{self.status.value!r} "
                f"to {new.value!r}."
            )

        self.status = new