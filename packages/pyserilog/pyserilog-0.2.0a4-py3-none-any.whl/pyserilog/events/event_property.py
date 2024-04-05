from pyserilog.guard import Guard
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.property_utils import ensure_valid_name


class EventProperty:
    def __init__(self, name: str, value: LogEventPropertyValue):
        Guard.against_null(name)
        ensure_valid_name(name)

        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> LogEventPropertyValue:
        return self._value

    def __eq__(self, other):
        if not isinstance(other, EventProperty):
            return False

        return self.name == other.name and self.value == other.value


