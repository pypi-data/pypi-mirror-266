from ncache.runtime.caching.Tag import Tag
from ncache.runtime.dependencies.FileDependency import FileDependency
from ncache.runtime.dependencies.KeyDependency import KeyDependency
from ncache.runtime.dependencies.OracleCacheDependency import OracleCacheDependency
from ncache.runtime.dependencies.SqlCacheDependency import SqlCacheDependency
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.JavaInstancesFactory import *
from ncache.client.enum.CacheItemPriority import CacheItemPriority
from ncache.runtime.Expiration import Expiration
from ncache.runtime.caching.NamedTagsDictionary import NamedTagsDictionary
from ncache.runtime.caching.datasource.ResyncOptions import ResyncOptions
from ncache.runtime.dependencies.CacheDependency import CacheDependency
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DataStructureAttributes:
    """
    DataStructureAttributes contains the information about the DataStructures.
    """
    def __init__(self):
        """
        Initializes DataTypeAttributes instance with default cache item priority.
        """
        self.__attributes = JavaInstancesFactory.get_java_instance("DataStructureAttributes")()

    def get_instance(self):
        return self.__attributes

    def set_instance(self, value):
        self.__attributes = value

    def get_dependency(self):
        """
        Gets the Cache Dependency instance that contains all dependencies associated with DataStructure.

        :return: The Cache Dependency instance associated with DataStructure.
        :rtype: CacheDependency
        """
        result = self.__attributes.getDependency()
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

    def get_expiration(self):
        """
        Gets the expiration mechanism for DataStructure.

        :return: Expiration instance that contains info about DataStructure expiration mechanism.
        :rtype: Expiration
        """
        result = self.__attributes.getExpiration()

        if result is not None:
            expiration = Expiration()
            expiration.set_instance(result)
            return expiration

        return result

    def get_group(self):
        """
        Gets the associated with the DataStructure. It can be queried on the basis of Groups.

        :return: The group associated with DataStructure.
        :rtype: str
        """
        result = self.__attributes.getGroup()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_named_tags(self):
        """
        Gets the NamedTags information associated with the DataStructure, it can be queried on the basis of NamedTags
        provided.

        :return: NamedTags associated with DataStructure.
        :rtype: NamedTagsDictionary
        """
        result = self.__attributes.getNamedTags()

        if result is not None:
            obj = NamedTagsDictionary()
            obj.set_instance(result)
            return obj

        return result

    def get_priority(self):
        """
        Gets the relative priority for DataStructure which is kept under consideration whenever cache starts to free up
        space and evicts items.

        :return: CacheItemPriority associated with DataStructure.
        :rtype: CacheItemPriority
        """
        result = self.__attributes.getPriority()

        enumtype = None
        if result is not None:
            enumtype = EnumUtil.get_cache_item_priority_value(result)

        return enumtype

    def get_resync_options(self):
        """
        Gets the ResyncOptions specific to the DataStructure.

        :return: ResyncOptions specific to the DataStructure.
        :rtype: ResyncOptions
        """
        result = self.__attributes.getResyncOptions()

        if result is not None:
            resyncoptions = ResyncOptions(False)
            resyncoptions.set_instance(result)
            return resyncoptions

        return result

    def get_tags(self):
        """
        Gets the tags information associated with the DataStructure, it can be queried on the basis of Tags provided.

        :return: List of Tags associated with DataStructure.
        :rtype: list
        """
        result = self.__attributes.getTags()
        if result is not None:
            result = TypeCaster.to_python_list(result, False, Tag("DummyTag"))
        return result

    def set_dependency(self, dependency):
        """
        Sets the Cache Dependency instance that contains all dependencies associated with DataStructure.

        :param dependency: The Cache Dependency instance to be associated with DataStructure.
        :type dependency: CacheDependency
        """
        if not isinstance(dependency, CacheDependency):
            raise TypeError(f"set_dependency failed: Expected parameter is an instance of {CacheDependency} but"
                            f"received {type(dependency)}")

        self.__attributes.setDependency(dependency.get_instance())

    def set_expiration(self, expiration):
        """
        Gets the expiration mechanism for DataStructure.

        :param expiration: Expiration instance that contains info about DataStructure expiration mechanism.
        :type expiration: Expiration
        """
        ValidateType.type_check(expiration, Expiration, self.set_expiration)
        self.__attributes.setExpiration(expiration.get_instance())

    def set_group(self, group):
        """
        Sets the group associated with the DataStructure. It can be queryed on the basis of Groups.

        :param group: The group to be associated with DataStructure.
        :type group: str
        """
        ValidateType.is_string(group, self.set_group)
        javagroup = TypeCaster.to_java_primitive_type(group)
        self.__attributes.setGroup(javagroup)

    def set_named_tags(self, namedtags):
        """
        Sets the NamedTags information associated with the DataStructure, it can be queried on the basis of NamedTags
        provided.

        :param namedtags: NamedTags to be associated with DataStructure.
        :type namedtags: NamedTagsDictionary
        """
        ValidateType.type_check(namedtags, NamedTagsDictionary, self.set_named_tags)

        self.__attributes.setNamedTags(namedtags.get_instance())

    def set_priority(self, priority):
        """
        Sets the relative priority for DataStructure which is kept under consideration whenever cache starts to free up
        space and evicts items.

        :param priority: CacheItemPriority to be associated with DataStructure.
        :type priority: CacheItemPriority
        """
        ValidateType.type_check(priority, CacheItemPriority, self.set_priority)
        priorityvalue = EnumUtil.get_cache_item_priority(priority.value)
        self.__attributes.setPriority(priorityvalue)

    def set_resync_options(self, resyncoptions):
        """
        Sets the ResyncOptions specific to the DataStructure.

        :param resyncoptions: ResyncOptions specific to the DataStructure.
        :type resyncoptions: ResyncOptions
        """
        ValidateType.type_check(resyncoptions, ResyncOptions, self.set_resync_options)
        self.__attributes.setResyncOptions(resyncoptions.get_instance())

    def set_tags(self, tags):
        """
        Sets the tags information associated with the DataStructure, it can be queried on the basis of Tags provided.

        :param tags: List of Tags to be associated with DataStructure.
        :type tags: list
        """
        ValidateType.type_check(tags, list, self.get_tags)

        for tag in tags:
            ValidateType.type_check(tag, Tag, self.set_tags)

        self.__attributes.setTags(TypeCaster.to_java_array_list(tags))
