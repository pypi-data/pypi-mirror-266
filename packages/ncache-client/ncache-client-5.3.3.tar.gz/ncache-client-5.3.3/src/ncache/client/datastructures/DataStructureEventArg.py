from ncache.client.enum.DistributedDataStructure import DistributedDataStructure
from ncache.client.enum.EventType import EventType
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class DataStructureEventArg:
    """
     This object is received when a collection event listener function is called. This class contains necessary
     information to identify the event and perform necessary actions accordingly.
     """
    def __init__(self, value):
        """
        Constructor that initializes the instance of this class.

        :param value: Instance of DataStructureEventArg class received from Cache
        """
        self.__datastructureeventarg = value

    def get_instance(self):
        return self.__datastructureeventarg

    def get_cache_name(self):
        """
        Gets the name of cache the collection event is registered against.

        :return: The name of cache the collection event is registered against.
        :rtype: str
        """
        result = self.__datastructureeventarg.getCacheName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_collection_item(self):
        """
        Gets the current collection item.

        :return: The current collection item.
        :rtype: object
        """
        result = self.__datastructureeventarg.getCollectionItem()

        collectionitem = None
        if result is not None:
            collectionitem = TypeCaster.to_python_primitive_type(result)
            if collectionitem is None:
                collectionitem = TypeCaster.deserialize(result)

        return collectionitem

    def get_collection_type(self):
        """
        The type of collection, pertaining to DistributedDataStructure, returned on fire of collection event.

        :return: The DistributedDataStructure enum.
        :rtype: DistributedDataStructure
        """
        collectiontype = self.__datastructureeventarg.getCollectionType()

        if collectiontype is not None:
            collectiontype = EnumUtil.get_collection_type_value(collectiontype)

        return collectiontype

    def get_event_type(self):
        """
        Gets the type of the event.

        :return: The EventType enum.
        :rtype: EventType
        """
        eventtype = self.__datastructureeventarg.getEventType()

        if eventtype is not None:
            eventtype = EnumUtil.get_event_type_value(eventtype)

        return eventtype

    def get_old_collection_item(self):
        """
        Gets the previous value of the collection item. This is only populated in case of update operation.

        :return: The previous value of the collection item.
        :rtype: object or None
        """
        result = self.__datastructureeventarg.getOldCollectionItem()

        oldcollectionitem = None
        if result is not None:
            oldcollectionitem = TypeCaster.to_python_primitive_type(result)
            if oldcollectionitem is None:
                oldcollectionitem = TypeCaster.deserialize(result)

        return oldcollectionitem
