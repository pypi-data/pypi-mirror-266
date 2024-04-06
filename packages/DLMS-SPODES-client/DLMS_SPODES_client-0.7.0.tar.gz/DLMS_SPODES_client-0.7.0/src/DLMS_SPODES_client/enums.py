from enum import IntEnum, auto
import logging


class Operation(IntEnum):
    OPEN = auto()
    CLOSE = auto()
    INIT_TYPE = auto()
    READ = auto()


class LogLevel(IntEnum):
    DEB = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    ERR = logging.ERROR
    CRIT = logging.CRITICAL
