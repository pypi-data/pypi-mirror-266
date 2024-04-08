from collections import Callable

from ncache.client.enum.CacheStatusNotificationType import CacheStatusNotificationType
from ncache.runtime.caching.events.CacheClearedListener import CacheClearedListener
from ncache.runtime.caching.events.CacheClientConnectivityChangedListener import CacheClientConnectivityChangedListener
from ncache.runtime.caching.events.CacheStatusEventListener import CacheStatusEventListener
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.ValidateType import ValidateType


class NotificationService:
    """
    This class contains properties and methods required for a Notification Service.
    """
    def __init__(self, value):
        self.__notificationservice = value

    def get_instance(self):
        return self.__notificationservice

    def add_cache_connectivity_changed_listener(self, callablefunction):
        """
        Registers event for notifying the application about the status of cache client connectivity.

        :param callablefunction: The callable listener function that is invoked when client connectivity status changes.
            This function should follow this signature: function(cacheid: str, client: ClientInfo)
        :type callablefunction: Callable
        """
        ValidateType.params_check(callablefunction, 2, self.add_cache_connectivity_changed_listener)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheClientConnectivityChangedListener)

        self.__notificationservice.addCacheConnectivityChangedListener(listener)

    def remove_cache_connectivity_changed_listener(self, callablefunction):
        """
        Unregisters event for notifying the application about the status of cache client connectivity.

        :param callablefunction: The listener function that was registered with client connectivity changed event.
        :type callablefunction: Callable
        """
        ValidateType.params_check(callablefunction, 2, self.remove_cache_connectivity_changed_listener)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheClientConnectivityChangedListener)

        self.__notificationservice.removeCacheConnectivityChangedListener(listener)

    def add_cache_cleared_listener(self, callablefunction):
        """
        Registers event for notifying applications when the cache is cleared.

        :param callablefunction: The callable listener function that is invoked whenever the cache is cleared. This
            function should follow this signature: function()
        :type callablefunction: Callable
        """
        ValidateType.params_check(callablefunction, 0, self.add_cache_cleared_listener)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheClearedListener)

        self.__notificationservice.addCacheClearedListener(listener)

    def remove_cache_cleared_listener(self, callablefunction):
        """
        Unregisters event for notifying applications when the cache is cleared.

        :param callablefunction: The listener that was registered with the cache cleared event.
        :type callablefunction: Callable
        """
        ValidateType.params_check(callablefunction, 0, self.remove_cache_cleared_listener)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheClearedListener)

        self.__notificationservice.removeCacheClearedListener(listener)

    def add_cache_status_event_listener(self, callablefunction, statusnotificationtypes):
        """
        Registers event for notifying applications when a node joins/leaves the cache or when cache is stopped.

        :param callablefunction: The callable listener function that is invoked whenever cache status changes. This
            function should follow this signature: function(event: ClusterEvent)
        :type callablefunction: Callable
        :param statusnotificationtypes: The list that specifies the events that listener is registered with.
        :type statusnotificationtypes: list
        """
        ValidateType.params_check(callablefunction, 1, self.add_cache_status_event_listener)
        ValidateType.type_check(statusnotificationtypes, list, self.add_cache_status_event_listener)
        for statusnotificationtype in statusnotificationtypes:
            ValidateType.type_check(statusnotificationtype, CacheStatusNotificationType, self.add_cache_status_event_listener)

        javastatusnotificationtypes = EventsListenerHelper.get_status_notification_type_enum_set(statusnotificationtypes)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheStatusEventListener)

        self.__notificationservice.addCacheStatusEventListener(listener, javastatusnotificationtypes)

    def remove_cache_status_event_listener(self, callablefunction, statusnotificationtypes):
        """
        Unregisters event for notifying applications when a node joins/lefts the cache or when cache is stopped.

        :param callablefunction: The listener that was registered with cache status event.
        :type callablefunction: Callable
        :param statusnotificationtypes: The list that specifies the events that listener is registered with.
        :type statusnotificationtypes: list
        """
        ValidateType.params_check(callablefunction, 1, self.remove_cache_status_event_listener)
        ValidateType.type_check(statusnotificationtypes, list, self.remove_cache_status_event_listener)
        for statusnotificationtype in statusnotificationtypes:
            ValidateType.type_check(statusnotificationtype, CacheStatusNotificationType,
                                    self.remove_cache_status_event_listener)

        javastatusnotificationtypes = EventsListenerHelper.get_status_notification_type_enum_set(statusnotificationtypes)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheStatusEventListener)

        self.__notificationservice.removeCacheStatusEventListener(listener, javastatusnotificationtypes)
