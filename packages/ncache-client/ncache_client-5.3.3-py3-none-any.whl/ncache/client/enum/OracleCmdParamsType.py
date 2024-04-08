from enum import Enum


class OracleCmdParamsType(Enum):
    """
    Describes the type of the parameters passed to the Oracle command.
    """
    B_FILE = 1
    """
    The BFILE datatype stores unstructured binary data in operating-system files outside the database.
    A BFILE column or attribute stores a file locator that points to an external file containing the data.
    The amount of BFILE data that can be stored is limited by the operating system.
    """
    BLOB = 2
    """
    The BLOB datatype stores unstructured binary data in the database.
    BLOBs can store up to 128 terabytes of binary data.
    """
    BYTE = 3,
    """
    Allows whole numbers from 0 to 255
    """
    CHAR = 4
    """
    The CHAR datatype stores fixed-length character strings.
    String length (in bytes or characters) is between 1 and 2000 bytes.
    The default is 1 byte.
    """
    CLOB = 5
    """
    The CLOB data types store up to 128 terabytes of character data in the database.
    CLOBs store database character set data.
    """
    DATE = 6
    """
    The Date datatype stores point-in-time values (dates and times) in a table.
    The Date datatype stores the year (including the century),
    the month, the day, the hours, the minutes, and the seconds (after midnight).
    """
    DECIMAL = 7
    """
    Decimal number datatype.
    """
    DOUBLE = 8
    """
    64-bit, double-precision floating-point number datatype.
    """
    INT_16 = 9
    """
    A 16-bit signed integer.
    """
    INT_32 = 10
    """
    A 32-bit signed integer.
    """
    INT_64 = 11
    """
    A 64-bit signed integer.
    """
    INTERVAL_DS = 12
    """
    Interval Day to Second literal.
    """
    INTERVAL_YM = 13
    """
    Interval Year to Month Literal.
    """
    LONG = 14
    """
    Long can store variable-length character data containing up to 2 gigabytes of information.
    Long data is text data that is to be appropriately converted when moving among different systems.
    """
    LONG_RAW = 15
    """
    The LONG RAW data types is used for data that is not to be interpreted (not converted when moving data between different systems) by Oracle Database.
    These data types are intended for binary data or byte strings.
    """
    N_CHAR = 16
    """
    The maximum length of an NCHAR column is 2000 bytes.
    It can hold up to 2000 characters.
    The actual data is subject to the maximum byte limit of 2000.
    The two size constraints must be satisfied simultaneously at run time.
    """
    N_CLOB = 17
    """
    The N_CLOB data types store up to 128 terabytes of character data in the database.
    N_CLOBs store Unicode national character set data.
    """
    N_VARCHAR_2 = 18
    """
    The maximum length of an NVARCHAR2 column is 4000 bytes.
    It can hold up to 4000 characters.
    The actual data is subject to the maximum byte limit of 4000.
    The two size constraints must be satisfied simultaneously at run time.
    """
    RAW = 19
    """
    The Raw data type is used for data that is not to be interpreted (not converted when moving data between different systems) by Oracle Database.
    These data types are intended for binary data or byte strings.
    """
    REF_CURSOR = 20
    """
    A REF CURSOR is a PL/SQL data type whose value is the memory address of a query work area on the database.
    """
    SINGLE = 21
    """
    Single byte character sets.
    """
    TIME_STAMP = 22
    """
    Get the system date and time returned in a Timestamp datatype.
    """
    TIME_STAMP_LTZ = 23
    """
    Timestamp WITH LOCAL TIME ZONE is stored in the database time zone.
    When a user selects the data, the value is adjusted to the user's session time zone.
    """
    TIME_STAMP_TZ = 24
    """
    Get the system date and time according to the timezone returned in a Timestamp datatype.
    """
    VARCHAR_2 = 25
    """
    The VARCHAR2 datatype stores variable-length character strings.
    Maximum string length (in bytes or characters) is between 1 and 4000 bytes for the VARCHAR2 column.
    """
    XML_TYPE = 26
    """
    XMLType can be used like any other user-defined type.
    """
