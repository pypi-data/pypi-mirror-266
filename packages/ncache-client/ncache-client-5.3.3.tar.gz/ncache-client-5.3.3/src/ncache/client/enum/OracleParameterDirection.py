from enum import Enum


class OracleParameterDirection(Enum):
    """
    Describes whether the passed parameters are output parameters or input parameters.
    """
    INPUT = 1
    """
    The parameter is an input parameter.
    """
    OUTPUT = 2
    """
    The parameter is an output parameter.
    """
