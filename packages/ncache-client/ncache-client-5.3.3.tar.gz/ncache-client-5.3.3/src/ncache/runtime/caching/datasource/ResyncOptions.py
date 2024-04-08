from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class ResyncOptions:
    """
    ResyncOptions class contain information for the items that would be resynced after expiration from the Read-Thru
    provider.
    """
    def __init__(self, resynconexpiration, providername=None):
        """
        Creates an instance of ResyncOptions.Creates an instance of ResyncOptions.

        :param resynconexpiration: flag that specifies whether the items are to be resynced after expiration.
        :type resynconexpiration: bool
        :param providername: After expiration items are resynced using the specified provider name.
        :type providername: str
        """
        ValidateType.type_check(resynconexpiration, bool)
        resynconexpiration = TypeCaster.to_java_primitive_type(resynconexpiration)

        if providername is None:
            self.__resyncoptions = JavaInstancesFactory.get_java_instance("ResyncOptions")(resynconexpiration)
        else:
            ValidateType.is_string(providername)

            providername = TypeCaster.to_java_primitive_type(providername)
            self.__resyncoptions = JavaInstancesFactory.get_java_instance("ResyncOptions")(resynconexpiration, providername)

    def set_instance(self, value):
        self.__resyncoptions = value

    def get_instance(self):
        return self.__resyncoptions

    def get_provider_name(self):
        """
        Gets the readthru provider name with which items will be resynced at expiry.

        :return: The name of the resync provider.
        :rtype: str
        """
        result = self.__resyncoptions.getProviderName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_resync_on_expiration(self):
        """
        Gets the flag that indicates whether the items are to be resynced at expiry or not.

        :return: resync on expiration flag.
        :rtype: bool
        """
        result = self.__resyncoptions.getResyncOnExpiration()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_provider_name(self, providername):
        """
        Sets the readthru provider name with which items will be resynced at expiry.

        :param providername: The name of the resync provider.
        :type providername: str
        """
        ValidateType.is_string(providername, self.set_provider_name)

        javaprovidername = TypeCaster.to_java_primitive_type(providername)
        self.__resyncoptions.setProviderName(javaprovidername)

    def set_resync_on_expiration(self, resynconexpiration):
        """
        Sets the flag that indicates whether the items are to be resynced at expiry or not.

        :param resynconexpiration: resync on expiration flag.
        :type resynconexpiration: bool
        """
        ValidateType.type_check(resynconexpiration, bool, self.set_resync_on_expiration)

        javaresynconexpiration = TypeCaster.to_java_primitive_type(resynconexpiration)
        self.__resyncoptions.setResyncOnExpiration(javaresynconexpiration)
