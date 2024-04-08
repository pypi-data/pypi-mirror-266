from datetime import datetime

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType
from ncache.util.JavaInstancesFactory import *


class LockHandle:
    """
    An instance of this class is used to lock and unlock the cache items in pessimistic concurrency model.
    """
    def __init__(self, lockhandle=None, lockid=None, lockdate=None):
        """
        Create a new LockHandle populates attributes from specified lockid and lockdate or lockhandle.

        :param lockhandle: The lockhandle instance.
        :type lockhandle: LockHandle
        :param lockid: Unique lock id for lock handle.
        :type lockid: str
        :param lockdate: The time when lock was acquired.
        :type lockdate: datetime
        """
        if lockid is not None and lockdate is not None and lockhandle is None:
            ValidateType.is_string(lockid, self.__init__)
            ValidateType.type_check(lockdate, datetime, self.__init__)

            lockid = TypeCaster.to_java_primitive_type(lockid)
            lockdate = TypeCaster.to_java_date(lockdate)

            self.__lockhandle = JavaInstancesFactory.get_java_instance("LockHandle")(lockid, lockdate)

        elif lockhandle is not None and lockdate is None and lockid is None:
            ValidateType.type_check(lockhandle, LockHandle, self.__init__)

            lockhandle = lockhandle.get_instance()
            self.__lockhandle = JavaInstancesFactory.get_java_instance("LockHandle")(lockhandle)

        elif lockhandle is None and lockdate is None and lockid is None:
            self.__lockhandle = JavaInstancesFactory.get_java_instance("LockHandle")()

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("LockHandle.__init__"))

    def set_instance(self, value):
        self.__lockhandle = value

    def get_instance(self):
        return self.__lockhandle

    def get_lock_date(self):
        """
        Gets the lock date.

        :return: Lock date instance.
        :rtype: datetime
        """
        result = self.__lockhandle.getLockDate()

        if result is not None:
            result = TypeCaster.to_python_date(result)

        return result

    def get_lock_id(self):
        """
        Get lock id

        :return: Lock id
        :rtype: str
        """
        result = self.__lockhandle.getLockId()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_lock_date(self, lockdate):
        """
        Sets lock date.

        :param lockdate: New lock date.
        :type lockdate: datetime
        """
        ValidateType.type_check(lockdate, datetime, self.set_lock_date)

        javalockdate = TypeCaster.to_java_date(lockdate)
        self.__lockhandle.setLockDate(javalockdate)

    def set_lock_id(self, lockid):
        """
        Sets the lock id.

        :param lockid: New lock id.
        :type lockid: str
        """
        ValidateType.is_string(lockid, self.set_lock_date)

        javalockid = TypeCaster.to_java_primitive_type(lockid)
        self.__lockhandle.setLockId(javalockid)
