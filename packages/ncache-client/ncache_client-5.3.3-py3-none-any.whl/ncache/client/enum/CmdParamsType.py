from enum import Enum


class CmdParamsType(Enum):
    """
    Describes the type of the parameters passed to the command.
    """
    BIG_INT = 1
    """
    A 64-bit signed integer.
    """
    BINARY = 2
    """
    A fixed-length stream of binary data ranging between 1 and 8,000 bytes.
    """
    BIT = 3
    """
    An unsigned numeric value that can be 0, 1, or None.
    """
    CHAR = 4
    """
    A fixed-length stream of non-Unicode characters ranging between 1 and 8,000 characters.
    """
    DATE_TIME = 5
    """
    Date and time data ranging in value from January 1, 1753 to December 31, 9999 to an accuracy of 3.33 milliseconds.
    """
    DECIMAL = 6
    """
    A fixed precision and scale numeric value between -10 38 -1 and 10 38 -1.
    """
    FLOAT = 7
    """
    A floating point number within the range of -1.79E +308 through 1.79E +308.
    """
    INT = 9
    """
    A 32-bit signed integer.
    """
    MONEY = 10
    """
    A currency value ranging from -2 63 (or -9,223,372,036,854,775,808) to 2 63 -1 (or +9,223,372,036,854,775,807) with 
    an accuracy to a ten-thousandth of a currency unit.
    """
    N_CHAR = 11  # Not supported by SQL Dependency
    """
    A fixed-length stream of Unicode characters ranging between 1 and 4,000 characters.
    """
    N_VAR_CHAR = 13
    """
    A variable-length stream of Unicode characters ranging between 1 and 4,000 characters. Implicit conversion fails if
    the string is greater than 4,000 characters. Explicitly set the object when working with strings longer than 4,000
    characters.
    """
    REAL = 14
    """
    A floating point number within the range of -3.40E +38 through 3.40E +38.
    """
    UNIQUE_IDENTIFIER = 15
    """
    A globally unique identifier  = or GUID).
    """
    SMALL_DATE_TIME = 16
    """
    Date and time data ranging in value from January 1, 1900 to June 6, 2079 to an accuracy of one minute.
    """
    SMALL_INT = 17
    """
    A 16-bit signed integer.
    """
    SMALL_MONEY = 18
    """
    A currency value ranging from -214,748.3648 to +214,748.3647 with an accuracy to a ten-thousandth of a currency unit.
    """
    TIMESTAMP = 20
    """
    Automatically generated binary numbers, which are guaranteed to be unique within a database. timestamp is used
    typically as a mechanism for version-stamping table rows. The storage size is 8 bytes.
    """
    TINY_INT = 21
    """
    An 8-bit unsigned integer.
    """
    VAR_BINARY = 22
    """
    A variable-length stream of binary data ranging between 1 and 8,000 bytes. Implicit conversion fails if the byte
    array is greater than 8,000 bytes. Explicitly set the object when working with byte arrays larger than 8,000 bytes.
    """
    VAR_CHAR = 23
    """
    A variable-length stream of non-Unicode characters ranging between 1 and 8,000 characters.
    """
    VARIANT = 24
    """
    A special data type that can contain numeric, string, binary, or date data as well as the SQL Server values Empty
    and None, which is assumed if no other type is declared.
    """
    XML = 26
    """
    An XML value. Obtain the XML as a string.
    """
    UDT = 30
    """
    A SQL Server user-defined type (UDT).
    """
    STRUCTURED = 31
    """
    A special data type for specifying structured data contained in table-valued parameters.
    """
    DATE = 32
    """
    Date data ranging in value from January 1,1 AD through December 31, 9999 AD.
    """
    TIME = 33
    """
    Time data based on a 24-hour clock. Time value range is 00:00:00 through 23:59:59.9999999 with an accuracy of 100
    nanoseconds.
    """
    DATE_TIME_2 = 34
    """
    Date and time data. Date value range is from January 1,1 AD through December 31, 9999 AD. Time value range is
    00:00:00 through 23:59:59.9999999 with an accuracy of 100 nanoseconds.
    """
    DATE_TIME_OFFSET = 35
    """
    Date and time data with time zone awareness. Date value range is from January 1,1 AD through December 31, 9999 AD.
    Time value range is 00:00:00 through 23:59:59.9999999 with an accuracy of 100 nanoseconds. Time zone value range is
    -14:00 through +14:00.
    """
