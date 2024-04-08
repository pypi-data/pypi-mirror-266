from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class Credentials:
    """
    Class that provides the security parameters for authorization.
    """
    def __init__(self, userid=None, password=None):
        """
        Creates an instance of the Credentials.

        :param userid: User id used to authenticate the user.
        :type userid: str
        :param password: Password used to authenticate the user.
        :type password: str
        """
        if userid is not None and password is not None:
            ValidateType.is_string(userid, self.__init__)
            ValidateType.is_string(password, self.__init__)

            userid = TypeCaster.to_java_primitive_type(userid)
            password = TypeCaster.to_java_primitive_type(password)

            self.__credentials = JavaInstancesFactory.get_java_instance("Credentials")(userid, password)

        elif userid is None and password is None:
            self.__credentials = JavaInstancesFactory.get_java_instance("Credentials")()

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("Credentials.__init__"))

    def get_instance(self):
        return self.__credentials

    def set_instance(self, value):
        self.__credentials = value

    def get_password(self):
        """
        Gets the password for the credentials.

        :return: The password in form of a string.
        :rtype: str
        """
        result = self.__credentials.getPassword()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_user_id(self):
        """
        Gets the user id for the credentials.

        :return: The user-id in form of a string.
        :rtype: str
        """
        result = self.__credentials.getUserID()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_password(self, password):
        """
        Sets the password for the credentials.

        :param password: The password in form of a string.
        :type password: str
        """
        ValidateType.is_string(password, self.set_password)
        javapassword = TypeCaster.to_java_primitive_type(password)

        self.__credentials.setPassword(javapassword)

    def set_user_id(self, userid):
        """
        Sets the user id for the credentials.

        :param userid: The user-id in form of a string.
        :type userid: str
        """
        ValidateType.is_string(userid, self.set_user_id)
        javauserid = TypeCaster.to_java_primitive_type(userid)

        self.__credentials.setUserID(javauserid)
