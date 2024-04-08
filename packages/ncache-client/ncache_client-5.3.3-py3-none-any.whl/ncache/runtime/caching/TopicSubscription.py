from collections import Callable

from ncache.runtime.caching.events.MessageReceivedListener import MessageReceivedListener
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.ValidateType import ValidateType


class TopicSubscription:
    """
    NCache provides TopicSubscription class which is returned against the desired topic,containing information for
    topic subscriptions.
    """
    def __init__(self, value):
        self.__topicsubscription = value

    def get_instance(self):
        return self.__topicsubscription

    def set_instance(self, value):
        self.__topicsubscription = value

    def add_message_received_listener(self, messagereceivedlistener):
        """
        Event to register subscriber against the topic so that it can receive the published messages.

        :param messagereceivedlistener: The listener function that is invoked whenever a message is received. This
            function should follow this signature: message_received_listener(sender: object, args: MessageEventArgs)
        :type messagereceivedlistener: Callable
        """
        ValidateType.params_check(messagereceivedlistener, 2, self.add_message_received_listener)

        eventlistener = EventsListenerHelper.get_listener(messagereceivedlistener, MessageReceivedListener)
        self.__topicsubscription.addMessageReceivedListener(eventlistener)

    def get_topic(self):
        """
        Retrieves Topic instance containing information about the topic.

        :return: Topic instance of the topic.
        :rtype: Topic
        """
        result = self.__topicsubscription.getTopic()

        if result is not None:
            from ncache.runtime.caching.Topic import Topic
            return Topic(result)

    def remove_message_received_listener(self, messagereceivedlistener):
        """
        Unregisters the user for message received event.

        :param messagereceivedlistener: The registered message received listener function.
        :type messagereceivedlistener: Callable
        """
        ValidateType.params_check(messagereceivedlistener, 2, self.remove_message_received_listener)

        listener = EventsListenerHelper.get_listener(messagereceivedlistener, MessageReceivedListener)
        self.__topicsubscription.removeMessageReceivedListener(listener)

    def un_subscribe(self):
        """
        Unsubscribes the subscription to this topic.
        """
        self.__topicsubscription.unSubscribe()
