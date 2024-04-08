from enum import Enum


class CacheStatusNotificationType(Enum):
    """
    NCache defines a CacheStatusNotificationType enum that specifies the type of events for which cache status changed
    notification is registered/unregistered.
    """
    MEMBER_JOINED = 1
    """
    User receives a notification whenever a node joins the cache.
    """
    MEMBER_LEFT = 2
    """
    User receives a notification whenever a node leaves the cache.
    """
    CACHE_STOPPED = 3
    """
    User receives a notification whenever the cache is stopped.
    """
    ALL = 4
    """
    User receives a notification whenever a node joins/leaves the cache and when the cache is stopped.
    """
