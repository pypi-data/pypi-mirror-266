from ncache.client.CacheItemVersion import CacheItemVersion
from ncache.client.enum.CacheItemPriority import CacheItemPriority
from ncache.client.enum.EntryType import EntryType
from ncache.runtime.caching.datasource.ResyncOptions import ResyncOptions
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class EventCacheItem:
    """
    This is a stripped down version of CacheItem. Contains basic information of an item present in the cache
    """
    def __init__(self, eventcacheitem):
        self.__eventcacheitem = eventcacheitem

    def clone(self):
        """
        Creates and returns a copy of this object.

        :return: Copy of this object.
        :rtype: EventCacheItem
        """
        result = self.__eventcacheitem.clone()

        if result is not None:
            obj = EventCacheItem(result)

            return obj

    def get_instance(self):
        return self.__eventcacheitem

    def set_instance(self, value):
        self.__eventcacheitem = value

    def get_cache_item_priority(self):
        """
        Specifies the CacheItemPriority of the item present in the cache

        :return: CacheItemPriority of the EventCacheItem.
        :rtype: CacheItemPriority
        """
        result = self.__eventcacheitem.getCacheItemPriority()

        enumtype = None
        if result is not None:
            enumtype = EnumUtil.get_cache_item_priority_value(result)

        return enumtype

    def get_cache_item_version(self):
        """
        Item version of the item

        :return: The version associated with the cache item.
        :rtype: CacheItemVersion
        """
        version = self.__eventcacheitem.getCacheItemVersion()

        if version is not None:
            version = CacheItemVersion(int(version.getVersion()))

        return version

    def get_entry_type(self):
        """
        Gets the entry type associated with the EventCacheItem.

        :return: The entry type associated with the EventCacheItem.
        :rtype: EntryType
        """
        result = self.__eventcacheitem.getEntryType()

        if result is not None:
            return EntryType(int(result.getValue()))

    def get_group(self):
        """
        Gets the group associated with the EventCacheItem.

        :return: The group associated with the EventCacheItem.
        :rtype: str
        """
        result = self.__eventcacheitem.getGroup()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_resync_expired_items(self):
        """
        Specifies whether item is to be resynced on expiration or not.

        :return: True if item is to be resynced, otherwise False.
        :rtype: bool
        """
        result = self.__eventcacheitem.getResyncExpiredItems()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_resync_options(self):
        """
        ResyncOptions contain information if items are to be resynced at expiry and readthrough provider name when item
        will be resynced at expiry.

        :return: The ResyncOptions specific to the EventCacheItem.
        :rtype: ResyncOptions
        """
        result = self.__eventcacheitem.getResyncOptions()

        if result is not None:
            options = ResyncOptions(False)
            options.set_instance(result)

            return options

    def get_value(self, objtype):
        """
        Will contain the value present in the cache but only if the event was registered against EventDataFilter.Metadata
        or EventDataFilter.DataWithMetadata otherwise it will be None.

        :param objtype: Specifies the class of value obtained from the EventCacheItem.
        :type objtype: type
        :return: The value stored in EventCacheItem.
        :rtype: object
        """
        ValidateType.type_check(objtype, type, self.get_value)

        pythontype, javatype = TypeCaster.is_java_primitive(objtype)

        if javatype is not None:
            return pythontype(self.__eventcacheitem.getValue(javatype))
        else:
            result = self.__eventcacheitem.getValue(JavaInstancesFactory.get_java_instance("JsonObject"))
            if result is not None:
                return TypeCaster.deserialize(result, objtype, isjsonobject=True)
