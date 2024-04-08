from ncache.util.JPypeInit import *


class JavaInstancesFactory:
    @staticmethod
    def get_java_instance(classname):
        return jp.JClass(environment.get(classname))
