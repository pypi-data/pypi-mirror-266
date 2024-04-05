from abc import ABC, abstractmethod

from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.parsing.destructuring import Destructuring


class IPropertyValueConverter(ABC):
    @abstractmethod
    def create_property_value_check_destructuring_and_depth(self,
                                                            value, destructure_objects: bool,
                                                            depth: int) -> LogEventPropertyValue:
        pass

    @abstractmethod
    def create_property_value_with_destructuring_and_depth(self, value, destructuring: Destructuring,
                                                           depth: int) -> LogEventPropertyValue:
        pass
