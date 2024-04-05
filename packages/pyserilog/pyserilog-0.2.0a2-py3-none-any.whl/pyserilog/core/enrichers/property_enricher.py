from pyserilog import Guard
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.events import property_utils
from pyserilog.events.log_event import LogEvent


class PropertyEnricher(ILogEventEnricher):
    def __init__(self, name: str, value, destructure_objects: bool = False):
        property_utils.ensure_valid_name(name)

        self._name = name
        self._value = value
        self._destructure_objects = destructure_objects

    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        Guard.against_null(log_event)
        Guard.against_null(property_factory)

        property_value = property_factory.create_property(self._name, self._value, self._destructure_objects)
        log_event.add_property_if_absent(property_value)
