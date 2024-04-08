from enum import Enum


class EntryType (Enum):
    """
    Specifies that the entry under question is a cache item.
    """
    CACHE_ITEM = 1
    """
    Specifies that the entry under question is a cache item.
    """

    LIST = 2
    """
    Specifies that the entry under question is a collection item of type list.
    """

    QUEUE = 3
    """
    Specifies that the entry under question is a collection item of type queue.
    """

    SET = 4
    """
    Specifies that the entry under question is a collection item of type set.
    """

    DICTIONARY = 5
    """
    Specifies that the entry under question is a collection item of type dictionary.
    """

    COUNTER = 6
    """
    Specifies that the entry under question is a collection item of type counter.
    """

    TYPE_LESS = 7
