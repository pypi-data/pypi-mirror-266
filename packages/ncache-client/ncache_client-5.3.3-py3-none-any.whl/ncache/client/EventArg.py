from ncache.client.EventCacheItem import EventCacheItem
from ncache.client.enum import EventType
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class EventArg:
    def __init__(self, args):
        self.__arg = args

    def get_old_item(self):
        """
        Only applicable for EventType.ITEM_UPDATED. Otherwise it will be None.

        :return: The value of the item before updation.
        :rtype: EventCacheItem
        """
        result = self.__arg.getOldItem()

        if result is not None:
            event_cache_item = EventCacheItem(result)

            result = event_cache_item

        return result

    def get_cache_name(self):
        """
        Name of the cache the event is raised against.

        :return: The name of the cache.
        :rtype: str
        """
        result = self.__arg.getCacheName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_event_type(self):
        """
        Event Type the event is raised against.

        :return: The event type associated with the EventArgs.
        :rtype: EventType
        """
        result = self.__arg.getEventType()

        if result is not None:
            result = EnumUtil.get_event_type_value(result)

        return result

    def get_item(self):
        """
        Contains the item if the event was registered against EventDataFilter.META_DATA or EventDataFilter.DATA_WITH_META_DATA

        :return: The EventCacheItem instance.
        :rtype: EventCacheItem
        """
        result = self.__arg.getItem()

        if result is not None:
            item = EventCacheItem(result)

            result = item

        return result
