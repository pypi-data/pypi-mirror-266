from enum import Enum


class ExpirationType(Enum):
    """
    The type of expiration to be used while expiring items in cache. The value of this type varies from item to item in
    cache.
    """
    NONE = 1
    """
    Indicates that no expiration is to take place.
    """
    SLIDING = 2
    """
    Indicates that item expiration in cache is to follow idle expiration.
    """
    ABSOLUTE = 3
    """
    Indicates that item expiration in cache is to follow fixed expiration.
    """
    DEFAULT_ABSOLUTE = 4
    """
    Indicates that item expiration in cache is to follow fixed expiration and value should be taken from
    'DefaultAbsolute' field in NCache Manager.
    """
    DEFAULT_ABSOLUTE_LONGER = 5
    """
    Indicates that item expiration in cache is to follow fixed expiration and value should be taken from
    'DefaultAbsoluteLonger' field in NCache Manager.
    """
    DEFAULT_SLIDING = 6
    """
    Indicates that item expiration in cache is to follow fixed expiration and value should be taken from 'DefaultSliding'
    field in NCache Manager.
    """
    DEFAULT_SLIDING_LONGER = 7
    """
    Indicates that item expiration in cache is to follow fixed expiration and value should be taken from
    'DefaultSlidingLonger' field in NCache Manager.
    """
