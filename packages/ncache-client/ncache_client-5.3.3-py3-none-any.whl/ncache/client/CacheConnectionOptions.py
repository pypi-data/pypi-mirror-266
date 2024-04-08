from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.JavaInstancesFactory import *
from ncache.client.Credentials import Credentials
from ncache.client.ServerInfo import ServerInfo
from ncache.client.enum.ClientCacheSyncMode import ClientCacheSyncMode
from ncache.client.enum.IsolationLevel import IsolationLevel
from ncache.client.enum.LogLevel import LogLevel
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheConnectionOptions:
    """
    Instance of this class can be used to define the parameters at the time of client connection with the cache.
    """
    def __init__(self):
        self.__cacheconnectionoptions = JavaInstancesFactory.get_java_instance("CacheConnectionOptions")()

    def get_instance(self):
        return self.__cacheconnectionoptions

    def set_instance(self, value):
        self.__cacheconnectionoptions = value

    def get_server_list(self):
        """
        Gets the list of ServerInfo in the cache.

        :return: The list of Server info's.
        :rtype: list
        """
        result = self.__cacheconnectionoptions.getServerList()

        if result is not None:
            result = TypeCaster.to_python_list(result, isjavatype=False, classinstance=ServerInfo())

        return result

    def set_server_list(self, serverlist):
        """
        Gets the list of ServerInfo in the cache.

        :param serverlist: The list of Server info's.
        :type serverlist: list
        """
        ValidateType.type_check(serverlist, list, self.set_server_list)
        for server in serverlist:
            ValidateType.type_check(server, ServerInfo, self.set_server_list)

        javaserverlist = TypeCaster.to_java_array_list(serverlist, isjavatype=False)
        self.__cacheconnectionoptions.setServerList(javaserverlist)

    def get_isolation_mode(self):
        """
        Gets the Isolation level of the cache.

        :return: The isolation level of the cache.
        :rtype: IsolationLevel
        """

        result = self.__cacheconnectionoptions.getIsolationMode()

        if result is not None:
            result = EnumUtil.get_isolation_level_value(result)

        return result

    def set_isolation_level(self, isolationlevel):
        """
        Sets the isolation level of the cache.

        :param isolationlevel: The isolation level of the cache.
        :type isolationlevel: IsolationLevel
        """
        ValidateType.type_check(isolationlevel, IsolationLevel, self.set_isolation_level)

        javaisolationlevel = EnumUtil.get_isolation_level(isolationlevel.value)
        self.__cacheconnectionoptions.setIsolationLevel(javaisolationlevel)

    def get_default_read_thru_provider(self):
        """
        Gets the name of the default ReadThruProvider.

        :return: The name of the default ReadThruProvider.
        :rtype: str
        """
        result = self.__cacheconnectionoptions.getDefaultReadThruProvider()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_default_read_thru_provider(self, providername):
        """
        Sets the name of the default ReadThruProvider.

        :param providername: The name of the default ReadThruProvider.
        :type providername: str
        """
        ValidateType.is_string(providername, self.set_default_read_thru_provider)
        javaprovidername = TypeCaster.to_java_primitive_type(providername)

        self.__cacheconnectionoptions.setDefaultReadThruProvider(javaprovidername)

    def get_default_write_thru_provider(self):
        """
        Gets the name of the default WriteThruProvider.

        :return: The name of the default WriteThruProvider.
        :rtype: str
        """
        result = self.__cacheconnectionoptions.getDefaultWriteThruProvider()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_default_write_thru_provider(self, providername):
        """
        Sets the name of the default WriteThruProvider.

        :param providername: The name of the default WriteThruProvider.
        :type providername: str
        """
        ValidateType.is_string(providername, self.set_default_write_thru_provider)
        javaprovidername = TypeCaster.to_java_primitive_type(providername)

        self.__cacheconnectionoptions.setDefaultWriteThruProvider(javaprovidername)

    def get_client_bind_ip(self):
        """
        Gets the IP for the client to be bind with.

        :return: The IP for the client to be bind with.
        :rtype: str
        """
        result = self.__cacheconnectionoptions.getClientBindIP()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_client_bind_ip(self, ip):
        """
        Sets the IP for the client to be bind with.

        :param ip: The IP for the client to be bind with.
        :type ip: str
        """
        ValidateType.is_string(ip, self.set_client_bind_ip)
        javaip = TypeCaster.to_java_primitive_type(ip)

        self.__cacheconnectionoptions.setClientBindIP(javaip)

    def get_app_name(self):
        """
        Gets the application name.If different client applications are connected to server and because of any issue
        which results in connection failure with server, after the client again establishes connection AppName is used
        to identify these different client applications.

        :return: The application name.
        :rtype: str
        """
        result = self.__cacheconnectionoptions.getAppName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_app_name(self, appname):
        """
        Sets the application name.If different client applications are connected to server and because of any issue
        which results in connection failure with server, after the client again establishes connection AppName is used
        to identify these different client applications.

        :param appname: The application name.
        :type appname: str
        """
        ValidateType.is_string(appname, self.set_app_name)
        javaappname = TypeCaster.to_java_primitive_type(appname)

        self.__cacheconnectionoptions.setAppName(javaappname)

    def get_load_balance(self):
        """
        When this flag is set, client tries to connect to the optimum server in terms of number of connected clients.

        :return: True if loadBalancing is enabled, otherwise False.
        """
        result = self.__cacheconnectionoptions.getLoadBalance()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_load_balance(self, value):
        """
        When this flag is set, client tries to connect to the optimum server in terms of number of connected clients.

        :param value: The boolean value indicating whether to set LoadBalancing True or False.
        :type value: bool
        """
        ValidateType.is_string(value, self.set_load_balance)
        javavalue = TypeCaster.to_java_primitive_type(value)

        self.__cacheconnectionoptions.setLoadBalance(javavalue)

    def get_client_cache_mode(self):
        """
        Gets ClientCacheSyncMode to specify how the Client cache is synchronized with the cluster caches through events.

        :return: The client cache sync mode associated with connection options.
        :rtype: ClientCacheSyncMode
        """
        result = self.__cacheconnectionoptions.getClientCacheMode()

        if result is not None:
            result = EnumUtil.get_client_cache_sync_mode_value(result)

        return result

    def get_client_request_timeout(self):
        """
        Clients operation timeout specified in seconds. Clients wait for the response from the server for this time. If
        the response is not received within this time, the operation is not successful.

        :return: The request timeout associated with connection options.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getClientRequestTimeOut()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_command_retries(self):
        """
        If client application sends request to server for any operation and a response is not received, then the number
        of retries it will make until it gets response is defined here.

        :return: An integer indicating the number of command retries.
        :rtype: int
        """
        result = self.__cacheconnectionoptions.getCommandRetries()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_command_retry_interval(self):
        """
        In case if client app doesn't get response against some operation call on server, the command retry interval
        defines the waiting period before the next attempt to send the operation the server is made. Type integer which
        defines seconds.

        :return: The command retry interval in form of TimeSpan.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getCommandRetryInterval()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_connection_retries(self):
        """
        Number of tries to re-establish a broken connection between client and server.

        :return: An integer indicating the number of retries.
        :rtype: int
        """
        result = self.__cacheconnectionoptions.getConnectionRetries()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_connection_timeout(self):
        """
        Client's connection timeout specified in seconds.

        :return: The client connection timeout in form of a TimeSpan.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getConnectionTimeout()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_enable_client_logs(self):
        """
        Gets the flag that specifies whether to create client logs or not.

        :return: True if client logs are enabled otherwise False.
        :rtype: bool
        """
        result = self.__cacheconnectionoptions.getEnableClientLogs()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_enable_keep_alive(self):
        """
        Gets the keep alive flag.

        :return: True if keep alive enabled otherwise false.
        :rtype: bool
        """
        result = self.__cacheconnectionoptions.getEnableKeepAlive()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_keep_alive_interval(self):
        """
        Gets the KeepAliveInterval, which will be in effect if the EnabledKeepAlive is set 'True' or is specified 'True'
        from the client configuration.

        :return: The keep alive interval in form of TimeSpan.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getKeepAliveInterval()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_log_level(self):
        """
        Gets the LogLevel either as INFO, ERROR or DEBUG.

        :return: The log level associated with connection options.
        :rtype: LogLevel
        """
        result = self.__cacheconnectionoptions.getLogLevel()

        if result is not None:
            result = EnumUtil.get_log_level_value(result)

        return result

    def get_retry_connection_delay(self):
        """
        The time after which client will try to reconnect to the server.

        :return: The retry connection delay in form of TimeSpan.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getRetryConnectionDelay()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_retry_interval(self):
        """
        Time in seconds to wait between two connection retries.

        :return: The retry interval in form of TimeSpan.
        :rtype: TimeSpan
        """
        result = self.__cacheconnectionoptions.getRetryInterval()

        if result is not None:
            timespan = TimeSpan(123)
            timespan.set_instance(result)

            return timespan

    def get_user_credentials(self):
        """
        Gets Credentials for the authentication of connection with the cache. This information is required when the
        security is enabled.

        :return: The credentials for the authentication of cache connection.
        :rtype: Credentials
        """
        result = self.__cacheconnectionoptions.getUserCredentials()

        if result is not None:
            credentials = Credentials()
            credentials.set_instance(result)

            return credentials

    def set_client_cache_mode(self, clientcachemode):
        """
        Sets ClientCacheSyncMode to specify how the Client cache is synchronized with the cluster caches through events.

        :param clientcachemode: The client cache sync mode to be associated with connection options.
        :type clientcachemode: ClientCacheSyncMode
        """
        ValidateType.type_check(clientcachemode, ClientCacheSyncMode, self.set_client_cache_mode)

        javaclientcachemode = EnumUtil.get_client_cache_sync_mode(clientcachemode.value)
        self.__cacheconnectionoptions.setClientCacheMode(javaclientcachemode)

    def set_client_request_timeout(self, timeout):
        """
        Clients operation timeout specified in seconds. Clients wait for the response from the server for this time. If
        the response is not received within this time, the operation is not successful.

        :param timeout: The request timeout to be associated with connection options.
        :type timeout: TimeSpan
        """
        ValidateType.type_check(timeout, TimeSpan, self.set_client_request_timeout)

        javatimeout = timeout.get_instance()
        self.__cacheconnectionoptions.setClientRequestTimeOut(javatimeout)

    def set_command_retries(self, retries):
        """
        Number of tries to re-establish a broken connection between client and server.

        :param retries: An int indicating the number of retries.
        :type retries: int
        """
        ValidateType.is_int(retries, self.set_command_retries)

        javaretries = TypeCaster.to_java_primitive_type(retries)
        self.__cacheconnectionoptions.setCommandRetries(javaretries)

    def set_command_retry_interval(self, retryinterval):
        """
        In case if client app doesn't get response against some operation call on server, the command retry interval
        defines the waiting period before the next attempt to send the operation the server is made. Type integer which
        defines seconds.

        :param retryinterval: The command retry interval in form of TimeSpan.
        :type retryinterval: TimeSpan
        """
        ValidateType.type_check(retryinterval, TimeSpan, self.get_command_retry_interval)

        javatimeout = retryinterval.get_instance()
        self.__cacheconnectionoptions.setCommandRetryInterval(javatimeout)

    def set_connection_retries(self, retries):
        """
        Number of tries to re-establish a broken connection between client and server.

        :param retries: An int indicating the number of retries.
        :type retries: int
        """
        ValidateType.is_int(retries, self.set_connection_retries)

        javaretries = TypeCaster.to_java_primitive_type(retries)
        self.__cacheconnectionoptions.setConnectionRetries(javaretries)

    def set_connection_timeout(self, timeout):
        """
        Client's connection timeout specified in seconds.

        :param timeout: The client connection timeout in form of a TimeSpan.
        :type timeout: TimeSpan
        """
        ValidateType.type_check(timeout, TimeSpan, self.set_connection_timeout)

        javatimeout = timeout.get_instance()
        self.__cacheconnectionoptions.setConnectionTimeout(javatimeout)

    def set_enable_client_logs(self, enablelogs):
        """
        Sets the flag that specifies whether to create client logs or not.

        :param enablelogs: The boolean value that specifies whether client logs are enabled or not.
        :type enablelogs: bool
        """
        ValidateType.type_check(enablelogs, bool, self.set_enable_client_logs)

        javaenablelogs = TypeCaster.to_java_primitive_type(enablelogs)
        self.__cacheconnectionoptions.setEnableClientLogs(javaenablelogs)

    def set_enable_keep_alive(self, enablekeepalive):
        """
        Sets the keep alive flag.

        :param enablekeepalive: A boolean value that specifies whether to enable keep alive or not.
        :type enablekeepalive: bool
        """
        ValidateType.type_check(enablekeepalive, bool, self.set_enable_keep_alive)

        javaenablekeepalive = TypeCaster.to_java_primitive_type(enablekeepalive)
        self.__cacheconnectionoptions.setEnableKeepAlive(javaenablekeepalive)

    def set_keep_alive_interval(self, interval):
        """
        Sets the KeepAliveInterval, which will be in effect if the EnabledKeepAlive is set 'True' or is specified 'True'
        from the client configuration.

        :param interval: The keep alive interval in form of TimeSpan.
        :type interval: TimeSpan
        """
        ValidateType.type_check(interval, TimeSpan, self.set_keep_alive_interval)

        javainterval = interval.get_instance()
        self.__cacheconnectionoptions.setKeepAliveInterval(javainterval)

    def set_log_level(self, loglevel):
        """
        Sets the LogLevel either as INFO, ERROR or DEBUG.

        :param loglevel: The log level to be associated with connection options.
        :type loglevel: LogLevel
        """
        ValidateType.type_check(loglevel, LogLevel, self.set_log_level)

        javaloglevel = EnumUtil.get_log_level(loglevel.value)
        self.__cacheconnectionoptions.setLogLevel(javaloglevel)

    def set_retry_connection_delay(self, connectiondelay):
        """
        The time after which client will try to reconnect to the server.

        :param connectiondelay: The retry connection delay in form of TimeSpan.
        :type connectiondelay: TimeSpan
        """
        ValidateType.type_check(connectiondelay, TimeSpan, self.set_retry_connection_delay)

        javaconnectiondelay = connectiondelay.get_instance()
        self.__cacheconnectionoptions.setRetryConnectionDelay(javaconnectiondelay)

    def set_retry_interval(self, retryinterval):
        """
        Time in seconds to wait between two connection retries.

        :param retryinterval: The retry interval in form of TimeSpan.
        :type retryinterval: TimeSpan
        """
        ValidateType.type_check(retryinterval, TimeSpan, self.set_retry_interval)

        javaretryinterval = retryinterval.get_instance()
        self.__cacheconnectionoptions.setRetryInterval(javaretryinterval)

    def set_user_credentials(self, credentials):
        """
        Sets Credentials for the authentication of connection with the cache. This information is required when the
        security is enabled.

        :param credentials: The credentials for the authentication of cache connection.
        :type credentials: Credentials
        """
        ValidateType.type_check(credentials, Credentials, self.set_user_credentials)

        javacredentials = credentials.get_instance()
        self.__cacheconnectionoptions.setUserCredentials(javacredentials)
