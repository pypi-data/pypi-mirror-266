from enum import Enum


class CommandType(Enum):
    """
    Specifies how a command string is interpreted.
    """
    TEXT = 1
    """
    An SQL text command. (Default.)
    """
    STORED_PROCEDURE = 4
    """
    The name of a stored procedure.
    """
    TABLE_DIRECT = 512
    """
    The name of a table.
    """