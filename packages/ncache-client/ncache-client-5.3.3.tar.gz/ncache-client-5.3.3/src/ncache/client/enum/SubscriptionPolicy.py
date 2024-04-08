from enum import Enum


class SubscriptionPolicy(Enum):
    """
    Defines the policy used in case of Durable subscription.
    """
    SHARED = 1
    """
    Shared subscription policy is for multiple subscribers on a single subscription. In this case messages are sent to
    any of the topic subscribers. This policy provides better load division over clients subscribing to a subscription.
    """
    EXCLUSIVE = 2
    """
    Exclusive subscription policy is for a single subscriber on a single subscription. In this case messages are
    received by the single subscriber only.
    """
