"""Infrastructure contract for LLM providers."""

from typing import Protocol

from centaurus.report.report import Report


class LLMProvider(Protocol):
    """Technical contract implemented by concrete LLM providers."""

    def generate(self, report: Report) -> str:
        """Generate a linguistic presentation for a Report."""
