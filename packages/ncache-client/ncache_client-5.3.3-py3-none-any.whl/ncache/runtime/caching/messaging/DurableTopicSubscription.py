from ncache.client.enum.SubscriptionPolicy import SubscriptionPolicy
from ncache.runtime.caching.TopicSubscription import TopicSubscription
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class DurableTopicSubscription(TopicSubscription):
    """
    Contains information about the subscription created
    """
    def __init__(self, value):
        """
        Initializes a new instance of this class.
        """
        super().__init__(value)
        self.__durablesubscription = value

    def get_instance(self):
        return self.__durablesubscription

    def set_instance(self, value):
        self.__durablesubscription = value

    def get_subscription_name(self):
        """
        Returns the name for durable subscriptions.

        :return: Name for durable subscriptions.
        :rtype: str
        """
        result = self.__durablesubscription.getSubscriptionName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_subscription_policy(self):
        """
        It returns the type of Subscription Policy user has subscribed with.

        :return: The type of Subscription Policy user has subscribed with.
        :rtype: SubscriptionPolicy
        """
        result = self.__durablesubscription.getSubscriptionPolicy()

        if result is not None:
            result = EnumUtil.get_subscription_policy_value(result)

        return result
