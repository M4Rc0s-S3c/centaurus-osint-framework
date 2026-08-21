"""Structured application request submitted to the Core."""

from dataclasses import dataclass

from centaurus.capabilities import (
    PUBLIC_EXPOSURE_ASSESSMENT,
    SUPPORTED_INTENTS,
    SUPPORTED_TARGET_TYPES,
)
from centaurus.request.target_factory import TargetFactory


@dataclass(frozen=True, slots=True)
class StructuredRequest:
    """Validated boundary between linguistic input and Core runtime."""

    target: str
    target_type: str
    intent: str

    def __post_init__(self) -> None:
        target_type = (
            self.target_type.strip().upper()
            if isinstance(self.target_type, str)
            else ""
        )
        intent = self.intent.strip() if isinstance(self.intent, str) else ""

        if target_type not in SUPPORTED_TARGET_TYPES:
            raise ValueError(f"unsupported target_type: {self.target_type!r}")
        if intent not in SUPPORTED_INTENTS:
            raise ValueError(f"unsupported intent: {self.intent!r}")

        candidate = TargetFactory.normalize(self.target, target_type)

        object.__setattr__(self, "target", candidate.value)
        object.__setattr__(self, "target_type", candidate.type)
        object.__setattr__(self, "intent", intent)
