from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster


class Iterator:
    def __init__(self, javaiterator, iskeysiterator=True, isdatastructureiterator=False, objtype=None, isjsonobject=False, iscacheiterator=False):
        self.__javaiterator = javaiterator
        self.__value = None
        self.__iskeysiterator = iskeysiterator
        self.__isdatastructureiterator = isdatastructureiterator
        self.__objtype = objtype
        self.__isjsonobject = isjsonobject
        self.__iscacheiterator = iscacheiterator

    def __iter__(self):
        return self

    def __next__(self):
        if bool(self.__javaiterator.hasNext()):
            javavalue = self.__javaiterator.next()
            if self.__iskeysiterator:
                self.__value = str(jp.java.lang.String(javavalue))

            elif self.__isdatastructureiterator:
                self.__value = TypeCaster.deserialize(javavalue, objtype=self.__objtype, isjsonobject=self.__isjsonobject)

            elif self.__iscacheiterator:
                entry = JObject(javavalue, java.util.Map.Entry)
                self.__value = str(jp.java.lang.String(entry.getKey()))

            else:
                self.__value = TypeCaster.to_java_primitive_type(javavalue)
            return self.__value
        else:
            raise StopIteration
