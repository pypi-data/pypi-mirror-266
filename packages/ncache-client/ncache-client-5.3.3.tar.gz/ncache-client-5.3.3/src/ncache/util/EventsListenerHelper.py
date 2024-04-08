from ncache.client.enum.CacheStatusNotificationType import CacheStatusNotificationType
from ncache.client.enum.EventType import EventType
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.JavaInstancesFactory import *


class EventsListenerHelper:
    registeredlisteners = {}

    @staticmethod
    def get_listener(callablefunction, listenerclass):
        listenerkey = callablefunction.__qualname__

        if listenerkey in EventsListenerHelper.registeredlisteners:
            return EventsListenerHelper.registeredlisteners[listenerkey][0]
        else:
            listener = listenerclass(callablefunction)

            EventsListenerHelper.registeredlisteners[listenerkey] = (listener, callablefunction)
            return listener

    @staticmethod
    def get_event_type_enum_set(pythoneventtypes):
        javaenumset = jp.java.util.EnumSet.allOf(JavaInstancesFactory.get_java_instance("EventType"))
        javaenumset.clear()

        for item in pythoneventtypes:
            javaenumset.add(EnumUtil.get_event_type(item.value))

        return javaenumset

    @staticmethod
    def get_event_type_list(javaeventenumset):
        pythoneventtypes = []

        for enum in javaeventenumset:
            pythoneventtypes.append(EventType(int(enum.getValue())))

        return pythoneventtypes

    @staticmethod
    def get_status_notification_type_enum_set(pythonstatusnotificationtypes):
        javaenumset = jp.java.util.EnumSet.allOf(JavaInstancesFactory.get_java_instance("CacheStatusNotificationType"))
        javaenumset.clear()

        for item in pythonstatusnotificationtypes:
            javaenumset.add(EnumUtil.get_cache_status_notification_type(item))

        return javaenumset

    @staticmethod
    def get_status_notification_type_list(javaeventenumset):
        pythoneventtypes = []

        for enum in javaeventenumset:
            pythoneventtypes.append(CacheStatusNotificationType(int(enum.getValue())))

        return pythoneventtypes
