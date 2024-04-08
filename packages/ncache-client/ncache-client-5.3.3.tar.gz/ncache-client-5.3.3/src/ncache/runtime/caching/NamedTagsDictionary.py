from datetime import datetime

from ncache.runtime.util.Iterator import Iterator
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class NamedTagsDictionary:
    """
    Represents a dictionary that can be associated with the cache items to provide extra information so that items are
    grouped together and can be queried efficiently based on the provided information.
    """
    def __init__(self):
        """
        Initialize the NameTagsDictionary object.
        """
        self.__namedtagsdictionary = JavaInstancesFactory.get_java_instance("NamedTagsDictionary")()

    def get_instance(self):
        return self.__namedtagsdictionary

    def set_instance(self, value):
        self.__namedtagsdictionary = value

    def add(self, key, value):
        """
        Adds the key value pair in named tags dictionary.

        :param key: Key of an item.
        :type key: str
        :param value: Value of an item.
        :type value: str or int or float or bool or datetime
        """
        ValidateType.is_string(key, self.add)
        ValidateType.is_none(value, self.add)

        javakey = TypeCaster.to_java_primitive_type(key)

        if type(value) is datetime:
            javadate = TypeCaster.to_java_date(value)
            self.__namedtagsdictionary.add(javakey, javadate)
        else:
            javatype = TypeCaster.is_python_primitive(value)
            if javatype is None:
                raise TypeError(f"add failed. value must be of type {type(str)}, {type(int)}, {type(float)}, {type(bool)}"
                                f", or {type(datetime)}")
            self.__namedtagsdictionary.add(javakey, javatype)

    def contains(self, key):
        """
        Search for the key in named tags dictionary and return true if it is found and otherwise false.

        :param key: The key to be searched.
        :type key: str
        :return: True if key exists otherwise false.
        :rtype: bool
        """
        ValidateType.is_string(key, self.contains)
        javakey = TypeCaster.to_java_primitive_type(key)

        return bool(self.__namedtagsdictionary.contains(javakey))

    def get_count(self):
        return int(self.__namedtagsdictionary.getCount())

    def get_iterator(self):
        """
        Returns an iterator that iterates through the entries of named tags dictionary.

        :return: An Iterator instance
        :rtype: Iterator
        """
        javaiterator = self.__namedtagsdictionary.getKeysIterator()
        iterator = Iterator(javaiterator, True)
        return iter(iterator)

    def get_value(self, key):
        """
        Gets the value of the specified key in the named tags dictionary. If key is not found returns None.

        :param key: The key to be searched.
        :type key: str
        :return: Associated value of the key if the key exists otherwise None.
        :rtype: str or int or float or bool or datetime
        """
        ValidateType.is_string(key)

        javakey = TypeCaster.to_java_primitive_type(key)

        result = self.__namedtagsdictionary.getValue(javakey)
        if result is None:
            return result

        pythontype = TypeCaster.to_python_primitive_type(result)
        if pythontype is None:
            pythontype = TypeCaster.to_python_date(result)

        return pythontype

    def remove(self, key):
        """
        Removes the key value pair from named tags dictionary.

        :param key: Key of an item.
        :type key: str
        """
        ValidateType.is_string(key)
        javakey = TypeCaster.to_java_primitive_type(key)

        self.__namedtagsdictionary.remove(javakey)
