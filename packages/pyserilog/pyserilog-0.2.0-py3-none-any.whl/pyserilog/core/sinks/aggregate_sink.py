from builtins import ExceptionGroup

from pyserilog.guard import Guard
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event import LogEvent


class AggregateSink(ILogEventSink):
    def __init__(self, sinks: list[ILogEventSink]):
        Guard.against_null(sinks)
        self._sinks = sinks

    def emit(self, log_event: LogEvent):
        exceptions: list[Exception] = []

        for sink in self._sinks:
            try:
                sink.emit(log_event)
            except Exception as ex:
                SelfLog.write_line("Caught exception while emitting to sink {0}: {1}", sink, ex)
                exceptions.append(ex)

        if len(exceptions) > 0:
            raise ExceptionGroup("Failed to emit a log event.", exceptions)
