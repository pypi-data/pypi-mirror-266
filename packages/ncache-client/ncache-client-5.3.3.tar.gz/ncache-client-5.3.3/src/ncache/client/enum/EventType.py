from enum import Enum


class EventType(Enum):
    """
    NCache provides an EventType enum which specifies the type of event to be registered by the user. Event types are
    specified at the time of notification registration.
    """

    ITEM_ADDED = 1
    """
    User receives a notification when an item is added in cache.
    """

    ITEM_UPDATED = 2
    """
    User receives a notification when an item is updated in cache
    """

    ITEM_REMOVED = 3
    """
    User receives a notification when an item is removed from cache.
    """
