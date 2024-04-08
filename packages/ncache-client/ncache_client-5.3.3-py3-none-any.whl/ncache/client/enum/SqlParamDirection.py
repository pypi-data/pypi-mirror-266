from enum import Enum


class SqlParamDirection(Enum):
    """
    Sets the SQL param direction.
    """
    INPUT = 1
    """
    Used for Input variables. The value will be passed from calling environment. This is the default.
    """
    OUTPUT = 2
    """
    Used for Output variable and value will be returned to calling environment.
    """
    INPUT_OUTPUT = 3
    """
    The parameter can perform both input and output.
    """
    RETURN_VALUE = 4
    """
    The parameter represents a return value from an operation such as a stored procedure, built-in function,
    or user-defined function.
    """
