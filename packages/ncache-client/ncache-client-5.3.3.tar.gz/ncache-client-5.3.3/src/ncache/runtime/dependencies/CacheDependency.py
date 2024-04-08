from typing import List

from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheDependency:
    """
    Tracks cache dependencies, which can be files, directories, or keys to other objects in application's Cache. This
    class cannot be inherited.
    """
    def __init__(self, dependency=None):
        """
        Creates a CacheDependency instance from  dependency.

        :param dependency: Another instance of the CacheDependency class that this instance is dependent upon.
        :type dependency: CacheDependency
        """
        if dependency is None:
            self.__cachedependency = JavaInstancesFactory.get_java_instance("CacheDependency")()
        else:
            ValidateType.type_check(dependency, CacheDependency, self.__init__)
            self.__cachedependency = JavaInstancesFactory.get_java_instance("CacheDependency")(dependency.get_instance())

    def get_instance(self):
        return self.__cachedependency

    def set_instance(self, value):
        self.__cachedependency = value

    def get_dependencies(self):
        """
        Get the List of Dependencies for the Cache Item.

        :return: List of Cache Dependencies.
        :rtype: List[CacheDependency]
        """
        result = self.__cachedependency.getDependencies()

        python_list = []

        for r in result:
            if isinstance(r, JavaInstancesFactory.get_java_instance('SqlCacheDependency')):
                from ncache.runtime.dependencies.SqlCacheDependency import SqlCacheDependency
                python_sql_cache_dependency = SqlCacheDependency('temp_query', 'temp_command')
                python_sql_cache_dependency.set_instance(r)
                python_list.append(python_sql_cache_dependency)
            
            elif isinstance(r, JavaInstancesFactory.get_java_instance('OracleCacheDependency')):
                from ncache.runtime.dependencies.OracleCacheDependency import OracleCacheDependency
                python_oracle_cache_dependency = OracleCacheDependency('temp_query', 'temp_command')
                python_oracle_cache_dependency.set_instance(r)
                python_list.append(python_oracle_cache_dependency)

            elif isinstance(r, JavaInstancesFactory.get_java_instance('FileDependency')):
                from ncache.runtime.dependencies.FileDependency import FileDependency
                python_file_dependency = FileDependency('temp_path')
                python_file_dependency.set_instance(r)
                python_list.append(python_file_dependency)
                
            elif isinstance(r, JavaInstancesFactory.get_java_instance('KeyDependency')):
                from ncache.runtime.dependencies.KeyDependency import KeyDependency
                python_key_dependency = KeyDependency('temp_query', 'temp_command')
                python_key_dependency.set_instance(r)
                python_list.append(python_key_dependency)

            else:
                python_cache_dependency = CacheDependency()
                python_cache_dependency.set_instance(r)
                python_list.append(python_cache_dependency)

        return python_list
        
    def __del__(self):
        """
        Releases the resources used by the CacheDependency object.
        """
        self.__cachedependency.dispose()
