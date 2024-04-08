from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("CacheClearedListener"), deferred=True)
class CacheClearedListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onCacheCleared(self):
        self.__callablefunction()
