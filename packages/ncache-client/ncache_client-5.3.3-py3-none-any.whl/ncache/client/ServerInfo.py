from ipaddress import IPv4Address

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class ServerInfo:
    """
    Provide connection information for the client to the server node in cache.
    """
    def __init__(self, servername=None, port=None, ipaddress=None):
        """
        Initializes a new instance of ServerInfo.

        :param servername: Specifies name of the server node where cache is running.
        :type servername: str
        :param port: Specifies port for client to connect to the server node.
        :type port: int
        :param ipaddress: Specifies IPv4Address of the server node where cache is running.
        :type ipaddress: IPv4Address
        """
        if servername is not None and ipaddress is None:
            ValidateType.is_string(servername, self.__init__)
            javaservername = TypeCaster.to_java_primitive_type(servername)

            if port is not None:
                ValidateType.is_int(port, self.__init__)
                javaport = TypeCaster.to_java_primitive_type(port)

                self.__serverinfo = JavaInstancesFactory.get_java_instance("ServerInfo")(javaservername, javaport)
                return

            self.__serverinfo = JavaInstancesFactory.get_java_instance("ServerInfo")(javaservername)
            return

        elif servername is None and ipaddress is not None:
            ValidateType.type_check(ipaddress, IPv4Address, self.__init__)
            strip = format(ipaddress)
            javastrip = TypeCaster.to_java_primitive_type(strip)
            javaipaddress = jp.java.net.InetAddress.getByName(javastrip)

            self.__serverinfo = JavaInstancesFactory.get_java_instance("ServerInfo")(javaipaddress)
            return

        elif servername is None and ipaddress is None and port is None:
            self.__serverinfo = JavaInstancesFactory.get_java_instance("ServerInfo")()

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("ServerInfo.__init__"))

    def get_instance(self):
        return self.__serverinfo

    def set_instance(self, value):
        self.__serverinfo = value

    def __str__(self):
        result = self.__serverinfo.toString()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def compare_to(self, obj):
        """
        Compares the ServerInfo on the basis of priority

        :param obj: The server info object to compare.
        :type obj: ServerInfo
        :return: 0 if equals, -1 if lesser and 1 if greater than the comparing serverInfo
        :rtype: int
        """
        ValidateType.type_check(obj, ServerInfo, self.compare_to)

        result = self.__serverinfo.compareTo(obj.get_instance())

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def __eq__(self, other):
        ValidateType.type_check(other, ServerInfo, self.__eq__)

        result = self.__serverinfo.equals(other.get_instance())

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_ip(self):
        """
        Gets the IPAddress of the server node where cache is running.

        :return: The IPAddress of the server node where cache is running.
        :rtype: IPv4Address
        """
        result = self.__serverinfo.getIP()

        if result is not None:
            hostname = result.getHostName()
            result = IPv4Address(hostname)

        return result

    def get_name(self):
        """
        Gets the name of the server node where cache is running.

        :return: The name of the server node where cache is running.
        :rtype: str
        """
        result = self.__serverinfo.getName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_port(self):
        """
        Gets the port for client to connect to the server node.

        :return: The port for client to connect to the server node.
        :rtype: int
        """
        result = self.__serverinfo.getPort()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_ip(self, ip):
        """
        Sets the IPAddress of the server node where cache is running.

        :param ip: The IPAddress of the server node where cache is running.
        :type ip: IPv4Address or str
        """
        if type(ip) is str:
            javaip = TypeCaster.to_java_primitive_type(ip)

            self.__serverinfo.setIP(javaip)
            return
        elif isinstance(ip, IPv4Address):
            javaip = format(ip)
            inetaddress = jp.java.net.InetAddress.getByName(javaip)

            self.__serverinfo.setIP(inetaddress)
            return
        else:
            raise TypeError(ExceptionHandler.get_invalid_ip_exception_message(IPv4Address))

    def set_name(self, name):
        """
        Sets the name of the server node where cache is running.

        :param name: The name of the server node where cache is running.
        :type name: str
        """
        ValidateType.is_string(name, self.set_name)

        javaname = TypeCaster.to_java_primitive_type(name)
        self.__serverinfo.setName(javaname)

    def set_port(self, port):
        """
        Sets the port for client to connect to the server node.

        :param port: The port for client to connect to the server node.
        :type port: int
        """
        ValidateType.is_int(port, self.set_port)

        javaport = TypeCaster.to_java_primitive_type(port)
        self.__serverinfo.setPort(javaport)
