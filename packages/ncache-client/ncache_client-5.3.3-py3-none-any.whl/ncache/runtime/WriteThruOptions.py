from collections import Callable

from ncache.client.enum.EventType import EventType
from ncache.client.enum.WriteMode import WriteMode
from ncache.runtime.caching.events.DataSourceModifiedListener import DataSourceModifiedListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType
from ncache.util.JavaInstancesFactory import *


class WriteThruOptions:
    """
    Class that defines write-through options regarding updating the data source.
    """
    __datamodificationlistener = None

    def __init__(self, writemode=WriteMode.NONE, providername=None):
        """
        Initializes a new instance of WriteThruOptions.

        :param writemode: write-through options.
        :type writemode: WriteMode
        :param providername: A unique identifier for the data source provider.
        :type providername: str
        """
        ValidateType.type_check(writemode, WriteMode, self.__init__)
        if providername is not None:
            ValidateType.is_string(providername, self.__init__)

        javawritemode = EnumUtil.get_write_mode(writemode.value)
        if providername is not None:
            javaprovidername = TypeCaster.to_java_primitive_type(providername)
        else:
            javaprovidername = jp.JObject(None, jp.java.lang.String)
        self.__writethruoptions = JavaInstancesFactory.get_java_instance("WriteThruOptions")(javawritemode, javaprovidername)

    def get_instance(self):
        return self.__writethruoptions

    def set_instance(self, value):
        self.__writethruoptions = value

    def get_data_source_modification_listener(self):
        """
        Gets the data source modified notification listener callback for write-through options.

        :return: The data source modified notification listener callback.
        :rtype: Callable
        """
        return self.__datamodificationlistener

    def get_event_types(self):
        """
        Gets the events list registered for datasource modification listener.

        :return: The events list.
        :rtype: list
        """
        result = self.__writethruoptions.getEventTypes()

        if result is not None:
            result = EventsListenerHelper.get_event_type_list(result)

        return result

    def get_mode(self):
        """
        Gets the WriteMode for write-through options.

        :return: write mode for write-through options.
        :rtype: WriteMode
        """
        result = self.__writethruoptions.getMode()

        if result is not None:
            result = EnumUtil.get_write_mode_value(int(result.getValue()))

        return result

    def get_provider_name(self):
        """
        Gets the unique identifier for the data source provider.

        :return: The name of datasource provider.
        :rtype: str
        """
        result = self.__writethruoptions.getProviderName()

        if result is not None:
            result = str(result)

        return result

    def set_data_source_modification_listener(self, callablefunction, eventtypes):
        """
        Sets the data source modified notification listener for write-through options.

        :param callablefunction: A listener function that is invoked whenever datasource is modified. This function
            should have this signature: callablefunction(key: str, writebehindopresult: WriteBehindOpResult)
        :type callablefunction: Callable
        :param eventtypes: The list of event types to be registered against the datasource listener.
        :type eventtypes: list
        """
        ValidateType.params_check(callablefunction, 2, self.set_data_source_modification_listener)
        for item in eventtypes:
            ValidateType.type_check(item, EventType, self.set_data_source_modification_listener)

        listener = DataSourceModifiedListener(callablefunction)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)

        self.__writethruoptions.setDataSourceModificationListener(listener, javaeventtypes)
        self.__datamodificationlistener = callablefunction

    def set_mode(self, writemode):
        """
        Sets the WriteMode for write-through options.

        :param writemode: write mode for write-through options.
        :type writemode: WriteMode
        """
        ValidateType.type_check(writemode, WriteMode, self.set_mode)

        javawritemode = EnumUtil.get_write_mode(writemode)
        self.__writethruoptions.setMode(javawritemode)

    def set_provider_name(self, providername):
        """
        Sets the unique identifier for the data source provider.

        :param providername:
        :return: The name of the datasource provider.
        :rtype: str
        """
        ValidateType.is_string(providername, self.set_provider_name)

        javaprovidername = TypeCaster.to_java_primitive_type(providername)
        self.__writethruoptions.setProviderName(javaprovidername)
