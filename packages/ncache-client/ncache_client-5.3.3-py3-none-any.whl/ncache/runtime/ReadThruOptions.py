from ncache.client.enum.ReadMode import ReadMode
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType
from ncache.util.JavaInstancesFactory import *


class ReadThruOptions:
    """
    Class that defines the fetch operation on cache can read from data source if item not found.
    """
    def __init__(self, readmode, providername=None):
        """
        Initializes a new instance of ReadThruOptions.

        :param readmode: ReadMode for read-through options.
        :type readmode: ReadMode
        :param providername: A unique identifier for the data source provider.
        :type providername: str
        """
        ValidateType.type_check(readmode, ReadMode, self.__init__)
        javareadmode = EnumUtil.get_read_mode(readmode.value)

        if providername is not None:
            ValidateType.is_string(providername, self.__init__)
            javaprovidername = TypeCaster.to_java_primitive_type(providername)

            self.__readthruoptions = JavaInstancesFactory.get_java_instance("ReadThruOptions")(javareadmode, javaprovidername)
        else:
            self.__readthruoptions = JavaInstancesFactory.get_java_instance("ReadThruOptions")(javareadmode)

    def get_instance(self):
        return self.__readthruoptions

    def set_instance(self, value):
        self.__readthruoptions = value

    def get_provider_name(self):
        """
        Gets the unique identifier for the data source provider.

        :return: The name of the datasource provider.
        :rtype: str
        """
        result = self.__readthruoptions.getProviderName()

        if result is not None:
            result = TypeCaster.to_java_primitive_type(result)

        return result

    def get_read_mode(self):
        """
        Gets the ReadMode for read-through options.

        :return: The readmode associated with readthruoptions.
        :rtype: ReadMode
        """
        result = self.__readthruoptions.getReadMode()

        if result is not None:
            result = EnumUtil.get_read_mode_value(result)

        return result

    def set_provider_name(self, providername):
        """
        Sets the unique identifier for the datasource provider.

        :param providername: The name of the datasource provider.
        :type providername: str
        """
        ValidateType.is_string(providername, self.set_provider_name)

        javaprovidername = TypeCaster.to_java_primitive_type(providername)
        self.__readthruoptions.setProviderName(javaprovidername)

    def set_read_mode(self, readmode):
        """
        Sets the ReadMode for read-through options.

        :param readmode: The readmode to be associated with readthruoptions.
        :type readmode: ReadMode
        """
        ValidateType.type_check(readmode, ReadMode, self.set_read_mode)

        javareadmode = EnumUtil.get_read_mode(readmode.value)
        self.__readthruoptions.setReadMode(javareadmode)
