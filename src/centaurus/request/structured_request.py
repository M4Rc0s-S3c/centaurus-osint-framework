"""Structured application request submitted to the Core."""

from dataclasses import dataclass

from centaurus.capabilities import (
    PUBLIC_EXPOSURE_ASSESSMENT,
    SUPPORTED_INTENTS,
    SUPPORTED_TARGET_TYPES,
)


@dataclass(frozen=True, slots=True)
class StructuredRequest:
    """Validated boundary between linguistic input and Core runtime."""

    target: str
    target_type: str
    intent: str

    def __post_init__(self) -> None:
        target = self.target.strip() if isinstance(self.target, str) else ""
        target_type = (
            self.target_type.strip().upper()
            if isinstance(self.target_type, str)
            else ""
        )
        intent = self.intent.strip() if isinstance(self.intent, str) else ""

        if not target:
            raise ValueError("target must be a non-empty string")
        if target_type not in SUPPORTED_TARGET_TYPES:
            raise ValueError(f"unsupported target_type: {self.target_type!r}")
        if intent not in SUPPORTED_INTENTS:
            raise ValueError(f"unsupported intent: {self.intent!r}")

        object.__setattr__(self, "target", target)
        object.__setattr__(self, "target_type", target_type)
        object.__setattr__(self, "intent", intent)
