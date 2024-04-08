from ncache.client.enum.CommandType import CommandType
from ncache.client.enum.OracleCommandType import OracleCommandType
from ncache.runtime.dependencies.CacheDependency import CacheDependency
from ncache.runtime.dependencies.OracleCmdParams import OracleCmdParams
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class OracleCacheDependency(CacheDependency):
    """
    Establishes a relationship between an item stored in an application's Cache object and either a row in a specific
    Oracle database table or the results of a Oracle query. This class can not be inherited.
    """
    def __init__(self, connectionstring, cmdtext, cmdtype=None, cmdparams=None):
        """
        Initializes a new instance of the OracleCacheDependency class.

        :param connectionstring: connection string to be used by dependency.
        :type connectionstring: str
        :param cmdtext: cmdText to be used by dependency
        :type cmdtext: str
        :param cmdtype: The type of the command.
        :type cmdtype: OracleCommandType
        :param cmdparams: Dict[str, OracleCmdParams] of Parameters to be passed to the command.
        :type cmdparams: dict
        """
        super().__init__()

        ValidateType.is_string(connectionstring, self.__init__)
        ValidateType.is_string(cmdtext, self.__init__)

        connectionstring = TypeCaster.to_java_primitive_type(connectionstring)
        cmdtext = TypeCaster.to_java_primitive_type(cmdtext)

        if cmdtype is None and cmdparams is None:
            self.__oraclecachedependency = JavaInstancesFactory.get_java_instance("OracleCacheDependency")(connectionstring, cmdtext)
            return

        elif cmdtype is not None and cmdparams is not None:
            ValidateType.type_check(cmdtype, OracleCommandType, self.__init__)

            for cmdparam in cmdparams:
                if type(cmdparam) is not str or type(cmdparams[cmdparam]) is not OracleCmdParams:
                    raise TypeError("Please provide value of type Dict[str, OracleCmdParams] for cmdparams")

            cmdtypevalue = EnumUtil.get_oracle_command_type(cmdtype.value)
            cmdparams = TypeCaster.to_java_hash_map(cmdparams)

            self.__oraclecachedependency = JavaInstancesFactory.get_java_instance("OracleCacheDependency")(connectionstring, cmdtext, cmdtypevalue, cmdparams)
            return

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("OracleCacheDependency.__init__"))

    def get_instance(self):
        return self.__oraclecachedependency

    def set_instance(self, value):
        self.__oraclecachedependency = value

    def get_command_params(self):
        """
        Gets the oracle command parameters passed to the Oracle command.

        :return: The oracle command parameters of the dependency.
        :rtype: dict
        """
        result = self.__oraclecachedependency.getCommandParams()

        if result is not None:
            result = TypeCaster.to_python_dict(result, False, OracleCmdParams())

        return result

    def get_command_text(self):
        """
        CommandText(Query string) to be used by dependency.

        :return: The commandText(Query string) of the dependency.
        :rtype: str
        """
        result = self.__oraclecachedependency.getCommandText()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_command_type(self):
        """
        Gets the type of the Oracle command passed to the OracleDependency.

        :return: The type of oracle command used for dependency.
        :rtype: CommandType
        """
        result = self.__oraclecachedependency.getCommandType()
        enumtype = EnumUtil.get_command_type_value(result)
        return enumtype

    def get_connection_string(self):
        """
        Gets the connection string that is required by the cache in order to connect with database.

        :return: The connection string of the dependency.
        :rtype: str
        """
        result = self.__oraclecachedependency.getConnectionString()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def __del__(self):
        pass
