from abc import ABC, abstractmethod

from pyserilog.events.log_event_property_value import LogEventPropertyValue


class ILogEventPropertyValueFactory(ABC):

    @abstractmethod
    def create_property_value(self, value, destructure_objects: bool = False) -> LogEventPropertyValue:
        pass
