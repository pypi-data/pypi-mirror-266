from ncache.util.TypeCaster import TypeCaster


class TopicDeleteEventArgs:
    """
    Arguments containing deleted topic information.
    """
    def __init__(self, topic):
        """
        Creates TopicDeleteEventArgs instance

        :param topic: Topic instance.
        """
        self.__topic = topic

    def get_topic_name(self):
        """
        Gets the name of the deleted topic.

        :return: The name of the deleted topic.
        :rtype: str
        """
        result = self.__topic.getTopicName()

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)

        return result
