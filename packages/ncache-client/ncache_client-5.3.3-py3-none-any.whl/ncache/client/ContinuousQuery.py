from collections import Callable

from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.QueryDataModificationListener import QueryDataModificationListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.JavaInstancesFactory import *
from ncache.client.QueryCommand import QueryCommand
from ncache.client.enum.EventDataFilter import EventDataFilter
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class ContinuousQuery:
    """
    Class to hold Object query and values, intended for notifications.
    """
    def __init__(self, command=None):
        """
        Initializes a new instance of the ContinuousQuery class.

        :param command: QueryCommand containing query text and values.
        :type command: QueryCommand
        """
        if command is not None:
            ValidateType.type_check(command, QueryCommand, self.__init__)
            self.__cq = JavaInstancesFactory.get_java_instance("ContinuousQuery")(command.get_instance())

    def get_instance(self):
        return self.__cq

    def set_instance(self, value):
        self.__cq = value

    def add_data_modification_listener(self, callablefunction, eventtypes, datafilter):
        """
        This method registers a custom listener that is fired on change in dataset of a continuous query

        :param callablefunction: The callable function that is invoked whenever there is a change in dataset of
            continuous Query. This function should follow this signature: callablefunction(key: str, eventarg: CQEventArg)
        :type callablefunction: Callable
        :param eventtypes: Registers the listener with the specified event types in the list.
        :type eventtypes: list
        :param datafilter: Tells whether to receive metadata, data with metadata or none when a notification is
            triggered.
        :type datafilter: EventDataFilter
        """
        ValidateType.params_check(callablefunction, 2, self.add_data_modification_listener)
        for item in eventtypes:
            ValidateType.type_check(item, EventType, self.add_data_modification_listener)
        ValidateType.type_check(datafilter, EventDataFilter, self.add_data_modification_listener)

        eventlistener = EventsListenerHelper.get_listener(callablefunction, QueryDataModificationListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        javadatafilter = EnumUtil.get_event_data_filter(datafilter.value)

        self.__cq.addDataModificationListener(eventlistener, javaeventtypes, javadatafilter)

    def __eq__(self, other):
        if other is None or not isinstance(other, ContinuousQuery):
            return False

        result = self.__cq.equals(other.get_instance())

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        else:
            result = False

        return result

    def get_query_command(self):
        """
        Gets the query command for the continuous query.

        :return: The QueryCommand instance.
        :rtype: QueryCommand
        """
        result = self.__cq.getQueryCommand()

        if result is not None:
            command = QueryCommand("dummyQuery")
            command.set_instance(result)
            return command

        return result

    def __hash__(self):
        result = self.__cq.hashCode()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def remove_data_modification_listener(self, callablefunction, eventtypes):
        """
        This method unregisters a custom listener that is fired on change in dataset of a continuous query.

        :param callablefunction: The listener that was registered with continuous query.
        :type callablefunction: callable
        :param eventtypes: Unregisters the listener with the specified event types in the list.
        :type eventtypes: list
        """
        for eventtype in eventtypes:
            ValidateType.type_check(eventtype, EventType, self.remove_data_modification_listener)
        ValidateType.params_check(callablefunction, 2, self.remove_data_modification_listener)

        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        listener = EventsListenerHelper.get_listener(callablefunction, QueryDataModificationListener)

        self.__cq.removeDataModificationListener(listener, javaeventtypes)

    def set_query_command(self, command):
        """
        Sets the query command for the continuous query.

        :param command: The QueryCommand instance.
        :type command: QueryCommand
        """
        ValidateType.type_check(command, QueryCommand, self.set_query_command)
        self.__cq.setQueryCommand(command.get_instance())
