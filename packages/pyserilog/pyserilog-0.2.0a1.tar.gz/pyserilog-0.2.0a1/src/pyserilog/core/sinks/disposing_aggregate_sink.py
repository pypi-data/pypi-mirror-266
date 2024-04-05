from builtins import ExceptionGroup

from pyserilog import Guard
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.debuging import SelfLog
from pyserilog.events.log_event import LogEvent


class DisposingAggregateSink(ILogEventSink):
    def __init__(self, sinks: list[ILogEventSink]):
        Guard.against_null(sinks)
        self._sinks = sinks

    def emit(self, log_event: LogEvent):
        exceptions = []
        for sink in self._sinks:
            try:
                sink.emit(log_event)
            except Exception as ex:
                SelfLog.write_line("Caught exception while emitting to sink {0}: {1}", sink, ex)
                exceptions.append(ex)

        if len(exceptions) > 0:
            raise ExceptionGroup(exceptions)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for sink in self._sinks:
            try:
                if hasattr(sink, "__exit__"):
                    sink.__exit__(exc_type, exc_val, exc_tb)
            except Exception as ex:
                SelfLog.write_line("Caught exception while disposing sink {0}: {1}", sink, ex)
