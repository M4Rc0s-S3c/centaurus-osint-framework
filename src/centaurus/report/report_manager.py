"""
Report Manager component.
"""

from datetime import datetime, timezone
from typing import Callable

from centaurus.finding.finding import Finding
from centaurus.investigation.investigation import Investigation
from centaurus.report.report import Report


def _utc_now() -> datetime:
    """Return the current UTC time for Report generation."""

    return datetime.now(timezone.utc)


class ReportManager:
    """
    Generate immutable Reports from Findings supplied by Core.

    ReportManager does not modify Investigation or Findings, apply Rules,
    inspect Evidence independently, or perform analyst assistance or presentation.
    """

    def __init__(
        self,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or _utc_now

    def generate(
        self,
        investigation: Investigation,
        findings: tuple[Finding, ...],
        *,
        analyst_question: str | None = None,
    ) -> Report:
        """
        Generate a Report for an Investigation from the supplied Findings.

        The supplied Findings are preserved in their original order. An empty
        Findings collection is valid and produces a Report with no Findings.
        ``analyst_question`` is optional immutable request provenance; it never
        changes Target, Intent, Rules, Findings or Evidence.
        """

        if not isinstance(investigation, Investigation):
            raise TypeError(
                "Expected investigation to be an Investigation instance."
            )

        if not isinstance(findings, tuple):
            raise TypeError(
                "Expected findings to be a tuple of Finding instances."
            )

        for finding in findings:
            if not isinstance(finding, Finding):
                raise TypeError(
                    "Expected all findings to be Finding instances."
                )

            if not any(
                finding is investigation_finding
                for investigation_finding in investigation.findings
            ):
                raise ValueError(
                    "All Findings must belong to the supplied Investigation."
                )

        if analyst_question is not None:
            if not isinstance(analyst_question, str):
                raise TypeError("analyst_question must be a string or None")
            analyst_question = analyst_question.strip()
            if not analyst_question:
                raise ValueError(
                    "analyst_question must be non-empty when supplied"
                )

        generated_at = self._clock()
        if isinstance(generated_at, datetime):
            generated_at = generated_at.replace(microsecond=0)

        return Report(
            investigation_id=investigation.id,
            generated_at=generated_at,
            target=investigation.target,
            target_type=investigation.target_type,
            intent=investigation.intent,
            findings=findings,
            analyst_question=analyst_question,
        )
