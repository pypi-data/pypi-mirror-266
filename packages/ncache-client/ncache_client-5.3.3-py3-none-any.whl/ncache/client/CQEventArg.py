from ncache.client.EventArg import EventArg
from ncache.runtime.util.EnumUtil import EnumUtil


class CQEventArg(EventArg):
    """
    This object is received when an even is raised and listener is executed. CQEventArg contains necessary information
    to identify the event and perform necessary actions accordingly.
    """
    def __init__(self, args):
        super().__init__(args)
        self.__args = args

    def get_instance(self):
        return self.__args

    def set_instance(self, value):
        self.__args = value

    def get_continuous_query(self):
        """
        Reference to the ContinuousQuery object it is registered against

        :return: The ContinuousQuery instance.
        :rtype: ContinuousQuery
        """
        result = self.__args.getContinuousQuery()

        if result is not None:
            from ncache.client.ContinuousQuery import ContinuousQuery

            query = ContinuousQuery()
            query.set_instance(result)

            return query

        return result

    def get_event_type(self):
        """
        Gets the type of the event.

        :return: The EventType enum.
        :rtype: EventType
        """
        eventtype = self.__args.getEventType()

        if eventtype is not None:
            eventtype = EnumUtil.get_event_type_value(eventtype)

        return eventtype

