from enum import Enum


class CacheItemRemovedReason(Enum):
    """
    Specifies the reason an item was removed from the Cache. This enumeration works in concert with the
    CacheItemRemovedCallback delegate to notify your applications when and why an object was removed from the Cache.
    """
    DEPENDENCY_CHANGED = 1
    """
    The item is removed from the cache because a file or key dependency changed.
    """
    EXPIRED = 2
    """
    The item is removed from the cache because it expired.
    """
    REMOVED = 3
    """
    The item is removed from the cache by a Cache.Remove method call or by an Cache.Insert method call that specified
    the same key.
    """
    UNDERUSED = 4
    """
    The item is removed from the cache because the system removed it to free memory.
    """
    DEPENDENCY_INVALID = 5
    """
    The item is removed from the cache because the its dependency was invalid.
    """
