from ncache.client.enum.CacheStatusNotificationType import CacheStatusNotificationType
from ncache.runtime.util.EnumUtil import EnumUtil
from ncache.util.TypeCaster import TypeCaster


class ClusterEvent:
    """
    ClusterEvent is used to notify interested parties that something has happened with respect to the cluster.
    """
    def __init__(self, value):
        """
        Creates a new object representing a cluster event.
        """
        self.__clusterevent = value

    def get_cache_id(self):
        """
        Returns cache-id of the stopped cache.

        :return: Returns cache-id of the stopped cache.
        :rtype: str
        """
        result = self.__clusterevent.getCacheId()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_event_type(self):
        """
        Gets the type of event.

        :return: the event type
        :rtype: CacheStatusNotificationType
        """
        result = self.__clusterevent.getEventType()

        if result is not None:
            result = EnumUtil.get_cache_status_notification_type_value(result)

        return result

    def get_ip(self):
        """
        Returns IP of the member node.

        :return: Returns IP of the member node.
        :rtype: str
        """
        result = self.__clusterevent.getIp()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result

    def get_port(self):
        """
        Returns the NCache Socket Server port.

        :return: NCache Socket Server port.
        :rtype: int
        """
        result = self.__clusterevent.getPort()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result
