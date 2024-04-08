from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.DataStructureDataChangeListener import DataStructureDataChangeListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.runtime.util.Iterator import Iterator
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DistributedList:
    """
    This class contains methods and parameters for distributed List.
    """
    def __init__(self, objtype, isjsonobject):
        """
        Initializes a new instance of DistributedList class

        :param objtype: Type of list values
        :type objtype: type
        """
        ValidateType.type_check(objtype, type, self.__init__)

        self.__list = None
        self.__objtype = objtype
        self.__isjsonobject = isjsonobject

    def __len__(self):
        result = self.__list.size()
        return TypeCaster.to_python_primitive_type(result)

    def set_instance(self, value):
        self.__list = value

    def get_instance(self):
        return self.__list

    def trim(self, start, end):
        """
        Trim an existing list so that it will contain only the specified range of elements.

        :param start: Starting index.
        :type start: int
        :param end: Ending index.
        :type end: int
        """
        ValidateType.is_int(start, self.trim)
        ValidateType.is_int(end, self.trim)

        javastart = TypeCaster.to_java_primitive_type(start)
        javaend = TypeCaster.to_java_primitive_type(end)

        self.__list.trim(javastart, javaend)

    def get_range(self, start, count):
        """
        Returns a list that will contain only the specified range of elements.

        :param start: Starting index.
        :type start: int
        :param count: Number of items.
        :type count: int
        :return: List containing the specified range of elements
        :rtype: list
        """
        ValidateType.is_int(start, self.get_range)
        ValidateType.is_int(count, self.get_range)

        javastart = TypeCaster.to_java_primitive_type(start)
        javacount = TypeCaster.to_java_primitive_type(count)

        result = self.__list.trim(javastart, javacount)

        if result is not None:
            result = TypeCaster.to_python_list(result, usejsonconversion=True)

        return result

    def add_range(self, collection):
        """
        Adds the elements of the specified collection to the end of the List.

        :param collection: The collection whose elements should be added to the end of the List.
        :type collection: list
        """
        ValidateType.type_check(collection, list, self.add_range)

        for i in range(len(collection)):
            ValidateType.validate_instance(collection[i], self.__objtype, self.add_range)
            collection[i] = TypeCaster.serialize(collection[i], verbose=True, isjsonobject=self.__isjsonobject)

        javacollection = TypeCaster.to_java_array_list(collection, donotconvert=True)

        self.__list.addRange(javacollection)

    def remove_range(self, index=None, count=None, collection=None):
        """
        Removes a range of elements from the List.

        :param index: The zero-based starting index of the range of elements to remove.
        :type index: int
        :param count:  The number of elements to remove.
        :type count: int
        :param collection: The collection whose elements should be removed from the List.
        :type collection: list
        """
        if index is not None and count is not None:
            ValidateType.is_int(index, self.remove_range)
            ValidateType.is_int(count, self.remove_range)

            javaindex = TypeCaster.to_java_primitive_type(index)
            javacount = TypeCaster.to_java_primitive_type(count)

            self.__list.removeRange(javaindex, javacount)
        elif collection is not None:
            ValidateType.type_check(collection, list, self.add_range)

            for i in range(len(collection)):
                ValidateType.validate_instance(collection[i], self.__objtype, self.remove_range)
                collection[i] = TypeCaster.serialize(collection[i], verbose=True, isjsonobject=self.__isjsonobject)

            javacollection = TypeCaster.to_java_array_list(collection, donotconvert=True)

            self.__list.removeRange(javacollection)
        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("DistributedList.remove_range"))

    def insert_after(self, pivot, value):
        """
        Inserts the element in the list after the first occurrence of specified element.

        :param pivot: Element after which value will be inserted.
        :type pivot: object
        :param value: Element to insert in the list.
        :type value: object
        """
        ValidateType.is_none(pivot, self.insert_after)
        ValidateType.is_none(value, self.insert_after)
        ValidateType.validate_instance(pivot, self.__objtype, self.insert_after)
        ValidateType.validate_instance(value, self.__objtype, self.insert_after)

        javapivot = TypeCaster.serialize(pivot, verbose=True, isjsonobject=self.__isjsonobject)
        javavalue = TypeCaster.serialize(value, verbose=True, isjsonobject=self.__isjsonobject)

        self.__list.insertAfter(javapivot, javavalue)

    def insert_before(self, pivot, value):
        """
        Inserts the element in the list before the first occurrence of specified element.

        :param pivot: Element before which value will be inserted.
        :type pivot: object
        :param value: Element to insert in the list.
        :type value: object
        """
        ValidateType.is_none(pivot, self.insert_before)
        ValidateType.is_none(value, self.insert_before)
        ValidateType.validate_instance(pivot, self.__objtype, self.insert_before)
        ValidateType.validate_instance(value, self.__objtype, self.insert_before)

        javapivot = TypeCaster.serialize(pivot, verbose=True, isjsonobject=self.__isjsonobject)
        javavalue = TypeCaster.serialize(value, verbose=True, isjsonobject=self.__isjsonobject)

        self.__list.insertBefore(javapivot, javavalue)

    def first(self):
        """
        Returns the first element of the list.

        :return: The first element in the list.
        :rtype: object
        """
        result = self.__list.first()

        if result is not None:
            result = TypeCaster.deserialize(result, isjsonobject=self.__isjsonobject, objtype=self.__objtype)

        return result

    def last(self):
        """
        Returns the last element of the list.

        :return: The last element in the list.
        :rtype: object
        """
        result = self.__list.last()

        if result is not None:
            result = TypeCaster.deserialize(result, isjsonobject=self.__isjsonobject, objtype=self.__objtype)

        return result

    def insert_at_head(self, value):
        """
        Insert the specified value at the head of the list.

        :param value: Element to insert in the list.
        :type value: object
        """
        ValidateType.is_none(value, self.insert_at_head)
        ValidateType.validate_instance(value, self.__objtype, self.insert_at_head)
        javavalue = TypeCaster.serialize(value, verbose=True, isjsonobject=self.__isjsonobject)

        self.__list.insertAtHead(javavalue)

    def insert_at_tail(self, value):
        """
        Insert the specified value at the tail of the list.

        :param value: Element to insert in the list.
        :type value: object
        """
        ValidateType.is_none(value, self.insert_at_tail)
        ValidateType.validate_instance(value, self.__objtype, self.insert_at_tail)
        javavalue = TypeCaster.serialize(value, verbose=True, isjsonobject=self.__isjsonobject)

        self.__list.insertAtTail(javavalue)

    def contains(self, obj):
        """
        Returns True if this list contains the specified element.

        :param obj: element whose presence in this list is to be tested
        :type obj: object
        :return: True if this list contains the specified element, False otherwise.
        :rtype: bool
        """
        ValidateType.is_none(obj, self.contains)
        ValidateType.validate_instance(obj, self.__objtype, self.contains)
        javaobj = TypeCaster.serialize(obj, verbose=False, isjsonobject=self.__isjsonobject)

        result = self.__list.contains(javaobj)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_iterator(self):
        """
        Returns an iterator that iterates through the entries of distributed list.

        :return: An Iterator instance
        :rtype: Iterator
        """
        javaiterator = self.__list.iterator()
        iterator = Iterator(javaiterator, iskeysiterator=False, isdatastructureiterator=True, objtype=self.__objtype, isjsonobject=self.__isjsonobject)
        return iter(iterator)

    def add(self, item, index=None):
        """
        Inserts the specified element at the specified position in this list (optional operation). Shifts the element
        currently at that position (if any) and any subsequent elements to the right (adds one to their indices).

        :param item: element to be inserted
        :type item: object
        :param index: index at which the specified element is to be inserted
        :type index: int
        :return: True if operation is successful, False otherwise, and None if index is specified.
        :rtype: bool or None
        """
        ValidateType.is_none(item, self.add)
        ValidateType.validate_instance(item, self.__objtype, self.add)
        javaitem = TypeCaster.serialize(item, verbose=False, isjsonobject=self.__isjsonobject)

        if index is not None:
            ValidateType.is_int(index, self.add)
            javaindex = TypeCaster.to_java_primitive_type(index)

            self.__list.add(javaindex, javaitem)
        else:
            result = self.__list.add(javaitem)

            if result is not None:
                result = TypeCaster.to_python_primitive_type(result)

            return result

    def remove(self, item):
        """
        Removes the specified element from this list. Returns the element that was removed from the list.

        :param item: Item to be removed from the List
        :type item: object
        :return: True if the operation was successful, False otherwise
        :rtype: bool
        """
        ValidateType.is_none(item, self.remove)
        ValidateType.validate_instance(item, self.__objtype, self.remove)
        javaitem = TypeCaster.serialize(item, verbose=False, isjsonobject=self.__isjsonobject)

        result = self.__list.remove(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def add_all(self, collection):
        """
        Appends all of the elements in the specified collection to the end of this list, in the order that they are
        returned by the specified collection's iterator.

        :param collection: list of items to be added in this list
        :type collection: list
        :return: True if this list changed as a result of the call, False otherwise
        :rtype: bool
        """
        ValidateType.type_check(collection, list, self.add_all)
        javacollection = []

        for i in collection:
            ValidateType.validate_instance(i, self.__objtype, self.add_all)
            javacollection.append(TypeCaster.serialize(i, verbose=True, isjsonobject=self.__isjsonobject))

        javacollection = TypeCaster.to_java_array_list(javacollection, donotconvert=True)

        result = self.__list.addAll(javacollection)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def remove_all(self, collection):
        """
        Removes from this list all of its elements that are contained in the specified collection.

        ::param collection: list of items to be removed from this list
        :type collection: list
        :return: True if this list changed as a result of the call, False otherwise
        :rtype: bool
        """
        ValidateType.type_check(collection, list, self.remove_all)

        for i in range(len(collection)):
            if collection[i] is None:
                ValidateType.validate_instance(collection[i], self.__objtype, self.remove_all)
            collection[i] = TypeCaster.serialize(collection[i], verbose=True, isjsonobject=self.__isjsonobject)

        javacollection = TypeCaster.to_java_array_list(collection, donotconvert=True)

        result = self.__list.removeAll(javacollection)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get(self, index):
        """
        Returns the element at the specified position in this list.

        :param index: index of the element to return
        :type index: int
        :return: The element at the specified position in this list
        :rtype: object
        """
        ValidateType.is_int(index, self.get)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__list.get(javaindex)

        if result is not None:
            result = TypeCaster.deserialize(result, isjsonobject=self.__isjsonobject, objtype=self.__objtype)

        return result

    def set(self, index, element):
        """
        Replaces the element at the specified position in this list with the specified element.

        :param index: index of the element to replace
        :type index: int
        :param element: element to be stored at the specified position
        :type element: object
        :return: the element previously at the specified position
        :rtype: object
        """
        ValidateType.is_int(index, self.set)
        ValidateType.is_none(element, self.set)
        ValidateType.validate_instance(element, self.__objtype, self.set)

        javaindex = TypeCaster.to_java_primitive_type(index)
        javaelement = TypeCaster.serialize(element, verbose=True, isjsonobject=self.__isjsonobject)

        result = self.__list.set(javaindex, javaelement)

        if result is not None:
            result = TypeCaster.deserialize(result, isjsonobject=self.__isjsonobject, objtype=self.__objtype)

        return result

    def index_of(self, item):
        """
        Returns the index of the first occurrence of the specified element in this list, or -1 if this list does not
        contain the element.

        :param item: element to search for
        :type item: object
        :return: the index of the first occurrence of the specified element in this list, or -1 if this list does not
            contain the element
        :rtype: int
        """
        ValidateType.is_none(item, self.index_of)
        ValidateType.validate_instance(item, self.__objtype, self.index_of)
        javaitem = TypeCaster.serialize(item, verbose=True, isjsonobject=self.__isjsonobject)

        result = self.__list.indexOf(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def sub_list(self, fromindex, toindex):
        """
        Returns a view of the portion of this list between the specified fromIndex, inclusive, and toIndex, exclusive.
        (If fromIndex and toIndex are equal, the returned list is empty.) The returned list is backed by this list, so
        non-structural changes in the returned list are reflected in this list, and vice-versa.

        :param fromindex: low endpoint (inclusive) of the subList
        :type fromindex: int
        :param toindex: high endpoint (exclusive) of the subList
        :type toindex: int
        :return: a view of the specified range within this list
        :rtype: list
        """
        ValidateType.is_int(fromindex, self.sub_list)
        ValidateType.is_int(toindex, self.sub_list)

        javafromindex = TypeCaster.to_java_primitive_type(fromindex)
        javatoindex = TypeCaster.to_java_primitive_type(toindex)

        result = self.__list.subList(javafromindex, javatoindex)

        if result is not None:
            result = TypeCaster.to_python_list(result, usejsonconversion=True, objtype=self.__objtype, isjsonobject=self.__isjsonobject)

        return result

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

        self.__list.addChangeListener(eventlistener, javaeventtypes, javadatafilter)

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

        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        listener = EventsListenerHelper.get_listener(callablefunction, DataStructureDataChangeListener)

        self.__list.removeChangeListener(listener, javaeventtypes)
