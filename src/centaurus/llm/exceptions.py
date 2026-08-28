"""Operational errors raised by the LLM subsystem."""


class LLMError(RuntimeError):
    """Base class for operational LLM errors."""


class LLMProviderError(LLMError):
    """Raised when an LLM provider cannot complete a request."""

    def __init__(
        self,
        message: str,
        *,
        cause_type: str = "ProviderError",
        provider: str | None = None,
        role: str | None = None,
        timeout_seconds: float | None = None,
        http_status: int | None = None,
        duration_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.cause_type = cause_type
        self.provider = provider
        self.role = role
        self.timeout_seconds = timeout_seconds
        self.http_status = http_status
        self.duration_seconds = duration_seconds


class LLMResponseError(LLMProviderError):
    """Raised when the provider response violates the expected contract."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        role: str | None = None,
        timeout_seconds: float | None = None,
        http_status: int | None = None,
        duration_seconds: float | None = None,
    ) -> None:
        super().__init__(
            message,
            cause_type="ResponseValidationError",
            provider=provider,
            role=role,
            timeout_seconds=timeout_seconds,
            http_status=http_status,
            duration_seconds=duration_seconds,
        )
