from ncache.util.JavaInstancesFactory import *


@JImplements(environment.get("QueryDataModificationListener"), deferred=True)
class QueryDataModificationListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onQueryDataModified(self, key, cqeventargs):
        from ncache.client.CQEventArg import CQEventArg

        cqeventargs = CQEventArg(cqeventargs)
        self.__callablefunction(str(key), cqeventargs)
