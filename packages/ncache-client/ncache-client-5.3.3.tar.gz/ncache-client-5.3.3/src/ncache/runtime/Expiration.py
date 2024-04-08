from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.client.enum.ExpirationType import ExpirationType
from ncache.util.ValidateType import ValidateType


class Expiration:
    """
    Class that provides values to specify expiration of items in cache.
    """
    def __init__(self, expirationtype=None, expireafter=None):
        """
        Initializes the instance of Expiration class

        :param expirationtype: The type of expiration to be used while expiring items in cache. The value of this type
            varies from item to item in cache.
        :type expirationtype: ExpirationType
        :param expireafter: Value of time in the form of datetime that shows after how much time, the item in cache is
            to be expired.
        :type expireafter: TimeSpan
        """
        if expirationtype is None and expireafter is None:
            self.__expiration = JavaInstancesFactory.get_java_instance("Expiration")()
            return
        elif expirationtype is not None:
            ValidateType.type_check(expirationtype, ExpirationType)
            expirationvalue = EnumUtil.get_expiration_type(expirationtype.value)
            if expireafter is not None:
                self.__expiration = JavaInstancesFactory.get_java_instance("Expiration")(expirationvalue, expireafter.get_instance())
                return
            self.__expiration = JavaInstancesFactory.get_java_instance("Expiration")(expirationvalue)
            return
        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("Expiration.__init__"))

    def set_instance(self, value):
        self.__expiration = value

    def get_instance(self):
        return self.__expiration

    def get_expiration_type(self):
        """
        Returns the type of expiration to be used while expiring items in cache. The value of this type varies from item
        to item in cache.

        :rtype: ExpirationType
        """
        result = self.__expiration.getExpirationType()
        enumtype = EnumUtil.get_expiration_type_value(result)
        if enumtype is not None:
            return enumtype

    def get_expire_after(self):
        """
        Get value of time in the form that shows after how much time, the item in cache is to be expired.

        :return: Value of time in the form that shows after how much time, the item in cache is to be expired.
        :rtype: TimeSpan
        """
        result = self.__expiration.getExpireAfter()
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan
        return result

    def set_expire_after(self, value):
        """
        Sets the value of time in the form of TimeSpan that shows after how much time, the item in cache is to be
        expired.

        :param value: The TimeSpan instance that indicates the time after which item will be expired from cache.
        :type value: TimeSpan
        """
        ValidateType.type_check(value, TimeSpan, self.set_expire_after)
        self.__expiration.setExpireAfter(value.get_instance())
