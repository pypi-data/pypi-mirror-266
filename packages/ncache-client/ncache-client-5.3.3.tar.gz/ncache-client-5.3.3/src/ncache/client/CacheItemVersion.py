from ncache.util.JavaInstancesFactory import *
from ncache.util.ValidateType import ValidateType


class CacheItemVersion:
    """
    Represents the version of each cache item. An instance of this class is used in the optimistic concurrency model to
    ensure the data integrity.
    """
    def __init__(self, version):
        """
        Creates an instance of CacheItemVersion class.
        :param version: version of the cache item.
        :type version: int
        """
        self.__cacheitemversion = JavaInstancesFactory.get_java_instance("CacheItemVersion")(version)

    def __str__(self):
        return str(self.__cacheitemversion.toString())

    def get_instance(self):
        return self.__cacheitemversion

    def set_instance(self, value):
        self.__cacheitemversion = value

    def compare_to(self, itemversion):
        """
        Compare CacheItemVersion with current instance of item version.

        :param itemversion: Item version to be compared.
        :type itemversion: CacheItemVersion
        :return: 0 if two instance are equal. An integer greater then 0 if this instance is greater. An integer less
            than 0 if this instance is smaller.
        """
        ValidateType.type_check(itemversion, CacheItemVersion, self.compare_to)
        return int(self.__cacheitemversion.compareTo(itemversion.get_instance()))

    def get_version(self):
        """
        Gets the item version

        :return: Item's version
        :rtype: int
        """
        return int(self.__cacheitemversion.getVersion())

    def set_version(self, version):
        ValidateType.is_int(version, self.set_version)
        version = jp.java.lang.Long(version)

        self.__cacheitemversion.setVersion(version)

