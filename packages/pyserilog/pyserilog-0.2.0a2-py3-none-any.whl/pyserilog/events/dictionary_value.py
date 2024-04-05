from pyserilog.core.string_writable import StringWriteable
from typing import Callable

from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue


class DictionaryValue(LogEventPropertyValue):
    def __init__(self, elements: list[tuple[ScalarValue, LogEventPropertyValue]]):
        self._elements = elements

    @property
    def elements(self) -> list[tuple[ScalarValue, LogEventPropertyValue]]:
        return self._elements

    def render(self, output: StringWriteable, text_format: str | None = None, formatter: Callable[[object], str] = None):
        output.write('[')
        delim: str = '('
        for kvp in self._elements:
            output.write(delim)
            delim = ', ('
            key: ScalarValue = kvp[0]
            key.render(output)
            value: LogEventPropertyValue = kvp[1]
            output.write(": ")
            value.render(output)
            output.write(")")

        output.write(']')
