from datetime import datetime

from ncache.util.ExceptionHandler import ExceptionHandler
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class TimeSpan:
    """
    Represents a time interval.
    """

    def __init__(self, ticks=None, hours=None, minutes=None, seconds=None, days=None, milliseconds=None):
        """
        Initialize an instance of TimeSpan Object

        :param hours: number of hours
        :type hours: int
        :param minutes: number of minutes
        :type minutes: int
        :param seconds: number of seconds
        :type seconds: int
        :param days: number of days
        :type days: int
        :param milliseconds: number of milliseconds
        :type milliseconds: int
        :param ticks: number of ticks
        :type ticks: int
        """
        if ticks is None and days is None and hours is None and minutes is None and seconds is None and milliseconds is None:
            self.__timespan = JavaInstancesFactory.get_java_instance("TimeSpan")()
            return
        elif (hours is not None) and (minutes is not None) and (seconds is not None):
            ValidateType.is_int(hours)
            ValidateType.is_int(minutes)
            ValidateType.is_int(seconds)

            javahours = TypeCaster.to_java_primitive_type(hours)
            javaminutes = TypeCaster.to_java_primitive_type(minutes)
            javaseconds = TypeCaster.to_java_primitive_type(seconds)
            if days is not None:
                ValidateType.is_int(days)
                javadays = TypeCaster.to_java_primitive_type(days)
                if milliseconds is not None:
                    ValidateType.is_int(milliseconds)
                    javamilliseconds = TypeCaster.to_java_primitive_type(milliseconds)
                    self.__timespan = JavaInstancesFactory.get_java_instance("TimeSpan")(javadays, javahours, javaminutes, javaseconds, javamilliseconds)
                    return

                self.__timespan = JavaInstancesFactory.get_java_instance("TimeSpan")(javadays, javahours, javaminutes, javaseconds)
                return

            self.__timespan = JavaInstancesFactory.get_java_instance("TimeSpan")(javahours, javaminutes, javaseconds)
            return
        elif ticks is not None and days is None and hours is None and minutes is None and seconds is None and milliseconds is None:
            ValidateType.is_int(ticks)
            self.__timespan = JavaInstancesFactory.get_java_instance("TimeSpan")(TypeCaster.to_java_long(ticks))
            return
        else:
            raise ValueError(ExceptionHandler.exceptionmessages.get("TimeSpan.__init__"))

    def set_instance(self, value):
        self.__timespan = value

    def get_instance(self):
        return self.__timespan

    def add(self, timespan):
        """
        Returns a new TimeSpan object whose value is the sum of the specified TimeSpan object and this instance.

        :param timespan: The time interval to add.
        :type timespan: TimeSpan
        :return: A new object that represents the value of this instance plus the value of timespan.
        :rtype: TimeSpan
        """
        ValidateType.type_check(timespan, TimeSpan, self.add)
        result = self.__timespan.Add(timespan.get_instance())
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan
        return result

    @staticmethod
    def compare(timespan1, timespan2):
        """
        Compares two TimeSpan values, returning an integer that indicates their relationship.

        :param timespan1: First TimeSpan object to be compared
        :type timespan1: TimeSpan
        :param timespan2: Second TimeSpan object to be compared
        :type timespan2: TimeSpan
        :return: A negative integer, zero, or a positive integer as this object is less than, equal to, or greater than
            the specified object.
        :rtype: int
        """
        ValidateType.type_check(timespan1, TimeSpan, TimeSpan.compare)
        ValidateType.type_check(timespan2, TimeSpan, TimeSpan.compare)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").Compare(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def compare_to(self, timespan):
        """
        Compares this object with the specified object. Returns a negative integer, zero, or a positive integer as this
        object is less than, equal to, or greater than the specified object.

        :param timespan: The object to be compared with this object.
        :type timespan: TimeSpan
        :return: A negative integer, zero, or a positive integer as this object is less than, equal to, or greater than
            the specified object.
        :rtype: int
        """
        ValidateType.type_check(timespan, TimeSpan, self.compare_to)

        result = self.__timespan.CompareTo(timespan.get_instance())
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def duration(self):
        """
        Returns a new TimeSpan object whose value is the absolute value of the current TimeSpan object.

        :return: A new object whose value is the absolute value of the current TimeSpan object.
        :rtype: TimeSpan
        """
        result = self.__timespan.Duration()
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan
        return result

    @staticmethod
    def to_equals(timespan1, timespan2):
        """
        Returns a value indicating whether two instances of TimeSpan are equal.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the values of t1 and t2 are equal; otherwise, false.
        """
        ValidateType.type_check(timespan1, TimeSpan, TimeSpan.to_equals)
        ValidateType.type_check(timespan2, TimeSpan, TimeSpan.to_equals)

        return bool(JavaInstancesFactory.get_java_instance("TimeSpan").equals(timespan1.get_instance(), timespan2.get_instance()))

    def equals(self, timespan):
        """
        Returns a value indicating whether this instance is equal to a specified TimeSpan object.

        :param timespan: An object to compare with this instance.
        :type timespan: TimeSpan
        :return: true if obj represents the same time interval as this instance; otherwise, false.
        :rtype: bool
        """
        ValidateType.type_check(timespan, TimeSpan, self.equals)

        return bool(self.__timespan.equals(timespan.get_instance()))

    @staticmethod
    def from_days(value):
        """
        Returns a TimeSpan that represents a specified number of days, where the specification is accurate to the
        nearest millisecond.

        :param value: A number of days, accurate to the nearest millisecond.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_days)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromDays(TypeCaster.to_java_double(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def from_hours(value):
        """
        Returns a TimeSpan that represents a specified number of hours, where the specification is accurate to the
        nearest millisecond.

        :param value: A number of hours accurate to the nearest millisecond.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_hours)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromHours(TypeCaster.to_java_double(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def from_milliseconds(value):
        """
        Returns a TimeSpan that represents a specified number of milliseconds.

        :param value: A number of milliseconds.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_milliseconds)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromMilliseconds(TypeCaster.to_java_double(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def from_minutes(value):
        """
        Returns a TimeSpan that represents a specified number of minutes, where the specification is accurate to the
        nearest millisecond.

        :param value: A number of minutes, accurate to the nearest millisecond.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_minutes)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromMinutes(TypeCaster.to_java_double(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def from_seconds(value):
        """
        Returns a TimeSpan that represents a specified number of seconds, where the specification is accurate to the
        nearest millisecond.

        :param value: A number of seconds, accurate to the nearest millisecond.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_seconds)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromSeconds(TypeCaster.to_java_double(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def from_ticks(value):
        """
        Returns a TimeSpan that represents a specified time, where the specification is in units of ticks.

        :param value: A number of ticks that represent a time.
        :type value: int
        :return: An object that represents value.
        :rtype: TimeSpan
        """
        ValidateType.is_int(value, TimeSpan.from_ticks)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").FromTicks(TypeCaster.to_java_long(value))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    def get_days(self):
        """
        Gets the days component of the time interval represented by the current TimeSpan class.

        :return: The day component of this instance. The return value can be positive or negative.
        :rtype: int
        """
        result = self.__timespan.getDays()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_hours(self):
        """
        Gets the hours component of the time interval represented by the current TimeSpan class.

        :return: The hour component of the current TimeSpan class. The return value ranges from -23 through 23.
        :rtype: int
        """
        result = self.__timespan.getHours()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_milliseconds(self):
        """
        Gets the milliseconds component of the time interval represented by the current TimeSpan class.

        :return: The millisecond component of the current TimeSpan class. The return value ranges from -999 through 999.
        :rtype: int
        """
        result = self.__timespan.getMilliseconds()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_minutes(self):
        """
        Gets the minutes component of the time interval represented by the current TimeSpan class.

        :return: The minute component of the current TimeSpan class. The return value ranges from -59 through 59.
        :rtype: int
        """
        result = self.__timespan.getMinutes()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_seconds(self):
        """
        Gets the seconds component of the time interval represented by the current TimeSpan class.

        :return: The second component of the current TimeSpan class. The return value ranges from -59 through 59.
        :rtype: int
        """
        result = self.__timespan.getSeconds()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_days(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional days.

        :return: The total number of days represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalDays()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_hours(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional hours.

        :return: The total number of hours represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalHours()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_milliseconds(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional milliseconds.

        :return: The total number of milliseconds represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalMilliseconds()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_minutes(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional minutes.

        :return: The total number of minutes represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalMinutes()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_seconds(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional seconds.

        :return: The total number of seconds represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalSeconds()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def get_total_ticks(self):
        """
        Gets the value of the current TimeSpan class expressed in whole and fractional milliseconds.

        :return: The total number of ticks represented by this instance.
        :rtype: int
        """
        result = self.__timespan.getTotalTicks()
        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    def __hash__(self):
        return TypeCaster.to_python_primitive_type(self.__timespan.hashCode())

    def negate(self):
        """
        Returns a new TimeSpan object whose value is the negated value of this instance.

        :return: A new object with the same numeric value as this instance, but with the opposite sign.
        :rtype: TimeSpan
        """
        result = self.__timespan.Negate()
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def op_addition(timespan1, timespan2):
        """
        Adds two specified TimeSpan instances.

        :param timespan1: The first time interval to add.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to add.
        :type timespan2: TimeSpan
        :return: An object whose value is the sum of the values of timespan1 and timespan2.
        :rtype: TimeSpan
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpAddition(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def op_equality(timespan1, timespan2):
        """
        Indicates whether two TimeSpan instances are equal.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the values of t1 and t2 are equal; otherwise, false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpEquality(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_greater_than(timespan1, timespan2):
        """
        Indicates whether a specified TimeSpan is greater than another specified TimeSpan.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the value of t1 is greater than the value of t2; otherwise, false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpGreaterThan(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_greater_than_or_equal(timespan1, timespan2):
        """
        Indicates whether a specified TimeSpan is greater than or equal to another specified TimeSpan.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the value of t1 is greater than or equal to the value of t2; otherwise,false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpGreaterThanOrEqual(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_inequality(timespan1, timespan2):
        """
        Indicates whether two TimeSpan instances are not equal.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the values of t1 and t2 are not equal; otherwise, false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpInequality(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_less_than(timespan1, timespan2):
        """
        Indicates whether a specified TimeSpan is less than another specified TimeSpan.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the value of t1 is less than the value of t2; otherwise, false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpLessThan(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_less_than_or_equal(timespan1, timespan2):
        """
        Indicates whether a specified TimeSpan is less than or equal to another specified TimeSpan.

        :param timespan1: The first time interval to compare.
        :type timespan1: TimeSpan
        :param timespan2: The second time interval to compare.
        :type timespan2: TimeSpan
        :return: true if the value of t1 is less than or equal to the value of t2; otherwise, false.
        :rtype: bool
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpLessThanOrEqual(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            result = bool(result)

        return result

    @staticmethod
    def op_subtraction(timespan1, timespan2):
        """
        Subtracts a specified TimeSpan from another specified TimeSpan.

        :param timespan1: The minuend.
        :type timespan1: TimeSpan
        :param timespan2: The subtrahend.
        :type timespan2: TimeSpan
        :return: An object whose value is the result of the value of t1 minus the value of t2.
        :rtype: TimeSpan
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpSubtraction(timespan1.get_instance(), timespan2.get_instance())
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def op_unary_negation(timespan):
        """
        Returns a TimeSpan whose value is the negated value of the specified instance.

        :param timespan: The time interval to be negated.
        :type timespan: TimeSpan
        :return: An object that has the same numeric value as this instance, but the opposite sign.
        :rtype: TimeSpan
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpUnaryNegation(timespan.get_instance())

        if result is not None:
            pythontimespan = TimeSpan()
            pythontimespan.set_instance(result)
            return pythontimespan

        return result

    @staticmethod
    def op_unary_plus(timespan):
        """
        Returns the specified instance of TimeSpan.

        :param timespan: The time interval to return.
        :type timespan: TimeSpan
        :return: The time interval specified by t.
        :rtype: TimeSpan
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").OpUnaryPlus(timespan.get_instance())
        if result is not None:
            pythontimespan = TimeSpan()
            pythontimespan.set_instance(result)
            return pythontimespan

        return result

    @staticmethod
    def subtract(fromtime, totime):
        """
        Gets the difference between two dates in the form of a Timespan.

        :param fromtime: The first date value to compare.
        :type fromtime: datetime
        :param totime: The second date value to compare.
        :type totime: datetime
        :return: The timespan instance indicating the difference between the dates.
        :rtype: TimeSpan
        """
        result = JavaInstancesFactory.get_java_instance("TimeSpan").subtract(TypeCaster.to_java_date(fromtime), TypeCaster.to_java_date(totime))
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def time_to_ticks(hour, minute, second):
        """
        Converts the specified hour,minutes and seconds to equivalent ticks.

        :param hour: Number of hours.
        :type hour: int
        :param minute: Number of minutes.
        :type minute: int
        :param second: Number of seconds.
        :type second: int
        :return: The number of ticks equivalent to the specified time.
        :rtype: int
        """
        ValidateType.is_int(hour, TimeSpan.time_to_ticks)
        ValidateType.is_int(minute, TimeSpan.time_to_ticks)
        ValidateType.is_int(second, TimeSpan.time_to_ticks)

        javahour = TypeCaster.to_java_primitive_type(hour)
        javaminute = TypeCaster.to_java_primitive_type(minute)
        javasecond = TypeCaster.to_java_primitive_type(second)

        result = JavaInstancesFactory.get_java_instance("TimeSpan").TimeToTicks(javahour, javaminute, javasecond)

        if result is not None:
            result = TypeCaster.to_python_primitive_type(result)
        return result

    @staticmethod
    def time_span_zero():
        result = JavaInstancesFactory.get_java_instance("TimeSpan").Zero
        if result is not None:
            timespan = TimeSpan(0)
            timespan.set_instance(result)
            result = timespan

        return result

    @staticmethod
    def time_span_min_value():
        result = JavaInstancesFactory.get_java_instance("TimeSpan").MinValue
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result

    @staticmethod
    def time_span_max_value():
        result = JavaInstancesFactory.get_java_instance("TimeSpan").MaxValue
        if result is not None:
            timespan = TimeSpan()
            timespan.set_instance(result)
            return timespan

        return result


class TimeSpanUtil:
    zero_time_span = TimeSpan.time_span_zero()
    min_value_time_span = TimeSpan.time_span_min_value()
    max_value_time_span = TimeSpan.time_span_max_value()
