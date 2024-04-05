from builtins import NotImplementedError

from pyserilog.core.string_writable import StringIOWriteable, StringWriteable

from pyserilog.formatting.display.level_output_format import LevelOutputFormat
from pyserilog.formatting.display.properties_output_format import PropertiesOutputFormat
from pyserilog.guard import Guard
from pyserilog.events.log_event import LogEvent
from pyserilog.events.message_template import MessageTemplate
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.formatting import ITextFormatter
from pyserilog.formatting.display.output_properties import OutputProperties
from pyserilog.parsing.message_template_parser import MessageTemplateParser
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.parsing.text_token import TextToken
from pyserilog.rendering.casing import Casing
from pyserilog.rendering.message_template_renderer import MessageTemplateRenderer
from pyserilog.rendering.padding import Padding


class MessageTemplateTextFormatter(ITextFormatter):
    def __init__(self, output_template: str):
        Guard.against_null(output_template)
        self._output_template: MessageTemplate = MessageTemplateParser().parse(output_template)

    def format(self, log_event: LogEvent, output: StringWriteable):
        for token in self._output_template.tokens:
            if isinstance(token, TextToken):
                MessageTemplateRenderer.render_text_token(token, output)
                continue
            assert isinstance(token, PropertyToken)
            pt = token
            if pt.property_name == OutputProperties.LEVEL_PROPERTY_NAME:
                moniker = LevelOutputFormat.get_level_moniker(log_event.level, pt.format)
                Padding.apply(output, moniker, pt.alignment)
            elif pt.property_name == OutputProperties.NEW_LINE_PROPERTY_NAME:
                Padding.apply(output, '\n', pt.alignment)
            elif pt.property_name == OutputProperties.EXCEPTION_PROPERTY_NAME:
                raise NotImplementedError
            else:

                writer = StringIOWriteable() if pt.alignment is not None else output

                if pt.property_name == OutputProperties.MESSAGE_PROPERTY_NAME:
                    MessageTemplateRenderer.render(log_event.message_template, log_event.properties, writer, pt.format)
                elif pt.property_name == OutputProperties.TIMESTAMP_PROPERTY_NAME:
                    ScalarValue.render_value(log_event.timestamp, writer, pt.format)
                elif pt.property_name == OutputProperties.PROPERTIES_PROPERTY_NAME:
                    PropertiesOutputFormat.render(log_event.message_template, log_event.properties,
                                                  self._output_template, writer, pt.format)
                else:
                    # If a property is missing, don't render anything (message templates render the raw token here).
                    if pt.property_name not in log_event.properties:
                        continue
                    property_value = log_event.properties[pt.property_name]
                    if isinstance(property_value, ScalarValue) and isinstance(property_value.value, str):
                        cased = Casing.format(property_value.value, pt.format)
                        writer.write(cased)
                    else:
                        property_value.render(writer, pt.format)

                if pt.alignment is not None:
                    Padding.apply(output, writer.getvalue(), pt.alignment)

                    writer.close()
