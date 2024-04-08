from enum import Enum


class DeliveryOption(Enum):
    """
    NCache provides a DeliveryOption enum which specifies how the message should be delivered to any registered
    subscribers. The delivery option is specified during message publishing phase.
    """
    ALL = 1
    """
    Delivers message to all registered subscribers, if no subscriber has been registered, it will return without any
    failure acknowledgment. Message will be sent to any subscriber when it registers on topic; unless message expiration
    has not occurred.
    """
    ANY = 2
    """
    Delivers message to any one of the registered subscribers. If acknowledgement is not received, the message is
    reassigned to another subscriber till it reaches its expiration time limit.
    """
