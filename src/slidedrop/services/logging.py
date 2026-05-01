from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ..settings import user_data_dir


def logs_directory() -> Path:
    return user_data_dir() / "logs"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("slidedrop")
    if logger.handlers:
        return logger

    log_dir = logs_directory()
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "slidedrop.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    dsn = os.getenv("SLIDEDROP_SENTRY_DSN")
    if dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=dsn,
                release=os.getenv("SLIDEDROP_RELEASE"),
                traces_sample_rate=float(os.getenv("SLIDEDROP_SENTRY_TRACES", "0")),
            )
            logger.info("Sentry SDK initialized (opt-in via SLIDEDROP_SENTRY_DSN).")
        except ImportError:
            logger.warning("SLIDEDROP_SENTRY_DSN is set but sentry-sdk is not installed.")

    return logger
