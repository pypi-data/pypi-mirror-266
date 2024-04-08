from enum import Enum


class DataTypeEventDataFilter(Enum):
    """
    This enum is to describe when registering a collection event, upon raise how much data is retrieved from cache when
    the event is raised. Only one value can be set.
    """
    NONE = 1
    """
    This specifies that no data or meta data is required when an event notification is raised.
    """
    DATA = 2
    """
    This specifies that item of collection is required when an event notification is raised.
    """
