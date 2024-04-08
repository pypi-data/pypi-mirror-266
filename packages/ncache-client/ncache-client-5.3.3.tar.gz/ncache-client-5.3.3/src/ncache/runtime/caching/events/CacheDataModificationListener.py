from ncache.client.enum.EventType import EventType
from ncache.util.JavaInstancesFactory import *
from ncache.client.CacheEventArg import CacheEventArg


@JImplements(environment.get("CacheDataModificationListener"), deferred=True)
class CacheDataModificationListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onCacheDataModified(self, key, cacheeventarg):
        eventarg = CacheEventArg(cacheeventarg)
        self.__callablefunction(str(key), eventarg)

    @JOverride
    def onCacheCleared(self, s, cacheeventarg):
        pass
