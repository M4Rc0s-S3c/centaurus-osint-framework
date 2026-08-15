"""
Report domain value object.
"""

from dataclasses import dataclass

from centaurus.finding.finding import Finding


@dataclass(frozen=True, slots=True)
class Report:
    """
    Immutable reporting result belonging to one Investigation.

    Report does not create or reinterpret domain knowledge. It preserves
    the Findings supplied for the reporting operation so their existing
    Rule/Evidence traceability remains available.
    """

    investigation_id: str
    findings: tuple[Finding, ...]

    def __post_init__(self) -> None:
        """Validate the minimal structural Report contract."""

        if not isinstance(self.investigation_id, str) or not self.investigation_id:
            raise ValueError("Report requires a non-empty investigation_id.")

        if not isinstance(self.findings, tuple):
            raise TypeError("Report findings must be a tuple.")

        if not all(isinstance(finding, Finding) for finding in self.findings):
            raise TypeError("Report findings must contain only Finding instances.")
