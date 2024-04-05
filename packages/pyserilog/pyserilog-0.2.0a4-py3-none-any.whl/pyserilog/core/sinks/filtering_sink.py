from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.ilog_event_filter import ILogEventFilter
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event import LogEvent


class FilteringSink(ILogEventSink):
    def __init__(self, sink: ILogEventSink, filters: list[ILogEventFilter], propagate_exceptions: bool):
        self._sink = sink
        self._filters = filters
        self._propagate_exceptions = propagate_exceptions

    def emit(self, log_event: LogEvent):
        try:
            for log_event_filter in self._filters:
                if not log_event_filter.is_enable(log_event):
                    return
            self._sink.emit(log_event)
        except Exception as ex:
            SelfLog.write_line("Caught exception while applying filters: {0}", ex)
            if self._propagate_exceptions:
                raise ex
