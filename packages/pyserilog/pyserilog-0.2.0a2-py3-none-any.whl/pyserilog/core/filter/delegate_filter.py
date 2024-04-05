from typing import Callable

from pyserilog.core.ilog_event_filter import ILogEventFilter
from pyserilog.events.log_event import LogEvent


class DelegateFilter(ILogEventFilter):
    def __init__(self, is_enable_func: Callable[[LogEvent], bool]):
        self._is_enable_func = is_enable_func

    def is_enable(self, log_event: LogEvent) -> bool:
        return self._is_enable_func(log_event)
