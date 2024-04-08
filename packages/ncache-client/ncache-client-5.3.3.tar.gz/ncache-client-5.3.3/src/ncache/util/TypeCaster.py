import collections
from datetime import datetime
from copy import copy

import jsons as json

from ncache.util.JavaInstancesFactory import *


class TypeCaster:
    @staticmethod
    def is_python_primitive(item):
        javatype = None

        if type(item) is str:
            javatype = jp.java.lang.String(item)

        elif type(item) is int:
            javatype = jp.java.lang.Integer(item)

        elif type(item) is float:
            javatype = jp.java.lang.Float(item)

        elif type(item) is bool:
            javatype = jp.java.lang.Boolean(item)

        return javatype

    @staticmethod
    def is_java_primitive(objtype):
        pythontype = objtype
        javatype = None

        if objtype is str:
            javatype = jp.java.lang.String

        elif objtype is int:
            javatype = jp.java.lang.Integer

        elif objtype is float:
            javatype = jp.java.lang.Float

        elif objtype is bool:
            javatype = jp.java.lang.Boolean

        return pythontype, javatype

    @staticmethod
    def serialize(value, verbose=False, isjsonobject=False):
        if verbose:
            if isjsonobject:
                serialized = json.dumps(value, verbose=True)
                if isinstance(value, collections.Collection):
                    return JavaInstancesFactory.get_java_instance("JsonArray")(serialized)
                return JavaInstancesFactory.get_java_instance("JsonObject")(serialized, str(type(value))[8:-2])
            return JavaInstancesFactory.get_java_instance("JsonValue")(TypeCaster.to_java_primitive_type(value))
        else:
            if isjsonobject:
                j = json.dumps(value)
                if isinstance(value, collections.Collection):
                    return JavaInstancesFactory.get_java_instance("JsonArray")(j)
                return JavaInstancesFactory.get_java_instance("JsonObject")(j, str(type(value))[8:-2])
            return JavaInstancesFactory.get_java_instance("JsonValue")(TypeCaster.to_java_primitive_type(value))

    @staticmethod
    def deserialize(jsonvalue, objtype=None, isjsonobject=False):
        if objtype is None:
            if isjsonobject:
                val = jsonvalue.toString().replace('"$type$":"' + str(objtype)[8:-2] + '", ', '')
                return json.loads(val)
            return TypeCaster.to_python_primitive_type(jsonvalue.getValue())

        else:
            if isjsonobject:
                val = jsonvalue.toString().replace('"$type$":"' + str(objtype)[8:-2] + '", ', '')
                return json.loads(val, objtype)

            return TypeCaster.to_python_primitive_type(jsonvalue.getValue())

    @staticmethod
    def to_python_list(javalist, isjavatype=False, classinstance=None, usejsonconversion=False, objtype=None, isjsonobject=True):
        pythonlist = []
        for j in javalist:
            if not usejsonconversion:
                if classinstance is not None:
                    instance = copy(classinstance)
                    instance.set_instance(j)
                pythonlist.append(instance if not isjavatype else TypeCaster.to_python_primitive_type(j))
            else:
                pythonlist.append(TypeCaster.deserialize(j, objtype, isjsonobject=isjsonobject))

        return pythonlist

    @staticmethod
    def to_python_set(javaset, isjavatype=False, classinstance=None, usejsonconversion=False):
        pythonset = {1, 2}
        pythonset.clear()
        for j in javaset:
            if not usejsonconversion:
                if classinstance is not None:
                    classinstance.set_instance(j)
                pythonset.add(classinstance if not isjavatype else TypeCaster.to_python_primitive_type(j))
            else:
                pythonset.add(TypeCaster.deserialize(str(j)))

        return pythonset

    @staticmethod
    def to_java_array_list(pythonlist, isjavatype=False, donotconvert=False):
        javaarray = jp.java.util.ArrayList()

        for p in pythonlist:
            if donotconvert:
                javaarray.add(p)
            else:
                javaarray.add(p.get_instance() if not isjavatype else TypeCaster.to_java_primitive_type(p))

        return javaarray

    @staticmethod
    def to_python_dict(javahashmap, isjavatype=False, classinstance=None):
        tempdict = {"key1": "value1", "key2": "value2"}
        tempdict.clear()

        for item in javahashmap:
            if classinstance is not None:
                classinstance.set_instance(javahashmap[item])

            tempdict[TypeCaster.to_python_primitive_type(item)] = classinstance if not isjavatype else TypeCaster.to_python_primitive_type(javahashmap[item])

        return tempdict

    @staticmethod
    def to_java_hash_map(pythondict, isjavatype=False, usejsonconversion=False, iskeyprimitive=True):
        javahashmap = jp.java.util.HashMap()

        for item in pythondict:
            if usejsonconversion:
                value = TypeCaster.to_java_primitive_type(pythondict[item])
                if value is None:
                    value = TypeCaster.serialize(pythondict[item], isjsonobject=True)
                javahashmap.put(TypeCaster.to_java_primitive_type(item) if iskeyprimitive
                                else item.get_instance(), value)
            else:
                javahashmap.put(TypeCaster.to_java_primitive_type(item) if iskeyprimitive
                                else item.get_instance(),
                                pythondict[item].get_instance() if not isjavatype
                                else TypeCaster.to_java_primitive_type(pythondict[item]))

        return javahashmap

    @staticmethod
    def to_python_date(javadate):
        timestamp = float(javadate.getTime())
        return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def to_java_date(pythondate):
        timestamp = pythondate.timestamp()
        return jp.java.util.Date(jp.java.lang.Long(timestamp) * 1000)

    @staticmethod
    def to_python_primitive_type(javatype):
        pythontype = None

        if type(javatype) is jp.java.lang.String or type(javatype) is str or type(javatype) is jp.JString:
            pythontype = str(javatype)

        elif type(javatype) is jp.java.lang.Integer or type(javatype) is jp.java.lang.Long or type(javatype) is jp.java.lang.Byte or type(javatype) is jp.JInt or type(javatype) is jp.JLong or type(javatype) is int or type(javatype) is jp.JByte:
            pythontype = int(javatype)

        elif type(javatype) is jp.java.lang.Float or type(javatype) is jp.java.lang.Double or type(javatype) is jp.JFloat or type(javatype) is jp.JDouble or type(javatype) is float:
            pythontype = float(javatype)

        elif type(javatype) is jp.java.lang.Boolean or type(javatype) is jp.JBoolean or type(javatype) is bool:
            pythontype = bool(javatype)

        else:
            pythontype = javatype

        return pythontype

    @staticmethod
    def to_java_primitive_type(pythontype):
        javatype = None

        if type(pythontype) is str:
            javatype = jp.java.lang.String(pythontype)

        elif type(pythontype) is int or type(pythontype) is JInt:
            javatype = jp.java.lang.Integer(pythontype)

        elif type(pythontype) is float:
            javatype = jp.java.lang.Float(pythontype)

        elif type(pythontype) is bool:
            javatype = jp.java.lang.Boolean(pythontype)

        return javatype

    @staticmethod
    def to_java_double(value):
        return jp.java.lang.Double(value)

    @staticmethod
    def to_java_long(value):
        return jp.java.lang.Long(value)
