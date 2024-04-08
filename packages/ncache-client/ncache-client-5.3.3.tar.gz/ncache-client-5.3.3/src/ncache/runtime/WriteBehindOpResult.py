from ncache.client.enum.EventType import EventType
from ncache.client.enum.WriteBehindOpStatus import WriteBehindOpStatus
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class WriteBehindOpResult:
    """
    Result of data source operation.
    """
    def __init__(self, value):
        self.__writebehindopresult = value

    def get_event_type(self):
        """
        Get EventType of writeBehindOpStatus.

        :return: The EventType enum.
        :rtype: EventType
        """
        result = self.__writebehindopresult.getEventType()

        if result is not None:
            result = EnumUtil.get_event_type_value(result)

        return result

    def get_exception(self):
        """
        Get exception message if operation failed.

        :return: The corresponding exception message.
        :rtype: str
        """
        result = self.__writebehindopresult.getException().getMessage()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_status(self):
        """
        Get WriteBehindOpStatus of data source operation.

        :return: The WriteBehindOpStatus enum
        :rtype: WriteBehindOpStatus
        """
        result = self.__writebehindopresult.getStatus()

        if result is not None:
            result = EnumUtil.get_write_behind_op_status_value(result)

        return result
