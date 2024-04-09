from abc import ABC, abstractmethod

from pyserilog.events.log_event import LogEvent


class ILogEventSink(ABC):

    @abstractmethod
    def emit(self, log_event: LogEvent):
        pass
