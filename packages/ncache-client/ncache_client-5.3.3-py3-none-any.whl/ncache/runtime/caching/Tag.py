from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType
from ncache.util.JavaInstancesFactory import *


class Tag:
    """
    Represents a string based identifier that can be associated with the cache items so that they are logically grouped
    together and can be retrieved efficiently. One or more tags can be associated with each cache item. To create an
    instance of Tag class you can use code as follows: tag = Tag("Alpha")
    """
    def __init__(self, tagname):
        """
        Initializes a new instance of Tag class.

        :param tagname: Name of the tag.
        :type tagname: str
        """
        ValidateType.is_string(tagname)
        self.__tag = JavaInstancesFactory.get_java_instance("Tag")(TypeCaster.to_java_primitive_type(tagname))

    def set_instance(self, value):
        self.__tag = value

    def get_instance(self):
        return self.__tag

    def get_tag_name(self):
        """
        Gets the string based tag name.

        :return: String based tag name.
        :rtype: str
        """
        result = self.__tag.getTagName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def set_tag_name(self, name):
        """
        Sets the string based tag name.

        :param name: String based tag name.
        :type name: str
        """
        ValidateType.is_string(name, self.set_tag_name)
        javaname = TypeCaster.to_java_primitive_type(name)

        self.__tag.setTagName(javaname)

    def __str__(self):
        result = self.__tag.toString()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def __eq__(self, other):
        ValidateType.type_check(other, Tag)
        result = self.__tag.equals(other.get_instance())
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def __hash__(self):
        result = self.__tag.getHashCode()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result
