"""
Report Manager component.
"""

from centaurus.finding.finding import Finding
from centaurus.investigation.investigation import Investigation
from centaurus.report.report import Report


class ReportManager:
    """
    Generate immutable Reports from Findings supplied by Core.

    ReportManager does not modify Investigation or Findings, apply Rules,
    inspect Evidence independently, or perform analyst assistance or presentation.
    """

    def generate(
        self,
        investigation: Investigation,
        findings: tuple[Finding, ...],
    ) -> Report:
        """
        Generate a Report for an Investigation from the supplied Findings.

        The supplied Findings are preserved in their original order. An empty
        Findings collection is valid and produces a Report with no Findings.
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

        return Report(
            investigation_id=investigation.id,
            findings=findings,
        )
