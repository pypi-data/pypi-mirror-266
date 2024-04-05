from pyserilog.core.string_writable import StringWriteable
from typing import Callable

from pyserilog.events.log_event_property_value import LogEventPropertyValue


class ScalarValue(LogEventPropertyValue):
    def __init__(self, value):
        self._value = value

    @staticmethod
    def Null():
        return ScalarValue(None)

    @property
    def value(self):
        return self._value

    def render(self, output: StringWriteable, text_format: str | None = None,
               formatter: Callable[[object, str | None], str] = None):
        self.render_value(self.value, output, text_format, formatter)

    @staticmethod
    def render_value(value, writer: StringWriteable, text_format: str | None = None,
                     formatter: Callable[[object, str | None], str] = None):
        if value is None:
            writer.write("null")
        elif isinstance(value, str):
            writer.write(f'"{value}"')
        else:
            if text_format is not None:
                try:
                    format_res = format(value, text_format) if formatter is None else formatter(value, text_format)
                    writer.write(format_res)
                except Exception as ex:
                    print(ex)
            else:
                writer.write(f"{value}")

    @staticmethod
    def Null():
        return ScalarValue(None)

    def __eq__(self, other):
        if not isinstance(other, ScalarValue):
            return False
        return other._value == self.value
