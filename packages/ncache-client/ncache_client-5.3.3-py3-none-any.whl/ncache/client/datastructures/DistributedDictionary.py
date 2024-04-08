from collections import Callable
from typing import Iterable, List

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.DataStructureDataChangeListener import DataStructureDataChangeListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DistributedDictionary:
    """
    This class contains methods and parameters for distributed Dictionary. The type of key is limited to string only.
    """
    def __init__(self, objtype, isjsonobject):
        """
        Initializes a new instance of DistributedDictionary class

        :param objtype: Type of dictionary values
        :type objtype: type
        """
        ValidateType.type_check(objtype, type, self.__init__)

        self.__dict = None
        self.__objtype = objtype
        self.__isjsonobject = isjsonobject

    def __len__(self):
        result = self.__dict.size()
        return TypeCaster.to_python_primitive_type(result)

    def get_instance(self):
        return self.__dict

    def set_instance(self, value):
        self.__dict = value

    def insert(self, entries):
        """
        Insert elements with the provided keys and values in DistributedDictionary.

        :param entries: Elements to be inserted
        :type entries: dict
        """
        ValidateType.type_check(entries, dict, self.insert)
        for key in entries.keys():
            if type(key) is not str or not isinstance(entries[key], self.__objtype):
                raise TypeError(ExceptionHandler.get_invalid_dict_key_item_exception_message(self.insert, self.__objtype))

        javaentries = self.__dict_entries_to_map(entries)

        self.__dict.insert(javaentries)

    def remove(self, keys):
        """
        Removes the element with the specified key(s) from DistributedDictionary.

        :param keys: The keys or key of the element(s) to remove.
        :type keys: list or str
        :return: The number of items that were removed if list of keys is passed, or the item removed if only one key
            is passed.
        :rtype: int or object
        """
        result = None
        if type(keys) is list:
            for key in keys:
                ValidateType.is_string(key, self.remove)

            javakeys = TypeCaster.to_java_array_list(keys, True)

            result = self.__dict.remove(javakeys)

            if result is not None:
                result = TypeCaster.to_python_primitive_type(result)
        elif type(keys) is str:
            javakeys = TypeCaster.to_java_primitive_type(keys)

            result = self.__dict.remove(javakeys)

            if result is not None:
                result = TypeCaster.deserialize(result, self.__objtype, isjsonobject=True)
        else:
            raise TypeError(ExceptionHandler.get_invalid_keys_exception_message(self.remove))

        return result

    def get(self, keys):
        """
        Returns the value(s) associated with the specified key(s).

        :param keys: The key(s) whose value(s) to get.
        :type keys: list or str
        :return: List of values or value against the provided key(s).
        :rtype: list or object
        """
        result = None
        if type(keys) is list:
            for key in keys:
                ValidateType.is_string(key, self.get)

            javakeys = TypeCaster.to_java_array_list(keys, True)

            result = self.__dict.get(javakeys)

            if result is not None:
                result = TypeCaster.to_python_list(result, objtype=self.__objtype, usejsonconversion=True)

        elif type(keys) is str:
            javakeys = TypeCaster.to_java_primitive_type(keys)

            result = self.__dict.get(javakeys)

            if result is not None:
                result = TypeCaster.deserialize(result, objtype=self.__objtype, isjsonobject=True)
        else:
            raise TypeError(ExceptionHandler.get_invalid_keys_exception_message(self.get))

        return result

    def is_empty(self):
        """
        Returns true if this dictionary contains no key-value mappings.

        :return: True if this map contains no key-value mappings, False otherwise
        :rtype: bool
        """
        result = self.__dict.isEmpty()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def contains_key(self, key):
        """
        Returns true if this map contains a mapping for the specified key.

        :param key: key whose presence in this map is to be tested
        :type key: str
        :return: True if this map contains a mapping for the specified key, False otherwise
        :rtype: bool
        """
        ValidateType.is_string(key, self.contains_key)
        javakey = TypeCaster.to_java_primitive_type(key)

        result = self.__dict.containsKey(javakey)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def put(self, key, value):
        """
        Associates the specified value with the specified key in this map (optional operation). If the map previously
        contained a mapping for the key, the old value is replaced by the specified value.

        :param key: key with which the specified value is to be associated
        :type key: str
        :param value: value to be associated with the specified key
        :type value: object
        :return: the previous value associated with key, or None if there was no mapping for key.
        :rtype: object or None
        """
        ValidateType.is_string(key, self.put)
        ValidateType.is_none(value, self.put)
        ValidateType.validate_instance(value, self.__objtype, self.put)

        javakey = TypeCaster.to_java_primitive_type(key)
        if TypeCaster.to_java_primitive_type(value) is None:
            javavalue = TypeCaster.serialize(value, isjsonobject=True)
        else:
            javavalue = TypeCaster.serialize(value, isjsonobject=False)

        result = self.__dict.put(javakey, javavalue)

        if result is not None:
            result = TypeCaster.deserialize(result)

        return result

    def put_all(self, collection):
        """
        Copies all of the mappings from the specified map to this map (optional operation). The effect of this call is
        equivalent to that of calling put(k, v) on this map once for each mapping from key k to value v in the specified
        map.

        :param collection: Dictionary to be stored in this map
        :type collection: dict
        """
        ValidateType.type_check(collection, dict, self.put_all)

        for key in collection.keys():
            ValidateType.is_string(key, self.put_all)
            ValidateType.validate_instance(collection[key], self.__objtype, self.put_all)

        javacollection = self.__dict_entries_to_map(collection)

        self.__dict.putAll(javacollection)

    def key_set(self):
        """
        Returns a Set view of the keys contained in this map. The set is backed by the map, so changes to the map are
        reflected in the set, and vice-versa.

        :return: A set view of the keys contained in this dictionary
        :rtype: set
        """
        result = self.__dict.keySet()

        if result is not None:
            result = TypeCaster.to_python_set(result, True)

        return result

    def values(self):
        """
        Returns a Collection view of the values contained in this map. The collection is backed by the map, so changes
        to the map are reflected in the collection, and vice-versa.

        :return: a collection view of the values contained in this map
        :rtype: list
        """
        result = self.__dict.values()

        if result is not None:
            if self.__objtype is int or self.__objtype is str or self.__objtype is float or self.__objtype is bool:
                result = TypeCaster.to_python_list(result, usejsonconversion=False, isjavatype=True)
            else:
                result = TypeCaster.to_python_list(result, usejsonconversion=True, isjsonobject=True, objtype=self.__objtype)

        return result

    def entry_set(self):
        """
        Returns a Set view of the mappings contained in this map. The set is backed by the map, so changes to the map
        are reflected in the set, and vice-versa.

        :return: a set view of the mappings contained in this map
        :rtype: set
        """
        result = self.__dict.entrySet()
        pythonset = {()}

        if result is not None:
            for entry in result:
                key = TypeCaster.to_python_primitive_type(entry.getKey())
                value = TypeCaster.deserialize(entry.getValue(), objtype=self.__objtype, isjsonobject=self.__isjsonobject)
                pythonset.add((key, value))

        return pythonset

    def get_iterator(self):
        return iter(self.key_set())

    def add_change_listener(self, callablefunction, eventtypes, eventdatafilter):
        """
        Allows you to register collection event notifications like Add, Update, and Remove on the collection.

        :param callablefunction: The listener that is invoked when an item is added, updated or removed from the
            collection.
        :type callablefunction: Callable
        :param eventtypes: The list of event types that are to be registered.
        :type eventtypes: list
        :param eventdatafilter: An enum that allows you to specify to which extent you want the data with the event.
        :type eventdatafilter: DataTypeEventDataFilter
        """
        ValidateType.params_check(callablefunction, 2, self.add_change_listener)
        ValidateType.type_check(eventtypes, list, self.add_change_listener)
        for item in eventtypes:
            ValidateType.type_check(item, EventType, self.add_change_listener)
        ValidateType.type_check(eventdatafilter, DataTypeEventDataFilter, self.add_change_listener)

        eventlistener = EventsListenerHelper.get_listener(callablefunction, DataStructureDataChangeListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        javadatafilter = EnumUtil.get_data_type_event_data_filter(eventdatafilter.value)

        self.__dict.addChangeListener(eventlistener, javaeventtypes, javadatafilter)

    def remove_change_listener(self, callablefunction, eventtypes):
        """
        Unregisters the callable listener function that was registered with collection changed notification.

        :param callablefunction: The callable listener function that was registered with collection changed notification.
        :type callablefunction: Callable
        :param eventtypes: The list of event types that were registered.
        :type eventtypes: list
        """
        ValidateType.type_check(eventtypes, list, self.remove_change_listener)
        for eventtype in eventtypes:
            ValidateType.type_check(eventtype, EventType, self.remove_change_listener)
        ValidateType.params_check(callablefunction, 2, self.remove_change_listener)

        listener = EventsListenerHelper.get_listener(callablefunction, DataStructureDataChangeListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)

        self.__dict.removeChangeListener(listener, javaeventtypes)

    @staticmethod
    def __dict_entries_to_map(entriesmap):
        javahashmap = jp.java.util.HashMap()

        for item in entriesmap:
            value = TypeCaster.to_java_primitive_type(entriesmap[item])
            if value is None:
                value = TypeCaster.serialize(entriesmap[item], isjsonobject=True)
            else:
                value = TypeCaster.serialize(entriesmap[item], isjsonobject=False)
            javahashmap.put(TypeCaster.to_java_primitive_type(item), value)

        return javahashmap
