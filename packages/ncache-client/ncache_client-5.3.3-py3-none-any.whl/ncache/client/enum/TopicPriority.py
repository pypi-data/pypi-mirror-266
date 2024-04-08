from enum import Enum


class TopicPriority(Enum):
    """
    Specifies the relative priority of topics stored in the Cache.
    """
    LOW = 1
    """
    Messages in topic with this priority level are the most likely to be deleted from the cache as the server frees system memory.
    """
    NORMAL = 2
    """
    Messages in topic with this priority level are likely to be deleted from the cache as the server frees system memory
    only after those topics with Low priority. This is the default priority of the topic.
    """
    HIGH = 3
    """
    Messages in topic with this priority level are less likely to be deleted from the cache as the server frees system
    memory.
    """
