from enum import Enum


class EventDataFilter(Enum):
    """
    NCache provides an enum EventDataFilter to specify how much data should be retrieved from cache when a notification
    is raised. This is specified when user registers a notification.
    """

    NONE = 1
    """
    This specifies that no data or meta data is required when an event notification is raised.
    """

    META_DATA = 2
    """
    This specifies that only meta data of cache item is required when an event notification is raised.
    Meta data includes information like groups, subgroups, cacheItemPriority, item version etc.
    """

    DATA_WITH_META_DATA = 4
    """
    This specifies that the value of the cache item is required along with all the meta data when an event notification
    is raised.
    """
