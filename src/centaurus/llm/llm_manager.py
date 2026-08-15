"""Application-level LLM manager."""

from centaurus.report.report import Report
from centaurus.llm.ollama_provider import OllamaProvider
from centaurus.llm.provider import LLMProvider


class LLMManager:
    """Coordinate linguistic presentation without creating domain knowledge."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or OllamaProvider()

    def generate(self, report: Report) -> str:
        """Present a Report linguistically through the configured provider."""

        if not isinstance(report, Report):
            raise TypeError("report must be a Report instance")

        return self._provider.generate(report)
