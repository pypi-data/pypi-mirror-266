from enum import Enum


class SqlCommandType(Enum):
    """
    Describes the type of the command passed to the SqlDependency.
    """
    TEXT = 1
    """
    An SQL text command. (Default.)
    """
    STORED_PROCEDURE = 4
    """
    The name of a stored procedure.
    """
