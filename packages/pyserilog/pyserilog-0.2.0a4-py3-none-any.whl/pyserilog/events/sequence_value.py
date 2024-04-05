from pyserilog.core.string_writable import StringWriteable
from typing import Callable

from pyserilog.events.log_event_property_value import LogEventPropertyValue


class SequenceValue(LogEventPropertyValue):
    def __init__(self, elements: list[LogEventPropertyValue]):
        self._elements = elements

    @staticmethod
    def empty():
        return SequenceValue([])

    @property
    def elements(self) -> list[LogEventPropertyValue]:
        return self._elements

    def render(self, output: StringWriteable, text_format: str | None = None, formatter: Callable[[object], str] = None):
        output.write("[")
        for elem in self.elements[:-1]:
            elem.render(output)
            output.write(", ")

        if len(self.elements) > 0:
            self._elements[-1].render(output)
        output.write(']')

    def __eq__(self, other):
        if isinstance(other, SequenceValue):
            return other.elements == self.elements
        return False
