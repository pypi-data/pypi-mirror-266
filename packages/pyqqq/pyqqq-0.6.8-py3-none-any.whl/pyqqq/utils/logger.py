import logging
from logging.handlers import TimedRotatingFileHandler
import pyqqq.config as c
import sys

_format = "%(levelname).1s %(name)s: %(message)s"

if not c.is_google_cloud_logging_enabled():
    _format = "%(asctime)s " + _format

_stdout_h = logging.StreamHandler(sys.stdout)
_stdout_h.setLevel(logging.DEBUG)
_stdout_h.addFilter(lambda r: r.levelno <= logging.WARNING)

_stderr_h = logging.StreamHandler(sys.stderr)
_stderr_h.setLevel(logging.ERROR)

logging.basicConfig(format=_format, handlers=[_stdout_h, _stderr_h])


def get_logger(
        name,
        level=logging.DEBUG,
        filename: str = None,
        when: str = 'h',
        interval: int = 1,
        backup_count: int = 24,
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers and filename:
        fh = TimedRotatingFileHandler(
            filename, when=when, backupCount=backup_count, interval=interval
        )
        fh.setLevel(level)
        fh.setFormatter(_format)
        logger.addHandler(fh)

    return logger
