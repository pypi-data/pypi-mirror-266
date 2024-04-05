from typing import Callable

from pyserilog.guard import Guard
import pyserilog.logger_configuration as logConf
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.sinks.conditional_sink import ConditionalSink
from pyserilog.core.sinks.dispose_delegating_sink import DisposeDelegatingSink
from pyserilog.core.sinks.disposing_aggregate_sink import DisposingAggregateSink
from pyserilog.core.sinks.secondary_logger_sink import SecondaryLoggerSink
from pyserilog.core.sinks.restricted_sink import RestrictedSink
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.level_alias import LevelAlias


class LoggerSinkConfiguration:

    def __init__(self, logger_configuration, add_sink_action):
        self._logger_configuration = Guard.against_null(logger_configuration)
        self._add_sink_action = Guard.against_null(add_sink_action)

    def sink(self, log_event_sink: ILogEventSink, restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
             level_switch: LoggingLevelSwitch | None = None):
        sink = log_event_sink
        if level_switch is not None:
            if restricted_to_minimum_level != LevelAlias.minimum:
                SelfLog.write_line(
                    "Sink {0} was configured with both a level switch and minimum level '{1}'; " + \
                    "the minimum level will be ignored and the switch level used",
                    sink, restricted_to_minimum_level)

            sink = RestrictedSink(log_event_sink, level_switch)
        elif restricted_to_minimum_level > LevelAlias.minimum:
            sink = RestrictedSink(log_event_sink, LoggingLevelSwitch(restricted_to_minimum_level))

        self._add_sink_action(sink)
        return self._logger_configuration

    def logger(self, configure_logger,
               restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
               level_switch: LoggingLevelSwitch | None = None):
        Guard.against_null(configure_logger)

        from pyserilog.core.logger import Logger
        if isinstance(configure_logger, Logger):
            if configure_logger.has_override_map:
                SelfLog.write_line("Minimum level overrides are not supported on sub-loggers " +
                                   "and may be removed completely in a future version.")
            second_sink = SecondaryLoggerSink(configure_logger, attempt_dispose=False)
            return self.sink(second_sink, restricted_to_minimum_level)
        log_configuration = logConf.LoggerConfiguration().minimum_level.level_is(LevelAlias.minimum)
        configure_logger(log_configuration)

        sub_logger = log_configuration.create_logger()

        if sub_logger.has_override_map:
            SelfLog.write_line(
                "Minimum level overrides are not supported on sub-loggers and may be removed" + \
                " completely in a future version.")

        secondary_sink = SecondaryLoggerSink(sub_logger, attempt_dispose=True)
        return self.sink(secondary_sink, restricted_to_minimum_level, level_switch)

    def conditional(self, condition: Callable[[LogEvent], bool], configure_sink: Callable):
        Guard.against_null(condition)
        Guard.against_null(configure_sink)

        return self.wrap(self, lambda s: ConditionalSink(s, condition), configure_sink, LevelAlias.minimum, None)

    @staticmethod
    def wrap(logger_sink_configuration, wrap_sink: Callable[[ILogEventSink], ILogEventSink],
             configure_wrapped_sink: Callable,
             restricted_to_minimum_level=LevelAlias.minimum, level_switch: LoggingLevelSwitch = None):
        """
        Helper method for wrapping sinks.
        :param logger_sink_configuration: The parent sink configuration.
        :param wrap_sink:
        :param configure_wrapped_sink:
        :param restricted_to_minimum_level: The minimum level for events passed through the sink.
         Ignored when "levelSwitch" is specified.
        :param level_switch: A switch allowing the pass-through minimum level to be changed at runtime. Can be None
        :return: Configuration object allowing method chaining
        """
        Guard.against_null(logger_sink_configuration)
        Guard.against_null(wrap_sink)
        Guard.against_null(configure_wrapped_sink)

        sinks_to_wrap: list[ILogEventSink] = []
        from pyserilog.logger_configuration import LoggerConfiguration
        capturing_configuration = LoggerConfiguration()
        capturing_logger_sink_configuration = LoggerSinkConfiguration(capturing_configuration, sinks_to_wrap.append)

        capturing_configuration._write_to = capturing_logger_sink_configuration

        configure_wrapped_sink(capturing_logger_sink_configuration)

        if len(sinks_to_wrap) == 0:
            return logger_sink_configuration._logger_configuration

        enclosed = sinks_to_wrap[0] if len(sinks_to_wrap) == 1 else DisposingAggregateSink(sinks_to_wrap)

        wrapper = wrap_sink(enclosed)

        if not hasattr(wrapper, "__exit__") and hasattr(enclosed, "__exit__"):
            wrapper = DisposeDelegatingSink(wrapper, enclosed)
        return logger_sink_configuration.sink(wrapper, restricted_to_minimum_level, level_switch)
