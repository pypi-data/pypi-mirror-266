from typing import Callable

from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.events.log_event import LogEvent


class DisposeDelegatingSink(ILogEventSink):
    def __init__(self, sink: ILogEventSink, exitable_func):
        self._sink = sink
        self._exitable = exitable_func

    def emit(self, log_event: LogEvent):
        self._sink.emit(log_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._exitable is not None and hasattr(self._exitable , "__exit__"):
            self._exitable.__exit__(exc_type, exc_val, exc_tb)
