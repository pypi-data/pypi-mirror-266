from ncache.runtime.caching.MessageEventArgs import MessageEventArgs
from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("MessageReceivedListener"), deferred=True)
class MessageReceivedListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onMessageReceived(self, sender, messageeventargs):
        from ncache.runtime.caching.TopicSubscription import TopicSubscription

        sen = TopicSubscription(sender)
        args = MessageEventArgs(messageeventargs)

        self.__callablefunction(sen, args)
