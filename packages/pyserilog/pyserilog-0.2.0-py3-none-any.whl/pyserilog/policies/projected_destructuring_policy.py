from typing import Callable

from pyserilog.guard import Guard
from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.core.ilog_event_property_value_factory import ILogEventPropertyValueFactory
from pyserilog.events.log_event_property_value import LogEventPropertyValue


class ProjectedDestructuringPolicy(IDestructuringPolicy):
    def __init__(self, can_apply_func: Callable[[type], bool], projection_func: Callable[[object], object]):
        self._can_apply_func: Callable[[type], bool] = Guard.against_null(can_apply_func)
        self._projection_func: Callable[[object], object] = Guard.against_null(projection_func)

    def try_destructure(self, value, property_value_factory: ILogEventPropertyValueFactory) -> \
            tuple[bool, LogEventPropertyValue | None]:
        Guard.against_null(value)

        if not self._can_apply_func(type(value)):
            return False, None
        projected = self._projection_func(value)
        result = property_value_factory.create_property_value(value=projected, destructure_objects=True)
        return True, result
