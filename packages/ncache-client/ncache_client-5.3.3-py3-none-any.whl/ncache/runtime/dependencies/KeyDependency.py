from datetime import datetime

from ncache.runtime.dependencies.CacheDependency import *
from ncache.client.enum.KeyDependencyType import KeyDependencyType
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.ExceptionHandler import ExceptionHandler


class KeyDependency(CacheDependency):
    """
    KeyDependency class is used for providing key based dependency in the cache.
    """
    def __init__(self, keys, keydependencytype=None, startafter=None):
        """
        Initializes a new instance of the KeyExpiration class that monitors a cache key for changes based on the update
        or remove operation performed and taking effect instantly.

        :param keys: The cache key or list of cache keys which will be monitored for updation or removal.
        :type keys: str or list
        :param keydependencytype: Specifies operation/operations upon which key dependency is to be triggered.
        :type keydependencytype: KeyDependencyType
        :param startafter: The time after which specified key is monitored.
        :type startafter: datetime
        """
        super().__init__()

        ValidateType.is_none(keys)

        if type(keys) is str:
            keys = TypeCaster.to_java_primitive_type(keys)

            if startafter is not None:
                ValidateType.type_check(startafter, datetime, self.__init__)
                javastartafter = TypeCaster.to_java_date(startafter)

                if keydependencytype is not None:
                    ValidateType.type_check(keydependencytype, KeyDependencyType, self.__init__)
                    keydependencytypevalue = EnumUtil.get_key_dependency_type(keydependencytype.value)

                    self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, javastartafter, keydependencytypevalue)
                    return

                self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, javastartafter)
                return

            elif startafter is None and keydependencytype is not None:
                ValidateType.type_check(keydependencytype, KeyDependencyType, self.__init__)
                keydependencytypevalue = EnumUtil.get_key_dependency_type(keydependencytype.value)

                self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, keydependencytypevalue)
                return

            self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys)
            return

        elif type(keys) is list and len(keys) != 0:
            for key in keys:
                if type(key) is not str:
                    raise TypeError("Please provide list containing " + str(str) + " only")

            keys = TypeCaster.to_java_array_list(keys, True)

            if startafter is not None:
                ValidateType.type_check(startafter, datetime, self.__init__)
                javastartafter = TypeCaster.to_java_date(startafter)

                if keydependencytype is not None:
                    ValidateType.type_check(keydependencytype, KeyDependencyType, self.__init__)
                    keydependencytypevalue = EnumUtil.get_key_dependency_type(keydependencytype.value)

                    self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, javastartafter, keydependencytypevalue)
                    return

                self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, javastartafter)
                return

            elif startafter is None and keydependencytype is not None:
                ValidateType.type_check(keydependencytype, KeyDependencyType, self.__init__)
                keydependencytypevalue = EnumUtil.get_key_dependency_type(keydependencytype.value)

                self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys, keydependencytypevalue)
                return

            self.__keydependency = JavaInstancesFactory.get_java_instance("KeyDependency")(keys)
            return

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("KeyDependency.__init__"))

    def set_instance(self, value):
        self.__keydependency = value

    def get_instance(self):
        return self.__keydependency

    def get_cache_keys(self):
        """
        Gets the list of cache keys.

        :return: The list of cache keys associated with the dependency.
        :rtype: list
        """
        result = self.__keydependency.getCacheKeys()

        if result is not None:
            result = TypeCaster.to_python_list(result, True)

        return result

    def get_key_dependency_type(self):
        """
        Enumeration specifying operation upon which key dependency is to be triggered.

        :return: KeyDependencyType associated with the dependency.
        :rtype: KeyDependencyType
        """
        result = self.__keydependency.getKeyDependencyType()
        enumtype = EnumUtil.get_key_dependency_type_value(result)
        return enumtype

    def get_start_after_ticks(self):
        """
        Gets the time after which dependency is to be started.

        :return: The time after which key dependency is started.
        """
        result = self.__keydependency.getStartAfterTicks()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_key_dependency_type(self, keydependencytype):
        """
        Enumeration specifying operation upon which key dependency is to be triggered.

        :param keydependencytype: The KeyDependencyType to be associated with the dependency.
        :type keydependencytype: KeyDependencyType
        """
        ValidateType.type_check(keydependencytype, KeyDependencyType, self.set_key_dependency_type)
        javaenum = EnumUtil.get_key_dependency_type(keydependencytype.value)
        self.__keydependency.setKeyDependencyType(javaenum)

    def __del__(self):
        pass
