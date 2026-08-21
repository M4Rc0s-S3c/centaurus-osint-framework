"""
Investigation aggregate.
"""

from uuid import uuid4

from centaurus.evidence.evidence import Evidence
from centaurus.finding.finding import Finding
from centaurus.report.report import Report
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
        *,
        target: str,
        intent: str,
        target_type: str = "DOMAIN",
    ) -> None:
        """
        Create a new Investigation from validated Target and Intent.
        """

        self.id = str(uuid4())

        self.target = target
        self.target_type = target_type.upper()
        self.intent = intent

        self.status = InvestigationStatus.CREATED

        #
        # Investigation owns Evidence.
        #

        self._evidences: list[Evidence] = []

        #
        # Investigation owns Findings.
        #

        self._findings: list[Finding] = []

        # Investigation owns one final Report.
        self._report: Report | None = None

    # ==========================================================
    # Public properties
    # ==========================================================

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

    @property
    def report(self) -> Report | None:
        """
        Return the final Report integrated into the Investigation, if any.
        """

        return self._report

    def add_report(
        self,
        report: Report,
    ) -> None:
        """
        Integrate the final Report into the Investigation.

        Core owns this integration boundary. A Report can only belong to the
        Investigation whose identifier it carries, and an Investigation can
        have at most one integrated Report.
        """

        if not isinstance(report, Report):
            raise TypeError(
                "Only Report instances can be added."
            )

        if report.investigation_id != self.id:
            raise ValueError(
                "Report belongs to a different Investigation."
            )

        if self._report is not None:
            raise InvalidInvestigationState(
                "Investigation already contains a Report."
            )

        self._report = report

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
        """Fail an Investigation from a controlled pre-terminal runtime state."""

        if self.status not in {
            InvestigationStatus.PLANNED,
            InvestigationStatus.RUNNING,
        }:
            raise InvalidInvestigationState(
                f"Cannot transition from "
                f"{self.status.value!r} "
                f"to {InvestigationStatus.FAILED.value!r}."
            )

        self.status = InvestigationStatus.FAILED

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
