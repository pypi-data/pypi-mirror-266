from ncache.client.enum.EventDataFilter import EventDataFilter
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class CacheEventDescriptor:
    """
    Instance of this class holds the link to the registered delegate. Keep it safe and use it to unregister the
    registered delegate when required. The bool isRegistered returns false when the descriptor has been consumed to
    unregister the delegate. Then this instance can then be disposed of. Upon re-registering for the interested event,
    a new descriptor will be created.
    """
    def __init__(self, value):
        self.__cacheeventdescriptor = value

    def get_instance(self):
        return self.__cacheeventdescriptor

    def set_instance(self, value):
        self.__cacheeventdescriptor = value

    def get_cache_name(self):
        """
        Name of the cache registered against

        :return: Name of the cache registered against
        :rtype: str
        """
        result = self.__cacheeventdescriptor.getCacheName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_data_filter(self):
        """
        Gets the datafilter of the descriptor.

        :return: EventDataFilter value of the descriptor.
        :rtype: EventDataFilter
        """
        result = self.__cacheeventdescriptor.getDataFilter()

        if result is not None:
            result = EnumUtil.get_event_data_filter_value(result)

        return result

    def get_is_registered(self):
        """
        Returns true if the linked event delegate is registered, returns false when the descriptor has been consumed.
        This property is ThreadSafe.

        :return: If descriptor is registered or not.
        :rtype: bool
        """
        result = self.__cacheeventdescriptor.getIsRegistered()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_registered_against(self):
        """
        Gets the Event Types against which the descriptor is registered.

        :return: The list containing all the registered event types.
        :rtype: list
        """
        result = self.__cacheeventdescriptor.getRegisteredAgainst()
        enumlist = []
        if result is not None:
            for res in result:
                enumlist.append(EnumUtil.get_event_type_value(res))
        return enumlist
