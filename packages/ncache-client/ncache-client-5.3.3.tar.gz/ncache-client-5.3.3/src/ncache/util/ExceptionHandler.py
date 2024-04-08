
class ExceptionHandler:
    exceptionmessages = {
        "TimeSpan.__init__": "Please provide value for \"ticks\" or \"hour, minutes, and seconds\" or \"hour, minutes, "
                             "seconds, and days\" or \"hour, minutes, seconds, days, and milliseconds\" or do not "
                             "provide any value",
        "SqlCacheDependency.__init__": "Please provide value for \"connectionstring and cmdtext\" or \"connectionstring,"
                                       " cmdtext, cmdtype, and cmdparams\"",
        "OracleCacheDependency.__init__": "Please provide value for \"connectionstring and cmdtext\" or \""
                                          "connectionstring, cmdtext, cmdtype, and cmdparams\"",
        "KeyDependency.__init__": "Please specify value for \"keys\" or \"keys and startafter\" or \"keys and "
                             "keydependencytype\" or \"keys, startafter, and keydependencytype\"",
        "FileDependency.__init__": "Please provide value for \"filenames: List[str] or str\" or \"filenames: List[str] "
                                   "or str and startafter\"",
        "Expiration.__init__": "Please specify value for \"expirationtype\" or \"expirationtype and expireafter\" or "
                             "do not specify any value",
        "DistributedList.remove_range": "Invalid set of parameters passed. Please specify value for \"index and count\" "
                                        "or \"collection\"",
        "DataStructureManager.create_counter": "Invalid set of parameters passed. Please specify value for \"key\" or \""
                                               "key and initialvalue\" or \"key, initialvalue, attributes, and options\"",
        "DataStructureManager.create_hashset": "Invalid set of parameters passed. Please pass value for \"key and "
                                               "objtype\" or \"key, objtype, datastructureattributes, and writethruoptions\"",
        "DataStructureManager.create_list": "Invalid set of parameters passed. Please pass value for \"key and objtype\""
                                            " or \"key, objtype, datastructureattributes, and writethruoptions\"",
        "DataStructureManager.create_dictionary": "Invalid set of parameters passed. Please pass value for \"key and "
                                                  "objtype\" or \"key, objtype, datastructureattributes, and writethruoptions\"",
        "DataStructureManager.create_queue": "Invalid set of parameters passed. Please pass value for \"key and objtype\""
                                             " or \"key, objtype, datastructureattributes, and writethruoptions\"",
        "InvalidHashSet": "Invalid type specified for HashSet. HashSet can only be of primitive types.",
        "ServerInfo.__init__": "Invalid set of arguments passed. Please provide value for \"servername\" or \"servername"
                               " and port\" or \"ipaddress\"",
        "LockHandle.__init__": "Invalid set of parameters passed. Please provide value for \"lockhandle\" or \"lockid "
                               "and lockdate\"",
        "Credentials.__init__": "Invalid set of arguments passed. Please provide value for \"userid and password\" or "
                                "do not pass any argument",
        "CacheReader.get_value": "Invalid set of parameters passed. Please provide value for \"index and objtype\" or \""
                                 "columnname and objtype\"",
        "CacheManager.__init__": "Invalid set of arguments provided. Please provide value for \"cachename\" or \""
                                 "cachename and cacheconnectionoptions\" or \"cachename, cacheconnectionoptions, "
                                 "clientcachename, and clientcacheconnectionoptions\"",
        "Cache.insert": "Invalid set of arguments passed. Please provide value for \"key: str and item: object\" or \""
                        "key: str and item: CacheItem\" or\"key: str, value: CacheItem, writethruoptions: "
                        "WriteThruOptions\" or \"key: str, value: CacheItem, writethruoptions: WriteThruOptions, "
                        "lockhandle: LockHandle and releaselock: bool\"",
        "Cache.get": "Invalid set of arguments passed. Please provide value for \"key and objtype\" or \"key, objtype "
                     "and readthruoptions\" or \"key, objtype, readthruoptions and cacheitemversion\" or \"key, objtype,"
                     " acquirelock, lockhandle and locktimeout\"",
        "Cache.get_cacheitem": "Invalid set of arguments passed. Please provide value for \"key\" or \"key and "
                               "readthruoptions\" or \"key, readthruoptions and cacheitemversion\" or \"key, "
                               "acquirelock, lockhandle and locktimeout\"",
        "Cache.delete": "Invalid set of arguments passed. Please provide value for \"key\" or \"key and writethruoptions"
                        "\" or \"key, lockhandle, version and writethruoptions\"",
        "Cache.remove": "Invalid set of arguments passed. Please provide value for \"key and objtype\" or \"key, "
                        "objtype and writethruoptions\" or \"key, lockhandle, version, writethruoptions and objtype\"",
        "Message.__init__": "Invalid set of arguments passed. Please provide value for \"payload\" or \"payload and "
                            "timespan\"",
        "SearchService.execute_reader": "Invalid set of arguments passed. Please provide value for \"querycommand\" or "
                                        "\"querycommand, getdata, and chunksize\"",
        "SearchService.get_by_tag": "Invalid set of arguments passed. \"tag\" and \"wildcardexpression\" cannot be "
                                    "specified at the same time.",
        "SearchService.get_keys_by_tag": "Invalid set of arguments passed. \"tag\" and \"wildcardexpression\" cannot be"
                                         " specified at the same time.",
        "MessagingService.remove_cache_notification_listener": "Invalid set of arguments passed. Please provide value "
                                                               "for \"descriptor\" or \"keys, callablefunction, and "
                                                               "eventtypes=None\"",
        "QueryCommand.set_parameters": f"Parameter values can only be of type {str}, {int}, {float}, or {bool}."
    }

    @staticmethod
    def get_invalid_type_exception_message(function, validtype, value):
        if function is not None:
            return f"{function.__name__} failed: Expected type is {validtype} but received {type(value)}"
        else:
            return f"Operation failed: Expected parameter is an instance of {validtype} but received {type(value)}"

    @staticmethod
    def get_none_value_exception_message(function):
        if function is not None:
            return f"{function.__name__} failed: Value cannot be None"
        else:
            return "Value cannot be None"

    @staticmethod
    def get_invalid_params_exception_message(callablefunction, validparamscount, paramscount, function):
        if function is None:
            return f"Operation failed: Expected number of parameters for {callablefunction.__name__} are " \
                   f"{validparamscount} but received {paramscount}"
        else:
            return f"{function.__name__} failed: Expected number of parameters for {callablefunction.__name__} are " \
                   f"{validparamscount} but received {paramscount}"

    @staticmethod
    def get_invalid_instance_exception_message(instance, function=None):
        if function is None:
            return f"Operation failed. Parameter value can only be of type {instance}"
        else:
            return f"{function.__name__} failed. Parameter value can only be of type {instance}"

    @staticmethod
    def get_invalid_range_exception_message(param, lowerlimit, upperlimit):
        return f"Value of \"{param}\" cannot be less than {lowerlimit} and greater than {upperlimit}"

    @staticmethod
    def get_invalid_cache_insert_exception_message(itemtype):
        return "writethruoptions, lockhandle, and releaselock can only be used with item of type " + str(itemtype)

    @staticmethod
    def get_invalid_cache_add_exception_message(itemtype):
        return "writethruoptions can only be used with item of type " + str(itemtype)

    @staticmethod
    def get_invalid_ip_exception_message(itemtype):
        return f"\"ip\" can only be of type {str} or {itemtype}"

    @staticmethod
    def get_invalid_keys_exception_message(function):
        return f"{function.__name__} failed. Parameter \"keys\" can only be of type {list} or {str}"

    @staticmethod
    def get_invalid_dict_key_item_exception_message(function, objtype):
        return f"{function.__name__} failed. Only {str} type of keys and {objtype} type of items are supported."
