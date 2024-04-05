from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.guard import Guard
from pyserilog.events.event_property import EventProperty
from pyserilog.events.property_utils import ensure_valid_name


class LogEventProperty:

    def __init__(self, name: str, value: LogEventPropertyValue):
        Guard.against_null(name)
        ensure_valid_name(name)
        self._name = name
        self._value = value

    @staticmethod
    def create_with_event_property(event_property: EventProperty):
        return LogEventProperty(event_property.name, event_property.value)

    @property
    def value(self) -> LogEventPropertyValue:
        return self._value

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return f"(name = {self.name} , value = {self.value})"

    def __eq__(self, other):
        if isinstance(other, LogEventProperty):
            return self.name == other.name and self.value == other.value
        return False
