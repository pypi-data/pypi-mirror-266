from ncache.client.enum.OracleCmdParamsType import OracleCmdParamsType
from ncache.client.enum.OracleParameterDirection import OracleParameterDirection
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.JavaInstancesFactory import *
from ncache.util.ValidateType import ValidateType


class OracleCmdParams:
    """
    Holds the type and value of the parameters passed to the command instance.
    """
    def __init__(self):
        """
        Creates an instance of Oracle command parameters with OracleParameterDirection.Input.
        """
        self.__oraclecmdparams = JavaInstancesFactory.get_java_instance("OracleCmdParams")()

    def get_instance(self):
        return self.__oraclecmdparams

    def set_instance(self, value):
        self.__oraclecmdparams = value

    def get_direction(self):
        """
        Gets the direction of the passed parameters (in/out).

        :return: The direction of parameters.
        :rtype: OracleParameterDirection
        """
        result = self.__oraclecmdparams.getDirection()
        enumtype = EnumUtil.get_key_dependency_type_value(result)
        return enumtype

    def get_type(self):
        """
        Gets the type of the command parameter.

        :return: The command param type.
        :rtype: OracleCmdParamsType
        """
        result = self.__oraclecmdparams.getType()
        enumtype = EnumUtil.get_key_dependency_type_value(result)
        return enumtype

    def get_value(self):
        """
        Gets the value of the command parameter.

        :return: The value against the command param.
        """
        return self.__oraclecmdparams.getValue()

    def set_direction(self, direction):
        """
        Sets the direction of the passed parameters (in/out).

        :param direction: The direction of parameters to set.
        :type direction: OracleParameterDirection
        """
        ValidateType.type_check(direction, OracleParameterDirection, self.set_direction)
        javaenum = EnumUtil.get_oracle_parameter_direction(direction.value)
        self.__oraclecmdparams.setKeyDependencyType(javaenum)

    def set_type(self, paramstype):
        """
        Sets the type of the command parameter.

        :param paramstype: The command param type.
        :type paramstype: OracleCmdParamsType
        """
        ValidateType.type_check(paramstype, OracleParameterDirection, self.set_direction)
        javaenum = EnumUtil.get_oracle_cmd_params_type(paramstype.value)
        self.__oraclecmdparams.setKeyDependencyType(javaenum)

    def set_value(self, value):
        self.__oraclecmdparams.setValue(value)
