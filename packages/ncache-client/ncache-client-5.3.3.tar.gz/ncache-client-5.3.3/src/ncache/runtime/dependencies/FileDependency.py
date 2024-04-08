from datetime import datetime

from ncache.runtime.dependencies.CacheDependency import *
from ncache.util.ExceptionHandler import ExceptionHandler


class FileDependency(CacheDependency):
    """
    FileDependency class is used to provide file based dependency to the user. If items are dependent on that file the
    items will be removed on file update.
    """
    def __init__(self, filenames, startafter=None):
        """
        Initializes a new instance of the FileExpiration class that monitors a file or directory for changes and
        indicates when change tracking is to begin.

        :param filenames: The file names or list of file names along with the path that are to be monitored.
        :type filenames: str or list
        :param startafter: The time after which the file will be monitored.
        :type startafter: datetime
        """
        super().__init__()

        if type(filenames) is list and len(filenames) != 0:
            for name in filenames:
                if type(name) is not str:
                    raise TypeError("Please provide list containing " + str(str) + " only")

            filenames = TypeCaster.to_java_array_list(filenames, True)

            if startafter is not None:
                ValidateType.type_check(startafter, datetime)
                startafter = TypeCaster.to_java_date(startafter)
                self.__filedependency = JavaInstancesFactory.get_java_instance("FileDependency")(filenames, startafter)
                return

            self.__filedependency = JavaInstancesFactory.get_java_instance("FileDependency")(filenames)
            return

        elif type(filenames) is str:
            ValidateType.is_string(filenames)
            filenames = TypeCaster.to_java_primitive_type(filenames)

            if startafter is not None:
                ValidateType.type_check(startafter, datetime)
                startafter = TypeCaster.to_java_date(startafter)
                self.__filedependency = JavaInstancesFactory.get_java_instance("FileDependency")(filenames, startafter)
                return

            self.__filedependency = JavaInstancesFactory.get_java_instance("FileDependency")(filenames)
            return

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("FileDependency.__init__"))

    def set_instance(self, value):
        self.__filedependency = value

    def get_instance(self):
        return self.__filedependency

    def get_file_names(self):
        """
        Gets the list of file names.

        :return: The list of file names associated with the dependency.
        :rtype: list
        """
        result = self.__filedependency.getFileNames()

        if result is not None:
            result = TypeCaster.to_python_list(result, True)

        return result

    def get_start_after_ticks(self):
        """
        Gets the time after which dependency is to be started.

        :return: The ticks after which dependency is started.
        :rtype: int
        """
        result = self.__filedependency.getStartAfterTicks()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def __del__(self):
        pass
