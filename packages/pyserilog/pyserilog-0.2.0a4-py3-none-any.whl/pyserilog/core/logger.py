from abc import abstractmethod
from typing import Callable, overload

from pyserilog import Guard
from pyserilog.ilogger import ILogger
from pyserilog.capturing.message_template_processor import MessageTemplateProcessor
from pyserilog.core.constants import Constants
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.level_override_map import LevelOverrideMap
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.enrichers.fixed_property_enricher import FixedPropertyEnricher
from pyserilog.core.pipeline.silet_logger import SilentLogger
from pyserilog.debuging import SelfLog
from pyserilog.events import property_utils
from pyserilog.events.event_property import EventProperty
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.message_template import MessageTemplate
import pyserilog.utils as utils


class Logger(ILogger, ILogEventSink):
    none = SilentLogger()

    def __init__(self, message_template_processor: MessageTemplateProcessor, minimum_level: LogEventLevel,
                 level_switch: LoggingLevelSwitch, sink: ILogEventSink, enricher: ILogEventEnricher,
                 exit_function: Callable, override_map: LevelOverrideMap):
        self._message_template_processor = message_template_processor
        self._minimum_level = minimum_level
        self._level_switch = level_switch
        self._sink = sink
        self._exit_function = exit_function
        self._override_map = override_map
        self._enricher = enricher



    def _for_class_type_context(self, class_type: type):
        if class_type is None:
            return self

        name = utils.full_name(class_type)
        return self._for_property_name_context(Constants.SOURCE_CONTEXT_PROPERTY_NAME, name)

    def _for_property_name_context(self, property_name: str, value, destructure_objects: bool = False):
        if not property_utils.is_valid_name(property_name):
            SelfLog.write_line("Attempt to call for_context() with invalid property name `{0}` (value: `{1}`)",
                               property_name, value)
            return self

        #     It'd be nice to do the destructuring lazily, but unfortunately `value` may be mutated between
        #     now and the first log event written.
        property_value = self._message_template_processor.create_property_value(value, destructure_objects)
        enricher = FixedPropertyEnricher(EventProperty(property_name, property_value))

        minimum_level: LogEventLevel = None
        level_switch: LoggingLevelSwitch = None

        if self._override_map is not None and property_name == Constants.SOURCE_CONTEXT_PROPERTY_NAME \
                and isinstance(value, str):
            minimum_level, level_switch = self._override_map.get_effective_level(value)
        else:
            minimum_level = self._minimum_level
            level_switch = self._level_switch

        return Logger(self._message_template_processor, minimum_level, level_switch, sink=self, enricher=enricher,
                      exit_function=None, override_map=self._override_map)

    def _for_enricher_context(self, enricher: ILogEventEnricher):
        raise NotImplementedError

    def bind_message_template(self, message_template: str, property_values: list[object] | None = None) -> \
            tuple[bool, MessageTemplate, list[LogEventProperty]]:
        if message_template is None:
            return False, None, None

        parsed_template, bound_event_properties = self._message_template_processor.process(message_template,
                                                                                           property_values)
        bound_properties = [] if len(bound_event_properties) == 0 else list(
            map(lambda x: LogEventProperty.create_with_event_property(x), bound_event_properties))
        return True, parsed_template, bound_properties

    def write_event(self, log_event: LogEvent):
        if log_event is None:
            return
        if not self.is_enable(log_event.level):
            return
        self.__dispatch(log_event)

    def emit(self, log_event: LogEvent):
        Guard.against_null(log_event)

        self.__dispatch(log_event)

    def is_enable(self, level: LogEventLevel) -> bool:
        if level < self._minimum_level:
            return False
        return self._level_switch is None or level >= self._level_switch.minimum_level

    @property
    def has_override_map(self) -> bool:
        return self._override_map is not None

    def bind_property(self, property_name: str, value, destructure_objects) -> tuple[bool, LogEventProperty | None]:
        if not property_utils.is_valid_name(property_name):
            return False, None
        prop = self._message_template_processor.create_property(property_name, value, destructure_objects)
        return True, prop

    def __dispatch(self, log_event: LogEvent):
        try:
            self._enricher.enrich(log_event, self._message_template_processor)
        except Exception as ex:
            SelfLog.write_line("Exception {0} caught while enriching {1} with {2}.", ex, log_event, self._enricher)
        self._sink.emit(log_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._exit_function is not None:
            self._exit_function(exc_type, exc_val, exc_tb)
