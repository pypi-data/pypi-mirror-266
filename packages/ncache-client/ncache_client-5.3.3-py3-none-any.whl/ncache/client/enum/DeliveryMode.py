from enum import Enum


class DeliveryMode(Enum):
    """
    NCache provides a DeliveryOption enum which specifies how the message should be delivered to any registered
    subscribers.The delivery option is specified during message publishing phase.
    """
    ASYNC = 1
    """
    Async invocation of messages.Using async method of delivery does not guarantee ordered delivery of messages.
    """
    SYNC = 2
    """
    Sync invocation of messages.Using sync method of delivery guarantees ordered delivery of messages.
    """
