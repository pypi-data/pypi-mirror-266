import collections

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.client.datastructures.Counter import Counter
from ncache.client.datastructures.DataStructureAttributes import DataStructureAttributes
from ncache.client.datastructures.DistributedDictionary import DistributedDictionary
from ncache.client.datastructures.DistributedHashSet import DistributedHashSet
from ncache.client.datastructures.DistributedList import DistributedList
from ncache.client.datastructures.DistributedQueue import DistributedQueue
from ncache.runtime.ReadThruOptions import ReadThruOptions
from ncache.runtime.WriteThruOptions import WriteThruOptions
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DataStructureManager:
    """
    This class contains create and get operations for the Counter and remove operation for all distributed data
    structures.
    """
    def __init__(self, value):
        """
        Initializes a new instance of DataStructureManager class
        """
        self.__manager = value

    def get_instance(self):
        return self.__manager

    def set_instance(self, value):
        self.__manager = value

    def create_counter(self, key, initialvalue=None, attributes=None, options=None):
        """
        Creates the counter against the provided key.

        :param key: Unique identifier for counter object.
        :type key: str
        :param initialvalue: Starting index of counter object.
        :type initialvalue: int
        :param attributes: DataStructureAttributes for providing user configuration for this collection.
        :type attributes: DataStructureAttributes
        :param options: WriteThruOptions regarding updating data source. This can be WriteThru, WriteBehind or None.
        :type options: WriteThruOptions
        :return: Interface for using counters.
        :rtype: Counter
        """
        ValidateType.is_string(key, self.create_counter)
        javakey = TypeCaster.to_java_primitive_type(key)

        result = None
        if initialvalue is not None:
            ValidateType.is_int(initialvalue, self.create_counter)
            javainitialvalue = TypeCaster.to_java_long(initialvalue)

            if attributes is not None and options is not None:
                ValidateType.type_check(attributes, DataStructureAttributes, self.create_counter)
                ValidateType.type_check(options, WriteThruOptions, self.create_counter)

                javaattributes = attributes.get_instance()
                javaoptions = options.get_instance()

                result = self.__manager.createCounter(javakey, javaattributes, javainitialvalue, javaoptions)
            elif attributes is None and options is None:
                result = self.__manager.createCounter(javakey, javainitialvalue)
            else:
                raise ValueError(ExceptionHandler.exceptionmessages.get("DataStructureManager.create_counter"))

        elif initialvalue is None and attributes is None and options is None:
            result = self.__manager.createCounter(javakey)

        if result is not None:
            counter = Counter()
            counter.set_instance(result)
            return counter
        else:
            return None

    def create_hashset(self, key, objtype, datastructureattributes=None, writethruoptions=None):
        """
        Creates distributed set against the provided collection name and configures it according to the provided user
        configuration as attributes of collection.

        :param key: Key of collection to be created.
        :type key: str
        :param objtype: Type of set items. Can only be primitive type.
        :type objtype: type
        :param datastructureattributes: DataStructureAttributes for providing user configuration for this collection.
        :type datastructureattributes: DataStructureAttributes
        :param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru,
            WriteBehind or None.
        :type writethruoptions: WriteThruOptions
        :return: Interface for using set.
        :rtype: DistributedHashSet
        """
        ValidateType.is_string(key, self.create_hashset)
        ValidateType.type_check(objtype, type, self.create_hashset)

        javakey = TypeCaster.to_java_primitive_type(key)
        isjsonobject = False
        pythontype, dstype = TypeCaster.is_java_primitive(objtype)

        if dstype is None:
            raise TypeError(ExceptionHandler.exceptionmessages.get("InvalidHashSet"))

        if datastructureattributes is not None and writethruoptions is not None:
            ValidateType.type_check(datastructureattributes, DataStructureAttributes, self.create_hashset)
            ValidateType.type_check(writethruoptions, WriteThruOptions, self.create_hashset)

            javadatastructureattributes = datastructureattributes.get_instance()
            javawritethruoptions = writethruoptions.get_instance()

            result = self.__manager.createHashSet(javakey, javadatastructureattributes, javawritethruoptions, dstype)

        elif datastructureattributes is None and writethruoptions is None:
            result = self.__manager.createHashSet(javakey, dstype)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("DataStructureManager.create_hashset"))

        if result is not None:
            hashset = DistributedHashSet(objtype, isjsonobject)
            hashset.set_instance(result)

            return hashset

    def create_list(self, key, objtype, datastructureattributes=None, writethruoptions=None):
        """
        Creates distributed list against the provided collection name and configures it according to the provided user
        configuration as attributes of collection.

        :param key: Key of collection to be created.
        :type key: str
        :param objtype: Type of list items.
        :type objtype: type
        :param datastructureattributes: DataStructureAttributes for providing user configuration for this collection.
        :type datastructureattributes: DataStructureAttributes
        :param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru,
            WriteBehind or None.
        :type writethruoptions: WriteThruOptions
        :return: Interface for using list.
        :rtype: DistributedList
        """
        ValidateType.is_string(key, self.create_list)
        ValidateType.type_check(objtype, type, self.create_list)

        javakey = TypeCaster.to_java_primitive_type(key)

        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif issubclass(objtype, collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if datastructureattributes is not None and writethruoptions is not None:
            ValidateType.type_check(datastructureattributes, DataStructureAttributes, self.create_list)
            ValidateType.type_check(writethruoptions, WriteThruOptions, self.create_list)

            javadatastructureattributes = datastructureattributes.get_instance()
            javawritethruoptions = writethruoptions.get_instance()

            result = self.__manager.createList(javakey, javadatastructureattributes, javawritethruoptions, dstype)

        elif datastructureattributes is None and writethruoptions is None:
            result = self.__manager.createList(javakey, dstype)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("DataStructureManager.create_list"))

        if result is not None:
            nclist = DistributedList(objtype, isjsonobject)
            nclist.set_instance(result)

            return nclist

    def create_dictionary(self, key, objtype, datastructureattributes=None, writethruoptions=None):
        """
        Creates distributed Dictionary against the provided collection name and configures it according to the provided user
        configuration as attributes of collection.

        :param key: Key of collection to be created.
        :type key: str
        :param objtype: Type of dictionary values.
        :type objtype: type
        :param datastructureattributes: DataStructureAttributes for providing user configuration for this collection.
        :type datastructureattributes: DataStructureAttributes
        :param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru,
            WriteBehind or None.
        :type writethruoptions: WriteThruOptions
        :return: Interface for using dictionary.
        :rtype: DistributedDictionary
        """
        ValidateType.is_string(key, self.create_dictionary)
        ValidateType.type_check(objtype, type, self.create_dictionary)

        javakey = TypeCaster.to_java_primitive_type(key)
        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif isinstance(objtype(), collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if datastructureattributes is not None and writethruoptions is not None:
            ValidateType.type_check(datastructureattributes, DataStructureAttributes, self.create_dictionary)
            ValidateType.type_check(writethruoptions, WriteThruOptions, self.create_dictionary)

            javadatastructureattributes = datastructureattributes.get_instance()
            javawritethruoptions = writethruoptions.get_instance()

            result = self.__manager.createMap(javakey, javadatastructureattributes, javawritethruoptions, dstype)

        elif datastructureattributes is None and writethruoptions is None:
            result = self.__manager.createMap(javakey, dstype)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("DataStructureManager.create_dictionary"))

        if result is not None:
            ncdictionary = DistributedDictionary(objtype, isjsonobject)
            ncdictionary.set_instance(result)

            return ncdictionary

    def create_queue(self, key, objtype, datastructureattributes=None, writethruoptions=None):
        """
        Creates distributed Queue against the provided collection name and configures it according to the provided user
        configuration as attributes of collection.

        :param key: Key of collection to be created.
        :type key: str
        :param objtype: Type of queue items.
        :type objtype: type
        :param datastructureattributes: DataStructureAttributes for providing user configuration for this collection.
        :type datastructureattributes: DataStructureAttributes
        :param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru,
            WriteBehind or None.
        :type writethruoptions: WriteThruOptions
        :return: Interface for using queue.
        :rtype: DistributedQueue
        """
        ValidateType.is_string(key, self.create_queue)
        ValidateType.type_check(objtype, type, self.create_queue)

        javakey = TypeCaster.to_java_primitive_type(key)
        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif isinstance(objtype(), collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if datastructureattributes is not None and writethruoptions is not None:
            ValidateType.type_check(datastructureattributes, DataStructureAttributes, self.create_queue)
            ValidateType.type_check(writethruoptions, WriteThruOptions, self.create_queue)

            javadatastructureattributes = datastructureattributes.get_instance()
            javawritethruoptions = writethruoptions.get_instance()

            result = self.__manager.createQueue(javakey, javadatastructureattributes, javawritethruoptions, dstype)

        elif datastructureattributes is None and writethruoptions is None:
            result = self.__manager.createQueue(javakey, dstype)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("DataStructureManager.create_queue"))

        if result is not None:
            ncqueue = DistributedQueue(objtype, isjsonobject)
            ncqueue.set_instance(result)

            return ncqueue

    def get_counter(self, key, readthruoptions=None):
        """
        Gets Counter interface against the provided key.

        :param key: Key of counter.
        :type key: str
        :param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
        :type readthruoptions: ReadThruOptions
        :return: Interface for using counters.
        :rtype: Counter
        """
        ValidateType.is_string(key, self.get_counter)
        javakey = TypeCaster.to_java_primitive_type(key)

        if readthruoptions is not None:
            ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_counter)
            javareadthruoptions = readthruoptions.get_instance()

            result = self.__manager.getCounter(javakey, javareadthruoptions)

        else:
            result = self.__manager.getCounter(javakey)

        if result is not None:
            nccounter = Counter()
            nccounter.set_instance(result)

            return nccounter

    def get_hashset(self, key, objtype, readthruoptions=None):
        """
        Gets distributed set interface against the provided collection key.

        :param key: Key of collection.
        :type key: str
        :param objtype: Type of set items.
        :type objtype: type
        :param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
        :type readthruoptions: ReadThruOptions
        :return: Interface for using set.
        :rtype: DistributedHashSet
        """
        ValidateType.is_string(key, self.get_hashset)
        ValidateType.type_check(objtype, type, self.get_hashset)

        isjsonobject = False
        pythontype, dstype = TypeCaster.is_java_primitive(objtype)
        if dstype is None:
            raise TypeError(ExceptionHandler.exceptionmessages.get("InvalidHashSet"))

        javakey = TypeCaster.to_java_primitive_type(key)
        if readthruoptions is not None:
            ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_hashset)
            javareadthruoptions = readthruoptions.get_instance()

            result = self.__manager.getHashSet(javakey, javareadthruoptions, dstype)

        else:
            result = self.__manager.getHashSet(javakey, dstype)

        if result is not None:
            ncset = DistributedHashSet(objtype, isjsonobject)
            ncset.set_instance(result)

            return ncset

    def get_list(self, key, objtype, readthruoptions=None):
        """
        Gets distributed list interface against the provided collection key.

        :param key: Key of collection.
        :type key: str
        :param objtype: Type of list items.
        :type objtype: type
        :param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
        :type readthruoptions: ReadThruOptions
        :return: Interface for using list.
        :rtype: DistributedList
        """
        ValidateType.is_string(key, self.get_list)
        ValidateType.type_check(objtype, type, self.get_list)

        javakey = TypeCaster.to_java_primitive_type(key)

        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif isinstance(objtype(), collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if readthruoptions is not None:
            ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_list)
            javareadthruoptions = readthruoptions.get_instance()

            result = self.__manager.getList(javakey, javareadthruoptions, dstype)

        else:
            result = self.__manager.getList(javakey, dstype)

        if result is not None:
            nclist = DistributedList(objtype, isjsonobject)
            nclist.set_instance(result)

            return nclist

    def get_dictionary(self, key, objtype, readthruoptions=None):
        """
        Gets distributed dictionary interface against the provided collection key.

        :param key: Key of collection.
        :type key: str
        :param objtype: Type of dictionary values.
        :type objtype: type
        :param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
        :type readthruoptions: ReadThruOptions
        :return: Interface for using dictionary.
        :rtype: DistributedDictionary
        """
        ValidateType.is_string(key, self.get_dictionary)
        ValidateType.type_check(objtype, type, self.get_dictionary)

        javakey = TypeCaster.to_java_primitive_type(key)

        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif isinstance(objtype(), collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if readthruoptions is not None:
            ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_dictionary)
            javareadthruoptions = readthruoptions.get_instance()

            result = self.__manager.getMap(javakey, javareadthruoptions, dstype)

        else:
            result = self.__manager.getMap(javakey, dstype)

        if result is not None:
            ncdictionary = DistributedDictionary(objtype, isjsonobject)
            ncdictionary.set_instance(result)

            return ncdictionary

    def get_queue(self, key, objtype, readthruoptions=None):
        """
        Gets distributed queue interface against the provided collection key.

        :param key: Key of collection.
        :type key: str
        :param objtype: Type of queue items.
        :type objtype: type
        :param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
        :type readthruoptions: ReadThruOptions
        :return: Interface for using queue.
        :rtype: DistributedQueue
        """
        ValidateType.is_string(key, self.get_queue)
        ValidateType.type_check(objtype, type, self.get_queue)

        javakey = TypeCaster.to_java_primitive_type(key)

        if objtype is int or objtype is str or objtype is bool or objtype is float:
            dstype = JavaInstancesFactory.get_java_instance("JsonValue")
            isjsonobject = False
        elif isinstance(objtype(), collections.Collection):
            dstype = JavaInstancesFactory.get_java_instance("JsonArray")
            isjsonobject = True
        else:
            dstype = JavaInstancesFactory.get_java_instance("JsonObject")
            isjsonobject = True

        if readthruoptions is not None:
            ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_queue)
            javareadthruoptions = readthruoptions.get_instance()

            result = self.__manager.getQueue(javakey, javareadthruoptions, dstype)

        else:
            result = self.__manager.getQueue(javakey, dstype)

        if result is not None:
            ncqueue = DistributedQueue(objtype, isjsonobject)
            ncqueue.set_instance(result)

            return ncqueue

    def remove(self, key, writethruoptions=None):
        """
        Remove the specified data structure.

        :param key: Key of the data type.
        :type key: str
        :param writethruoptions: WriteThruOptions regarding updating data source. This can be WriteThru, WriteBehind or
            None.
        :type writethruoptions: WriteThruOptions
        """
        ValidateType.is_string(key, self.remove)
        javakey = TypeCaster.to_java_primitive_type(key)

        if writethruoptions is not None:
            ValidateType.type_check(writethruoptions, WriteThruOptions, self.remove)
            javawritethruoptions = writethruoptions.get_instance()

            self.__manager.remove(javakey, javawritethruoptions)

        else:
            self.__manager.remove(javakey)
