"""
Report domain value object.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from centaurus.finding.finding import Finding


@dataclass(frozen=True, slots=True)
class Report:
    """
    Immutable reporting result belonging to one Investigation.

    Report does not create or reinterpret domain knowledge. It preserves
    investigation context, analyst-request provenance, generation time and
    the Findings supplied for the reporting operation so their existing
    Rule/Evidence traceability remains available.
    """

    investigation_id: str
    generated_at: datetime
    target: str
    target_type: str
    intent: str
    findings: tuple[Finding, ...]
    analyst_question: str | None = None

    def __post_init__(self) -> None:
        """Validate the structural Report contract."""

        if not isinstance(self.investigation_id, str) or not self.investigation_id:
            raise ValueError("Report requires a non-empty investigation_id.")

        if not isinstance(self.generated_at, datetime):
            raise TypeError("Report generated_at must be a datetime instance.")
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("Report generated_at must be timezone-aware.")
        if self.generated_at.utcoffset() != timedelta(0):
            raise ValueError("Report generated_at must use UTC.")

        if not isinstance(self.target, str) or not self.target:
            raise ValueError("Report requires a non-empty target.")
        if not isinstance(self.target_type, str) or not self.target_type:
            raise ValueError("Report requires a non-empty target_type.")
        if self.target_type != self.target_type.upper():
            raise ValueError("Report target_type must be uppercase.")
        if not isinstance(self.intent, str) or not self.intent:
            raise ValueError("Report requires a non-empty intent.")

        if self.analyst_question is not None:
            if not isinstance(self.analyst_question, str):
                raise TypeError("Report analyst_question must be a string or None.")
            analyst_question = self.analyst_question.strip()
            if not analyst_question:
                raise ValueError(
                    "Report analyst_question must be non-empty when supplied."
                )
            object.__setattr__(self, "analyst_question", analyst_question)

        if not isinstance(self.findings, tuple):
            raise TypeError("Report findings must be a tuple.")

        if not all(isinstance(finding, Finding) for finding in self.findings):
            raise TypeError("Report findings must contain only Finding instances.")
