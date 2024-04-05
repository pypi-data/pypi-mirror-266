from pyserilog.events.log_event import LogEvent
from pyserilog.guard import Guard
from pyserilog.core import logging_level_switch
from pyserilog.core.ilog_event_sink import ILogEventSink


class RestrictedSink(ILogEventSink):

    def __init__(self, sink: ILogEventSink, level_switch: logging_level_switch):
        self._sink: ILogEventSink = Guard.against_null(sink)
        self._levelSwitch: logging_level_switch = Guard.against_null(level_switch)

    def emit(self, log_event: LogEvent):
        Guard.against_null(log_event)

        if log_event.level < self._levelSwitch.minimum_level:
            return
        self._sink.emit(log_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._sink, "__exit__"):
            self._sink.__exit__(exc_type, exc_val, exc_tb)
