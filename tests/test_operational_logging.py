import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from centaurus.config import RuntimeSettings
from centaurus.observability import configure_logging


def make_settings(workspace: Path, *, level: str = "INFO") -> RuntimeSettings:
    return RuntimeSettings(
        workspace=workspace,
        ollama_base_url="http://ollama:11434",
        ollama_model="qwen3:4b",
        ollama_timeout=60.0,
        ollama_interpretation_timeout=60.0,
        log_level=level,
    )


def _runtime_handlers() -> list[RotatingFileHandler]:
    return [
        handler
        for handler in logging.getLogger("centaurus").handlers
        if isinstance(handler, RotatingFileHandler)
    ]


def _close_centaurus_runtime_handlers() -> None:
    logger = logging.getLogger("centaurus")
    for handler in _runtime_handlers():
        logger.removeHandler(handler)
        handler.close()


def test_operational_logging_is_persisted_outside_investigation_knowledge(
    tmp_path: Path,
) -> None:
    settings = make_settings(tmp_path)
    try:
        configure_logging(settings)
        logging.getLogger("centaurus.tests").info(
            "investigation finished id=INV-LOG-001 findings=2"
        )
        for handler in logging.getLogger("centaurus").handlers:
            handler.flush()

        content = settings.log_path.read_text(encoding="utf-8")

        assert settings.log_path == tmp_path / "logs" / "centaurus.log"
        assert "INV-LOG-001" in content
        assert "findings=2" in content
        assert "investigations" not in settings.log_path.parts
    finally:
        _close_centaurus_runtime_handlers()


def test_reconfiguration_replaces_runtime_handler_without_duplicate_records(
    tmp_path: Path,
) -> None:
    settings = make_settings(tmp_path, level="DEBUG")
    try:
        configure_logging(settings)
        configure_logging(settings)
        logging.getLogger("centaurus.tests").debug("single-record")
        for handler in logging.getLogger("centaurus").handlers:
            handler.flush()

        content = settings.log_path.read_text(encoding="utf-8")

        assert content.count("single-record") == 1
        assert len(_runtime_handlers()) == 1
    finally:
        _close_centaurus_runtime_handlers()
