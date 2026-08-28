"""Ollama implementation of the LLM provider contract."""

import logging
import time

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


logger = logging.getLogger("centaurus.llm.ollama_provider")
_PROVIDER = "ollama"
_ROLE = "analyst_assistance"


def _safe_counter(data: object, key: str) -> int | None:
    """Return a non-sensitive integer counter from an Ollama response."""

    if not isinstance(data, dict):
        return None
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value < 0:
        return None
    return value


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
            "OLLAMA_ANALYST_ASSISTANCE_TIMEOUT",
            300.0,
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
            # LLM #2 is the final model use in an Investigation. Release the
            # heavy model resource immediately after this request instead of
            # retaining it under Ollama's default keep-alive policy.
            "keep_alive": 0,
            "stream": False,
            "think": self._inference_profile.think,
            "format": PRESENTATION_SCHEMA,
            "options": self._inference_profile.options(),
        }

        client = self._client or httpx.Client(timeout=self._timeout)
        started = time.monotonic()
        try:
            response = client.post(
                f"{self._base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
        except httpx.ReadTimeout as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama",
                cause_type="ReadTimeout",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                duration_seconds=time.monotonic() - started,
            ) from exc
        except (httpx.ConnectTimeout, httpx.ConnectError, OSError) as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama",
                cause_type="ConnectError",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                duration_seconds=time.monotonic() - started,
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama",
                cause_type="HTTPStatusError",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                http_status=exc.response.status_code,
                duration_seconds=time.monotonic() - started,
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama",
                cause_type="TimeoutError",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                duration_seconds=time.monotonic() - started,
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(
                "Unable to obtain a response from Ollama",
                cause_type="TransportError",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                duration_seconds=time.monotonic() - started,
            ) from exc
        finally:
            if self._owns_client:
                client.close()

        elapsed = time.monotonic() - started
        http_status = getattr(response, "status_code", None)
        try:
            data = response.json()
        except ValueError as exc:
            raise LLMResponseError(
                "Ollama returned invalid JSON",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                http_status=http_status,
                duration_seconds=elapsed,
            ) from exc

        text = data.get("response") if isinstance(data, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise LLMResponseError(
                "Ollama returned an empty or invalid response",
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                http_status=http_status,
                duration_seconds=elapsed,
            )

        try:
            presentation = parse_analyst_presentation(report, text)
        except LLMResponseError as exc:
            raise LLMResponseError(
                str(exc),
                provider=_PROVIDER,
                role=_ROLE,
                timeout_seconds=self._timeout,
                http_status=http_status,
                duration_seconds=elapsed,
            ) from exc

        logger.info(
            "LLM provider completed provider=%s role=%s duration_seconds=%.3f "
            "http_status=%s prompt_eval_count=%s eval_count=%s",
            _PROVIDER,
            _ROLE,
            elapsed,
            http_status,
            _safe_counter(data, "prompt_eval_count"),
            _safe_counter(data, "eval_count"),
        )
        return render_analyst_presentation(report, presentation)
