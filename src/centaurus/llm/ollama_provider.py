"""Ollama implementation of the LLM provider contract."""

import httpx

from centaurus.config import configured_positive_float, configured_text

from centaurus.report.report import Report
from centaurus.llm.exceptions import LLMProviderError, LLMResponseError
from centaurus.llm.inference_profile import (
    ANALYST_ASSISTANCE_INFERENCE_PROFILE,
    OllamaInferenceProfile,
)
from centaurus.llm.prompt import SYSTEM_PROMPT
from centaurus.llm.presentation import (
    PRESENTATION_SCHEMA,
    parse_analyst_presentation,
    render_analyst_presentation,
)
from centaurus.llm.serialization import serialize_report


class OllamaProvider:
    """Generate grounded Report analyst assistance through local Ollama."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        client: httpx.Client | None = None,
        inference_profile: OllamaInferenceProfile | None = None,
    ) -> None:
        self._base_url = configured_text(
            base_url,
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ).rstrip("/")
        self._model = configured_text(model, "OLLAMA_MODEL", "qwen3:4b")
        self._timeout = configured_positive_float(
            timeout,
            "OLLAMA_TIMEOUT",
            60.0,
        )
        self._client = client
        self._owns_client = client is None
        self._inference_profile = (
            inference_profile or ANALYST_ASSISTANCE_INFERENCE_PROFILE
        )

    def generate(self, report: Report) -> str:
        """Generate and validate a grounded analyst-assistance presentation."""

        if not isinstance(report, Report):
            raise TypeError("report must be a Report instance")

        payload = {
            "model": self._model,
            "system": SYSTEM_PROMPT,
            "prompt": serialize_report(report),
            "stream": False,
            "think": self._inference_profile.think,
            "format": PRESENTATION_SCHEMA,
            "options": self._inference_profile.options(),
        }

        client = self._client or httpx.Client(timeout=self._timeout)
        try:
            response = client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
        except (httpx.HTTPError, OSError) as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama"
            ) from exc
        finally:
            if self._owns_client:
                client.close()

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMResponseError("Ollama returned invalid JSON") from exc

        text = data.get("response") if isinstance(data, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise LLMResponseError(
                "Ollama returned an empty or invalid response"
            )

        presentation = parse_analyst_presentation(report, text)
        return render_analyst_presentation(report, presentation)
