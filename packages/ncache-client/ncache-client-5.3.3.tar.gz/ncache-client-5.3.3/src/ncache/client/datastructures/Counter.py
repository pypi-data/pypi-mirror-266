from collections import Callable

from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.DataStructureDataChangeListener import DataStructureDataChangeListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class Counter:
    """
    This class contains methods and parameters for Distributed Counter.
    """
    def __init__(self):
        """
        Initializes a new instance of Counter class
        """
        self.__counter = None

    def get_instance(self):
        return self.__counter

    def set_instance(self, value):
        self.__counter = value

    def decrement(self):
        """
        Decrement the value of distributed counter by one.

        :return: Current value of the counter.
        :rtype: int
        """
        result = self.__counter.decrement()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def decrement_by(self, value):
        """
        Decrement the value of distributed counter by the amount specified.

        :param value: The value to decrement by.
        :type value: int
        :return: Current value of the counter.
        :rtype: int
        """
        ValidateType.type_check(value, int, self.decrement_by)
        javavalue = TypeCaster.to_java_long(value)

        result = self.__counter.decrementBy(javavalue)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_value(self):
        """
        Gets the value of counter.

        :return: Current value of the counter.
        :rtype: int
        """

        result = self.__counter.getValue()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def increment(self):
        """
        Increment the value of distributed counter by one.

        :return: Current value of the counter.
        :rtype: int
        """
        result = self.__counter.increment()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def increment_by(self, value):
        """
        Increment the value of distributed counter by the amount specified.

        :param value: The value to increment by.
        :type value: int
        :return: Current value of the counter.
        :rtype: int
        """

        ValidateType.type_check(value, int, self.increment_by)
        javavalue = TypeCaster.to_java_long(value)

        result = self.__counter.incrementBy(javavalue)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_value(self, value):
        """
        Sets the given value of the counter.

        :param value: Value to be assigned to the counter.
        :type value: int
        :return: Current value of the counter.
        :rtype: int
        """
        ValidateType.type_check(value, int, self.set_value)
        javavalue = TypeCaster.to_java_long(value)

        result = self.__counter.setValue(javavalue)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def add_change_listener(self, callablefunction, eventtypes, eventdatafilter):
        """
        Allows you to register collection event notifications like Add, Update, and Remove on the collection.

        :param callablefunction: The callable function that is invoked when an item is added, updated or removed from
            the collection. This function should follow this signature:
            callablefunction(collectionname: str, eventarg: DataStructureEventArg)
        :type callablefunction: Callable
        :param eventtypes: The list of event types that are to be registered.
        :type eventtypes: list
        :param eventdatafilter: An enum which allows you to specify to which extent you want the data with the event.
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

        self.__counter.addChangeListener(eventlistener, javaeventtypes, javadatafilter)

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

        self.__counter.removeChangeListener(listener, javaeventtypes)
