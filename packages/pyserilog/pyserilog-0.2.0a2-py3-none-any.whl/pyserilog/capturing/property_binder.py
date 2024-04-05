from pyserilog.capturing.property_value_converter import PropertyValueConverter
from pyserilog.debuging import SelfLog
from pyserilog.events.event_property import EventProperty
from pyserilog.events.message_template import MessageTemplate
from pyserilog.parsing.property_token import PropertyToken


class PropertyBinder:
    def __init__(self, value_converter: PropertyValueConverter):
        self._value_converter = value_converter

    def construct_properties(self, message_template: MessageTemplate, message_template_parameters: list[object]) -> \
            list[EventProperty]:
        if message_template_parameters is None or len(message_template_parameters) == 0:
            if message_template.named_properties is not None or message_template.positional_properties is not None:
                SelfLog.write_line("Required properties not provided for: {0}", message_template)
            return []

        if message_template.positional_properties is not None:
            return self._construct_positional_properties(message_template, message_template_parameters)
        return self._construct_named_properties(message_template, message_template_parameters)

    def _construct_positional_properties(self, template: MessageTemplate, message_template_parameters: list[object]) \
            -> list[EventProperty]:
        if not len(template.positional_properties) == len(message_template_parameters):
            SelfLog.write_line("Positional property count does not match parameter count: {0}", template)

        result = {}
        for prop in template.positional_properties:
            (have_position, position) = prop.try_get_positional_value()
            if have_position:
                if position < 0 or position >= len(message_template_parameters):
                    SelfLog.write_line("Unassigned positional value {0} in: {1}", position, template)
                else:
                    value = message_template_parameters[position]
                    result[position] = self.__construct_property(property_token=prop, value=value)

        keys = list(result.keys())
        keys.sort()
        final_result = []
        for key in keys:
            final_result.append(result[key])
        return final_result

    def _construct_named_properties(self, template: MessageTemplate, message_template_parameters: list[object]):
        named_properties = template.named_properties
        if named_properties is None:
            return []
        matched_run = len(named_properties)
        if not len(named_properties) == len(message_template_parameters):
            matched_run = min(len(named_properties), len(message_template_parameters))
            SelfLog.write_line("Named property count does not match parameter count: {0}", template)

        result = []
        for i in range(matched_run):
            prop = named_properties[i]
            value = message_template_parameters[i]
            result.append(self.__construct_property(property_token=prop, value=value))

        for i in range(matched_run, len(message_template_parameters)):
            value = self._value_converter.create_property_value_check_destructuring(message_template_parameters[i])
            result.append(EventProperty(f"__{i}", value))
        return result

    def __construct_property(self, property_token: PropertyToken, value) -> EventProperty:
        log_event_prop_value = self._value_converter. \
            create_property_value_with_destructuring(value, property_token.destructuring)
        return EventProperty(property_token.property_name, log_event_prop_value)
