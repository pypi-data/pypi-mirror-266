from abc import abstractmethod
from typing import overload

from pyserilog.ilogger import ILogger
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.message_template import MessageTemplate


class SilentLogger(ILogger):

    def for_context(self, property_name: str, value: str, destructure_objects: bool = False):
        raise NotImplementedError

    def for_context(self, enricher: ILogEventEnricher):
        raise NotImplementedError

    def for_context(self, klass_type: type):
        raise NotImplementedError

    def write_event(self, log_event: LogEvent):
        pass

    def bind_message_template(self, message_template: str, property_values: list[object] | None) -> \
            tuple[bool, MessageTemplate, list[LogEventProperty]]:
        return False, None, None

    def _for_enricher_context(self, enricher: ILogEventEnricher):
        return self

    def _for_property_name_context(self, property_name: str, value, destructure_objects: bool = False):
        return self

    def _for_class_type_context(self, class_type: type):
        return self

    def bind_property(self, property_name: str, value, destructure_objects) -> tuple[bool, LogEventProperty | None]:
        return False, None

    def is_enable(self, level: LogEventLevel) -> bool:
        return False

    def write(self, level: LogEventLevel, message_template: str, property_values: list | None = None,
              exception: Exception | None = None):
        super().write(level, message_template, property_values, exception)

    def write_with_level(self, level: LogEventLevel, message_template: str, *property_value):
        pass

    def debug(self, message_template: str, *property_value):
        pass

    def information(self, message_template: str, *property_value):
        pass

    def warning(self, message_template: str, *property_value):
        pass

    def error(self, message_template: str, *property_value):
        pass

    def fatal(self, message_template: str, *property_value):
        pass
