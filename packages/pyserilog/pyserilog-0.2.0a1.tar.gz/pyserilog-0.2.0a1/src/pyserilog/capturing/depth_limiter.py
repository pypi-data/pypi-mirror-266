import threading

from pyserilog.capturing.iproperty_value_converter import IPropertyValueConverter
from pyserilog.core.ilog_event_property_value_factory import ILogEventPropertyValueFactory
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.parsing.destructuring import Destructuring


class DepthLimiter(ILogEventPropertyValueFactory):
    local = threading.local()

    def __init__(self, maximum_depth: int, property_value_converter: IPropertyValueConverter):
        self._maximum_depth = maximum_depth
        self._property_value_converter = property_value_converter

    @property
    def current_dept(self):
        return self.local.current_depth

    @staticmethod
    def set_current_depth(depth: int):
        loc = DepthLimiter.local
        loc.current_depth = depth

    def create_property_value(self, value, destructure_objects: bool = False) -> LogEventPropertyValue:
        stored_depth = self.current_dept

        created = self.__default_if_maximum_depth(stored_depth)
        if created is None:
            created = self._property_value_converter.create_property_value_check_destructuring_and_depth \
                (value, destructure_objects, stored_depth + 1)
        self.set_current_depth(stored_depth)
        return created

    # TODO refactor merge to object
    def create_property_value_with_destructure(self, value, destructuring: Destructuring) -> LogEventPropertyValue:
        stored_depth = self.current_dept

        created = self.__default_if_maximum_depth(stored_depth)
        if created is None:
            created = self._property_value_converter.create_property_value_with_destructuring_and_depth \
                (value, destructuring, stored_depth + 1)
        self.set_current_depth(stored_depth)
        return created

    def __default_if_maximum_depth(self, depth: int) -> ScalarValue:
        if depth == self._maximum_depth:
            SelfLog.write_line("Maximum destructuring depth reached.")
            return ScalarValue.Null()
        return None
