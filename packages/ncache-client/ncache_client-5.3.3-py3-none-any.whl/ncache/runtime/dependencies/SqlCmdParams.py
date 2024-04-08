from datetime import datetime

from ncache.client.enum.CmdParamsType import CmdParamsType
from ncache.client.enum.SqlCmpOptions import SqlCmpOptions
from ncache.client.enum.SqlDataRowVersion import SqlDataRowVersion
from ncache.client.enum.SqlParamDirection import SqlParamDirection
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class SqlCmdParams:
    """
    Holds the information about the type and value of the parameters passed to the command.
    """
    def __init__(self):
        """
        Default Constructor
        """
        self.__sqlcmdparams = JavaInstancesFactory.get_java_instance("SqlCmdParams")()

    def get_instance(self):
        return self.__sqlcmdparams

    def set_instance(self, value):
        self.__sqlcmdparams = value

    def get_cmd_params_type(self):
        """
        Gets the SqlDbType of the passed parameter.

        :return: The SqlDbType of the parameter.
        :rtype: CmdParamsType
        """
        result = self.__sqlcmdparams.getCmdParamsType()
        enumtype = EnumUtil.get_cmd_params_type_value(result)
        return enumtype

    def get_compare_info(self):
        """
        Gets the CompareInfo object that defines how string comparisons should be performed for this parameter.

        :return: The object that defines string comparisons for the parameter.
        :rtype: SqlCmpOptions
        """
        result = self.__sqlcmdparams.getCompareInfo()
        enumtype = EnumUtil.get_sql_cmp_options_value(result)
        return enumtype

    def get_is_nullable(self):
        """
        Gets a value that indicates whether the parameter accepts None values.

        :return: True if the parameter accepts None value otherwise false.
        :rtype: bool
        """
        result = self.__sqlcmdparams.getIsNullable()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_locale_id(self):
        """
        Gets the locale identifier that determines conventions and language for a particular region.

        :return: The locale id.
        :rtype: int
        """
        result = self.__sqlcmdparams.getLocaleId()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_off_set(self):
        """
        Gets the offset to the Value property.

        :return: The offset of the value.
        :rtype: int
        """
        result = self.__sqlcmdparams.getoffset()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_precision(self):
        """
        Gets the maximum number of digits used to represent the Value property.

        :return: The precision of the value ranging from -128 to +127.
        :rtype: int
        """
        result = self.__sqlcmdparams.getPrecision()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_scale(self):
        """
        Gets the number of decimal places to which Value is resolved.

        :return: The scale of the value ranging from -128 to +127.
        :rtype: int
        """
        result = self.__sqlcmdparams.getScale()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_size(self):
        """
        Gets the maximum size, in bytes, of the data within the column.

        :return: The data size within the column.
        :rtype: int
        """
        result = self.__sqlcmdparams.getSize()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_source_column(self):
        """
        Gets the name of the source column mapped to the DataSet and used for loading or returning the Value.

        :return: The name of the source column.
        :rtype: str
        """
        result = self.__sqlcmdparams.getSourceColumn()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_source_column_null_mapping(self):
        """
        Gets a value which indicates whether the source column is nullable. This allows SqlCommandBuilder to correctly
        generate Update statements for nullable columns.

        :return: True if source column accepts None values otherwise false.
        :rtype: bool
        """
        result = self.__sqlcmdparams.getSourceColumnNullMapping()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_source_version(self):
        """
        Sets the DataRowVersion to use when you load Value.

        :return: The DataRowVersion of the value.
        :rtype: SqlDataRowVersion
        """
        result = self.__sqlcmdparams.getSourceVersion()
        enumtype = EnumUtil.get_sql_data_row_version_value(result)
        return enumtype

    def get_sql_parameter_direction(self):
        """
        Gets a value that indicates whether the parameter is input-only, output-only, bidirectional, or a stored
        procedure return value parameter.

        :return: The sql param direction of parameter.
        :rtype: SqlParamDirection
        """
        result = self.__sqlcmdparams.getSqlParameterDirection()
        enumtype = EnumUtil.get_sql_param_direction_value(result)
        return enumtype

    def get_sql_value(self):
        """
        Gets the value of the parameter as an SQL type.

        :return: The value of the parameter as SQL type.
        :rtype: object
        """
        return self.__sqlcmdparams.getSqlValue()

    def get_type_name(self):
        """
        Gets the type name for a table-valued parameter.

        :return: The typename of the table-valued parameter.
        :rtype: str
        """
        result = self.__sqlcmdparams.getTypeName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_udt_type_name(self):
        """
        Gets a string that represents a user-defined type as a parameter.

        :return: The user-defined type as parameter.
        :rtype: str
        """
        result = self.__sqlcmdparams.getUdtTypeName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_value(self):
        """
        Gets the value of the passed parameter.

        :return: The parameter value.
        :rtype: object
        """
        result = self.__sqlcmdparams.getValue()

        if result is not None and 'Date' in type(result).__name__:
            result = TypeCaster.to_python_date(result)

        return result

    def set_cmd_params_type(self, paramstype):
        """
        Sets the SqlDbType of the passed parameter.

        :param paramstype: The SqlDbType of the parameter.
        :type paramstype: CmdParamsType
        """
        ValidateType.type_check(paramstype, CmdParamsType, self.set_cmd_params_type)
        javaenum = EnumUtil.get_cmd_params_type(paramstype.value)
        self.__sqlcmdparams.setCmdParamsType(javaenum)

    def set_compare_info(self, info):
        """
        Sets the CompareInfo object that defines how string comparisons should be performed for this parameter.

        :param info: The object that defines string comparisons for the parameter.
        :rtype: SqlCmpOptions
        """
        ValidateType.type_check(info, SqlCmpOptions, self.set_compare_info)
        javaenum = EnumUtil.get_sql_cmp_options(info.value)
        self.__sqlcmdparams.setCompareInfo(javaenum)

    def set_is_nullable(self, isnullable):
        """
        Sets a value that indicates whether the parameter accepts None values.

        :param isnullable: The boolean that specifies whether parameter accepts None values or not.
        :type isnullable: bool
        """
        ValidateType.type_check(isnullable, bool, self.set_is_nullable)

        self.__sqlcmdparams.setIsNullable(TypeCaster.to_java_primitive_type(isnullable))

    def set_locale_id(self, localeid):
        """
        Sets the locale identifier that determines conventions and language for a particular region.

        :param localeid: The locale id.
        :type localeid: int
        """
        ValidateType.type_check(localeid, int, self.set_locale_id)

        self.__sqlcmdparams.setLocaleId(TypeCaster.to_java_primitive_type(localeid))

    def set_off_set(self, offset):
        """
        Sets the offset to the Value property.

        :param offset: The offset of the value.
        :type offset: int
        """
        ValidateType.type_check(offset, int, self.set_off_set)

        self.__sqlcmdparams.setoffset(TypeCaster.to_java_primitive_type(offset))

    def set_precision(self, precision):
        """
        Sets the maximum number of digits used to represent the Value property.

        :param precision: The precision in range of -128 to +127 of the value.
        :type precision: int
        """
        ValidateType.type_check(precision, int, self.set_precision)

        if (precision < -128) or (precision > 127):
            raise ValueError(ExceptionHandler.get_invalid_range_exception_message("precision", "-128", "+127"))

        self.__sqlcmdparams.setprecision(TypeCaster.to_java_primitive_type(precision).byteValue())

    def set_scale(self, scale):
        """
        Sets the number of decimal places to which Value is resolved.

        :param scale: The scale in range of -128 to +127 of the value.
        :type scale: int
        """
        ValidateType.type_check(scale, int, self.set_off_set)

        if (scale < -128) or (scale > 127):
            raise ValueError(ExceptionHandler.get_invalid_range_exception_message("scale", "-128", "+127"))

        self.__sqlcmdparams.setScale(TypeCaster.to_java_primitive_type(scale).byteValue())

    def set_size(self, size):
        """
        Sets the maximum size, in bytes, of the data within the column.

        :param size: The data size within the column.
        :type size: int
        """
        ValidateType.type_check(size, int, self.set_size)

        self.__sqlcmdparams.setSize(TypeCaster.to_java_primitive_type(size))

    def set_source_column(self, sourcecolumn):
        """
        Sets the name of the source column mapped to the DataSet and used for loading or returning the Value.

        :param sourcecolumn: The name of the source column.
        :type sourcecolumn: str
        """
        ValidateType.type_check(sourcecolumn, str, self.set_source_column)

        self.__sqlcmdparams.setSourceColumn(TypeCaster.to_java_primitive_type(sourcecolumn))

    def set_source_column_null_mapping(self, nullmaping):
        """
        Sets a value which indicates whether the source column is nullable. This allows SqlCommandBuilder to correctly
        generate Update statements for nullable columns.

        :param nullmaping: Specifies whether source column accepts None values or not.
        :type nullmaping: bool
        """
        ValidateType.type_check(nullmaping, bool, self.set_source_column_null_mapping)

        self.__sqlcmdparams.setSourceColumnNullMapping(TypeCaster.to_java_primitive_type(nullmaping))

    def set_source_version(self, version):
        """
        Sets the DataRowVersion to use when you load Value.

        :param version: The DataRowVersion of the value.
        :type version: SqlDataRowVersion
        """
        ValidateType.type_check(version, SqlDataRowVersion, self.set_source_version)
        javaenum = EnumUtil.get_sql_data_row_version(version.value)
        self.__sqlcmdparams.setSourceVersion(javaenum)

    def set_sql_parameter_direction(self, direction):
        """
        Sets a value that indicates whether the parameter is input-only, output-only, bidirectional, or a stored
        procedure return value parameter.

        :param direction: The sql param direction of parameter.
        :type direction: SqlParamDirection
        """
        ValidateType.type_check(direction, SqlParamDirection, self.set_sql_parameter_direction)
        javaenum = EnumUtil.get_sql_param_direction(direction.value)
        self.__sqlcmdparams.setSqlParameterDirection(javaenum)

    def set_sql_value(self, value):
        """
        Sets the value of the parameter as a SQL type.

        :param value: The value of the parameter as SQL type.
        :type value: object
        """
        ValidateType.is_none(value, self.set_sql_value)

        self.__sqlcmdparams.setSqlValue(value)

    def set_udt_type_name(self, name):
        """
        Sets a string that represents a user-defined type as a parameter.

        :param name: The user-defined type as parameter.
        :type name: str
        """
        ValidateType.type_check(name, str, self.set_udt_type_name)

        self.__sqlcmdparams.setUdtTypeName(TypeCaster.to_java_primitive_type(name))

    def set_type_name(self, name):
        """
        Sets the type name for a table-valued parameter.

        :param name: The typename of the table-valued parameter.
        :type name: str
        """
        ValidateType.type_check(name, str, self.set_type_name)

        self.__sqlcmdparams.setTypeName(TypeCaster.to_java_primitive_type(name))

    def set_value(self, value):
        """
        Sets the value of the passed parameter.

        :param value: The parameter value.
        :type value: object
        """
        ValidateType.is_none(value, self.set_value)
        javavalue = value

        if type(value) is datetime:
            javavalue = TypeCaster.to_java_date(value)

        self.__sqlcmdparams.setValue(javavalue)
