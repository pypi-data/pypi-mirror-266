import asyncio
import collections
from asyncio import Task
from typing import Type

from ncache.client.CacheItem import CacheItem
from ncache.client.CacheItemAttributes import CacheItemAttributes
from ncache.client.datastructures.DataStructureManager import DataStructureManager
from ncache.client.services.SearchService import SearchService
from ncache.client.services.MessagingService import MessagingService
from ncache.client.services.NotificationService import NotificationService
from ncache.client.CacheItemVersion import CacheItemVersion
from ncache.runtime.WriteThruOptions import WriteThruOptions
from ncache.runtime.ReadThruOptions import ReadThruOptions
from ncache.client.LockHandle import LockHandle
from ncache.runtime.util.TimeSpan import TimeSpan
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType
from ncache.runtime.util.Iterator import Iterator


class Cache:
	"""
	This class contains the services and methods that are used to perform operations on the cache.
	"""
	def __init__(self, cache):
		"""
		This function gets an instance of the Cache
		:param cache: Instance of the Cache.
		"""
		self.__cache = cache

	def __str__(self):
		result = self.__cache.toString()

		if result is not None:
			result = TypeCaster.to_python_primitive_type(result)
		
		return result

	def get_instance(self):
		return self.__cache

	def set_instance(self, value):
		self.__cache = value

	def get_count(self):
		"""
		Gets the number of items stored in the cache

		:return: The number of items stored in the cache.
		:rtype: int
		"""
		result = self.__cache.getCount()

		if result is not None:
			result = TypeCaster.to_python_primitive_type(result)

		return result

	def get_notification_service(self):
		"""
		Gets an instance of NotificationService

		:return: An instance of NotificationService
		:rtype: NotificationService
		"""

		result = self.__cache.getNotificationService()

		if result is not None:
			result = NotificationService(result)

		return result

	def get_messaging_service(self):
		"""
		Gets an instance of MessagingService

		:return: An instance of MessagingService
		:rtype: MessagingService
		"""
		result = self.__cache.getMessagingService()

		if result is not None:
			result = MessagingService(result)

		return result

	def get_search_service(self):
		"""
		Gets an instance of SearchService.

		:return: An instance of SearchService
		:rtype: SearchService
		"""
		result = self.__cache.getSearchService()

		if result is not None:
			result = SearchService(result)

		return result

	def get_data_structures_manager(self):
		"""
		Gets an instance of DataStructureManager.

		:return: An instance of DataStructureManager
		:rtype: DataStructureManager
		"""
		result = self.__cache.getDataStructuresManager()

		if result is not None:
			result = DataStructureManager(result)

		return result

	def add(self, key, item, writethruoptions=None):
		"""
		Adds an item or CacheItem into the Cache object with a cache key to reference its location. You can also
		specify WriteThruOptions

		:param key: Unique key to identify the cache item.
		:type key: str
		:param item: The item (object) or CacheItem to be stored in the cache.
		:type item: object or CacheItem
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either
		:type writethruoptions: WriteThruOptions
		:return: Represents the version of each cache item.
		:rtype: CacheItemVersion
		"""

		ValidateType.is_key_value_valid(key, item, self.add)
		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.add)

		javatype = TypeCaster.is_python_primitive(item)
		javakey = TypeCaster.to_java_primitive_type(key)
		if javatype is not None:
			if writethruoptions is None:
				res = self.__cache.add(javakey, javatype)
			else:
				raise TypeError(ExceptionHandler.get_invalid_cache_add_exception_message(CacheItem))

		elif isinstance(item, CacheItem):
			if writethruoptions is None:
				res = self.__cache.add(javakey, item.get_instance())
			else:
				res = self.__cache.add(javakey, item.get_instance(), writethruoptions.get_instance())
		else:
			if writethruoptions is None:
				res = self.__cache.add(javakey, TypeCaster.serialize(item, isjsonobject=True))
			else:
				raise TypeError(ExceptionHandler.get_invalid_cache_add_exception_message(CacheItem))

		if res is not None:
			return CacheItemVersion(int(res.getVersion()))

	def add_bulk(self, items, writethruoptions=None):
		"""
		Adds a Dictionary of cache keys with CacheItem to the cache. You can also specify WriteThruOptions

		:param items: Dictionary of keys and CacheItem. Keys must be unique.
		:type items: dict
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:return: Dictionary of Keys along with Exception for items that were unable to store in cache.
		:rtype: dict
		"""
		ValidateType.type_check(items, dict, self.add_bulk)
		for item in items:
			ValidateType.is_string(item, self.add_bulk)
			ValidateType.type_check(items[item], CacheItem, self.add_bulk)
		javaitems = TypeCaster.to_java_hash_map(items, False)

		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.add_bulk)
			javawritethruoptions = writethruoptions.get_instance()

			result = self.__cache.addBulk(javaitems, javawritethruoptions)
		else:
			result = self.__cache.addBulk(javaitems)

		if result is not None:
			return self.__bulk_result_to_dict(result, True)

	def add_async(self, key, item, writethruoptions=None):
		"""
		Adds an item or a CacheItem to the cache asynchronously with a cache key to reference its location and with or without WriteThruOptions.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param item: The item (object) or CacheItem to be stored in the cache.
		:type item: object
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either
		:type writethruoptions: WriteThruOptions
		:return: Task that performs an add operation in the background.
		:rtype: Task
		"""
		return asyncio.create_task(self.__return_coroutine(self.add, key, item, writethruoptions))

	def insert(self, key, item, writethruoptions=None, lockhandle=None, releaselock=None):
		"""
		Inserts an item or a CacheItem to the cache.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param item: The value or the CacheItem that is to be inserted into the cache.
		:type item: object or CacheItem
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:param lockhandle: An instance of LockHandle that holds the lock information. If the item is locked, then it can only be updated if the correct lockHandle is specified.
		:type lockhandle: LockHandle
		:param releaselock: A flag to determine whether or not the lock should be released after operation is performed.
		:type releaselock: bool
		:return: Represents the version of each cache item.
		:rtype: CacheItemVersion
		"""

		ValidateType.is_key_value_valid(key, item, self.insert)
		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.insert)

		if lockhandle is not None and releaselock is not None:
			ValidateType.type_check(lockhandle, LockHandle, self.insert)
			ValidateType.type_check(releaselock, bool, self.insert)

		javatype = TypeCaster.is_python_primitive(item)

		javakey = TypeCaster.to_java_primitive_type(key)

		if javatype is not None:
			if writethruoptions is not None or lockhandle is not None or releaselock is not None:
				raise TypeError(ExceptionHandler.get_invalid_cache_insert_exception_message(CacheItem))
			res = self.__cache.insert(javakey, javatype)

		elif isinstance(item, CacheItem):
			value = item.get_instance()

			if lockhandle is not None and releaselock is not None:
				javawritethruoptions = None
				
				if writethruoptions is not None:
					javawritethruoptions = writethruoptions.get_instance()
				
				javalockhandle = lockhandle.get_instance()
				javareleaselock = TypeCaster.to_java_primitive_type(releaselock)
				res = self.__cache.insert(javakey, value, javawritethruoptions, javalockhandle, javareleaselock)

			elif lockhandle is not None or releaselock is not None:
				raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.insert"))

			else:
				javawritethruoptions = None
				
				if writethruoptions is not None:
					javawritethruoptions = writethruoptions.get_instance()
					
				res = self.__cache.insert(javakey, value, javawritethruoptions)

		else:
			if writethruoptions is not None or lockhandle is not None or releaselock is not None:
				raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.insert"))
			value = TypeCaster.serialize(item, isjsonobject=True, verbose=True)
			res = self.__cache.insert(javakey, value)

		if res is not None:
			return CacheItemVersion(int(res.getVersion()))

	def insert_bulk(self, items, writethruoptions=None):
		"""
		Inserts a Dictionary of cache keys with CacheItem to the cache with or without the WriteThruOptions.

		:param items: Dictionary of keys and CacheItem. Keys must be unique.
		:type items: dict
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:return: Dictionary of Keys along with Exception for items that were unable to store in cache.
		:rtype: dict
		"""
		ValidateType.type_check(items, dict, self.insert_bulk)
		for item in items:
			ValidateType.is_string(item, self.insert_bulk)
			ValidateType.type_check(items[item], CacheItem, self.insert_bulk)
		javaitems = TypeCaster.to_java_hash_map(items, False)

		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.insert_bulk)
			javawritethruoptions = writethruoptions.get_instance()

			result = self.__cache.insertBulk(javaitems, javawritethruoptions)
		else:
			result = self.__cache.insertBulk(javaitems)

		if result is not None:
			return self.__bulk_result_to_dict(result, True)

	def insert_async(self, key, item, writethruoptions=None):
		"""
		Inserts an item or a CacheItem to the cache asynchronously with a cache key to reference its location and with or without WriteThruOptions.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param item: The item (object) or CacheItem to be stored in the cache.
		:type item: object
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:return: Task that performs an insert operation in the background.
		:rtype: Task
		"""
		return asyncio.create_task(self.__return_coroutine(self.insert, key, item, writethruoptions))

	def update_attributes(self, key, attributes):
		"""
		Update CacheItemAttributes of an existing item in cache.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param attributes: An instance of CacheItemAttributes to update item in the cache.
		:type attributes: CacheItemAttributes
		:return: Flag that determines status of the update operation. True if attributes of the item in cache was updated successfully otherwise False.
		:rtype: bool
		"""
		ValidateType.is_string(key, self.update_attributes)
		ValidateType.type_check(attributes, CacheItemAttributes, self.update_attributes)

		javakey = TypeCaster.to_java_primitive_type(key)
		javaattributes = attributes.get_instance()

		result = self.__cache.updateAttributes(javakey, javaattributes)

		if result is not None:
			result = TypeCaster.to_python_primitive_type(result)

		return result

	def get(self, key, objtype, readthruoptions=None, cacheitemversion=None, acquirelock=None, locktimeout=None, lockhandle=None):
		"""
		Retrieves the specified item from the Cache object.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param objtype: Type of the item to be retrieved from cache
		:type objtype: type
		:param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
		:type readthruoptions: ReadThruOptions
		:param acquirelock: A flag to determine whether to acquire a lock or not.
		:type acquirelock: bool
		:param locktimeout: The TimeSpan after which the lock is automatically released.
		:type locktimeout: TimeSpan
		:param lockhandle: An instance of LockHandle to hold the lock information.
		:type lockhandle: LockHandle
		:param cacheitemversion: The version of the object. If None is passed for CacheItemVersion, then the version of the object from the cache is returned. If non-None CacheItemVersion is passed, then object is returned from the cache only if that is the current version of the object in the cache.
		:type cacheitemversion: CacheItemVersion
		:return: The retrieved cache item, or a None reference if the key is not found.
		:rtype: object
		"""

		ValidateType.is_string(key, self.get)
		javakey = TypeCaster.to_java_primitive_type(key)

		ValidateType.type_check(objtype, type, self.get)

		if readthruoptions is not None:
			ValidateType.type_check(readthruoptions, ReadThruOptions, self.get)

		if locktimeout is not None and lockhandle is not None and acquirelock is not None:
			ValidateType.type_check(lockhandle, LockHandle, self.get)
			ValidateType.type_check(locktimeout, TimeSpan, self.get)
			ValidateType.type_check(acquirelock, bool, self.get)

		if cacheitemversion is not None:
			ValidateType.type_check(cacheitemversion, CacheItemVersion, self.get)

		pythontype, javatype = TypeCaster.is_java_primitive(objtype)

		usejsonconversoin = False
		if javatype is None:
			if isinstance(objtype(), collections.Collection):
				javatype = JavaInstancesFactory.get_java_instance("JsonArray")
			else:
				javatype = JavaInstancesFactory.get_java_instance("JsonObject")
			usejsonconversoin = True
		
		if cacheitemversion is not None:
			javacacheitemversion = cacheitemversion.get_instance()
			javareadthruoptions = None
			
			if readthruoptions is not None:
				javareadthruoptions = readthruoptions.get_instance()

			result = self.__cache.get(javakey, javacacheitemversion, javareadthruoptions, javatype)

		elif locktimeout is not None and lockhandle is not None and acquirelock is not None:
			javalockhandle = lockhandle.get_instance()
			javalocktimeout = locktimeout.get_instance()
			javaacquirelock = TypeCaster.to_java_primitive_type(acquirelock)
			result = self.__cache.get(javakey, javaacquirelock, javalocktimeout, javalockhandle, javatype)

		elif locktimeout is None and lockhandle is None and acquirelock is None and cacheitemversion is None:
			javareadthruoptions = None
			
			if readthruoptions is not None:
				javareadthruoptions = readthruoptions.get_instance()

			result = self.__cache.get(javakey, javareadthruoptions, javatype)

		else:
			raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.get"))

		if result is not None:
			if not usejsonconversoin:
				result = pythontype(result)
			else:
				result = TypeCaster.deserialize(result, objtype, isjsonobject=True)
		return result

	def get_bulk(self, keys, objtype, readthruoptions=None):
		"""
		Retrieves the objects from cache for the given keys as key-value pairs in form of a Dictionary.

		:param keys: The list keys against which items are to be fetched from cache.
		:type keys: list
		:param objtype: Type of the item to be retrieved from cache
		:type objtype: type
		:param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
		:type readthruoptions: ReadThruOptions
		:return: The retrieved cache items as Dictionary of key-value pairs.
		:rtype: dict
		"""
		ValidateType.type_check(objtype, type, self.get_bulk)
		ValidateType.type_check(keys, list, self.get_bulk)
		for key in keys:
			ValidateType.is_string(key, self.get_bulk)
		javakeys = TypeCaster.to_java_array_list(keys, True)

		pythontype, javatype = TypeCaster.is_java_primitive(objtype)

		if javatype is None:
			javatype = JavaInstancesFactory.get_java_instance("JsonObject")

		javareadthruoptions = None

		if readthruoptions is not None:
			ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_bulk)
			javareadthruoptions = readthruoptions.get_instance()

		result = self.__cache.getBulk(javakeys, javareadthruoptions, javatype)

		if result is not None:
			return self.__bulk_result_to_dict(result, False, objtype)

	def get_cacheitem(self, key, readthruoptions=None, cacheitemversion=None, acquirelock=None, locktimeout=None, lockhandle=None):
		"""
		Retrieves the specified CacheItem from the Cache object.

		:param key: Unique key to identify the cache item.
		:type key: str
		:param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
		:type readthruoptions: ReadThruOptions
		:param acquirelock: A flag to determine whether to acquire a lock or not.
		:type acquirelock: bool
		:param locktimeout: The TimeSpan after which the lock is automatically released.
		:type locktimeout: TimeSpan
		:param lockhandle: An instance of LockHandle to hold the lock information.
		:type lockhandle: LockHandle
		:param cacheitemversion: The version of the object. If None is passed for CacheItemVersion, then the version of
			the object from the cache is returned. If non-None CacheItemVersion is passed, then object is returned from
			the cache only if that is the current version of the object in the cache.
		:type cacheitemversion: CacheItemVersion
		:return: The retrieved CacheItem, or a None reference if the key is not found.
		:rtype: CacheItem
		"""
		ValidateType.is_string(key, self.get_cacheitem)
		javakey = TypeCaster.to_java_primitive_type(key)
		if readthruoptions is not None:
			ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_cacheitem)

		if cacheitemversion is not None:
			ValidateType.type_check(cacheitemversion, CacheItemVersion, self.get_cacheitem)

		if acquirelock is not None and lockhandle is not None and locktimeout is not None:
			ValidateType.type_check(acquirelock, bool, self.get_cacheitem)
			ValidateType.type_check(lockhandle, LockHandle, self.get_cacheitem)
			ValidateType.type_check(locktimeout, TimeSpan, self.get_cacheitem)

		if cacheitemversion is not None:
			javareadthruoptions = None
			
			if readthruoptions is not None:
				javareadthruoptions = readthruoptions.get_instance()

			javacacheitemversion = cacheitemversion.get_instance()
			result = self.__cache.getCacheItem(javakey, javacacheitemversion, javareadthruoptions)

		elif acquirelock is not None and lockhandle is not None and locktimeout is not None:
			javaacquirelock = TypeCaster.to_java_primitive_type(acquirelock)
			javalockhandle = lockhandle.get_instance()
			javalocktimeout = locktimeout.get_instance()
			result = self.__cache.getCacheItem(javakey, javaacquirelock, javalocktimeout, javalockhandle)

		elif cacheitemversion is None and acquirelock is None and lockhandle is None and locktimeout is None:
			javareadthruoptions = None
			
			if readthruoptions is not None:
				javareadthruoptions = readthruoptions.get_instance()

			result = self.__cache.getCacheItem(javakey, javareadthruoptions)

		else:
			raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.get_cacheitem"))

		if result is not None:
			cacheitem = CacheItem()
			cacheitem.set_instance(result)
			return cacheitem

		return result

	def get_cacheitem_bulk(self, keys, readthruoptions=None):
		"""
		Retrieves the CacheItems from cache for the given keys as key-value pairs in form of a Dictionary.

		:param keys: The keys against which CacheItems are to be fetched from cache.
		:type keys: list
		:param readthruoptions: ReadThruOptions to read from data source. These can be either ReadThru, ReadThruForced or None.
		:type readthruoptions: ReadThruOptions
		:return: The retrieved CacheItems as Dictionary of key-value pairs.
		:rtype: dict
		"""
		ValidateType.type_check(keys, list, self.get_cacheitem_bulk)
		for key in keys:
			ValidateType.is_string(key, self.get_cacheitem_bulk)
		javakeys = TypeCaster.to_java_array_list(keys, True)

		if readthruoptions is not None:
			ValidateType.type_check(readthruoptions, ReadThruOptions, self.get_cacheitem_bulk)
			javareadthruoptions = readthruoptions.get_instance()
			result = self.__cache.getCacheItemBulk(javakeys, javareadthruoptions)

		else:
			result = self.__cache.getCacheItemBulk(javakeys)

		if result is not None:
			return self.__bulk_result_to_dict(result, iscacheitem=True)

	def get_if_newer(self, key, cacheitemversion, objtype):
		"""
		Gets an object from the cache only if a newer version of the object exists in cache.

		:param key: Unique key used to reference the desired object.
		:type key: str
		:param cacheitemversion: The CacheItemVersion of the object.
		:type cacheitemversion: CacheItemVersion
		:param objtype: Type of the item to be removed from cache
		:type objtype: type
		:return: If a newer object exists in the cache, the object is returned. Otherwise, None is returned.
		:rtype: object or None
		"""
		ValidateType.is_string(key, self.get_if_newer)
		ValidateType.type_check(cacheitemversion, CacheItemVersion, self.get_if_newer)
		ValidateType.type_check(objtype, type, self.get_if_newer)

		javakey = TypeCaster.to_java_primitive_type(key)
		javacacheitemversion = cacheitemversion.get_instance()
		pythontype, javatype = TypeCaster.is_java_primitive(objtype)

		usejsonconversoin = False
		if javatype is None:
			if isinstance(objtype(), collections.Collection):
				javatype = JavaInstancesFactory.get_java_instance("JsonArray")
			else:
				javatype = JavaInstancesFactory.get_java_instance("JsonObject")
			usejsonconversoin = True

		result = self.__cache.getIfNewer(javakey, javacacheitemversion, javatype)

		if result is not None:
			if not usejsonconversoin:
				result = pythontype(result)
			else:
				result = TypeCaster.deserialize(result, objtype, isjsonobject=True)
		return result

	def get_if_newer_cacheitem(self, key, cacheitemversion):
		"""
		Gets an object from the cache only if a newer version of the object exists in cache.

		:param key: Unique key used to reference the desired object.
		:type key: str
		:param cacheitemversion: The CacheItemVersion of the object.
		:type cacheitemversion: CacheItemVersion
		:return: If a newer CacheItem exists in the cache, the CacheItem is returned. Otherwise, None is returned.
		:rtype: CacheItem or None
		"""
		ValidateType.is_string(key, self.get_cacheitem)
		ValidateType.type_check(cacheitemversion, CacheItemVersion, self.get_if_newer_cacheitem)

		javacacheitemversion = cacheitemversion.get_instance()
		javakey = TypeCaster.to_java_primitive_type(key)

		result = self.__cache.getIfNewerCacheItem(javakey, javacacheitemversion)

		if result is not None:
			cacheitem = CacheItem()
			cacheitem.set_instance(result)
			return cacheitem

		return result

	def delete(self, key, writethruoptions=None, lockhandle=None, version=None):
		"""
		Deletes the item with the specified key from cache.

		:param key: Unique key of the item to be deleted.
		:type key: str
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:param lockhandle: If the item is locked, it can be removed only if the correct lockhandle is specified. lockhandle should be the same which was used initially to lock the item.
		:type lockhandle: LockHandle
		:param version: The version of the item to be removed. The item is removed from the cache only if this is still the most recent version in the cache.
		:type version: CacheItemVersion
		"""

		ValidateType.is_string(key, self.delete)
		javakey = TypeCaster.to_java_primitive_type(key)

		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.delete)
		if lockhandle is not None and version is not None:
			ValidateType.type_check(lockhandle, LockHandle, self.delete)
			ValidateType.type_check(version, CacheItemVersion, self.delete)

		if version is not None:
			javawritethruoptions = None
			javalockhandle = None
			
			if writethruoptions is not None:
				javawritethruoptions = writethruoptions.get_instance()

			if lockhandle is not None:
				javalockhandle = lockhandle.get_instance()

			javaversion = version.get_instance()
			self.__cache.delete(javakey, javalockhandle, javaversion, javawritethruoptions)
			
		elif version is None and lockhandle is None:
			javawritethruoptions = None
			if writethruoptions is not None:
				javawritethruoptions = writethruoptions.get_instance()
			
			self.__cache.delete(javakey, javawritethruoptions)

		else:
			raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.delete"))

	def delete_async(self, key, writethruoptions=None):
		"""
		Deletes an item from the cache asynchronously with a cache key to reference its location.

		:param key:  Unique key of the item to be deleted.
		:type key: str
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:return: Task that performs a delete operation in the background
		:rtype: Task
		"""
		return asyncio.create_task(self.__return_coroutine(self.delete, key, writethruoptions))

	def delete_bulk(self, keys, writethruoptions=None):
		"""
		Deletes the specified items from the Cache. You can also specify the write option such that the items may be removed from both cache and data source.

		:param keys: Unique list of keys of the items to be deleted.
		:type keys: list
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		"""
		ValidateType.type_check(keys, list, self.delete_bulk)
		for key in keys:
			ValidateType.is_string(key, self.delete_bulk)
		javakeys = TypeCaster.to_java_array_list(keys, True)
		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.delete_bulk)

		if writethruoptions is not None:
			javawritethruoptions = writethruoptions.get_instance()
			self.__cache.deleteBulk(javakeys, javawritethruoptions)
		else:
			self.__cache.deleteBulk(javakeys)

	def remove(self, key, objtype, writethruoptions=None, lockhandle=None, version=None):
		"""
		Removes and retrieves the item with the specified key from cache.

		:param key: Unique key of the item to be deleted.
		:type key: str
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either
		:type writethruoptions: WriteThruOptions
		:param objtype: Type of the item to be removed from cache
		:type objtype: type
		:param lockhandle: If the item is locked, it can be removed only if the correct lockhandle is specified. lockhandle should be the same which was used initially to lock the item.
		:type lockhandle: LockHandle
		:param version: The version of the item to be removed. The item is removed from the cache only if this is still the most recent version in the cache.
		:type version: CacheItemVersion
		:return: The removed item if the key exists otherwise None is returned.
		:rtype: object
		"""

		ValidateType.is_string(key, self.remove)
		javakey = TypeCaster.to_java_primitive_type(key)

		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.remove)
		if lockhandle is not None and version is not None:
			ValidateType.type_check(lockhandle, LockHandle, self.remove)
			ValidateType.type_check(version, CacheItemVersion, self.remove)

		pythontype, javatype = TypeCaster.is_java_primitive(objtype)
		usejsonconversoin = False

		if javatype is None:
			if isinstance(objtype(), collections.Collection):
				javatype = JavaInstancesFactory.get_java_instance("JsonArray")
			else:
				javatype = JavaInstancesFactory.get_java_instance("JsonObject")
			usejsonconversoin = True

		if version is not None:
			javawritethruoptions = None
			javalockhandle = None

			if writethruoptions is not None:
				javawritethruoptions = writethruoptions.get_instance()

			if lockhandle is not None:
				javalockhandle = lockhandle.get_instance()

			javaversion = version.get_instance()
			result = self.__cache.remove(javakey, javalockhandle, javaversion, javawritethruoptions, javatype)

		elif lockhandle is not None:
			javalockhandle = lockhandle.get_instance()
			javawritethruoptions = None
			javaversion = None

			if version is not None:
				javaversion = version.get_instance()

			if writethruoptions is not None:
				javawritethruoptions = writethruoptions.get_instance()

			result = self.__cache.remove(javakey, javalockhandle, javaversion, javawritethruoptions, javatype)
		elif lockhandle is None and version is None:
			javawritethruoptions = None
			
			if writethruoptions is not None:
				javawritethruoptions = writethruoptions.get_instance()

			result = self.__cache.remove(javakey, javawritethruoptions, javatype)

		else:
			raise ValueError(ExceptionHandler.exceptionmessages.get("Cache.remove"))

		if result is not None:
			if not usejsonconversoin:
				result = pythontype(result)
			else:
				result = TypeCaster.deserialize(result, objtype, isjsonobject=True)
		return result

	def remove_async(self, key, objtype, writethruoptions=None):
		"""
		Removes an item from the cache asynchronously with a cache key to reference its location.

		:param key:  Unique key of the item to be deleted.
		:type key: str
		:param objtype: Type of the item to be removed from cache
		:type objtype: type
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WriteThru, WriteBehind or None.
		:type writethruoptions: WriteThruOptions
		:return: Task that performs a remove operation in the background. Once completed returns the removed cache item
		:rtype: Task
		"""
		return asyncio.create_task(self.__return_coroutine(self.remove, key, objtype, writethruoptions))

	def remove_bulk(self, keys, objtype, writethruoptions=None):
		"""
		Removes the specified items from the Cache and returns them to the application in the form of a Dictionary.

		:param keys: List of Unique keys of the item to be removed.
		:type keys: list
		:param objtype: Type of the item to be retrieved from cache
		:type objtype: type
		:param writethruoptions: WriteThruOptions regarding updating the data source. This can be either WRITE_THRU, WRITE_BEHIND or NONE.
		:type writethruoptions: WriteThruOptions
		:return: The removed items from cache in form of a Dictionary.
		:rtype: dict
		"""
		ValidateType.type_check(keys, list, self.remove_bulk)
		for key in keys:
			ValidateType.is_string(key, self.remove_bulk)

		ValidateType.type_check(objtype, type, self.remove_bulk)
		pythontype, javatype = TypeCaster.is_java_primitive(objtype)

		if javatype is None:
			javatype = JavaInstancesFactory.get_java_instance("JsonObject")

		javakeys = TypeCaster.to_java_array_list(keys, True)
		if writethruoptions is not None:
			ValidateType.type_check(writethruoptions, WriteThruOptions, self.remove_bulk)
			javawritethruoptions = writethruoptions.get_instance()

			result = self.__cache.removeBulk(javakeys, javawritethruoptions, javatype)
		else:
			result = self.__cache.removeBulk(javakeys, javatype)

		return self.__bulk_result_to_dict(result, False, objtype)

	def contains(self, key):
		"""
		Determines whether the cache contains a specific key.

		:param key: The key to locate in the cache.
		:type key: str
		:return: True if the Cache contains an element with the specified key; otherwise, False
		:rtype: bool
		"""
		ValidateType.is_string(key, self.contains)
		javakey = TypeCaster.to_java_primitive_type(key)

		result = self.__cache.contains(javakey)

		if result is not None:
			result = TypeCaster.to_python_primitive_type(result)

		return result

	def contains_bulk(self, keys):
		"""
		Determines whether the cache contains specified keys.

		:param keys: List of keys.
		:type keys: list
		:return: Dictionary of Keys with flag to determine presence of each key in cache. <b>True</b> if the Cache contains an element with the specified key; otherwise, <b>False</b>.
		:rtype: dict
		"""
		ValidateType.type_check(keys, list, self.contains_bulk)
		for key in keys:
			ValidateType.is_string(key, self.contains_bulk)

		javakeys = TypeCaster.to_java_array_list(keys, isjavatype=True)
		result = self.__cache.containsBulk(javakeys)

		if result is not None:
			return self.__bulk_result_to_dict(result)

	def clear(self):
		"""
		Removes all elements from the Cache.
		"""
		self.__cache.clear()

	def clear_client_cache(self):
		"""
		Removes all elements from the client cache.
		"""
		self.__cache.clearClientCache()

	def unlock(self, key, lockhandle=None):
		"""
		Unlocks a locked cached item if the correct lockhandle is provided. Forcefully unlocks the item if no lockhandle is provided.

		:param key: Key of the cached item to be unlocked.
		:type key: str
		:param lockhandle: An instance of LockHandle that is generated when the lock is acquired.
		:type lockhandle: LockHandle
		"""
		ValidateType.is_string(key, self.unlock)
		javakey = TypeCaster.to_java_primitive_type(key)

		if lockhandle is not None:
			ValidateType.type_check(lockhandle, LockHandle, self.unlock)
			javalockhandle = lockhandle.get_instance()

			self.__cache.unlock(javakey, javalockhandle)

		else:
			self.__cache.unlock(javakey)

	def lock(self, key, locktimeout, lockhandle):
		"""
		Acquires a lock on an item in the cache.

		:param key: Key of cached item to be locked.
		:type key:str
		:param locktimeout: An instance of TimeSpan after which the lock is automatically released.
		:type locktimeout: TimeSpan
		:param lockhandle: An instance of LockHandle that will be filled in with the lock information if lock is acquired successfully.
		:type lockhandle: LockHandle
		:return: Whether or not lock was acquired successfully.
		:rtype: bool
		"""
		ValidateType.is_string(key, self.lock)
		ValidateType.type_check(lockhandle, LockHandle, self.lock)
		ValidateType.type_check(locktimeout, TimeSpan, self.lock)

		javakey = TypeCaster.to_java_primitive_type(key)
		javalocktimeout = locktimeout.get_instance()
		javalockhandle = lockhandle.get_instance()

		result = self.__cache.lock(javakey, javalocktimeout, javalockhandle)

		if result is not None:
			result = TypeCaster.to_python_primitive_type(result)

		return result

	def as_iterable(self):
		javaiterator = self.__cache.asIterator()
		iterator = Iterator(javaiterator, iskeysiterator=False, iscacheiterator=True)
		return iter(iterator)

	def close(self):
		"""
		Closes this resource, relinquishing any underlying resources.
		"""
		self.__cache.close()

	async def __return_coroutine(self, function, *args):
		if function == self.delete:
			return function(args[0], args[1])
		else:
			return function(args[0], args[1], args[2])
		# For the time being, we have only 2 or 3 possible arguments. This function has to be made generic if needed in future.

	@staticmethod
	def __bulk_result_to_dict(javabulkmap, isexception=False, objtype=None, iscacheitem=False):
		pythondict = {}

		for item in javabulkmap:
			key = TypeCaster.to_python_primitive_type(item)
			if isexception:
				pythondict[key] = javabulkmap[item]
			elif iscacheitem:
				cacheitem = CacheItem()
				cacheitem.set_instance(javabulkmap[item])
				pythondict[key] = cacheitem
			else:
				pythontype = TypeCaster.to_python_primitive_type(javabulkmap[item])

				if pythontype is not None:
					pythondict[key] = pythontype
				else:
					pythondict[key] = TypeCaster.deserialize(javabulkmap[item], objtype, isjsonobject=True)

		return pythondict
