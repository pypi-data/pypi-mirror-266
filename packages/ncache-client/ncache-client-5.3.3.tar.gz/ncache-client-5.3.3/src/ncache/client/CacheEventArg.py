from ncache.client.CacheEventDescriptor import CacheEventDescriptor
from ncache.client.EventArg import EventArg
from ncache.client.enum.CacheItemRemovedReason import CacheItemRemovedReason
from ncache.client.enum.EventType import EventType
from ncache.runtime.util.EnumUtil import EnumUtil


class CacheEventArg(EventArg):
    """
    This object is received when an event is raised and listener is called. CacheEventArg contains necessary information
    to identify the event and perform necessary actions accordingly. This class is consistent for both selective and
    general events
    """
    def __init__(self, value):
        super().__init__(value)
        self.__cacheeventarg = value

    def get_cache_item_removed_reason(self):
        """
        Only applicable for EventType.ITEM_REMOVE Otherwise default value is DependencyChanged

        :return: The CacheItemRemovedReason enum
        :rtype: CacheItemRemovedReason
        """
        reason = self.__cacheeventarg.getCacheItemRemovedReason()

        if reason is not None:
            reason = EnumUtil.get_cache_item_removed_reason_value(reason)

        return reason

    def get_descriptor(self):
        """
        Only applicable for general events otherwise it will be None

        :return: The descriptor associated with the cache event args.
        :rtype: CacheEventDescriptor or None
        """
        descriptor = self.__cacheeventarg.getDescriptor()
        if descriptor is not None:
            return CacheEventDescriptor(descriptor)

    def get_event_type(self):
        """
        Event Type the event is raised against.

        :return: The event type associated with the EventArgs.
        :rtype: EventType
        """
        eventtype = self.__cacheeventarg.getEventType()

        if eventtype is not None:
            eventtype = EnumUtil.get_event_type_value(eventtype)

        return eventtype
