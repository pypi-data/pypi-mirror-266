from ncache.client.Credentials import Credentials
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheConnection:
    """
    Instance of this class can be used to define the parameters to establish connection with cache.
    """
    def __init__(self, server, port=None):
        """
        Initializes new instance of CacheConnection.

        :param server: Specifies the name of server on which cache is running.
        :type server: str
        :param port: Specifies the port of server on which cache is running.
        :type port: int
        """
        ValidateType.is_string(server, self.__init__)
        javaserver = TypeCaster.to_java_primitive_type(server)

        if port is not None:
            ValidateType.is_int(port, self.__init__)
            javaport = TypeCaster.to_java_primitive_type(port)

            self.__cacheconnection = JavaInstancesFactory.get_java_instance("CacheConnection")(javaserver, javaport)

        else:
            self.__cacheconnection = JavaInstancesFactory.get_java_instance("CacheConnection")(javaserver)

    def get_server(self):
        """
        Gets the name of server on which cache is running.

        :return: The name of server on which cache is running.
        :rtype: str
        """
        result = self.__cacheconnection.getServer()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_port(self):
        """
        Gets the port of server on which cache is running.

        :return: The port of server on which cache is running.
        :rtype: int
        """
        result = self.__cacheconnection.getPort()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_user_credentials(self):
        """
        Gets Credentials of the cache for authorization.

        :return: The credentials of the cache for authorization.
        :rtype: Credentials
        """
        result = self.__cacheconnection.getUserCredentials()

        if result is not None:
            credentials = Credentials()
            credentials.set_instance(result)

            return credentials

    def set_user_credentials(self, credentials):
        """
        Sets Credentials of the cache for authorization.

        :param credentials: The credentials of the cache for authorization.
        :type credentials: Credentials
        """
        ValidateType.type_check(credentials, Credentials, self.set_user_credentials)
        javacredentials = credentials.get_instance()

        self.__cacheconnection.setUserCredentials(javacredentials)
