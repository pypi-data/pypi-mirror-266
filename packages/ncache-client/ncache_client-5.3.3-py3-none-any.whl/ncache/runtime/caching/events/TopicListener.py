from ncache.runtime.caching.MessageFailedEventArgs import MessageFailedEventArgs
from ncache.runtime.caching.TopicDeleteEventArgs import TopicDeleteEventArgs
from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("TopicListener"), deferred=True)
class TopicListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onTopicDeleted(self, sender, args):
        from ncache.runtime.caching.TopicSubscription import TopicSubscription

        sen = TopicSubscription(sender)
        arg = TopicDeleteEventArgs(args)

        self.__callablefunction(sen, arg)

    @JOverride
    def onMessageDeliveryFailure(self, sender, args):
        from ncache.runtime.caching.TopicSubscription import TopicSubscription

        sen = TopicSubscription(sender)
        arg = MessageFailedEventArgs(args)

        self.__callablefunction(sen, arg)
