from typing import Callable

from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.events.log_event import LogEvent


class ConditionalSink(ILogEventSink):
    def __init__(self, wrapper: ILogEventSink, condition: Callable[[LogEvent], bool]):
        self._wrapper = wrapper
        self._condition = condition

    def emit(self, log_event: LogEvent):
        if self._condition(log_event):
            self._wrapper.emit(log_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._wrapper, "__exit__"):
            self._wrapper.__exit__(exc_type, exc_val, exc_tb)
