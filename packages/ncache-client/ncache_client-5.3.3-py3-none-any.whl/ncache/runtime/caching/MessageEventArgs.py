from ncache.client.enum.DeliveryOption import DeliveryOption
from ncache.runtime.caching.Message import Message
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class MessageEventArgs:
    """
    Arguments containing details of received message including topic, sender and type.
    """
    def __init__(self, value):
        """
        Creates MessageEventArgs instance.
        """
        self.__args = value

    def get_message(self):
        """
        Gets the message to be delivered.

        :return: The message to be delivered.
        :rtype: Message
        """
        result = self.__args.getMessage()

        if result is not None:
            message = Message("dummyPayload")
            message.set_instance(result)
            return message

        return result

    def get_delivery_option(self):
        """
        Gets the enum that indicates how the message should be delivered.

        :return: The DeliveryOption enum.
        :rtype: DeliveryOption
        """
        result = self.__args.getDeliveryOption()

        enumtype = None

        if result is not None:
            enumtype = EnumUtil.get_delivery_option_value(result)

        return enumtype

    def get_topic(self):
        """
        Gets the topic to which the message belongs.

        :return: The topic to which the message belongs.
        :rtype: Topic
        """
        result = self.__args.getTopic()

        if result is not None:
            from ncache.runtime.caching.Topic import Topic

            topic = Topic(result)
            return topic

        return result

    def get_topic_name(self):
        """
        Gets the name of the topic on which message is published.

        :return: The name of the topic on which message is published.
        :rtype: str
        """
        result = self.__args.getTopicName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result
