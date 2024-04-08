from ncache.client.ClientInfo import ClientInfo
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster


@JImplements(environment.get("CacheClientConnectivityChangedListener"), deferred=True)
class CacheClientConnectivityChangedListener:
    def __init__(self, callablefunction):
        self.callablefunction = callablefunction

    @JOverride
    def onClientConnectivityChanged(self, cacheid, clientinfo):
        cacheid = TypeCaster.to_python_primitive_type(cacheid)
        clientinfo = ClientInfo(clientinfo)

        self.callablefunction(cacheid, clientinfo)
