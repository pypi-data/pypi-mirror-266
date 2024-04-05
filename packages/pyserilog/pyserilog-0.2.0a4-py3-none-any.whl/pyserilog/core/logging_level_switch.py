from pyserilog.events.log_event_level import LogEventLevel


class LoggingLevelSwitch:

    def __init__(self, initial_minimum_level: LogEventLevel = LogEventLevel.INFORMATION):
        self._minimum_level = initial_minimum_level

    @property
    def minimum_level(self) -> LogEventLevel:
        return self._minimum_level

    @minimum_level.setter
    def minimum_level(self, value: LogEventLevel):
        self._minimum_level = value

    def __str__(self):
        return str(self._minimum_level)