from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.runtime.util.Iterator import Iterator
from ncache.client.enum.EventType import EventType
from ncache.runtime.caching.events.DataStructureDataChangeListener import DataStructureDataChangeListener
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.EventsListenerHelper import EventsListenerHelper
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class DistributedHashSet:
    """
    This class contains methods and parameters for distributed HashSet.
    """
    def __init__(self, objtype, isjsonobject):
        """
        Initializes a new instance of DistributedHashSet class

        :param objtype: Type of hash set values
        :type objtype: type
        """
        ValidateType.type_check(objtype, type, self.__init__)

        self.__set = None
        self.__objtype = objtype
        self.__isjsonobject = isjsonobject

    def __len__(self):
        result = self.__set.size()
        return TypeCaster.to_python_primitive_type(result)

    def get_instance(self):
        return self.__set

    def set_instance(self, value):
        self.__set = value

    def add_range(self, collection):
        """
        Insert elements of the provided collection in DistributedHashSet.

        :param collection: List of elements to be inserted in the DistributedHashSet.
        :type collection: list
        """
        ValidateType.type_check(collection, list, self.add_range)

        for i in range(len(collection)):
            ValidateType.validate_instance(collection[i], self.__objtype, self.add_range)
            collection[i] = TypeCaster.to_java_primitive_type(collection[i])

        javacollection = TypeCaster.to_java_array_list(collection, donotconvert=True)

        self.__set.addRange(javacollection)

    def remove_random(self):
        """
        Removes and returns a random element from the set.

        :return: Random element from set.
        :rtype: object
        """
        result = self.__set.removeRandom()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_random(self, count=None):
        """
        Returns a random element from the set or count distinct random elements from the set if count is specified.

        :param count: Number of required elements.
        :type count: int
        :return: Random element from set.
        :rtype: object
        """
        islistresult = False

        if count is not None:
            ValidateType.is_int(count, self.get_random)
            javacount = TypeCaster.to_java_primitive_type(count)
            islistresult = True
            result = self.__set.getRandom(javacount)
        else:
            result = self.__set.getRandom()

        if result is not None:
            if islistresult:
                result = TypeCaster.to_python_list(result, usejsonconversion=False, isjavatype=True)
            else:
                result = TypeCaster.to_python_primitive_type(result)

        return result

    def remove_all(self, items):
        """
        Remove the specified items from the set.

        :param items: List of items to remove from the set.
        :type items: list
        :return: The number of members that were removed from the set.
        :rtype: int
        """
        ValidateType.type_check(items, list, self.remove_all)

        for i in range(len(items)):
            ValidateType.validate_instance(items[i], self.__objtype, self.remove_all)
            items[i] = TypeCaster.to_java_primitive_type(items[i])

        javaitems = TypeCaster.to_java_array_list(items, isjavatype=True)

        result = self.__set.removeAll(javaitems)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def remove(self, item):
        """
        Remove the specified item from the set.

        :param item: Item to remove from the set.
        :type item: object
        :return: True if the item was removed successfully, False otherwise.
        :rtype: bool
        """
        ValidateType.type_check(item, self.__objtype, self.remove)

        javaitem = TypeCaster.to_java_primitive_type(item)

        result = self.__set.remove(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def union(self, otherset):
        """
        Returns the union of current set with the specified set.

        :param otherset: Key of set to compare with.
        :type otherset: str
        :return: Union of current set with the specified set.
        :rtype: set
        """
        ValidateType.is_string(otherset, self.union)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.union(javaotherset)

        if result is not None:
            result = TypeCaster.to_python_set(result, isjavatype=True)

        return result

    def intersect(self, otherset):
        """
        Returns the intersection of current set with the specified set.

        :param otherset: Key of set to compare with.
        :type otherset: str
        :return: Intersection of current set with the specified set.
        :rtype: set
        """
        ValidateType.is_string(otherset, self.intersect)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.intersect(javaotherset)

        if result is not None:
            result = TypeCaster.to_python_set(result, isjavatype=True)

        return result

    def difference(self, otherset):
        """
        Returns the difference of current set with the specified set.

        :param otherset: Key of set to compare with.
        :type otherset: str
        :return: Difference of current set with the specified set.
        :rtype: set
        """
        ValidateType.is_string(otherset, self.difference)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.difference(javaotherset)

        if result is not None:
            result = TypeCaster.to_python_set(result, isjavatype=True)

        return result

    def store_union(self, destination, otherset):
        """
        Take union of current set with the specified set and store the result in a new destination set.

        :param destination: Key of destination set.
        :type destination: str
        :param otherset: Name of set to compare with.
        :type otherset: str
        :return: Interface of destination set handler.
        :rtype: DistributedHashSet
        """
        ValidateType.is_string(destination, self.store_union)
        ValidateType.is_string(otherset, self.store_union)

        javadestination = TypeCaster.to_java_primitive_type(destination)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.storeUnion(javadestination, javaotherset)

        resultset = DistributedHashSet(self.__objtype, isjsonobject=self.__isjsonobject)

        if result is not None:
            resultset.set_instance(result)
            return resultset
        else:
            return result

    def store_difference(self, destination, otherset):
        """
        Take difference of current set with the specified set and store the result in a new destination set.

        :param destination: Key of destination set.
        :type destination: str
        :param otherset: Name of set to compare with.
        :type otherset: str
        :return: Interface of destination set handler.
        :rtype: DistributedHashSet
        """
        ValidateType.is_string(destination, self.store_difference)
        ValidateType.is_string(otherset, self.store_difference)

        javadestination = TypeCaster.to_java_primitive_type(destination)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.storeDifference(javadestination, javaotherset)

        resultset = DistributedHashSet(self.__objtype, isjsonobject=self.__isjsonobject)

        if result is not None:
            resultset.set_instance(result)
            return resultset
        else:
            return result

    def store_intersection(self, destination, otherset):
        """
        Take intersection of current set with the specified set and store the result in a new destination set.

        :param destination: Key of destination set.
        :type destination: str
        :param otherset: Name of set to compare with.
        :type otherset: str
        :return: Interface of destination set handler.
        :rtype: DistributedHashSet
        """
        ValidateType.is_string(destination, self.store_intersection)
        ValidateType.is_string(otherset, self.store_intersection)

        javadestination = TypeCaster.to_java_primitive_type(destination)
        javaotherset = TypeCaster.to_java_primitive_type(otherset)

        result = self.__set.storeIntersection(javadestination, javaotherset)

        resultset = DistributedHashSet(self.__objtype, isjsonobject=self.__isjsonobject)

        if result is not None:
            resultset.set_instance(result)
            return resultset
        else:
            return result

    def is_empty(self):
        """
        Returns True if this hash set contains no key-value mappings.

        :return: True if this map contains no key-value mappings, False otherwise
        :rtype: bool
        """
        result = self.__set.isEmpty()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def contains(self, obj):
        """
        Returns true if this collection contains the specified element.

        :param obj: Element whose presence in this collection is to be tested
        :type obj: object
        :return: True if this collection contains the specified element, False otherwise
        :rtype: bool
        """
        ValidateType.is_none(obj, self.contains)
        ValidateType.validate_instance(obj, self.__objtype, self.contains)
        javaobj = TypeCaster.to_java_primitive_type(obj)

        result = self.__set.contains(javaobj)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_iterator(self):
        """
        Returns an iterator that iterates through the entries of distributed hashset.

        :return: An Iterator instance
        :rtype: Iterator
        """
        javaiterator = self.__set.iterator()
        iterator = Iterator(javaiterator, iskeysiterator=False, isdatastructureiterator=False)
        return iter(iterator)

    def add(self, item):
        """
        Ensures that this collection contains the specified element (optional operation). Returns True if this
        collection changed as a result of the call. (Returns False if this collection does not permit duplicates and
        already contains the specified element.)

        :param item: Element whose presence in this collection is to be ensured
        :type item: object
        :return: True if this collection changed as a result of the call, False otherwise
        :rtype: bool
        """
        ValidateType.is_none(item, self.add)
        ValidateType.validate_instance(item, self.__objtype, self.add)
        javaitem = TypeCaster.to_java_primitive_type(item)

        result = self.__set.add(javaitem)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def add_all(self, collection):
        """
        Adds all of the elements in the specified collection to this collection

        :param collection: List containing elements to be added to this collection
        :type collection: list
        :return: True if this collection changed as a result of the call, False otherwise
        :rtype: bool
        """
        ValidateType.type_check(collection, list, self.add_all)

        for i in range(len(collection)):
            ValidateType.validate_instance(collection[i], self.__objtype, self.add_all)
            collection[i] = TypeCaster.to_java_primitive_type(collection[i])

        javacollection = TypeCaster.to_java_array_list(collection, donotconvert=True)

        result = self.__set.addAll(javacollection)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def add_change_listener(self, callablefunction, eventtypes, eventdatafilter):
        """
        Allows you to register collection event notifications like Add, Update, and Remove on the collection.

        :param callablefunction: The listener that is invoked when an item is added, updated or removed from the
            collection.
        :type callablefunction: Callable
        :param eventtypes: The list of event types that are to be registered.
        :type eventtypes: list
        :param eventdatafilter: An enum that allows you to specify to which extent you want the data with the event.
        :type eventdatafilter: DataTypeEventDataFilter
        """
        ValidateType.params_check(callablefunction, 2, self.add_change_listener)
        ValidateType.type_check(eventtypes, list, self.add_change_listener)
        for item in eventtypes:
            ValidateType.type_check(item, EventType, self.add_change_listener)
        ValidateType.type_check(eventdatafilter, DataTypeEventDataFilter, self.add_change_listener)

        eventlistener = EventsListenerHelper.get_listener(callablefunction, DataStructureDataChangeListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)
        javadatafilter = EnumUtil.get_data_type_event_data_filter(eventdatafilter.value)

        self.__set.addChangeListener(eventlistener, javaeventtypes, javadatafilter)

    def remove_change_listener(self, callablefunction, eventtypes):
        """
        Unregisters the callable listener function that was registered with collection changed notification.

        :param callablefunction: The callable listener function that was registered with collection changed notification.
        :type callablefunction: Callable
        :param eventtypes: The list of event types that were registered.
        :type eventtypes: list
        """
        ValidateType.type_check(eventtypes, list, self.remove_change_listener)
        for eventtype in eventtypes:
            ValidateType.type_check(eventtype, EventType, self.remove_change_listener)
        ValidateType.params_check(callablefunction, 2, self.remove_change_listener)

        listener = EventsListenerHelper.get_listener(callablefunction, DataStructureDataChangeListener)
        javaeventtypes = EventsListenerHelper.get_event_type_enum_set(eventtypes)

        self.__set.removeChangeListener(listener, javaeventtypes)
