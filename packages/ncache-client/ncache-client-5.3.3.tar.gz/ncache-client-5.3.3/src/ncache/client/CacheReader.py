import collections
import json
from datetime import datetime

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheReader:
    """
    Reads one or more than forward-only stream of result sets by executing OQ commands on cache source.
    """
    def __init__(self, value):
        self.__reader = value

    def get_instance(self):
        return self.__reader

    def set_instance(self, value):
        self.__reader = value

    def get_boolean(self, index):
        """
        Gets value of specified index as bool.

        :param index: Index of column.
        :type index: int
        :return: bool value on specified index.
        :rtype: bool
        """
        ValidateType.is_int(index, self.get_boolean)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__reader.getBoolean(javaindex)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_date(self, index):
        """
        Gets value of specified index as str.

        :param index: Index of column.
        :type index: int
        :return: datetime value at specified index.
        :rtype: datetime
        """
        ValidateType.is_int(index, self.get_date)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__reader.getDate(javaindex)

        if result is not None:
            result = TypeCaster.to_python_date(result)

        return result

    def get_field_count(self):
        """
        Gets number of columns.

        :return: Number of columns.
        :rtype: int
        """
        result = self.__reader.getFieldCount()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_int(self, index):
        """
        Gets value of specified index as int.

        :param index: Index of column.
        :type index: int
        :return: int value on specified index.
        :rtype: int
        """
        ValidateType.is_int(index, self.get_int)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__reader.getInt(javaindex)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_is_closed(self):
        """
        Returns True, if reader is closed else False.

        :return: True, if reader is closed else False.
        :rtype: bool
        """
        result = self.__reader.getIsClosed()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_name(self, index):
        """
        Returns name of specified column index.

        :param index: Index of column.
        :type index: int
        :return: Name of column.
        :rtype: str
        """
        ValidateType.is_int(index, self.get_name)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__reader.getName(javaindex)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_ordinal(self, columnname):
        """
        Returns index of specified column name.

        :param columnname: Name of column.
        :type columnname: str
        :return: Index of column.
        :rtype: int
        """
        ValidateType.is_string(columnname, self.get_ordinal)
        javacolumnname = TypeCaster.to_java_primitive_type(columnname)

        result = self.__reader.getOrdinal(javacolumnname)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_string(self, index):
        """
        Gets value of specified index as str.

        :param index: Index of column.
        :type index: int
        :return: str value on specified index.
        :rtype: str
        """
        ValidateType.is_int(index, self.get_string)
        javaindex = TypeCaster.to_java_primitive_type(index)

        result = self.__reader.getString(javaindex)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def json_to_object(self, json_data, class_type):
        class_attrs = vars(class_type()).keys()
        result = {key: json_data[key] for key in class_attrs}
        return result

    def get_value(self, objtype, index=None, columnname=None):
        """
        Gets value of specified column name/index.

        :param columnname: Name of column.
        :type columnname: str
        :param index: Index of column.
        :type index: int
        :param objtype: Specifies the class of value obtained from the cache.
        :type objtype: type
        :return: Object value of specified column name/index.
        :rtype: object
        """
        ValidateType.type_check(objtype, type, self.get_value)

        if index is not None:
            ValidateType.is_int(index, self.get_value)

        pythontype, javatype = TypeCaster.is_java_primitive(objtype)

        if javatype is None:
            if isinstance(objtype, collections.Collection):
                javatype = JavaInstancesFactory.get_java_instance("JsonArray")
            else:
                javatype = JavaInstancesFactory.get_java_instance("JsonObject")

        if columnname is not None:
            ValidateType.is_string(columnname, self.get_value)
            javacolumnname = TypeCaster.to_java_primitive_type(columnname)

            result = self.__reader.getValue(javacolumnname, javatype)
        elif index is not None:
            javaindex = TypeCaster.to_java_primitive_type(index)
            result = self.__reader.getValue(javaindex, javatype)
        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("CacheReader.get_value"))

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        if index is not None:
            if not isinstance(result, (int, float, str, bool)):
                json_object = json.loads(result.toString())
                result = self.json_to_object(json_object, objtype)

        return result

    def get_values(self, objects, objtype, objectcount):
        """
        Populates list of objects with values in current row.

        :param objectcount: Number of values to be populated.
        :type objectcount: int
        :param objects: List of objects to be populated.
        :type objects: list
        :param objtype: Specifies the class of values obtained from the list.
        :type objtype: type
        :return: Number of objects copied in specified array.
        :rtype: int
        """
        ValidateType.type_check(objtype, type, self.get_values)
        ValidateType.type_check(objects, list, self.get_values)
        ValidateType.type_check(objectcount, int, self.get_values)

        javaarray = jp.JArray(jp.java.lang.Object)(objectcount)

        pythontype, javatype = TypeCaster.is_java_primitive(objtype)

        if javatype is None:
            if isinstance(objtype(), collections.Collection):
                javatype = JavaInstancesFactory.get_java_instance("JsonArray")
            else:
                javatype = JavaInstancesFactory.get_java_instance("JsonObject")

        result = self.__reader.getValues(javaarray, javatype)

        if result is not None:

            for item in javaarray:
                objects.append(TypeCaster.to_python_primitive_type(item))

            return result

    def read(self):
        """
        Advances CacheReader to next record.

        :return: True if there are more rows; else False.
        :rtype: bool
        """
        result = self.__reader.read()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def close(self):
        """
        Closes this resource, relinquishing any underlying resources.
        """
        self.__reader.close()
