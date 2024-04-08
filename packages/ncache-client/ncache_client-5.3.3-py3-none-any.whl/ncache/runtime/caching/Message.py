from datetime import datetime

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class Message:
    """
    Abstract interface implemented by Protocol Message objects.
    """
    def __init__(self, payload, timespan=None):
        """
        Initializes an instance of Message.

        :param payload: Payload of message.
        :type payload: object
        :param timespan: Expiry time of message.
        :type timespan: TimeSpan
        """
        ValidateType.is_none(payload, self.__init__)

        javatype = TypeCaster.is_python_primitive(payload)
        if javatype is not None:
            javatype = JavaInstancesFactory.get_java_instance("JsonValue")(javatype)
        else:
            javatype = TypeCaster.serialize(payload, isjsonobject=True, verbose=True)

        if timespan is not None:
            ValidateType.type_check(timespan, TimeSpan, self.__init__)
            self.__message = JavaInstancesFactory.get_java_instance("Message")(javatype, timespan.get_instance())

        elif timespan is None:
            self.__message = JavaInstancesFactory.get_java_instance("Message")(javatype)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("Message.__init__"))

    def get_instance(self):
        return self.__message

    def set_instance(self, value):
        self.__message = value

    def get_creation_time(self):
        """
        Creation time in datetime for the message.

        :return: The date that specifies creation time of message.
        :rtype: datetime
        """
        result = self.__message.getCreationTime()

        if result is not None:
            result = TypeCaster.to_python_date(result)

        return result

    def get_expiration_time(self):
        """
        ExpirationTime of TimeSpan type after which the message is expired from the topic. This can also accept None
        value, which will ensure that the message is not expired from the topic. In case of no expiration time specified,
        None is considered as default.

        :return: Timespan that indicates the expiration time of the message.
        :rtype: TimeSpan
        """
        result = self.__message.getExpirationTime()

        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    def get_message_id(self):
        """
        Auto generated ID for the message, as same messages can be stored on different topics.

        :return: Message id of the message.
        :rtype: str
        """
        result = self.__message.getMessageId()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_payload(self):
        """
        The actual data object of interest for subscribers, for example, Order.

        :return: The underlying payload of the message.
        :rtype: object
        """
        jsonvaluebase = JavaInstancesFactory.get_java_instance("JsonValueBase")
        result = self.__message.getPayloadAsJson(jsonvaluebase)

        if result is not None:
            result = TypeCaster.deserialize(result, isjsonobject=True)

        return result

    def set_creation_time(self, value):
        """
        Creation time in datetime for the message.

        :param value: The creation time of the message.
        :type value: datetime
        """
        ValidateType.type_check(value, datetime, self.set_creation_time)
        javavalue = TypeCaster.to_java_date(value)

        self.__message.setCreationTime(javavalue)

    def set_expiration_time(self, value):
        """
        Sets the expiration time of the message.

        :param value: The value that is to be set as expiration time.
        :type value: TimeSpan
        """
        ValidateType.type_check(value, TimeSpan, self.set_expiration_time)

        self.__message.setExpirationTime(value.get_instance())

    def set_message_id(self, value):
        """
        Sets the message id of the message.

        :param value: The id to be set to message.
        :type value: str
        """
        ValidateType.is_string(value, self.set_message_id)

        javavalue = TypeCaster.to_java_primitive_type(value)

        self.__message.setMessageId(javavalue)

    @staticmethod
    def get_no_expiration():
        result = JavaInstancesFactory.get_java_instance("Message").getNoExpiration()

        if result is not None:
            ts = TimeSpan()
            ts.set_instance(result)

            result = ts
        
        return result
