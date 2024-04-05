from pyserilog.events.log_event_level import LogEventLevel


class LevelAlias:
    minimum: LogEventLevel = LogEventLevel.VERBOSE
    maximum: LogEventLevel = LogEventLevel.FATAL

