import datetime
from abc import ABC, abstractmethod
from multipledispatch import dispatch

from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.message_template import MessageTemplate

no_property_values = []


class ILogger(ABC):

    @abstractmethod
    def write_event(self, log_event: LogEvent):
        pass

    def write(self, level: LogEventLevel, message_template: str, property_values: list | None = None,
              exception: Exception | None = None):
        if not self.is_enable(level) or message_template is None:
            return

        (checked, parsed_template, bound_properties) = self.bind_message_template(message_template, property_values)
        if checked:
            event = LogEvent(datetime.datetime.now(), level, exception, parsed_template, bound_properties)
            self.write_event(event)

    def is_enable(self, level: LogEventLevel) -> bool:
        return True

    def write_with_level(self, level: LogEventLevel, message_template: str, *property_value,
                         exception: BaseException = None):
        res = []
        if property_value is not None:
            for p in property_value:
                res.append(p)
        self.write(level, message_template, res)

    def verbose(self, message_template: str, *property_value):
        self.write_with_level(LogEventLevel.VERBOSE, message_template, *property_value)

    def debug(self, message_template: str, *property_value):
        self.write_with_level(LogEventLevel.DEBUG, message_template, *property_value)

    def information(self, message_template: str, *property_value):
        self.write_with_level(LogEventLevel.INFORMATION, message_template, *property_value)

    def warning(self, message_template: str, *property_value):
        self.write_with_level(LogEventLevel.WARNING, message_template, *property_value)

    def error(self, message_template: str, *property_value, exception: BaseException | None = None):
        self.write_with_level(LogEventLevel.ERROR, message_template, *property_value, exception=exception)

    def fatal(self, message_template: str, *property_value, exception: BaseException | None = None):
        self.write_with_level(LogEventLevel.FATAL, message_template, *property_value, exception=exception)

    @abstractmethod
    def bind_message_template(self, message_template: str, property_values: list[object] | None) -> \
            tuple[bool, MessageTemplate, list[LogEventProperty]]:
        pass

    @dispatch(str, object)
    def for_context(self, property_name: str, value: object):
        return self._for_property_name_context(property_name, value, False)

    @dispatch(str, object, bool)
    def for_context(self, property_name: str, value: object, destructure_objects: bool):
        return self._for_property_name_context(property_name, value, destructure_objects)

    @dispatch(type)
    def for_context(self, klass_type: type):
        return self._for_class_type_context(klass_type)

    @dispatch(ILogEventEnricher)
    def for_context(self, enricher: ILogEventEnricher):
        return self._for_enricher_context(enricher)

    # def for_context(self, **kwargs):
    #     """
    #     enricher: ILogEventEnricher
    #     :param kwargs:
    #     :return:
    #     """
    #
    #     def get_value(key, default_value=None):
    #         if key in kwargs:
    #             return kwargs[key]
    #         return default_value
    #
    #     if len(kwargs) == 1:
    #         if 'enricher' in kwargs:
    #             enricher = kwargs.pop('enricher')
    #             if isinstance(enricher, ILogEventEnricher):
    #                 return self._for_enricher_context(enricher)
    #             else:
    #                 raise TypeError("enricher should be type of ILogEventEnricher")
    #         if 'class_type' in kwargs:
    #             class_type = kwargs.pop('class_type')
    #             if isinstance(class_type, type):
    #                 return self._for_class_type_context(class_type)
    #             else:
    #                 raise TypeError("enricher should be type of ILogEventEnricher")
    #         elif 'enrichers' in kwargs:
    #             enrichers = kwargs.pop('enrichers')
    #             raise NotImplementedError
    #     elif (len(kwargs) == 2 or len(kwargs) == 3) and 'property_name' in kwargs:
    #         property_name: str = kwargs.pop('property_name')
    #         value = kwargs.pop('value')
    #         destructure_objects = kwargs.pop('destructureObjects', False)
    #         return self._for_property_name_context(property_name, value, destructure_objects)
    #     raise NotImplementedError

    @abstractmethod
    def _for_enricher_context(self, enricher: ILogEventEnricher):
        pass

    @abstractmethod
    def _for_property_name_context(self, property_name: str, value, destructure_objects: bool = False):
        pass

    @abstractmethod
    def _for_class_type_context(self, class_type: type):
        pass

    @abstractmethod
    def bind_property(self, property_name: str, value, destructure_objects) -> tuple[bool, LogEventProperty | None]:
        pass
