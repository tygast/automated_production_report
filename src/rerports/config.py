import logging
import logging.config
import logging.handlers
import sys

from pathlib import Path
from typing import Optional


import toml

LOGGERS = {}
LOGGING = False


def set_logging(logging: Optional[Path] = None, log=False):
    if not log:
        return

    if logging is not None:
        config = toml.load(logging)
        logging.config.dictConfig(config)

    global LOGGING
    LOGGING = True
    for name in LOGGERS:
        logger = logging.getLogger(name)
        logger.disabled = False
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            if isinstance(handler, logging.NullHandler):
                logger.removeHandler(handler)

        for h, v in logging._handlers.items():
            logger.addHandler(v)


def get_logger(name):
    global LOGGERS
    global LOGGING

    if LOGGING:
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            if isinstance(handler, logging.NullHandler):
                logger.removeHandler(handler)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s — %(name)s — %(levelname)s — "
            "%(funcName)s:%(lineno)d — %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:

        logger = logging.getLogger(name)
        handler = logging.NullHandler()
        logger.addHandler(handler)
    LOGGERS[name] = logger
    return logger
