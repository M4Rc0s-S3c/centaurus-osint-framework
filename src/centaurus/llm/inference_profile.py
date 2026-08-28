"""Versioned Ollama inference profiles for the two logical LLM roles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OllamaInferenceProfile:
    """Immutable generation parameters applied to one logical LLM role."""

    think: bool
    temperature: float
    top_p: float
    top_k: int
    min_p: float
    seed: int
    num_ctx: int | None = None
    num_predict: int | None = None

    def options(self) -> dict[str, float | int]:
        """Return the Ollama ``options`` payload for this profile."""

        options: dict[str, float | int] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "min_p": self.min_p,
            "seed": self.seed,
        }
        if self.num_ctx is not None:
            options["num_ctx"] = self.num_ctx
        if self.num_predict is not None:
            options["num_predict"] = self.num_predict
        return options


# Qwen3 non-thinking candidate baseline used by both current logical roles.
# The profiles remain separate constants because their responsibilities and future
# evolution are independent even while the candidate sampling defaults are equal.
INTERPRETATION_INFERENCE_PROFILE = OllamaInferenceProfile(
    think=False,
    temperature=0.7,
    top_p=0.8,
    top_k=20,
    min_p=0.0,
    seed=42,
)

ANALYST_ASSISTANCE_INFERENCE_PROFILE = OllamaInferenceProfile(
    think=False,
    temperature=0.7,
    top_p=0.8,
    top_k=20,
    min_p=0.0,
    seed=42,
)
