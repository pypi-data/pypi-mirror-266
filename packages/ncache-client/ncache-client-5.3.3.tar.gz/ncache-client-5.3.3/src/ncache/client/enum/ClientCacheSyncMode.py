from enum import Enum


class ClientCacheSyncMode(Enum):
    """
    Gets/Sets Enumeration to specify how the Client cache is synchronized with the cluster caches through events.
    """
    PESSIMISTIC = 1
    """
    In "PESSIMISTIC" mode of synchronization, client cache always checks for the "version" of the cached item before
    returning it to the application.
    """
    OPTIMISTIC = 2
    """
    It is possible that client caches are not synchronized with clustered cache for a small period of time. If during
    this time users gets an item from the client cache, he may get an old version. This is the "OPTIMISTIC" mode of
    synchronization.
    """
