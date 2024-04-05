from pyserilog.core.string_writable import StringIOWriteable,StringWriteable

from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events import message_template
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.parsing.text_token import TextToken
from pyserilog.rendering.padding import Padding


class MessageTemplateRenderer:
    json_value_formatter: JsonValueFormatter = JsonValueFormatter("$type")

    @staticmethod
    def render(message_template: message_template, properties: dict[str, LogEventPropertyValue], output: StringWriteable,
               text_format: str = None):
        is_literal = False
        is_json = False

        if text_format is not None:
            if 'j' in text_format:
                is_json = True
            if 'l' in text_format:
                is_literal = True

        for token in message_template.tokens:
            if isinstance(token, TextToken):
                MessageTemplateRenderer.render_text_token(token , output)
            elif isinstance(token, PropertyToken):
                MessageTemplateRenderer.render_property_token(token, properties, output, is_literal, is_json)

    @staticmethod
    def render_text_token(token: TextToken, output: StringWriteable):
        output.write(token.text)

    @staticmethod
    def render_property_token(pt: PropertyToken, properties: dict[str, LogEventPropertyValue],
                              output: StringWriteable, is_literal: bool, is_json: bool):
        if pt.property_name not in properties:
            output.write(pt.raw_text)
            return

        property_value = properties[pt.property_name]
        if pt.alignment is None:
            MessageTemplateRenderer.render_value(property_value, is_literal, is_json, output, pt.format)
            return
        value_output = StringIOWriteable()
        MessageTemplateRenderer.render_value(property_value, is_literal, is_json, value_output, pt.format)
        sb = value_output.getvalue()
        if len(sb) >= pt.alignment.width:
            output.write(sb)
            return
        Padding.apply(output, sb, pt.alignment)

    @staticmethod
    def render_value(property_value: LogEventPropertyValue, is_literal: bool, is_json: bool, output: StringWriteable,
                     text_format: str | None = None):
        if is_literal and isinstance(property_value, ScalarValue) and isinstance(property_value.value, str):
            output.write(property_value.value)
        elif is_json and text_format is None:
            MessageTemplateRenderer.json_value_formatter.format(property_value, output)
        else:
            property_value.render(output, text_format)
