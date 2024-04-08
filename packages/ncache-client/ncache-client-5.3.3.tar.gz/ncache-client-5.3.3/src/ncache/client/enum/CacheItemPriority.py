from enum import Enum


class CacheItemPriority(Enum):
    """
    Specifies the relative priority of items stored in the Cache. When the application's cache is full or runs low on
    memory, the Cache selectively purges items to free system memory. When an item is added to the Cache, you can assign
    it a relative priority compared to the other items stored in the Cache. Items you assign higher priority values to
    are less likely to be deleted from the Cache when the server is processing a large number of requests, while items
    you assign lower priority values are more likely to be deleted. The default is NORMAL.
    """
    NORMAL = 1
    """
    Cache items with this priority level are likely to be deleted from the cache as the server frees system memory only
    after those items with Low or BELOW_NORMAL priority. This is the default.
    """
    LOW = 2
    """
    Cache items with this priority level are the most likely to be deleted from the cache as the server frees system
    memory.
    """
    BELOW_NORMAL = 3
    """
    Cache items with this priority level are more likely to be deleted from the cache as the server frees system memory
    than items assigned a NORMAL priority.
    """
    ABOVE_NORMAL = 5
    """
    Cache items with this priority level are less likely to be deleted as the server frees system memory than those
    assigned a NORMAL priority.
    """
    HIGH = 5
    """
    Cache items with this priority level are the least likely to be deleted from the cache as the server frees system
    memory.
    """
    NOT_REMOVABLE = 6
    """
    The cache items with this priority level will not be deleted from the cache as the server frees system memory.
    """
    DEFAULT = 7
    """
    The default value for a cached item's priority is NORMAL
    """
