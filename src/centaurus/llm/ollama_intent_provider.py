"""Ollama provider for the LLM interpretation instance."""

import json
import os

import httpx

from centaurus.llm.exceptions import LLMProviderError, LLMResponseError
from centaurus.llm.interpretation_prompt import INTERPRETATION_SYSTEM_PROMPT
from centaurus.request.structured_request import SUPPORTED_INTENTS


class OllamaIntentProvider:
    """Classify user language through a dedicated Ollama configuration."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = (
            base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ).rstrip("/")
        self._model = model or os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self._timeout = (
            timeout
            if timeout is not None
            else float(
                os.getenv(
                    "OLLAMA_INTERPRETATION_TIMEOUT",
                    os.getenv("OLLAMA_TIMEOUT", "60"),
                )
            )
        )
        self._client = client
        self._owns_client = client is None

    def classify_intent(self, user_input: str) -> str:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        payload = {
            "model": self._model,
            "system": INTERPRETATION_SYSTEM_PROMPT,
            "prompt": user_input.strip(),
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
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
