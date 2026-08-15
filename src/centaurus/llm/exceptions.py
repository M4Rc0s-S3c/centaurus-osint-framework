"""Operational errors raised by the LLM subsystem."""


class LLMError(RuntimeError):
    """Base class for operational LLM errors."""


class LLMProviderError(LLMError):
    """Raised when an LLM provider cannot complete a request."""


class LLMResponseError(LLMProviderError):
    """Raised when the provider response violates the expected contract."""
