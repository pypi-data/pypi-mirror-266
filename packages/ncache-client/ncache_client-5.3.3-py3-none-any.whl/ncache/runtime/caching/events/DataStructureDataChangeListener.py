from ncache.client.datastructures.DataStructureEventArg import DataStructureEventArg
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster


@JImplements(environment.get("DataStructureDataChangeListener"), deferred=True)
class DataStructureDataChangeListener:
    def __init__(self, callablefunction):
        self.__callablefunction = callablefunction

    @JOverride
    def onDataStructureChanged(self, collectionname, collectioneventargs):
        collectionname = TypeCaster.to_python_primitive_type(collectionname)
        args = DataStructureEventArg(collectioneventargs)

        self.__callablefunction(collectionname, args)
