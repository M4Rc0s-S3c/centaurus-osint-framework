"""Minimal environment-backed runtime configuration.

CENTAURUS keeps operational configuration outside the domain.  The product
composition root resolves the small set of deployment settings from the
environment and injects concrete infrastructure dependencies into the Core.
No third-party settings framework is required for the current TFM surface.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from pathlib import Path


_DEFAULT_WORKSPACE = "/workspace"
_DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL = "qwen3:4b"
_DEFAULT_OLLAMA_TIMEOUT = 60.0
_DEFAULT_LOG_LEVEL = "INFO"
_ALLOWED_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

_TOOL_TIMEOUTS: dict[str, tuple[str, float]] = {
    "whois": ("CENTAURUS_WHOIS_TIMEOUT", 10.0),
    "rdap": ("CENTAURUS_RDAP_TIMEOUT", 10.0),
    "crtsh": ("CENTAURUS_CRTSH_TIMEOUT", 30.0),
    "dnsrecon": ("CENTAURUS_DNSRECON_TIMEOUT", 120.0),
    "sublist3r": ("CENTAURUS_SUBLIST3R_TIMEOUT", 180.0),
    "theharvester": ("CENTAURUS_THEHARVESTER_TIMEOUT", 300.0),
}


class RuntimeConfigurationError(ValueError):
    """Raised when external runtime configuration is malformed."""


def configured_text(
    explicit: str | None,
    env_name: str,
    default: str,
) -> str:
    """Resolve a non-empty text setting from explicit value, env, then default."""

    if explicit is not None:
        value = str(explicit).strip()
    else:
        raw = os.getenv(env_name)
        value = raw.strip() if raw is not None else default.strip()

    if not value:
        raise RuntimeConfigurationError(f"{env_name} must be a non-empty value")
    return value


def configured_positive_float(
    explicit: float | int | str | None,
    env_name: str,
    default: float,
) -> float:
    """Resolve and validate a strictly positive numeric runtime setting."""

    raw: float | int | str
    if explicit is not None:
        raw = explicit
    else:
        raw = os.getenv(env_name, str(default))

    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeConfigurationError(
            f"{env_name} must be a positive number"
        ) from exc

    if value <= 0:
        raise RuntimeConfigurationError(f"{env_name} must be greater than zero")
    return value


def resolve_workspace(workspace: str | Path | None = None) -> Path:
    """Resolve the workspace root while preserving explicit dependency injection."""

    if workspace is not None:
        value = str(workspace).strip()
        if not value:
            raise RuntimeConfigurationError("workspace must be a non-empty path")
        return Path(workspace)

    configured = configured_text(None, "CENTAURUS_WORKSPACE", _DEFAULT_WORKSPACE)
    return Path(configured)


def tool_timeout(tool_name: str, explicit: float | None = None) -> float:
    """Return the externally configurable timeout for one supported tool adapter."""

    normalized = str(tool_name).strip().lower()
    try:
        env_name, default = _TOOL_TIMEOUTS[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported tool timeout configuration: {tool_name}") from exc

    return configured_positive_float(explicit, env_name, default)


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    """Immutable configuration resolved at the application composition root."""

    workspace: Path
    ollama_base_url: str
    ollama_model: str
    ollama_timeout: float
    ollama_interpretation_timeout: float
    log_level: str

    @property
    def log_path(self) -> Path:
        """Return the operational log path outside Investigation knowledge folders."""

        return self.workspace / "logs" / "centaurus.log"

    @classmethod
    def from_env(cls) -> "RuntimeSettings":
        """Load and validate the complete product-level runtime configuration."""

        ollama_timeout = configured_positive_float(
            None,
            "OLLAMA_TIMEOUT",
            _DEFAULT_OLLAMA_TIMEOUT,
        )
        interpretation_timeout = configured_positive_float(
            None,
            "OLLAMA_INTERPRETATION_TIMEOUT",
            ollama_timeout,
        )
        log_level = configured_text(
            None,
            "CENTAURUS_LOG_LEVEL",
            _DEFAULT_LOG_LEVEL,
        ).upper()
        if log_level not in _ALLOWED_LOG_LEVELS:
            allowed = ", ".join(sorted(_ALLOWED_LOG_LEVELS))
            raise RuntimeConfigurationError(
                f"CENTAURUS_LOG_LEVEL must be one of: {allowed}"
            )

        # Resolve through logging to catch aliases/typos now instead of silently
        # accepting a value that would later disable records unexpectedly.
        if not isinstance(logging.getLevelName(log_level), int):
            raise RuntimeConfigurationError(
                f"Unsupported CENTAURUS_LOG_LEVEL: {log_level}"
            )

        # Validate plugin timeout configuration at application startup. Plugin
        # adapters resolve the same centralized definitions when instantiated by
        # PluginManager, preserving their existing construction boundary.
        for tool_name in _TOOL_TIMEOUTS:
            tool_timeout(tool_name)

        return cls(
            workspace=resolve_workspace(),
            ollama_base_url=configured_text(
                None,
                "OLLAMA_BASE_URL",
                _DEFAULT_OLLAMA_BASE_URL,
            ).rstrip("/"),
            ollama_model=configured_text(
                None,
                "OLLAMA_MODEL",
                _DEFAULT_OLLAMA_MODEL,
            ),
            ollama_timeout=ollama_timeout,
            ollama_interpretation_timeout=interpretation_timeout,
            log_level=log_level,
        )
