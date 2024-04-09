from pyserilog import  Guard
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.events.log_event import LogEvent
from pyserilog.ilogger import ILogger


class SecondaryLoggerSink(ILogEventSink):
    def __init__(self, logger: ILogger, attempt_dispose: bool = False):
        self._logger: ILogger = Guard.against_null(logger)
        self._attempt_dispose: bool = attempt_dispose

    def emit(self, log_event: LogEvent):
        Guard.against_null(log_event)

        copy = log_event.copy()
        self._logger.write_event(copy)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._attempt_dispose:
            return

        if hasattr(self._logger, "__exit__"):
            self._logger.__exit__(exc_type, exc_val, exc_tb)
