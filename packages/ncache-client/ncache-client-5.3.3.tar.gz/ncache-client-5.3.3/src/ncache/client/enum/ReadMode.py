from enum import Enum


class ReadMode(Enum):
    """
    Enumeration that defines the read mode if item is not found in cache.
    """
    NONE = 1
    """
    Return None if item not found.
    """
    READ_THRU = 2
    """
    Look data source for item if not found.
    """
    READ_THRU_FORCED = 3
    """
    Forcefully look data source for item and update/add item in cache.
    """
