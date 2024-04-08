from enum import Enum


class TopicSearchOptions(Enum):
    """
    Specifies the option through which the topic is searched by.
    """
    BY_NAME = 1
    """
    Search by name.
    """
    BY_PATTERN = 2
    """
    Search by pattern.
    """
