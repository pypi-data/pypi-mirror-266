import inspect

from ncache.util.ExceptionHandler import ExceptionHandler


class ValidateType:
    @staticmethod
    def is_key_value_valid(key, value, function=None):
        ValidateType.is_string(key, function)
        ValidateType.is_none(value, function)

    @staticmethod
    def is_string(value, function=None):
        ValidateType.type_check(value, str, function)

    @staticmethod
    def is_none(value, function=None):
        if value is None:
            raise TypeError(ExceptionHandler.get_none_value_exception_message(function))

    @staticmethod
    def is_int(value, function=None):
        ValidateType.type_check(value, int, function)

    @staticmethod
    def type_check(value, validtype, function=None):
        if type(value) is not validtype:
            raise TypeError(ExceptionHandler.get_invalid_type_exception_message(function, validtype, value))

    @staticmethod
    def params_check(callablefunction, validparamscount, function=None):
        paramscount = len(inspect.signature(callablefunction).parameters)

        if paramscount != validparamscount:
            raise AttributeError(ExceptionHandler.get_invalid_params_exception_message(callablefunction, validparamscount, paramscount, function))

    @staticmethod
    def validate_instance(value, instance, function=None):
        if not isinstance(value, instance):
            raise TypeError(ExceptionHandler.get_invalid_instance_exception_message(instance, function))
