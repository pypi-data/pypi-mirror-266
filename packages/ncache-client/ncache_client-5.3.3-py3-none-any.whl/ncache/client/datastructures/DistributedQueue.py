from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.DataStructureDataChangeListener import DataStructureDataChangeListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.runtime.util.Iterator import Iterator
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DistributedQueue:
    """
    This class contains methods and parameters for distributed Queue.
    """
    def __init__(self, objtype, isjsonobject):
        """
        Initializes a new instance of DistributedQueue class

        :param objtype: Type of queue items
        :type objtype: type
        """
        ValidateType.type_check(objtype, type, self.__init__)

        self.__queue = None
        self.__objtype = objtype
        self.__isjsonobject = isjsonobject

    def __len__(self):
        result = self.__queue.size()
        return TypeCaster.to_python_primitive_type(result)

    def get_instance(self):
        return self.__queue

    def set_instance(self, value):
        self.__queue = value

    def contains(self, item):
        """
        Returns true if this collection contains the specified element.

        :param item: element whose presence in this collection is to be tested
        :type item: object
        :return: True if this collection contains the specified element, False otherwise
        """
        ValidateType.validate_instance(item, self.__objtype, self.contains)
        javaitem = TypeCaster.serialize(item, verbose=False, isjsonobject=self.__isjsonobject)

        result = self.__queue.contains(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_iterator(self):
        """
        Returns an iterator that iterates through the entries of distributed queue.

        :return: An Iterator instance
        :rtype: Iterator
        """
        javaiterator = self.__queue.iterator()
        iterator = Iterator(javaiterator, iskeysiterator=False, isdatastructureiterator=True, objtype=self.__objtype, isjsonobject=self.__isjsonobject)
        return iter(iterator)

    def add(self, obj):
        """
        Inserts the specified element into this queue if it is possible to do so immediately without violating capacity
        restrictions, returning True upon success and throwing an IllegalStateException if no space is currently
        available.

        :param obj: The element to add
        :type obj: object
        :return: Return True upon success, False otherwise
        :rtype: bool
        """
        ValidateType.is_none(obj, self.add)
        ValidateType.validate_instance(obj, self.__objtype, self.add)

        javaobj = TypeCaster.serialize(obj, verbose=False, isjsonobject=self.__isjsonobject)
        result = self.__queue.add(javaobj)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def remove(self):
        """
        Retrieves and removes the head of this queue. This method differs from poll only in that it throws an exception
        if this queue is empty.

        :return: the head of this queue
        :rtype: object
        """
        result = self.__queue.remove()

        if result is not None:
            result = TypeCaster.deserialize(result, self.__objtype, isjsonobject=self.__isjsonobject)

        return result

    def offer(self, item):
        """
        Inserts the specified element into this queue if it is possible to do so immediately without violating capacity
        restrictions. When using a capacity-restricted queue, this method is generally preferable to add(E), which can
        fail to insert an element only by throwing an exception.

        :param item: The element to add
        :type item: object
        :return: True if the element was added to this queue, False otherwise
        :rtype: bool
        """
        ValidateType.is_none(item, self.offer)
        ValidateType.validate_instance(item, self.__objtype, self.offer)

        javaitem = TypeCaster.serialize(item, verbose=False, isjsonobject=self.__isjsonobject)
        result = self.__queue.offer(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def poll(self):
        """
        Retrieves and removes the head of this queue, or returns None if this queue is empty.

        :return: the head of this queue, or None if this queue is empty
        :rtype: object or None
        """
        result = self.__queue.poll()

        if result is not None:
            result = TypeCaster.deserialize(result, self.__objtype, isjsonobject=self.__isjsonobject)

        return result

    def element(self):
        """
        Retrieves, but does not remove, the head of this queue. This method differs from peek only in that it throws an
        exception if this queue is empty.

        :return: the head of this queue
        :rtype: object
        """
        result = self.__queue.element()

        if result is not None:
            result = TypeCaster.deserialize(result, self.__objtype, isjsonobject=self.__isjsonobject)

        return result

    def peek(self):
        """
        Retrieves, but does not remove, the head of this queue, or returns None if this queue is empty.

        :return: the head of this queue, or None if this queue is empty
        :rtype: object or None
        """
        result = self.__queue.peek()

        if result is not None:
            result = TypeCaster.deserialize(result, self.__objtype, isjsonobject=self.__isjsonobject)

        return result

    def add_change_listener(self, callablefunction, eventtypes, eventdatafilter):
        """
        Allows you to register collection event notifications like Add, Update, and Remove on the collection.

        :param callablefunction: The listener that is invoked when an item is added, updated or removed from the
            collection. This function should follow this signature:
            callablefunction(collectionname: str, eventarg: DataStructureEventArg)
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

        self.__queue.addChangeListener(eventlistener, javaeventtypes, javadatafilter)

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

        self.__queue.removeChangeListener(listener, javaeventtypes)
