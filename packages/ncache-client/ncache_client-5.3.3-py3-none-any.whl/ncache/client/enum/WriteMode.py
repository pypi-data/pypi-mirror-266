from enum import Enum


class WriteMode(Enum):
    """
    Enumeration that defines the update operation on cache can update data source.
    """
    NONE = 1
    """
    Does not update data source.
    """
    WRITE_THRU = 2
    """
    Updates data source synchronously.
    """
    WRITE_BEHIND = 3
    """
    Updates data source asynchronously.
    """
