import asyncio
from asyncio import Task
from collections import Callable

from ncache.util.JavaInstancesFactory import *
from ncache.client.enum.DeliveryMode import DeliveryMode
from ncache.client.enum.DeliveryOption import DeliveryOption
from ncache.client.enum.SubscriptionPolicy import SubscriptionPolicy
from ncache.client.enum.TopicPriority import TopicPriority
from ncache.client.enum.TopicSearchOptions import TopicSearchOptions
from ncache.runtime.caching.Message import Message
from ncache.runtime.caching.TopicSubscription import TopicSubscription
from ncache.runtime.caching.events.MessageReceivedListener import MessageReceivedListener
from ncache.runtime.caching.events.TopicListener import TopicListener
from ncache.runtime.caching.messaging.DurableTopicSubscription import DurableTopicSubscription
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class Topic:
    """
    The Topic interface facilitates creating subscription and publishing of messages against the topic. This also
    provides event registrations for message delivery failure, receiving messages and deleting topics.
    """
    def __init__(self, value):
        self.__topic = value

    def get_instance(self):
        return self.__topic

    def set_instance(self, value):
        self.__topic = value

    def add_message_delivery_failure_listener(self, messagefailedeventlistener):
        """
        This method registers for message delivery failure events on this topic.

        :param messagefailedeventlistener: The listener that is invoked whenever there is failure in message delivery.
            This function should follow this signature: message_failed_event_listener(sender: object, args: MessageFailedEventArgs)
        :type messagefailedeventlistener: Callable
        """
        ValidateType.params_check(messagefailedeventlistener, 2, self.add_message_delivery_failure_listener)

        eventlistener = EventsListenerHelper.get_listener(messagefailedeventlistener, TopicListener)
        self.__topic.addMessageDeliveryFailureListener(eventlistener)

    def add_topic_deleted_listener(self, topicdeletedlistener):
        """
        This method registers for topic deleted event.

        :param topicdeletedlistener: The listener function that is invoked whenever this topic is deleted. This function
            should follow this signature: message_failed_event_listener(sender: TopicListener, args: TopicDeleteEventArgs)
        :type topicdeletedlistener: Callable
        """

        ValidateType.params_check(topicdeletedlistener, 2, self.add_topic_deleted_listener)

        eventlistener = EventsListenerHelper.get_listener(topicdeletedlistener, TopicListener)
        self.__topic.addTopicDeletedListener(eventlistener)

    def create_durable_subscription(self, subscriptionname, subscriptionpolicy, messagereceivedlistener, expirationtime, deliverymode=None):
        """
        This method is used to create a durable subscription to this topic.

        :param subscriptionname: Name of the durable subscription.
        :type subscriptionname: str
        :param subscriptionpolicy: Policy that is subscription is Shared or Exclusive.
        :type subscriptionpolicy: SubscriptionPolicy
        :param messagereceivedlistener: Message is delivered to registered user through this listener function. This
            function should follow this signature: message_received_listener(sender: TopicListener, args: MessageEventArgs)
        :type messagereceivedlistener: Callable
        :param expirationtime: A timespan that specifies the expiration time of the subscription.
        :type expirationtime: TimeSpan
        :param deliverymode: Specifies whether to deliver messages to register subscribers synchronously or asynchronously.
        :type deliverymode: DeliveryMode
        :return: Instance of DurableTopicSubscription.
        :rtype: DurableTopicSubscription
        """
        ValidateType.is_string(subscriptionname, self.create_durable_subscription)
        ValidateType.type_check(subscriptionpolicy, SubscriptionPolicy, self.create_durable_subscription)
        ValidateType.params_check(messagereceivedlistener, 2, self.create_durable_subscription)
        ValidateType.type_check(expirationtime, TimeSpan, self.create_durable_subscription)

        javasubscriptionname = TypeCaster.to_java_primitive_type(subscriptionname)
        javasubscriptionpolicy = EnumUtil.get_subscription_policy(subscriptionpolicy.value)
        javaexpirationtime = expirationtime.get_instance()
        eventlistener = EventsListenerHelper.get_listener(messagereceivedlistener, MessageReceivedListener)

        if deliverymode is not None:
            ValidateType.type_check(deliverymode, DeliveryMode, self.create_durable_subscription)
            javadeliverymode = EnumUtil.get_delivery_mode(deliverymode.name)

            result = self.__topic.createDurableSubscription(javasubscriptionname, javasubscriptionpolicy, eventlistener, javaexpirationtime, javadeliverymode)

        else:
            result = self.__topic.createDurableSubscription(javasubscriptionname, javasubscriptionpolicy, eventlistener, javaexpirationtime)

        if result is not None:
            result = DurableTopicSubscription(result)
            return result

    def get_is_closed(self):
        """
        Specifies whether topic is closed or not.

        :return: True if topic is closed, otherwise False.
        :rtype: bool
        """
        result = self.__topic.getIsClosed()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_search_options(self):
        """
        Specifies whether user has subscribed to pattern based or simple subscription.

        :return: The topic search options for this topic.
        :rtype: TopicSearchOptions
        """
        result = self.__topic.getSearchOptions()

        if result is not None:
            result = EnumUtil.get_topic_search_options_value(result)

        return result

    def publish(self, message, deliveryoption, notifydeliveryfailure=None, sequencename=None, ):
        """
        This method is used to publish the message to the topic with the specified DeliveryOption and sequence name if
        provided. Order of messages with same sequence name is retained.

        :param message: Message to be published.
        :type message: Message
        :param deliveryoption: Specifies how message is delivered to registered subscribers.
        :type deliveryoption: DeliveryOption
        :param notifydeliveryfailure: Specifies whether MessageDeliveryFailure event is required for this message.
        :type notifydeliveryfailure: bool
        :param sequencename: Sequence name of the message to be published. The messages with same sequence name will be
            delivered in the same order as they are published.
        :type sequencename: str
        """
        ValidateType.type_check(message, Message, self.publish)
        ValidateType.type_check(deliveryoption, DeliveryOption, self.publish)

        javamessage = message.get_instance()
        javadeliveryoption = EnumUtil.get_delivery_option(deliveryoption.value)

        if notifydeliveryfailure is not None and sequencename is not None:
            ValidateType.type_check(notifydeliveryfailure, bool, self.publish)
            ValidateType.is_string(sequencename, self.publish)

            javanotifydeliveryfailure = TypeCaster.to_java_primitive_type(notifydeliveryfailure)
            javasequencename = TypeCaster.to_java_primitive_type(sequencename)

            self.__topic.publish(javamessage, javadeliveryoption, javasequencename, javanotifydeliveryfailure)
            return

        elif notifydeliveryfailure is not None and sequencename is None:
            ValidateType.type_check(notifydeliveryfailure, bool, self.publish)
            javanotifydeliveryfailure = TypeCaster.to_java_primitive_type(notifydeliveryfailure)

            self.__topic.publish(javamessage, javadeliveryoption, javanotifydeliveryfailure)
            return

        elif notifydeliveryfailure is None and sequencename is not None:
            ValidateType.is_string(sequencename, self.publish)
            javasequencename = TypeCaster.to_java_primitive_type(sequencename)

            self.__topic.publish(javamessage, javadeliveryoption, javasequencename)
            return

        elif notifydeliveryfailure is None and sequencename is None:
            self.__topic.publish(javamessage, javadeliveryoption)
            return

    async def publish_async(self, message, deliveryoption, notifydeliveryfailure=None):
        """
        This method is used to Publish a message asynchronously to the topic with specified delivery option.

        :param message: Message to be published.
        :type message: Message
        :param deliveryoption: Specifies how message is delivered to registered subscribers.
        :type deliveryoption: DeliveryOption
        :param notifydeliveryfailure: Specifies whether MessageDeliveryFailure event is required for this message.
        :type notifydeliveryfailure: bool
        :return: Task that performs a publish operation in the background.
        :rtype: Task
        """
        ValidateType.type_check(message, Message, self.publish_async)
        ValidateType.type_check(deliveryoption, DeliveryOption, self.publish_async)

        if notifydeliveryfailure is not None:
            ValidateType.type_check(notifydeliveryfailure, bool, self.publish_async)

            return asyncio.create_task(self.__return_coroutine(self.publish, message, deliveryoption, notifydeliveryfailure))
        return asyncio.create_task(self.__return_coroutine(self.publish, message, deliveryoption))

    def publish_bulk(self, messages, notifydeliveryfailure=None):
        """
        This method is used to Publish messages to the topic with specified DeliveryOption.

        :param messages: Collection of message-deliveryoption pairs in form of a dict.
        :type messages: dict
        :param notifydeliveryfailure: Specifies whether MessageDeliveryFailure event is required for this message.
        :type notifydeliveryfailure: bool
        :return: Dict that contains message along with the exception that occurred while message publishing.
        :rtype: dict
        """
        ValidateType.type_check(messages, dict, self.publish_bulk)
        for message in messages:
            ValidateType.type_check(message, Message, self.publish_bulk)
            ValidateType.type_check(messages[message], DeliveryOption, self.publish_bulk)

        javamessages = self.__publish_bulk_messages_to_hashmap(messages)

        if notifydeliveryfailure is not None:
            ValidateType.type_check(notifydeliveryfailure, bool, self.publish_bulk)
            javanotifydeliveryfailure = TypeCaster.to_java_primitive_type(notifydeliveryfailure)

            result = self.__topic.publishBulk(javamessages, javanotifydeliveryfailure)

        else:
            result = self.__topic.publishBulk(javamessages)

        if result is not None:
            result = self.__publish_bulk_result_to_dict(result)

        return result

    def remove_message_delivery_failure_listener(self):
        """
        This method unregisters for message delivery failure callbacks on this topic.
        """
        self.__topic.removeMessageDeliveryFailureListener()

    def remove_topic_deleted_listener(self):
        """
        This method unregisters for topic deleted event.
        """
        self.__topic.removeTopicDeletedListener()

    def get_name(self):
        """
        Gets the name of the Topic.

        :return: The name of the Topic.
        :rtype: str
        """
        result = self.__topic.getName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_message_count(self):
        """
        Gets the number of messages published for this topic.

        :return: The number of messages published for this topic.
        :rtype: int
        """

        result = self.__topic.getMessageCount()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_priority(self):
        """
        The relative priority of the topic.

        :return: The priority of the topic.
        :rtype: TopicPriority
        """
        result = self.__topic.getPriority()

        if result is not None:
            result = EnumUtil.get_topic_priority_value(result)

        return result

    def get_expiration_time(self):
        """
        Gets the expiry time of message for this topic. Its default value is TimeSpan.MaxValue.

        :return: The expiry time of message for this topic.
        :rtype: TimeSpan
        """
        result = self.__topic.getExpirationTime()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def set_expiration_time(self, timespan):
        """
        Sets the expiry time of message for this topic.

        :param timespan: The expiry time of message for this topic.
        :type timespan: TimeSpan
        """
        ValidateType.type_check(timespan, TimeSpan, self.set_expiration_time)
        javatimespan = timespan.get_instance()

        self.__topic.setExpirationTime(javatimespan)

    def create_subscription(self, messagereceivedeventlistener, deliverymode=None):
        """
        This method is used to subscribe against topic on cache if topic exists.

        :param messagereceivedeventlistener: The callable listener function that is invoked whenever a message is
            published against the topic. This function should follow this signature:
            message_received_listener(sender: object, args: MessageEventArgs)
        :type messagereceivedeventlistener: Callable
        :param deliverymode: Specifies whether to deliver messages to register subscribers synchronously or asynchronously.
        :type deliverymode: DeliveryMode
        :return: The created topic subscription.
        :rtype: TopicSubscription
        """
        ValidateType.params_check(messagereceivedeventlistener, 2, self.create_subscription)
        eventlistener = EventsListenerHelper.get_listener(messagereceivedeventlistener, MessageReceivedListener)

        if deliverymode is not None:
            ValidateType.type_check(deliverymode, DeliveryMode, self.create_subscription)
            javadeliverymode = EnumUtil.get_delivery_mode(deliverymode.name)

            result = self.__topic.createSubscription(eventlistener, javadeliverymode)

        else:
            result = self.__topic.createSubscription(eventlistener)

        if result is not None:
            subscription = TopicSubscription(result)
            return subscription

    def close(self):
        """
        Closes this resource, relinquishing any underlying resources.
        """
        self.__topic.close()

    @staticmethod
    async def __return_coroutine(function, *args):
        if len(args) == 2:
            return function(args[0], args[1])
        else:
            return function(args[0], args[1], args[2])
        # For the time being, we have only 2 or 3 possible arguments. This function has to be made generic if needed in future.

    @staticmethod
    def __publish_bulk_messages_to_hashmap(messagesdict):
        javahashmap = jp.java.util.HashMap()

        for item in messagesdict:
            javamessage = item.get_instance()
            javadeliveryoption = EnumUtil.get_delivery_option(messagesdict[item].value)

            javahashmap.put(javamessage, javadeliveryoption)

        return javahashmap

    @staticmethod
    def __publish_bulk_result_to_dict(javabulkmap):
        pythondict = {}

        for item in javabulkmap:
            key = TypeCaster.to_python_primitive_type(item)
            pythondict[key] = javabulkmap[item]
        return pythondict
