from ncache.client.enum.SqlCommandType import SqlCommandType
from ncache.runtime.dependencies.CacheDependency import *
from ncache.runtime.dependencies.SqlCmdParams import SqlCmdParams
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.ExceptionHandler import ExceptionHandler


class SqlCacheDependency(CacheDependency):
    """
    Establishes a relationship between an item stored in an application's Cache object and either a row in a specific
    SQL Server database table or the results of an SQL Server query.
    """
    def __init__(self, connectionstring, cmdtext, cmdtype=None, cmdparams=None):
        """
        Initializes a new instance of the SqlCacheDependency class, using the supplied connection string and
        query string.

        :param connectionstring: connection string to be used by dependency.
        :type connectionstring: str
        :param cmdtext: cmdText to be used by dependency
        :type cmdtext: str
        :param cmdtype: The type of the command. (text/stored procedure)
        :type cmdtype: SqlCommandType
        :param cmdparams: Dict[str, SqlCmdParams] of Parameters to be passed to the command.
        :type cmdparams: dict
        """
        super().__init__()

        ValidateType.is_string(connectionstring, self.__init__)
        ValidateType.is_string(cmdtext, self.__init__)

        connectionstring = TypeCaster.to_java_primitive_type(connectionstring)
        cmdtext = TypeCaster.to_java_primitive_type(cmdtext)

        if cmdtype is None and cmdparams is None:
            self.__sqlcachedependency = JavaInstancesFactory.get_java_instance("SqlCacheDependency")(connectionstring, cmdtext)
            return

        elif cmdtype is not None and cmdparams is not None:
            ValidateType.type_check(cmdtype, SqlCommandType, self.__init__)

            for cmdparam in cmdparams:
                ValidateType.is_string(cmdparam, self.__init__)
                ValidateType.type_check(cmdparams[cmdparam], SqlCmdParams, self.__init__)

            cmdtypevalue = EnumUtil.get_sql_command_type(cmdtype.value)
            cmdparams = TypeCaster.to_java_hash_map(cmdparams)

            self.__sqlcachedependency = JavaInstancesFactory.get_java_instance("SqlCacheDependency")(connectionstring, cmdtext, cmdtypevalue, cmdparams)
            return

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("SqlCacheDependency.__init__"))

    def get_instance(self):
        return self.__sqlcachedependency

    def set_instance(self, value):
        self.__sqlcachedependency = value

    def get_command_params(self):
        """
        Gets the sql command parameters passed to SqlCacheDependency.

        :return: The sql command parameters of the dependency.
        :rtype: dict
        """
        result = self.__sqlcachedependency.getCommandParams()

        if result is not None:
            result = TypeCaster.to_python_dict(result, False, SqlCmdParams())

        return result

    def get_command_text(self):
        """
        CommandText(Query string) to be used by dependency.

        :return: The commandText(Query string) of the dependency.
        :rtype: str
        """
        result = self.__sqlcachedependency.getCommandText()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_command_type(self):
        """
        Gets the type of the sql command passed to the SqlDependency.

        :return: The type of sql command used for dependency.
        :rtype: CommandType
        """
        result = self.__sqlcachedependency.getCommandType()
        enumtype = EnumUtil.get_command_type_value(result)
        return enumtype

    def get_connection_string(self):
        """
        Gets the connection string that is required by the cache in order to connect with database.

        :return: The connection string of the dependency.
        :rtype: str
        """
        result = self.__sqlcachedependency.getConnectionString()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def __del__(self):
        pass
