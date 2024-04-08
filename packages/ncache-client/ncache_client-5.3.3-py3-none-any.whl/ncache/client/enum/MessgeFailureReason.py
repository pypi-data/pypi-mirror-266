from enum import Enum


class MessageFailureReason(Enum):
    """
    Failed because it could not be delivered within expiration time.
    """
    EXPIRED = 1
    """
    Failed because it could not be delivered within expiration time.
    """
    EVICTED = 2
    """
    Failed because it got evicted before delivery.
    """
