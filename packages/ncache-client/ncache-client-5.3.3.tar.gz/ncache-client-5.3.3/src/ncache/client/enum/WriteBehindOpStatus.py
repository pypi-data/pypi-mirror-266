from enum import Enum


class WriteBehindOpStatus(Enum):
    """
    Enumeration that defines the staus of write behind operation.
    """
    FAILURE = 1
    """
    If user code returned false
    """

    SUCCESS = 2
    """
    If write behind operation was successful
    """
