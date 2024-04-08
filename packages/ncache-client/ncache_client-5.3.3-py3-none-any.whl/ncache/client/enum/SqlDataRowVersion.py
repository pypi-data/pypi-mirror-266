from enum import Enum


class SqlDataRowVersion(Enum):
    """
    Sets the DataRowVersion to use when you load Value.
    """
    ORIGINAL = 256
    """
    The row contains its original values.
    """
    CURRENT = 512
    """
    The row contains current values.
    """
    PROPOSED = 1024
    """
    The row contains a proposed value.
    """
    DEFAULT = 1536
    """
    The default version of System.Data.DataRowState. For a DataRowState value of Added, Modified or Deleted, the default
    version is Current. For a System.Data.DataRowState value of Detached, the version is Proposed.
    """
