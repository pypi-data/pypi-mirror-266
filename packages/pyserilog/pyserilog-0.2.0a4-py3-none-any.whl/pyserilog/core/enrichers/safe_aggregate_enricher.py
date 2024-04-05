from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event import LogEvent


class SafeAggregateEnricher(ILogEventEnricher):
    def __init__(self, enrichers: list[ILogEventEnricher]):
        self._enrichers = enrichers

    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        for enricher in self._enrichers:
            try:
                enricher.enrich(log_event, property_factory)
            except Exception as ex:
                SelfLog.write_line("Exception {0} caught while enriching {1} with {2}.", ex, log_event, enricher)
