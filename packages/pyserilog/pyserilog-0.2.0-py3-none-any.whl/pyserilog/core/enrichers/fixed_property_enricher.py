from pyserilog.guard import Guard
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.events.log_event import LogEvent
from pyserilog.events.event_property import EventProperty


class FixedPropertyEnricher(ILogEventEnricher):
    def __init__(self, event_property: EventProperty):
        self._event_property = event_property

    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        Guard.against_null(log_event)

        log_event.add_property_if_absent(self._event_property)
