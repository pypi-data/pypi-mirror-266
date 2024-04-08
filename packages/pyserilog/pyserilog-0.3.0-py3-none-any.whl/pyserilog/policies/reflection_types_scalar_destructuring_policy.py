from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.core.ilog_event_property_value_factory import ILogEventPropertyValueFactory
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue


class ReflectionTypesScalarDestructuringPolicy(IDestructuringPolicy):
    def try_destructure(self, value, property_value_factory: ILogEventPropertyValueFactory) \
            -> tuple[bool, LogEventPropertyValue | None]:
        if not isinstance(value, type):
            return False, None
        return True, ScalarValue(value)
