from ncache.client.enum.MessgeFailureReason import MessageFailureReason
from ncache.runtime.caching.MessageEventArgs import MessageEventArgs
from ncache.runtime.util.EnumUtil import EnumUtil


class MessageFailedEventArgs(MessageEventArgs):
    """
    Arguments containing message failure information.
    """
    def __init__(self, value):
        """
        Initializes a new instance of MessageFailedEventArgs class
        """
        self.__args = value

    def get_message_failure_reason(self):
        """
        Gets the reason due to which message was not delivered.

        :return: The MessageFailureReason enum.
        :rtype: MessageFailureReason
        """
        result = self.__args.getSubscriptionPolicy()

        if result is not None:
            result = EnumUtil.get_message_failure_reason_value(result)

        return result
