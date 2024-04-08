from enum import Enum


class IsolationLevel(Enum):
    """
    Specifies the Isolation level of the Cache.
    """
    DEFAULT = 1
    """
    Isolation level of Cache will be read from the configuration file.
    """
    IN_PROC = 2
    """
    InProc specifies low Isolation level i.e Cache process is embedded inside the application process.
    """
    OUT_PROC = 3
    """
    OutProc specifies high isolation level i.e Cache process runs in a separate process.
    """
