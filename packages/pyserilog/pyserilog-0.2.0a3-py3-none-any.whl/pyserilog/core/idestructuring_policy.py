from abc import ABC, abstractmethod

from pyserilog.core.ilog_event_property_value_factory import ILogEventPropertyValueFactory
from pyserilog.events.log_event_property_value import LogEventPropertyValue


class IDestructuringPolicy(ABC):
    @abstractmethod
    def try_destructure(self, value, property_value_factory: ILogEventPropertyValueFactory) \
            -> tuple[bool, LogEventPropertyValue | None]:
        pass
