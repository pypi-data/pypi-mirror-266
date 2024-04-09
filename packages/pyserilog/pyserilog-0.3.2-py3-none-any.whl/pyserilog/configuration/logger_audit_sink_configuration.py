from typing import Callable

from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.level_alias import LevelAlias


class LoggerAuditSinkConfiguration:

    def __init__(self, logger_configuration, add_sink_function):
        self._sink_configuration: LoggerSinkConfiguration = \
            LoggerSinkConfiguration(logger_configuration, add_sink_function)

    def sink(self, log_event_sink: ILogEventSink, restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
             level_switch: LoggingLevelSwitch | None = None):
        return self._sink_configuration.sink(log_event_sink, restricted_to_minimum_level, level_switch)

    def logger(self, configure_logger_function: Callable,
               restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
               level_switch: LoggingLevelSwitch | None = None
               ):
        return self._sink_configuration.logger(configure_logger_function, restricted_to_minimum_level, level_switch)
