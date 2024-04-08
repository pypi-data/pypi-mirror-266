from enum import Enum


class KeyDependencyType(Enum):
    """
    An enumeration that defines the operation upon which key dependency is to be triggered.
    """
    UPDATE_OR_REMOVE = 1
    """
    Trigger key dependency when an update or remove operation takes place on the cache item. This is the default value.
    """
    REMOVE_ONLY = 2
    """
    Trigger key dependency when a remove operation takes place on the cache item.
    """
