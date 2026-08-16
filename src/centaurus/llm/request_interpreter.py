"""LLM #1 application boundary for natural-language requests."""

from centaurus.llm.intent_provider import IntentProvider
from centaurus.llm.ollama_intent_provider import OllamaIntentProvider
from centaurus.request import StructuredRequest, TargetFactory


class RequestInterpreter:
    """Combine deterministic Target construction with semantic Intent classification."""

    def __init__(
        self,
        provider: IntentProvider | None = None,
        target_factory: TargetFactory | None = None,
    ) -> None:
        self._provider = provider or OllamaIntentProvider()
        self._target_factory = target_factory or TargetFactory()

    def interpret(self, user_input: str) -> StructuredRequest:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")

        target = self._target_factory.create(user_input)
        intent = self._provider.classify_intent(user_input)

        return StructuredRequest(
            target=target.value,
            target_type=target.type,
            intent=intent,
        )
