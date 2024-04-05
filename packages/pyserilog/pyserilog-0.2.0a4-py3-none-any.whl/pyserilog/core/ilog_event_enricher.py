from abc import ABC, abstractmethod

from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.events.log_event import LogEvent


class ILogEventEnricher(ABC):

    @abstractmethod
    def enrich(self, log_event: LogEvent, property_factory: ILogEventPropertyFactory):
        pass
