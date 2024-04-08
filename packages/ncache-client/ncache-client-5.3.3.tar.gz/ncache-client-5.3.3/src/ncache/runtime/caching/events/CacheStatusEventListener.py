from ncache.client.ClusterEvent import ClusterEvent
from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("CacheStatusEventListener"), deferred=True)
class CacheStatusEventListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onCacheStatusChanged(self, javaevent):
        event = ClusterEvent(javaevent)

        self.__callablefunction(event)
