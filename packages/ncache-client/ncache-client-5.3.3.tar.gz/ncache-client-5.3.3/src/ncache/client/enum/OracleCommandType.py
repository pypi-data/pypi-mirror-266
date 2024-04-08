from enum import Enum


class OracleCommandType(Enum):
    """
    Describes the type of the Oracle command passed to the OracleDependency.
    """
    TEXT = 1
    """
    SQL statement to execute against the database.
    """
    STORED_PROCEDURE = 2
    """
    When the CommandType property is set to StoredProcedure, the CommandText property should be set to the name of
    the stored procedure.
    """
