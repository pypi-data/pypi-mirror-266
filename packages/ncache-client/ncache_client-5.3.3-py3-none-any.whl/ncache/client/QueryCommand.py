from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class QueryCommand:
    """
    Class to hold query text and values.
    """
    def __init__(self, query):
        """
        Initialized new instance of QueryCommand.

        :param query: SQL-like query text.
        :type query: str
        """
        ValidateType.is_string(query, self.__init__)

        javaquery = TypeCaster.to_java_primitive_type(query)
        self.__querycommand = JavaInstancesFactory.get_java_instance("QueryCommand")(javaquery)

    def get_instance(self):
        return self.__querycommand

    def set_instance(self, value):
        self.__querycommand = value

    def get_parameters(self):
        """
        Gets the query parameters in form of a Dict.

        :return: The query parameter Dict.
        :rtype: dict
        """
        result = self.__querycommand.getParameters()

        if result is not None:
            result = TypeCaster.to_python_dict(result, isjavatype=True)

        return result

    def get_query(self):
        """
        Gets the query text.

        :return: The query text.
        :rtype: str
        """
        result = self.__querycommand.getQuery()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_parameters(self, parameters):
        """
        Sets the query parameters.

        :param parameters: Parameters to be added in query parameters.
        :type parameters: dict
        """
        ValidateType.type_check(parameters, dict, self.set_parameters)
        javaparameters = self.__querycommand.getParameters()

        for p in parameters:
            ValidateType.is_string(p, self.set_parameters)
            javatype = TypeCaster.to_java_primitive_type(parameters[p])
            if javatype is None:
                if isinstance(parameters[p], list):
                    javaarray = TypeCaster.to_java_array_list(parameters[p],True)
                    javaparameters.put(TypeCaster.to_java_primitive_type(p), javaarray)
                else:
                    raise TypeError(ExceptionHandler.exceptionmessages.get("QueryCommand.set_parameters"))

            else:
                javaparameters.put(TypeCaster.to_java_primitive_type(p), TypeCaster.to_java_primitive_type(parameters[p]))
