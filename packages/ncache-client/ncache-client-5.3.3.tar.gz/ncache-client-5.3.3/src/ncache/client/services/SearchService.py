import collections

from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.client.CacheReader import CacheReader
from ncache.client.QueryCommand import QueryCommand
from ncache.client.enum.TagSearchOptions import TagSearchOptions
from ncache.runtime.caching.Tag import Tag
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class SearchService:
    """
    This class contains properties and methods required for Search Service.
    """
    def __init__(self, value):
        self.__searchservice = value

    def get_instance(self):
        return self.__searchservice

    def set_instance(self, value):
        self.__searchservice = value

    def execute_non_query(self, querycommand):
        """
        Executes Delete statements on cache. Returns number of affected rows after query is executed.

        :param querycommand: QueryCommand containing query text and values.
        :type querycommand: QueryCommand
        :return: Number of rows affected after query is executed.
        :rtype: int
        """
        ValidateType.type_check(querycommand, QueryCommand, self.execute_non_query)
        javaquerycommand = querycommand.get_instance()

        result = self.__searchservice.executeNonQuery(javaquerycommand)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def execute_reader(self, querycommand, getdata=None, chunksize=None):
        """
        Performs search on the cache based on the query specified. Returns list of key-value pairs in a data reader
        which fulfills the query criteria. This key-value pair has cache key and its respective value.You can specify
        the flag for specifying if you want data with keys.

        :param querycommand: QueryCommand containing query text and values.
        :type querycommand: QueryCommand
        :param getdata: Flag to indicate whether the resulting values have to be returned with keys or not.
        :type getdata: bool
        :param chunksize: Size of data/keys packets received after search, default value is 512*1024 KB.
        :type chunksize: int
        :return: Reads forward-only stream of result sets of the query executed on cache.
        :rtype: CacheReader
        """
        ValidateType.type_check(querycommand, QueryCommand, self.execute_reader)
        javaquerycommand = querycommand.get_instance()

        if getdata is not None and chunksize is not None:
            ValidateType.type_check(getdata, bool, self.execute_reader)
            ValidateType.is_int(chunksize, self.execute_reader)

            javagetdata = TypeCaster.to_java_primitive_type(getdata)
            javachunksize = TypeCaster.to_java_primitive_type(chunksize)

            result = self.__searchservice.executeReader(javaquerycommand, javagetdata, javachunksize)

        elif getdata is None and chunksize is None:
            result = self.__searchservice.executeReader(javaquerycommand)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("SearchService.execute_reader"))

        if result is not None:
            qc = CacheReader("DummyQuery")
            qc.set_instance(result)
            return qc

        return result

    def execute_scalar(self, querycommand, objtype):
        """
        Executes the query, and returns the first column of the first row in the result set returned by the query.
        Additional columns or rows are ignored.

        :param querycommand: QueryCommand containing query text and values.
        :type querycommand: QueryCommand
        :param objtype: Specifies the type of value obtained from the cache.
        :type objtype: type
        :return: The first column of the first row in the result set, or None if the result set is empty.
        :rtype: object
        """
        ValidateType.type_check(querycommand, QueryCommand, self.execute_scalar)
        ValidateType.type_check(objtype, type, self.execute_scalar)

        javaquerycommand = querycommand.get_instance()
        pythontype, javatype = TypeCaster.is_java_primitive(objtype)

        usejsonconversoin = False
        if javatype is None:
            if isinstance(objtype(), collections.Collection):
                javatype = JavaInstancesFactory.get_java_instance("JsonArray")
            else:
                javatype = JavaInstancesFactory.get_java_instance("JsonObject")
            usejsonconversoin = True

        result = self.__searchservice.executeScalar(javaquerycommand, javatype)

        if result is not None:
            if not usejsonconversoin:
                result = pythontype(result)
            else:
                result = TypeCaster.deserialize(result, objtype, isjsonobject=True)
        return result

    def remove_by_tag(self, tag):
        """
        Removes the cached objects with the specified tag.

        :param tag: A Tag to search cache with.
        :type tag: Tag
        """
        ValidateType.type_check(tag, Tag, self.remove_by_tag)
        javatag = tag.get_instance()

        self.__searchservice.removeByTag(javatag)

    def remove_by_tags(self, tags, tagsearchoptions):
        """
        Removes the cached objects that have tags with specified TagSearchOptions.

        :param tags: List of tags to search cache with.
        :type tags: list
        :param tagsearchoptions: TagSearchOptions specifies the search type for the tags.
        :type tagsearchoptions: TagSearchOptions
        """
        ValidateType.type_check(tagsearchoptions, TagSearchOptions, self.get_by_tag)
        ValidateType.type_check(tags, list, self.remove_by_tags)
        for tag in tags:
            ValidateType.type_check(tag, Tag, self.remove_by_tags)

        javatags = TypeCaster.to_java_array_list(tags)
        javatagsearchoptions = EnumUtil.get_tag_search_options(tagsearchoptions.value)

        self.__searchservice.removeByTags(javatags, javatagsearchoptions)

    def get_by_tag(self, tag, wildcardexpression=None):
        """
        Gets all the cached items with the specified tag.

        :param tag: Name of tag to search the cache items with.
        :type tag: Tag
        :param wildcardexpression: The wild card Expression to search with.
        :type wildcardexpression: str
        :return: A Map containing the cache keys and associated objects with the type specified.
        :rtype: dict
        """
        if tag is not None and wildcardexpression is None:
            ValidateType.type_check(tag, Tag, self.get_by_tag)
            javatag = tag.get_instance()

            result = self.__searchservice.getByTag(javatag)

        elif tag is None and wildcardexpression is not None:
            ValidateType.is_string(wildcardexpression, self.get_by_tag)
            javawildcardexpression = TypeCaster.to_java_primitive_type(wildcardexpression)

            result = self.__searchservice.getByTag(javawildcardexpression)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("SearchService.get_by_tag"))

        if result is not None:
            result = self.__result_to_dict(result)

        return result

    def get_by_tags(self, tags, tagsearchoptions):
        """
        Returns the cached objects that have tags with specified TagSearchOptions.

        :param tagsearchoptions: TagSearchOptions specifies the search type for the tags.
        :type tagsearchoptions: TagSearchOptions
        :param tags: List of tags to search cache with.
        :type tags: list
        :return: Cached objects that have tags with specified TagSearchOptions.
        :rtype: dict
        """
        ValidateType.type_check(tagsearchoptions, TagSearchOptions, self.get_by_tag)
        ValidateType.type_check(tags, list, self.get_by_tags)
        for tag in tags:
            ValidateType.type_check(tag, Tag, self.get_by_tags)

        javatags = TypeCaster.to_java_array_list(tags)
        javatagsearchoptions = EnumUtil.get_tag_search_options(tagsearchoptions.value)

        result = self.__searchservice.getByTags(javatags, javatagsearchoptions)

        if result is not None:
            result = self.__result_to_dict(result)

        return result

    def get_keys_by_tag(self, tag=None, wildcardexpression=None):
        """
        Gets all keys of the objects with the specified tag.

        :param tag: Name of tag to search the cache items with.
        :type tag: Tag
        :param wildcardexpression: The wild card Expression to search with.
        :type wildcardexpression: str
        :return: List containing the cache keys.
        :rtype: list
        """
        if wildcardexpression is not None and tag is None:
            ValidateType.is_string(wildcardexpression, self.get_keys_by_tag)
            javawildcardexpression = TypeCaster.to_java_primitive_type(wildcardexpression)

            result = self.__searchservice.getKeysByTag(javawildcardexpression)

        elif wildcardexpression is None and tag is not None:
            ValidateType.type_check(tag, Tag, self.get_keys_by_tag)
            javatag = tag.get_instance()

            result = self.__searchservice.getKeysByTag(javatag)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("SearchService.get_keys_by_tag"))

        if result is not None:
            result = TypeCaster.to_python_list(result, isjavatype=True)

        return result

    def get_keys_by_tags(self, tags, tagsearchoptions):
        """
        Returns keys of the cached items that have tags with specified TagSearchOptions.

        :param tags: List of tags to search cache with.
        :type tags: list
        :param tagsearchoptions: TagSearchOptions specifies the search type for the tags.
        :type tagsearchoptions: TagSearchOptions
        :return: Collection containing the cache keys.
        :rtype: list
        """
        ValidateType.type_check(tags, list, self.get_keys_by_tags)
        for tag in tags:
            ValidateType.type_check(tag, Tag, self.get_keys_by_tags)

        javatags = TypeCaster.to_java_array_list(tags, isjavatype=False)
        javatagsearchoptions = EnumUtil.get_tag_search_options(tagsearchoptions.value)

        result = self.__searchservice.getKeysByTags(javatags, javatagsearchoptions)

        if result is not None:
            result = TypeCaster.to_python_list(result, isjavatype=True)

        return result

    def get_group_data(self, group):
        """
        Retrieves the key and value pairs of the specified group.

        :param group: Name of group whose data is to be returned.
        :type group: str
        :return: A Dict containing key-value pairs of the specified group.
        :rtype: dict
        """
        ValidateType.type_check(group, str, self.get_group_data)

        javagroup = TypeCaster.to_java_primitive_type(group)

        result = self.__searchservice.getGroupData(javagroup)

        if result is not None:
            result = self.__result_to_dict(result)

        return result

    def remove_group_data(self, group):
        """
        Remove the data items pertaining to the specified group from cache.

        :param group: Name of group whose data is to be removed.
        :type group: str
        """
        ValidateType.is_string(group, self.remove_group_data)
        javagroup = TypeCaster.to_java_primitive_type(group)

        self.__searchservice.removeGroupData(javagroup)

    def get_group_keys(self, group):
        """
        Retrieves the keys of the items in the specified group.

        :param group: Name of group whose keys are to be returned.
        :type group: str
        :return: List of keys of the group.
        :rtype: list
        """
        ValidateType.is_string(group, self.get_group_keys)
        javagroup = TypeCaster.to_java_primitive_type(group)

        result = self.__searchservice.getGroupKeys(javagroup)

        if result is not None:
            result = TypeCaster.to_python_list(result, isjavatype=True)

        return result

    @staticmethod
    def __result_to_dict(javabulkmap, objtype=None):
        pythondict = {}

        for item in javabulkmap:
            key = TypeCaster.to_python_primitive_type(item)
            pythontype = TypeCaster.to_python_primitive_type(javabulkmap[item])

            if pythontype is not None:
                pythondict[key] = pythontype
            else:
                pythondict[key] = TypeCaster.deserialize(javabulkmap[item], objtype, isjsonobject=True)

        return pythondict
