import logging
import os
from config import config

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("veritas")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    formatter = logging.Formatter(
        "%(asctime)s — %(levelname)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
