import asyncio
from asyncio import Task
from collections import Callable

from ncache.client.CacheEventDescriptor import CacheEventDescriptor
from ncache.client.ContinuousQuery import ContinuousQuery
from ncache.client.enum.EventDataFilter import EventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.client.enum.TopicPriority import TopicPriority
from ncache.client.enum.TopicSearchOptions import TopicSearchOptions
from ncache.runtime.caching.Topic import Topic
from ncache.runtime.caching.events.CacheDataModificationListener import CacheDataModificationListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class MessagingService:
    """
    This class contains properties and methods required for Messaging Service.
    """
    def __init__(self, value):
        self.__messagingservice = value

    def get_topic(self, topicname, searchoptions=None):
        """
        Retrieves the topic instance against the TopicSearchOptions and provided name or pattern.

        :param topicname: Name or pattern to identify topic.
        :type topicname: str
        :param searchoptions: TopicSearchOptions specifies to search topic by name or pattern.
        :type searchoptions: TopicSearchOptions
        :return: Returns the topic instance, None if it does not exist.
        :rtype: Topic or None
        """
        ValidateType.is_string(topicname, self.get_topic)
        javatopicname = TypeCaster.to_java_primitive_type(topicname)

        if searchoptions is not None:
            ValidateType.type_check(searchoptions, TopicSearchOptions, self.get_topic)
            javasearchoptions = EnumUtil.get_topic_search_options(searchoptions.value)

            result = self.__messagingservice.getTopic(javatopicname, javasearchoptions)

        else:
            result = self.__messagingservice.getTopic(javatopicname)

        if result is not None:
            result = Topic(result)

        return result

    def create_topic(self, topicname, topicpriority=None):
        """
        Creates and retrieves the topic instance against the specified topic name and priority.

        :param topicname: Name or pattern to identify topic.
        :type topicname: str
        :param topicpriority: Specifies the relative priority of the topic stored in cache.
        :type topicpriority: TopicPriority
        :return: The topic instance.
        :rtype: Topic
        """
        ValidateType.is_string(topicname, self.create_topic)
        javatopicname = TypeCaster.to_java_primitive_type(topicname)

        if topicpriority is not None:
            ValidateType.type_check(topicpriority, TopicPriority, self.create_topic)
            javatopicpriority = EnumUtil.get_topic_priority(topicpriority.value)

            result = self.__messagingservice.createTopic(javatopicname, javatopicpriority)

        else:
            result = self.__messagingservice.createTopic(javatopicname)

        if result is not None:
            result = Topic(result)

        return result

    def delete_topic(self, topicname):
        """
        Deletes the topic instance against the specified topic name.

        :param topicname: Name or pattern to identify topic.
        :type topicname: str
        """
        ValidateType.is_string(topicname, self.delete_topic)
        javatopicname = TypeCaster.to_java_primitive_type(topicname)

        self.__messagingservice.deleteTopic(javatopicname)

    def delete_topic_async(self, topicname):
        """
        Deletes the topic instance asynchronously against the specified topic name.

        :param topicname: Name or pattern to identify topic.
        :type topicname: str
        :return: Future task that performs a delete topic operation in background.Methods of Task can be used to
            determine status of the task.
        :rtype: Task
        """
        ValidateType.is_string(topicname, self.delete_topic_async)
        return asyncio.create_task(self.__return_coroutine(self.delete_topic, topicname))

    def register_cq(self, query):
        """
        Registers the specified continuous query with the cache server. You can use this method multiple times in your
        application depending on its need to receive the notifications for a change in the dataset of your query. This
        method takes as argument an object of ContinuousQuery which has the query and the listeners registered to it.

        :param query: SQL-like query to be executed on cache.
        :type query: ContinuousQuery
        """
        ValidateType.type_check(query, ContinuousQuery, self.register_cq)

        self.__messagingservice.registerCQ(query.get_instance())

    def un_register_cq(self, query):
        """
        Unregisters an already registered continuous query to deactivate it on the cache server. Like registerCQ, it
        takes as argument an object of ContinuousQuery to unregister the listeners which are no more fired after this
        call.

        :param query: SQL-like query to be executed on cache.
        :type query: ContinuousQuery
        """
        ValidateType.type_check(query, ContinuousQuery, self.un_register_cq)

        self.__messagingservice.unRegisterCQ(query.get_instance())

    def add_cache_notification_listener(self, callablefunction, eventtypes, eventdatafilter, keys=None):
        """
        Registers cache notification EventType of type item added, updated or removed against specified key(s) in cache.
        Notification is register against all the keys if no key is specified.

        :param callablefunction: Callable function to be invoked when an item is updated or removed. This
            function should follow this signature: callablefunction(key: str, eventarg: CacheEventArg)
        :type callablefunction: Callable
        :param eventtypes: List of Event types the listener is registered against.
        :type eventtypes: list
        :param eventdatafilter: Tells whether to receive metadata, data with metadata or none when a notification is
            triggered.
        :type eventdatafilter: EventDataFilter
        :param keys: Key or list of keys to identify the cache item.
        :type keys: list or str
        :return: Instance of CacheEventDescriptor if no key is specified. it is required to unregister the notifications.
        :rtype: CacheEventDescriptor or None
        """
        ValidateType.params_check(callablefunction, 2, self.add_cache_notification_listener)
        ValidateType.type_check(eventtypes, list, self.add_cache_notification_listener)
        for eventtype in eventtypes:
            ValidateType.type_check(eventtype, EventType, self.add_cache_notification_listener)
        ValidateType.type_check(eventdatafilter, EventDataFilter, self.add_cache_notification_listener)

        eventlistener = EventsListenerHelper.get_listener(callablefunction, CacheDataModificationListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        javaeventdatafilter = EnumUtil.get_event_data_filter(eventdatafilter.value)

        if keys is not None:
            if type(keys) is str:
                javakey = TypeCaster.to_java_primitive_type(keys)

                self.__messagingservice.addCacheNotificationListener(javakey, eventlistener, javaeventtypes, javaeventdatafilter)
                return

            elif type(keys) is list:
                for key in keys:
                    ValidateType.is_string(key, self.add_cache_notification_listener)

                javakeys = TypeCaster.to_java_array_list(keys, isjavatype=True)

                self.__messagingservice.addCacheNotificationListener(javakeys, eventlistener, javaeventtypes, javaeventdatafilter)
                return

            else:
                raise TypeError(ExceptionHandler.get_invalid_keys_exception_message(self.add_cache_notification_listener))

        else:
            result = self.__messagingservice.addCacheNotificationListener(eventlistener, javaeventtypes, javaeventdatafilter)

            if result is not None:
                descriptor = CacheEventDescriptor(result)
                return descriptor

    def remove_cache_notification_listener(self, descriptor=None, keys=None, callablefunction=None, eventtypes=None):
        """
        Unregisters cache notification against specified key(s) in cache. If no key is specified, this method
        unregisters a cache level event that may have been registered.

        :param descriptor: The descriptor returned when the general event was registered.
        :type descriptor: CacheEventDescriptor
        :param keys: Key or list of keys to identify the cache item.
        :type keys: list or str
        :param callablefunction: Callable function that is invoked when specified event(s) are triggered in cache.
        :type callablefunction: Callable
        :param eventtypes: List of Event types the listener is registered against.
        :type eventtypes: list
        """
        if descriptor is not None and eventtypes is None and callablefunction is None and keys is None:
            ValidateType.type_check(descriptor, CacheEventDescriptor, self.remove_cache_notification_listener)
            javadescriptor = descriptor.get_instance()

            self.__messagingservice.removeCacheNotificationListener(javadescriptor)
            return

        elif eventtypes is not None and callablefunction is not None and keys is not None:
            ValidateType.params_check(callablefunction, 2, self.add_cache_notification_listener)
            ValidateType.type_check(eventtypes, list, self.add_cache_notification_listener)
            for eventtype in eventtypes:
                ValidateType.type_check(eventtype, EventType, self.add_cache_notification_listener)

            eventlistener = EventsListenerHelper.get_listener(callablefunction, CacheDataModificationListener)
            javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)

            if type(keys) is str:
                javakey = TypeCaster.to_java_primitive_type(keys)

                self.__messagingservice.removeCacheNotificationListener(javakey, eventlistener, javaeventtypes)
                return

            elif type(keys) is list:
                for key in keys:
                    ValidateType.is_string(key, self.remove_cache_notification_listener)

                javakeys = TypeCaster.to_java_array_list(keys, isjavatype=True)

                self.__messagingservice.removeCacheNotificationListener(javakeys, eventlistener, javaeventtypes)
                return

            else:
                raise TypeError(ExceptionHandler.get_invalid_keys_exception_message(self.remove_cache_notification_listener))

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("MessagingService.remove_cache_notification_listener"))

    @staticmethod
    async def __return_coroutine(function, arg):
        return function(arg)
        # For the time being, we have only 1 possible argument. This function has to be made generic if needed in future.
