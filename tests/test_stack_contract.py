from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _dependency_name(requirement: str) -> str:
    return re.split(r"[<>=!~ ;\[]", requirement, maxsplit=1)[0].strip().lower()


def test_runtime_dependency_set_is_minimal_and_matches_as_built_stack() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = {
        _dependency_name(requirement)
        for requirement in data["project"]["dependencies"]
    }

    assert dependencies == {
        "python-whois",
        "httpx",
        "typer",
        "rich",
        "prompt-toolkit",
    }
    assert dependencies.isdisjoint(
        {"pydantic", "pydantic-settings", "orjson", "loguru"}
    )


def test_standard_library_covers_settings_json_and_operational_logging() -> None:
    runtime = (ROOT / "src/centaurus/config/runtime.py").read_text(encoding="utf-8")
    logging_source = (ROOT / "src/centaurus/observability/logging.py").read_text(
        encoding="utf-8"
    )
    report_store = (
        ROOT / "src/centaurus/persistence/filesystem/report_store.py"
    ).read_text(encoding="utf-8")

    assert "from dataclasses import dataclass" in runtime
    assert "import os" in runtime
    assert "from logging.handlers import RotatingFileHandler" in logging_source
    assert "import json" in report_store

    combined = "\n".join((runtime, logging_source, report_store)).lower()
    assert "pydantic" not in combined
    assert "orjson" not in combined
    assert "loguru" not in combined


def test_compose_exposes_complete_operational_configuration_surface() -> None:
    compose = (ROOT / "docker/compose.yml").read_text(encoding="utf-8")

    expected = {
        "CENTAURUS_WORKSPACE",
        "CENTAURUS_LOG_LEVEL",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "OLLAMA_TIMEOUT",
        "OLLAMA_INTERPRETATION_TIMEOUT",
        "OLLAMA_ANALYST_ASSISTANCE_TIMEOUT",
        "OLLAMA_ANALYST_ASSISTANCE_NUM_CTX",
        "OLLAMA_ANALYST_ASSISTANCE_NUM_PREDICT",
        "CENTAURUS_WHOIS_TIMEOUT",
        "CENTAURUS_RDAP_TIMEOUT",
        "CENTAURUS_CRTSH_TIMEOUT",
        "CENTAURUS_DNSRECON_TIMEOUT",
        "CENTAURUS_SUBLIST3R_TIMEOUT",
        "CENTAURUS_THEHARVESTER_TIMEOUT",
    }

    for variable in expected:
        assert f"{variable}:" in compose


def test_compose_freezes_candidate_ollama_d2_role_defaults() -> None:
    compose = (ROOT / "docker/compose.yml").read_text(encoding="utf-8")

    assert 'OLLAMA_ANALYST_ASSISTANCE_TIMEOUT: "${OLLAMA_ANALYST_ASSISTANCE_TIMEOUT:-300}"' in compose
    assert 'OLLAMA_ANALYST_ASSISTANCE_NUM_CTX: "${OLLAMA_ANALYST_ASSISTANCE_NUM_CTX:-8192}"' in compose
    assert 'OLLAMA_ANALYST_ASSISTANCE_NUM_PREDICT: "${OLLAMA_ANALYST_ASSISTANCE_NUM_PREDICT:-}"' in compose
