"""Standard-library operational logging for CENTAURUS.

The log is operational metadata, not domain knowledge.  It lives below the
workspace ``logs/`` branch and intentionally does not replace persisted RAW,
Evidence, Finding, Report or ExecutionFailure artifacts.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import time

from centaurus.config import RuntimeConfigurationError, RuntimeSettings


_LOGGER_NAME = "centaurus"
_HANDLER_MARKER = "_centaurus_runtime_handler"
_MAX_LOG_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3


def configure_logging(settings: RuntimeSettings) -> logging.Logger:
    """Configure one bounded UTF-8 operational log for the product runtime."""

    if not isinstance(settings, RuntimeSettings):
        raise TypeError("settings must be a RuntimeSettings instance")

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, settings.log_level))
    logger.propagate = False

    for handler in list(logger.handlers):
        if getattr(handler, _HANDLER_MARKER, False):
            logger.removeHandler(handler)
            handler.close()

    try:
        settings.log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            settings.log_path,
            maxBytes=_MAX_LOG_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeConfigurationError(
            f"Unable to initialize operational log at {settings.log_path}"
        ) from exc

    setattr(handler, _HANDLER_MARKER, True)
    formatter = logging.Formatter(
        "%(asctime)sZ %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
