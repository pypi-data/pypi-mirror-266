from typing import Callable

from pyserilog.core.constants import Constants
from pyserilog.debuging import SelfLog
from pyserilog.events.log_event import LogEvent
from pyserilog.events.scalar_value import ScalarValue
import pyserilog.utils as utils


class Matching:

    @staticmethod
    def from_source(source: type | str):
        if isinstance(source, type):
            return Matching.with_property(Constants.SOURCE_CONTEXT_PROPERTY_NAME, utils.full_name(source))

        def func(s: str):
            return s is not None and s.startswith(source) and (len(s) == len(source) or s[len(source)] == '.')

        return Matching.with_property(Constants.SOURCE_CONTEXT_PROPERTY_NAME, func)

    @staticmethod
    def with_property(property_name: str, value=None) -> Callable[[LogEvent], bool]:
        def func(x: LogEvent):
            return property_name in x.properties

        if value is None:
            return func

        if isinstance(value, Callable) or isinstance(value, type(lambda: 0)):
            def func_callable(x: LogEvent):
                if property_name not in x.properties:
                    return False
                val = x.properties[property_name]
                if isinstance(val, ScalarValue):
                    try:
                        res = value(val.value)
                        return res
                    except TypeError as ex:
                        return False
                return False

            return func_callable

        def func2(x: LogEvent):
            scalar = ScalarValue(value)
            return property_name in x.properties and scalar == x.properties[property_name]

        return func2
