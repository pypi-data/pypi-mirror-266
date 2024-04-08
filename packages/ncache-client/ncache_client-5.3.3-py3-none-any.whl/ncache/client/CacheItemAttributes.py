from datetime import datetime

from ncache.runtime.dependencies.CacheDependency import CacheDependency
from ncache.runtime.dependencies.FileDependency import FileDependency
from ncache.runtime.dependencies.KeyDependency import KeyDependency
from ncache.runtime.dependencies.OracleCacheDependency import OracleCacheDependency
from ncache.runtime.dependencies.SqlCacheDependency import SqlCacheDependency
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheItemAttributes:
    """
    CacheItemAttributes contains the information about the cache item.
    """
    def __init__(self):
        """
        Initializes an instance of CacheItemAttributes
        """
        self.__cacheitemattributes = JavaInstancesFactory.get_java_instance("CacheItemAttributes")()

    def get_instance(self):
        return self.__cacheitemattributes

    def set_instance(self, value):
        self.__cacheitemattributes = value

    def get_absolute_expiration(self):
        """
        Gets Absolute Expiration for the object

        :return: Absolute Expiration for the object
        :rtype: TimeSpan
        """
        result = self.__cacheitemattributes.getAbsoluteExpiration()

        if result is not None:
            result = TypeCaster.to_python_date(result)

        return result

    def set_absolute_expiration(self, expiration):
        """
        Sets the Absolute expiration for the object. You can add an item to the cache with absolute expiration by
        specifying the exact date and time at which the item should be invalidated. When this time is elapsed, the item
        will be removed from the cache.

        :param expiration: Absolute expiration value to be set.
        :type expiration: datetime
        """
        ValidateType.type_check(expiration, datetime, self.set_absolute_expiration)

        javaexpiration = TypeCaster.to_java_date(expiration)
        self.__cacheitemattributes.setAbsoluteExpiration(javaexpiration)

    def get_dependency(self):
        """
        Gets the file or cache key dependencies for the item. When any dependency changes, the object becomes invalid
        and is removed from the cache. If there are no dependencies , this property contains a None.

        :return: The file or cache key dependencies for the item.
        :rtype: CacheDependency
        """
        result = self.__cacheitemattributes.getDependency()
        dependencytype = EnumUtil.get_dependency_type_info(result)
        dependency = None

        if dependencytype == 1:
            dependency = KeyDependency("key")
            dependency.set_instance(result)
        elif dependencytype == 2:
            dependency = FileDependency("key")
            dependency.set_instance(result)
        elif dependencytype == 5:
            dependency = SqlCacheDependency("ConString", "CmdText")
            dependency.set_instance(result)
        elif dependencytype == 6:
            dependency = OracleCacheDependency("ConString", "CmdText")
            dependency.set_instance(result)
        else:
            dependency = CacheDependency()
            dependency.set_instance(result)

        return dependency

    def set_dependency(self, dependency):
        """
        Sets the file or cache key dependencies for the item. When any dependency changes, the object becomes invalid
        and is removed from the cache. If there are no dependencies, this property contains a None.

        :param dependency: cacheDependency object
        :type dependency: CacheDependency
        """
        if not isinstance(dependency, CacheDependency):
            raise TypeError(f"set_dependency failed: Expected parameter is an instance of {CacheDependency} but"
                            f"received {type(dependency)}")

        self.__cacheitemattributes.setDependency(dependency.get_instance())
