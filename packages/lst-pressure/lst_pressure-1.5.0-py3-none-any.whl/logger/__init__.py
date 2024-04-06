import sys
from conf import Conf, LogLevel
import warnings

conf = Conf()


def debug(*args, **kwargs):
    if conf.LOG_LEVEL == LogLevel.DEBUG:
        print("DEBUG", *args, **kwargs, file=sys.stderr)


def info(*args, **kwargs):
    if (conf.LOG_LEVEL == LogLevel.INFO or conf.LOG_LEVEL == LogLevel.DEBUG) and not conf.TEST_MODE:
        print("INFO", *args, **kwargs, file=sys.stderr)


def warn(*args, **kwargs):
    if (
        conf.LOG_LEVEL == LogLevel.INFO
        or conf.LOG_LEVEL == LogLevel.DEBUG
        or conf.LOG_LEVEL == LogLevel.WARN
    ):
        warnings.warn(*args, **kwargs)


def error(*args, **kwargs):
    print("ERROR", *args, **kwargs, file=sys.stderr)


__all__ = ["debug", "info", "warn", "error"]

# Automatically added by katversion
__version__ = '1.5.0'
