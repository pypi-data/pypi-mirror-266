from enum import Enum


class DistributedDataStructure(Enum):
    """
    Enumeration that defines the data type.
    """
    LIST = 1
    """
    For distributed list.
    """
    QUEUE = 2
    """
    For distributed queue.
    """
    SET = 3
    """
    For distributed set.
    """
    DICTIONARY = 4
    """
    For distributed dictionary.
    """
    COUNTER = 5
    """
    For distributed counter.
    """
