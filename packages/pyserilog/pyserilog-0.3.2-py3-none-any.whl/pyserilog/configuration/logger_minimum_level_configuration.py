from typing import Callable

from pyserilog.guard import Guard
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.events.log_event_level import LogEventLevel


class LoggerMinimumLevelConfiguration:

    def __init__(self, logger_configuration, set_minimum_func: Callable[[LogEventLevel], None],
                 set_level_switch_func: Callable[[LoggingLevelSwitch], None],
                 add_override_func: Callable[[str, LoggingLevelSwitch], None]):
        self._logger_configuration = Guard.against_null(logger_configuration)
        self._set_minimum_func: Callable[[LogEventLevel], None] = set_minimum_func
        self._set_level_switch_func: Callable[[LoggingLevelSwitch], None] = set_level_switch_func
        self._add_override_func: Callable[[str, LoggingLevelSwitch], None] = add_override_func

    def level_is(self, minimum_level: LogEventLevel):
        """
        Sets the minimum level at which events will be passed to sinks.
        :param minimum_level: The minimum level to set.
        :return: Configuration object allowing method chaining.
        """
        self._set_minimum_func(minimum_level)
        return self._logger_configuration

    def controlled_by(self, level_switch: LoggingLevelSwitch):
        """
        Sets the minimum level to be dynamically controlled by the provided switch.
        :param level_switch: The switch.
        :return: Configuration object allowing method chaining.
        """
        Guard.against_null(level_switch)

        self._set_level_switch_func(level_switch)
        return self._logger_configuration

    def verbose(self):
        """
        Anything and everything you might want to know about a running block of code.
        :return: Configuration object allowing method chaining.
        """
        return self.level_is(LogEventLevel.VERBOSE)

    def debug(self):
        """
        Internal system events that aren't necessarily observable from the outside.
        :return: Configuration object allowing method chaining.
        """
        return self.level_is(LogEventLevel.DEBUG)

    def information(self):
        """
        The lifeblood of operational intelligence - things happen.
        :return: Configuration object allowing method chaining.
        """
        return self.level_is(LogEventLevel.INFORMATION)

    def warning(self):
        """
        Functionality is unavailable, invariants are broken  or data is lost.
        :return: Configuration object allowing method chaining.
        """
        return self.level_is(LogEventLevel.WARNING)

    def error(self):
        """
        Functionality is unavailable, invariants are broken or data is lost.
        :return: Configuration object allowing method chaining.
        """
        return self.level_is(LogEventLevel.ERROR)

    def fatal(self):
        """
        If you have a pager, it goes off when one of these occurs.
        :return:
        """
        return self.level_is(LogEventLevel.FATAL)

    def override(self, source: str, level_switch: LoggingLevelSwitch | LogEventLevel):
        Guard.against_null(source)
        Guard.against_null(level_switch)

        if not isinstance(level_switch, LoggingLevelSwitch):
            return self.override(source, LoggingLevelSwitch(level_switch))
        trimmed = source.strip()
        if len(trimmed) == 0:
            raise ValueError(f"A source source must be provided.")

        self._add_override_func(trimmed, level_switch)
        return self._logger_configuration
