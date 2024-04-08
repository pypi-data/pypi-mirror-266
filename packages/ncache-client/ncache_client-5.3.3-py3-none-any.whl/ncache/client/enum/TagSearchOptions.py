from enum import Enum


class TagSearchOptions(Enum):
    """
    Enumeration that defines the tag search options.
    """
    BY_ALL_TAGS = 1
    """
    Search objects that have all of the tags in common.
    """
    BY_ANY_TAG = 2
    """
    Search objects that have any of the specified tags in common.
    """
