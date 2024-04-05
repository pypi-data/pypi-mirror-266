from typing import Callable

from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.events.log_event import LogEvent


class ConditionalEnricher(ILogEventEnricher):
    def __init__(self, wrapped: ILogEventEnricher, condition: Callable[[LogEvent], bool]):
        self._wrapped = wrapped
        self._condition = condition

    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        if self._condition(log_event):
            self._wrapped.enrich(log_event, property_factory)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._wrapped, "__exit__"):
            self._wrapped.__exit__(exc_type, exc_val, exc_tb)
