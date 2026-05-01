from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from ..settings import user_data_dir


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("slidedrop")
    if logger.handlers:
        return logger

    log_dir = user_data_dir() / "logs"
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
    return logger
