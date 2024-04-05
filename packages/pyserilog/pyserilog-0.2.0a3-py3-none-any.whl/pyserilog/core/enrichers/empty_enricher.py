from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.events.log_event import LogEvent


class EmptyEnricher(ILogEventEnricher):
    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        return
