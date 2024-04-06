from pyserilog.core.string_writable import StringWriteable
from typing import Callable

from pyserilog.guard import Guard
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.log_event_property_value import LogEventPropertyValue


class StructureValue(LogEventPropertyValue):

    def __init__(self, properties: list[LogEventProperty], type_tag: str | None = None):
        Guard.against_null(properties)

        self._properties = properties
        self._type_tag = type_tag

    @property
    def properties(self) -> list[LogEventProperty]:
        return self._properties

    @property
    def type_tag(self) -> str | None:
        return self._type_tag

    def render(self, output: StringWriteable, text_format: str | None = None, formatter: Callable[[object], str] = None):
        if self.type_tag is not None:
            output.write(str(self.type_tag))
            output.write(" ")
        output.write("{ ")
        for prop in self._properties[:-1]:
            self._render(prop, output)
            output.write(", ")
        if len(self.properties) > 0:
            last = self.properties[-1]

            self._render(last, output)
        output.write(" }")

    @staticmethod
    def _render(prop: LogEventProperty, output: StringWriteable, text_format: str | None = None,
                formatter: Callable[[object], str] = None):
        output.write(prop.name)
        output.write(": ")
        prop.value.render(output, text_format, formatter)
