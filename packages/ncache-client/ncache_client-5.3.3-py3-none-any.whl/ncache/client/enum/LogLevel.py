from enum import Enum


class LogLevel(Enum):
    """
    Defines the level of logging you want to use.
    """
    INFO = 1
    """
    Info level describes some useful information about any operation performed on cache.
    """
    ERROR = 2
    """
    This log flag gives the cause of errors that are raised during operation execution.
    """
    DEBUG = 3
    """
    This log option prints detailed information about any operations in cache.
    """
