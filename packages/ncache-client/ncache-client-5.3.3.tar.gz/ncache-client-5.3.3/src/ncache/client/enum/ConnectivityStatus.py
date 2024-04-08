from enum import Enum


class ConnectivityStatus(Enum):
    """
    Cache connectivity status contains the connectivity status of Cache nodes.
    """
    DISCONNECTED = 1
    """
    Client is connected to the Cache.
    """
    CONNECTED = 2
    """
    Client is disconnected from Cache.
    """
