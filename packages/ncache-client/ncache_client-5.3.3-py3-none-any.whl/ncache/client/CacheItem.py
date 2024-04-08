import inspect
from datetime import datetime
from typing import Callable

from ncache.runtime.caching.events.CacheDataModificationListener import CacheDataModificationListener
from ncache.runtime.dependencies.FileDependency import FileDependency
from ncache.runtime.dependencies.KeyDependency import KeyDependency
from ncache.runtime.dependencies.OracleCacheDependency import OracleCacheDependency
from ncache.runtime.dependencies.SqlCacheDependency import SqlCacheDependency
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.JavaInstancesFactory import *
from ncache.util.ValidateType import ValidateType
from ncache.client.enum.EventType import EventType
from ncache.client.enum.EventDataFilter import EventDataFilter
from ncache.client.enum.CacheItemPriority import CacheItemPriority
from ncache.runtime.dependencies.CacheDependency import CacheDependency
from ncache.runtime.Expiration import Expiration
from ncache.runtime.caching.NamedTagsDictionary import NamedTagsDictionary
from ncache.runtime.caching.datasource.ResyncOptions import ResyncOptions
from ncache.runtime.caching.Tag import Tag
from ncache.client.CacheItemVersion import CacheItemVersion
from ncache.util.TypeCaster import TypeCaster


class CacheItem:
    """
    NCache uses a "key" and "value" structure for storing objects in cache. When an object is added in cache it is
    stored as value and metadata against the specified key. This combination of value and metadata is defined as
    CacheItem in NCache. The value of the objects stored in the cache can range from being simple string types to
    complex objects. CacheItem class in NCache has properties that enable you to set metadata for the item to be added
    in cache in an organized way. In scenarios where multiple attributes have to be set while adding an item in cache
    using CacheItem is preferred.Using CacheItem class object removes the problem of using multiple API overloads on
    adding/updating data in cache.You can easily use the basic API overload and add/update data easily using CacheItem.
    """
    def __init__(self, value=None):
        """
        Initialize new instance of cache item.

        :param value: Actual object to be stored in cache.
        :type value: object
        """

        if value is None:
            self.__cacheitem = JavaInstancesFactory.get_java_instance("CacheItem")()
        else:
            javatype = TypeCaster.is_python_primitive(value)
            if javatype is not None:
                self.__cacheitem = JavaInstancesFactory.get_java_instance("CacheItem")(javatype)
            else:
                self.__cacheitem = JavaInstancesFactory.get_java_instance("CacheItem")(TypeCaster.serialize(value, isjsonobject=True, verbose=True))

    def set_instance(self, value):
        self.__cacheitem = value

    def get_instance(self):
        return self.__cacheitem

    def add_cache_data_notification_listener(self, callablefunction, eventtypes, datafilter):
        """
        You can use this to notify applications when their objects are updated or removed in the cache.
        Listeners can be registered against event type/types for the key the items is inserted against.

        :param callablefunction: Callable function to be invoked when an item is updated or removed. This
        function should follow this signature: callablefunction(key: str, eventarg: CacheEventArg)
        :type callablefunction: Callable
        :param eventtypes: List of Event types the listener is registered against.
        :type eventtypes: list
        :param datafilter: Tells whether to receive metadata, data with metadata or none when a notification is
            triggered.
        :type datafilter: EventDataFilter
        """
        ValidateType.params_check(callablefunction, 2, self.add_cache_data_notification_listener)
        for item in eventtypes:
            ValidateType.type_check(item, EventType, self.add_cache_data_notification_listener)
        ValidateType.type_check(datafilter, EventDataFilter, self.add_cache_data_notification_listener)

        eventlistener = EventsListenerHelper.get_listener(callablefunction, CacheDataModificationListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        javadatafilter = EnumUtil.get_event_data_filter(datafilter.value)

        self.__cacheitem.addCacheDataNotificationListener(eventlistener, javaeventtypes, javadatafilter)

    def get_cache_item_priority(self):
        """
        Gets the relative priority for cache item which is kept under consideration whenever cache starts to free up
        space and evicts items.

        :return: CacheItemPriority associated with cache item.
        :rtype: CacheItemPriority
        """
        result = self.__cacheitem.getCacheItemPriority()

        enumtype = None
        if result is not None:
            enumtype = EnumUtil.get_cache_item_priority_value(result)

        return enumtype

    def get_cache_item_version(self):
        """
        Gets the version associated with the cache item.Version is basically a numeric value that is used to represent
        the version of the cached item which changes with every update to an item.

        :return: The version associated with the cache item.
        :rtype: CacheItemVersion
        """
        version = self.__cacheitem.getCacheItemVersion()

        if version is not None:
            version = CacheItemVersion(int(version.getVersion()))

        return version

    def get_creation_time(self):
        """
        Gets the time when the item was added in cache for the first time.

        :return: The date of creation of the cache item.
        :rtype: datetime
        """
        result = self.__cacheitem.getCreationTime()

        if result is not None:
            result = TypeCaster.to_python_date(result)

        return result

    def get_dependency(self):
        """
        Gets the Cache Dependency instance that contains all dependencies associated with cache item.

        :return: The Cache Dependency instance associated with cache item.
        :rtype: CacheDependency
        """
        result = self.__cacheitem.getDependency()
        dependencytype = EnumUtil.get_dependency_type_info(result)
        dependency = None

        if dependencytype == 1:
            dependency = KeyDependency("key")
            dependency.set_instance(result)
        elif dependencytype == 2:
            dependency = FileDependency("key")
            dependency.set_instance(result)
        elif dependencytype == 5:
            dependency = SqlCacheDependency("ConString", "CmdText")
            dependency.set_instance(result)
        elif dependencytype == 6:
            dependency = OracleCacheDependency("ConString", "CmdText")
            dependency.set_instance(result)
        else:
            dependency = CacheDependency()
            dependency.set_instance(result)

        return dependency

    def get_expiration(self):
        """
        Gets the expiration mechanism for cache item.

        :return: Expiration instance that contains info about cache item expiration mechanism.
        :rtype: Expiration
        """
        result = self.__cacheitem.getExpiration()

        if result is not None:
            expiration = Expiration()
            expiration.set_instance(result)
            return expiration

        return result

    def get_group(self):
        """
        Gets the group associated with the cache item. It can be queried on the basis of Groups.

        :return: The group associated with cache item.
        :rtype: str
        """
        result = self.__cacheitem.getGroup()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_last_modified_time(self):
        """
        Gets the lastModifiedTime of the cache item.CacheItem stores the last modified time of the cache item. If an
        item is updated in cache its last modified time is updated as well. Last modified time is checked when Least
        Recently Used based eviction is triggered.

        :return: The last modification time of the cache item.
        :rtype: datetime
        """
        result = self.__cacheitem.getLastModifiedTime()

        if result is not None:
            timestamp = float(result.getTime())
            result = datetime.fromtimestamp(timestamp / 1000)

        return result

    def get_named_tags(self):
        """
        Gets the NamedTags information associated with the cache item, it can be queried on the basis of NamedTags
        provided.

        :return: NamedTags associated with cache item.
        :rtype: NamedTagsDictionary
        """
        result = self.__cacheitem.getNamedTags()

        if result is not None:
            obj = NamedTagsDictionary()
            obj.set_instance(result)
            return obj

        return result

    def get_resync_options(self):
        """
        Gets the ResyncOptions specific to the cache item.

        :return: ResyncOptions specific to the cache item.
        :rtype: ResyncOptions
        """
        result = self.__cacheitem.getResyncOptions()

        if result is not None:
            resyncoptions = ResyncOptions(False)
            resyncoptions.set_instance(result)
            return resyncoptions

        return result

    def get_tags(self):
        """
        Gets the tags information associated with the cache item, it can be queried on the basis of Tags provided.

        :return: List of Tags associated with cache item.
        :rtype: list
        """
        result = self.__cacheitem.getTags()
        if result is not None:
            result = TypeCaster.to_python_list(result, False, Tag("DummyTag"))
        return result

    def get_value(self, objtype):
        """
        Returns the value stored in the cache item.

        :param objtype: Specifies the type of value obtained from the cacheItem.
        :type objtype: type
        :return: Returns the value stored in the cache item.
        :rtype: object
        """
        ValidateType.type_check(objtype, type, self.get_value)

        pythontype, javatype = TypeCaster.is_java_primitive(objtype)

        if javatype is not None:
            return pythontype(self.__cacheitem.getValue(javatype))
        else:
            result = self.__cacheitem.getValue(JavaInstancesFactory.get_java_instance("JsonObject"))
            if result is not None:
                return TypeCaster.deserialize(result, objtype, isjsonobject=True)

    def remove_cache_data_notification_listener(self, callablefunction: Callable, eventtypes):
        """
        Unregisters the user from cache data modification notifications.

        :param callablefunction: The callable function that is registered for notifications.
        :param eventtypes: List of Event types the listener is to be unregistered against.
        :type eventtypes: list
        """
        for eventtype in eventtypes:
            ValidateType.type_check(eventtype, EventType, self.remove_cache_data_notification_listener)
        ValidateType.params_check(callablefunction, 2, self.remove_cache_data_notification_listener)

        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        listener = EventsListenerHelper.get_listener(callablefunction, CacheDataModificationListener)

        self.__cacheitem.removeCacheDataNotificationListener(listener, javaeventtypes)

    def set_cache_item_priority(self, priority):
        """
        Sets the CacheItemPriority of the cache item.

        :param priority: CacheItemPriority to be associated with cache item.
        :type priority: CacheItemPriority
        """
        ValidateType.type_check(priority, CacheItemPriority, self.set_cache_item_priority)
        priorityvalue = EnumUtil.get_cache_item_priority(priority.value)
        self.__cacheitem.setCacheItemPriority(priorityvalue)

    def set_cache_item_version(self, version):
        """
        Sets the CacheItemVersion of the cache item.

        :param version: CacheItemVersion value It is basically a numeric value that is used to represent the version
            of the cached item which changes
        :type version: CacheItemVersion
        """
        ValidateType.type_check(version, CacheItemVersion, self.set_cache_item_version)

        self.__cacheitem.setCacheItemVersion(JavaInstancesFactory.get_java_instance("CacheItemVersion")(version.get_version()))

    def set_dependency(self, dependency):
        """
        Sets CacheDependency of CacheItem

        :param dependency: The Cache Dependency instance to be associated with cache item.
        :type dependency: CacheDependency
        """
        ValidateType.validate_instance(dependency, CacheDependency, self.set_dependency)

        self.__cacheitem.setDependency(dependency.get_instance())

    def set_expiration(self, expiration):
        """
        Sets the Expiration of the cache item.

        :param expiration: Expiration value This property sets Expiration for the cache item. After the specified
            timespan, the item expires from cache.
        :type expiration: Expiration
        """
        ValidateType.type_check(expiration, Expiration, self.set_expiration)
        self.__cacheitem.setExpiration(expiration.get_instance())

    def set_group(self, groupname):
        """
        Sets the group associated with the cache item. It can be queried on the basis of Groups.

        :param groupname: The group to be associated with cache item.
        :type groupname: str
        """
        ValidateType.is_string(groupname, self.set_group)
        self.__cacheitem.setGroup(TypeCaster.to_java_primitive_type(groupname))

    def set_named_tags(self, namedtags):
        """
        Sets NamedTags of CacheItem

        :param namedtags: NamedTags to be associated with cache item.
        :type namedtags: NamedTagsDictionary
        """
        ValidateType.type_check(namedtags, NamedTagsDictionary, self.set_named_tags)

        self.__cacheitem.setNamedTags(namedtags.get_instance())

    def set_resync_options(self, resyncoptions):
        """
        Sets ResyncOption of CacheItem

        :param resyncoptions: ResyncOptions specific to the cache item.
        :type resyncoptions: ResyncOptions
        """
        ValidateType.type_check(resyncoptions, ResyncOptions, self.set_resync_options)
        self.__cacheitem.setResyncOptions(resyncoptions.get_instance())

    def set_tags(self, tags):
        """
        Sets the tags information associated with the cache item, it can be queried on the basis of Tags provided.

        :param tags: List of Tags to be associated with cache item.
        :type tags: list
        """
        ValidateType.type_check(tags, list, self.get_tags)

        for tag in tags:
            ValidateType.type_check(tag, Tag, self.set_tags)

        self.__cacheitem.setTags(TypeCaster.to_java_array_list(tags))

    def set_value(self, value):
        """
        Sets the value of the cache item.

        :param value: Actual object to be stored in cache.
        :type value: object
        """
        ValidateType.is_none(value, self.set_value)

        if not isinstance(value, object):
            raise TypeError(f"{self.set_value.__name__} failed. Parameter \"value\" is not instance of object")

        javatype = TypeCaster.is_python_primitive(value)

        if javatype is not None:
            self.__cacheitem.setValue(javatype)
        else:
            self.__cacheitem.setValue(TypeCaster.serialize(value, isjsonobject=True))
