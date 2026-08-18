from pathlib import Path

import pytest

from centaurus.config import RuntimeConfigurationError, RuntimeSettings, resolve_workspace
from centaurus.plugins.crtsh import Plugin as CrtshPlugin
from centaurus.plugins.dnsrecon import Plugin as DnsreconPlugin
from centaurus.plugins.rdap import Plugin as RdapPlugin
from centaurus.plugins.sublist3r import Plugin as Sublist3rPlugin
from centaurus.plugins.theharvester import Plugin as TheHarvesterPlugin
from centaurus.plugins.whois import Plugin as WhoisPlugin


_RUNTIME_ENV = (
    "CENTAURUS_WORKSPACE",
    "CENTAURUS_LOG_LEVEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_TIMEOUT",
    "OLLAMA_INTERPRETATION_TIMEOUT",
    "CENTAURUS_WHOIS_TIMEOUT",
    "CENTAURUS_RDAP_TIMEOUT",
    "CENTAURUS_CRTSH_TIMEOUT",
    "CENTAURUS_DNSRECON_TIMEOUT",
    "CENTAURUS_SUBLIST3R_TIMEOUT",
    "CENTAURUS_THEHARVESTER_TIMEOUT",
)


def _clear_runtime_env(monkeypatch) -> None:
    for name in _RUNTIME_ENV:
        monkeypatch.delenv(name, raising=False)


def test_runtime_settings_have_valid_minimal_defaults(monkeypatch) -> None:
    _clear_runtime_env(monkeypatch)

    settings = RuntimeSettings.from_env()

    assert settings.workspace == Path("/workspace")
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "qwen3:4b"
    assert settings.ollama_timeout == 60.0
    assert settings.ollama_interpretation_timeout == 60.0
    assert settings.log_level == "INFO"
    assert settings.log_path == Path("/workspace/logs/centaurus.log")


def test_runtime_settings_load_external_overrides(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CENTAURUS_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("CENTAURUS_LOG_LEVEL", "debug")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.internal:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen-test")
    monkeypatch.setenv("OLLAMA_TIMEOUT", "75.5")
    monkeypatch.setenv("OLLAMA_INTERPRETATION_TIMEOUT", "12")
    monkeypatch.setenv("CENTAURUS_DNSRECON_TIMEOUT", "222")

    settings = RuntimeSettings.from_env()

    assert settings.workspace == tmp_path
    assert settings.ollama_base_url == "http://ollama.internal:11434"
    assert settings.ollama_model == "qwen-test"
    assert settings.ollama_timeout == 75.5
    assert settings.ollama_interpretation_timeout == 12.0
    assert settings.log_level == "DEBUG"


def test_interpretation_timeout_inherits_general_ollama_timeout(monkeypatch) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv("OLLAMA_TIMEOUT", "44")

    settings = RuntimeSettings.from_env()

    assert settings.ollama_timeout == 44.0
    assert settings.ollama_interpretation_timeout == 44.0


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("OLLAMA_TIMEOUT", "not-a-number", "positive number"),
        ("OLLAMA_TIMEOUT", "0", "greater than zero"),
        ("CENTAURUS_DNSRECON_TIMEOUT", "invalid", "positive number"),
        ("CENTAURUS_LOG_LEVEL", "verbose", "must be one of"),
    ],
)
def test_runtime_settings_reject_malformed_external_configuration(
    monkeypatch,
    name: str,
    value: str,
    message: str,
) -> None:
    _clear_runtime_env(monkeypatch)
    monkeypatch.setenv(name, value)

    with pytest.raises(RuntimeConfigurationError, match=message):
        RuntimeSettings.from_env()


def test_explicit_workspace_overrides_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CENTAURUS_WORKSPACE", "/ignored")
    explicit = tmp_path / "explicit"

    assert resolve_workspace(explicit) == explicit


@pytest.mark.parametrize(
    ("env_name", "factory", "expected"),
    [
        ("CENTAURUS_WHOIS_TIMEOUT", WhoisPlugin, 11.0),
        ("CENTAURUS_RDAP_TIMEOUT", RdapPlugin, 12.0),
        ("CENTAURUS_CRTSH_TIMEOUT", CrtshPlugin, 13.0),
        ("CENTAURUS_DNSRECON_TIMEOUT", DnsreconPlugin, 14.0),
        ("CENTAURUS_SUBLIST3R_TIMEOUT", Sublist3rPlugin, 15.0),
        ("CENTAURUS_THEHARVESTER_TIMEOUT", TheHarvesterPlugin, 16.0),
    ],
)
def test_tool_adapters_accept_external_timeout_overrides(
    monkeypatch,
    env_name: str,
    factory,
    expected: float,
) -> None:
    monkeypatch.setenv(env_name, str(expected))

    plugin = factory()

    assert plugin._timeout == expected


def test_tool_timeout_override_must_be_positive(monkeypatch) -> None:
    monkeypatch.setenv("CENTAURUS_DNSRECON_TIMEOUT", "-1")

    with pytest.raises(RuntimeConfigurationError, match="greater than zero"):
        DnsreconPlugin()


def test_explicit_llm_timeout_does_not_depend_on_environment(monkeypatch) -> None:
    from centaurus.llm.ollama_intent_provider import OllamaIntentProvider

    monkeypatch.setenv("OLLAMA_TIMEOUT", "invalid")

    provider = OllamaIntentProvider(timeout=9)

    assert provider._timeout == 9.0
