from pyserilog.core.ilog_event_property_factory import ILogEventPropertyFactory
from pyserilog.core.pipeline.message_template_cache import MessageTemplateCache
from pyserilog.events.message_template import MessageTemplate
from pyserilog.events.event_property import EventProperty
from pyserilog.parsing.message_template_parser import MessageTemplateParser
from pyserilog.capturing.property_value_converter import PropertyValueConverter
from pyserilog.capturing.property_binder import PropertyBinder


class MessageTemplateProcessor(ILogEventPropertyFactory):
    __parser = MessageTemplateCache(MessageTemplateParser())

    def __init__(self, property_value_converter: PropertyValueConverter):
        self._property_value_converter = property_value_converter
        self._property_binder = PropertyBinder(self._property_value_converter)

    def create_property(self, name: str, value, destructure_objects: bool = False):
        return self._property_value_converter.create_property(name, value, destructure_objects)

    def create_property_value(self, value, destructure_objects: bool = False ):
        return self._property_value_converter.create_property_value_check_destructuring(value , destructure_objects)

    def process(self, message_template: str, message_template_parameters: list) -> \
            tuple[MessageTemplate, list[EventProperty]]:
        parsed_template = self.__parser.parse(message_template)
        properties = self._property_binder.construct_properties(parsed_template, message_template_parameters)
        return parsed_template, properties
