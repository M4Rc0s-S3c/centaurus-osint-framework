"""Provider contract for the LLM interpretation instance."""

from typing import Protocol


class IntentProvider(Protocol):
    """Classify user language into an existing domain Intent."""

    def classify_intent(self, user_input: str) -> str:
        """Return one validated Intent identifier."""
        ...
