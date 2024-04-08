from ncache.client.CacheConnectionOptions import CacheConnectionOptions
from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.client.Cache import Cache
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class CacheManager:
    """
    Provides and manages the instance of Cache class
    """
    @staticmethod
    def get_cache(cachename, cacheconnectionoptions=None, clientcachename=None, clientcacheconnectionoptions=None):
        """
        Returns an instance of Cache for this application.

        :param cachename: The identifier for the Cache.
        :type cachename: str
        :param cacheconnectionoptions: CacheConnectionOptions parameters for cache connection.
        :type cacheconnectionoptions: CacheConnectionOptions
        :param clientcachename: The identifier for the ClientCache
        :type clientcachename: str
        :param clientcacheconnectionoptions: CacheConnectionOptions parameters for ClientCache connection.
        :type clientcacheconnectionoptions: CacheConnectionOptions
        :return: Instance of Cache.
        :rtype: Cache
        """
        cachemanager = JavaInstancesFactory.get_java_instance("CacheManager")

        ValidateType.is_string(cachename, CacheManager.get_cache)
        javacachename = TypeCaster.to_java_primitive_type(cachename)

        if cacheconnectionoptions is not None:
            ValidateType.type_check(cacheconnectionoptions, CacheConnectionOptions, CacheManager.get_cache)
            javacacheconnectionoptions = cacheconnectionoptions.get_instance()

            if clientcachename is not None and clientcacheconnectionoptions is not None:
                ValidateType.is_string(clientcachename, CacheManager.get_cache)
                ValidateType.type_check(clientcacheconnectionoptions, CacheConnectionOptions, CacheManager.get_cache)
                javaclientcachename = TypeCaster.to_java_primitive_type(clientcachename)
                javaclientcacheconnectionoptions = clientcacheconnectionoptions.get_instance()

                cache = cachemanager.getCache(javacachename, javacacheconnectionoptions, javaclientcachename, javaclientcacheconnectionoptions)
                return Cache(cache)

            cache = cachemanager.getCache(javacachename, javacacheconnectionoptions)
            return Cache(cache)

        elif cachename is not None and cacheconnectionoptions is None and clientcacheconnectionoptions is None and clientcachename is None:
            cache = cachemanager.getCache(javacachename)
            return Cache(cache)

        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("CacheManager.__init__"))

