from abc import ABC, abstractmethod

from pyserilog.events.log_event import LogEvent


class ILogEventFilter(ABC):
    """
    Provides filtering of the log event stream.
    """

    @abstractmethod
    def is_enable(self, log_event: LogEvent) -> bool:
        """
        Returns true if the provided event is enabled. Otherwise
        :param log_event: The event to test.
        :return: True if the event is enabled by this filter. If False is returned, the event will not be emitted.
        """
        pass
