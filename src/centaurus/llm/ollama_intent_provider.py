"""Ollama provider for the LLM interpretation instance."""

import json

import httpx

from centaurus.config import configured_positive_float, configured_text

from centaurus.llm.exceptions import LLMProviderError, LLMResponseError
from centaurus.llm.inference_profile import (
    INTERPRETATION_INFERENCE_PROFILE,
    OllamaInferenceProfile,
)
from centaurus.llm.interpretation_prompt import (
    INTERPRETATION_SCHEMA,
    INTERPRETATION_SYSTEM_PROMPT,
)
from centaurus.request.structured_request import SUPPORTED_INTENTS


class OllamaIntentProvider:
    """Classify user language through a dedicated Ollama configuration."""

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
        if timeout is not None:
            self._timeout = configured_positive_float(
                timeout,
                "OLLAMA_INTERPRETATION_TIMEOUT",
                60.0,
            )
        else:
            inherited_timeout = configured_positive_float(
                None,
                "OLLAMA_TIMEOUT",
                60.0,
            )
            self._timeout = configured_positive_float(
                None,
                "OLLAMA_INTERPRETATION_TIMEOUT",
                inherited_timeout,
            )
        self._client = client
        self._owns_client = client is None
        self._inference_profile = (
            inference_profile or INTERPRETATION_INFERENCE_PROFILE
        )

    def classify_intent(self, user_input: str) -> str:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        payload = {
            "model": self._model,
            "system": INTERPRETATION_SYSTEM_PROMPT,
            "prompt": user_input.strip(),
            "stream": False,
            "think": self._inference_profile.think,
            "format": INTERPRETATION_SCHEMA,
            "options": self._inference_profile.options(),
        }

        client = self._client or httpx.Client(timeout=self._timeout)
        try:
            response = client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
        except (httpx.HTTPError, OSError) as exc:
            raise LLMProviderError(
                "Unable to obtain an interpretation response from Ollama"
            ) from exc
        finally:
            if self._owns_client:
                client.close()

        try:
            data = response.json()
            raw = data.get("response") if isinstance(data, dict) else None
            parsed = json.loads(raw) if isinstance(raw, str) else None
        except (ValueError, TypeError) as exc:
            raise LLMResponseError("Ollama returned an invalid interpretation") from exc

        intent = parsed.get("intent") if isinstance(parsed, dict) else None
        if intent not in SUPPORTED_INTENTS:
            raise LLMResponseError("Ollama returned an unsupported Intent")

        return intent
