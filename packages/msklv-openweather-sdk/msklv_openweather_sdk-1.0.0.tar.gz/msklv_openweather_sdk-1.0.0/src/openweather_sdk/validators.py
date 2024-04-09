import inspect
from datetime import datetime

from openweather_sdk.exceptions import (
    AttributeValidationException,
    InvalidTimeException,
)


def _validate_selected_attr(value, possible_values):
    caller_function = inspect.currentframe().f_back.f_code
    caller_function_name = caller_function.co_name
    if value not in possible_values:
        raise AttributeValidationException(
            f"{caller_function_name} must be one of {', '.join(possible_values)}"
        )
    return value


def _validate_non_negative_integer_attr(value):
    caller_function = inspect.currentframe().f_back.f_code
    caller_function_name = caller_function.co_name
    if not isinstance(value, int) or value < 1:
        raise AttributeValidationException(
            f"{caller_function_name} must be non-negative integer"
        )
    return value


def _validate_time(start, end):
    if not isinstance(start, int):
        raise InvalidTimeException("The start time should be an integer.")
    if not isinstance(end, int):
        raise InvalidTimeException("The end time should be an integer.")
    if start > end:
        raise InvalidTimeException("The end time must be after start time.")
    cur_time = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
    if start < 1606435200 or start > cur_time:
        raise InvalidTimeException(
            "The start time should be greater than or equal to 1606435200 (00:00 27 Nov 2020) and less than or equal to the current time."
        )
    if end > cur_time:
        raise InvalidTimeException(
            "The end time should be less than or equal to the current time."
        )
    return start, end
