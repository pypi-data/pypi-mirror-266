from ipaddress import IPv4Address

from ncache.util.JavaInstancesFactory import *
from ncache.client.enum.ConnectivityStatus import ConnectivityStatus
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class ClientInfo:
    """
    This class provides detailed information about cache client.
    """
    def __init__(self, value=None):
        """
        Initialize a new instance of ClientInfo class.
        """
        if value is None:
            self.__clientinfo = JavaInstancesFactory.get_java_instance("ClientInfo")()
        else:
            self.__clientinfo = value

    def __str__(self):
        """
        Converts Client Info to string , contains client id , Application name ,Process id , machine name and address.

        :return: ClientInfo in string form
        :rtype: str
        """
        result = self.__clientinfo.toString()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def clone(self):
        """
        Clones the object and returns the newly created clone of the object.

        :return: The newly cloned ClientInfo object
        :rtype: ClientInfo
        """
        result = self.__clientinfo.clone()

        if result is not None:
            clientinfo = ClientInfo(result)
            return clientinfo

    def get_app_name(self):
        """
        Gets Application's Name.

        :return: The name of the application.
        :rtype: str
        """
        result = self.__clientinfo.getAppName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_client_id(self):
        """
        Gets client id.

        :return: The unique id of client.
        :rtype: str
        """
        result = self.__clientinfo.getClientID()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_client_version(self):
        """
        Gets the client version of the cache client.

        :return: The client version of the cache client.
        :rtype: int
        """
        result = self.__clientinfo.getClientVersion()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_cores(self):
        """
        Get the available cores of the cache client.

        :return: The available cores of the cache client.
        :rtype: int
        """
        result = self.__clientinfo.getCores()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_ip_address(self):
        """
        Gets the ip address of the cache client.

        :return: The ipAddress of client.
        :rtype: IPv4Address
        """
        result = self.__clientinfo.getiPAddress()

        if result is not None:
            hostname = result.getHostName()
            result = IPv4Address(hostname)

        return result

    def get_mac_address(self):
        """
        Gets the mac address of the cache client.

        :return: The mac address of the cache client.
        :rtype: str
        """
        result = self.__clientinfo.getMacAddress()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_machine_name(self):
        """
        Gets the machine name of the cache client.

        :return: The machine name of the cache client.
        :rtype: str
        """
        result = self.__clientinfo.getMachineName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_process_id(self):
        """
        Gets the process id of the cache client.

        :return: The process id of the cache client.
        :rtype: int
        """
        result = self.__clientinfo.getProcessID()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_status(self):
        """
        Gets the connectivity status of the cache client.

        :return: The connectivity status of the cache client.
        :rtype: ConnectivityStatus
        """
        result = self.__clientinfo.getStatus()

        if result is not None:
            result = ConnectivityStatus(result.getValue() + 1)

        return result

    def set_app_name(self, appname):
        """
        Sets Application's Name.

        :param appname: The name to be given to application.
        :type appname: str
        """
        ValidateType.is_string(appname, self.set_app_name)
        javaappname = TypeCaster.to_java_primitive_type(appname)

        self.__clientinfo.setAppName(javaappname)

    def set_client_id(self, clientid):
        """
        Sets client id.

        :param clientid: Unique id of client.
        :type clientid: str
        """
        ValidateType.is_string(clientid, self.set_client_id)
        javaclientid = TypeCaster.to_java_primitive_type(clientid)

        self.__clientinfo.setClientID(javaclientid)

    def set_client_version(self, clientversion):
        """
        Sets the client version of the cache client.

        :param clientversion: The client version of the cache client.
        :type clientversion: int
        :return:
        """
        ValidateType.is_int(clientversion, self.set_client_version)
        javaclientversion = TypeCaster.to_java_primitive_type(clientversion)

        self.__clientinfo.setClientVersion(javaclientversion)

    def set_cores(self, cores):
        """
        Sets the available cores of the cache client.

        :param cores: Available cores of the cache client.
        :type cores: int
        :return:
        """
        ValidateType.is_int(cores, self.set_cores)
        javacores = TypeCaster.to_java_primitive_type(cores)

        self.__clientinfo.setCores(javacores)

    def set_ip_address(self, ipaddress):
        """
        Sets the ip Address of the cache client.

        :param ipaddress: The ip address of the client.
        :type ipaddress: IPv4Address
        """
        ValidateType.type_check(ipaddress, IPv4Address, self.set_ip_address)

        javaip = format(ipaddress)
        inetaddress = jp.java.net.InetAddress.getByName(javaip)

        self.__clientinfo.setiPAddress(inetaddress)

    def set_mac_address(self, macaddress):
        """
        Sets the mac address of the cache client.

        :param macaddress: The mac address of the client.
        :type macaddress: str
        """
        ValidateType.is_string(macaddress, self.set_mac_address)
        javamacaddress = TypeCaster.to_java_primitive_type(macaddress)

        self.__clientinfo.setMacAddress(javamacaddress)

    def set_machine_name(self, machinename):
        """
        Sets the machine name of the cache client.

        :param machinename: The machine name of the cache client.
        :type machinename: str
        """
        ValidateType.is_string(machinename, self.set_machine_name)
        javamachinename = TypeCaster.to_java_primitive_type(machinename)

        self.__clientinfo.setMacAddress(javamachinename)

    def set_process_id(self, processid):
        """
        Sets the process id of the cache client.

        :param processid: The process id of the cache client.
        :type processid: int
        """
        ValidateType.is_int(processid, self.set_process_id)
        javaprocessid = TypeCaster.to_java_primitive_type(processid)

        self.__clientinfo.setProcessID(javaprocessid)
