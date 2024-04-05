from pyserilog.core.string_writable import StringIOWriteable,StringWriteable

from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.parsing.message_template_token import MessageTemplateToken
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.rendering.message_template_renderer import MessageTemplateRenderer


class MessageTemplate:
    def __init__(self, tokens: list[MessageTemplateToken], text: str | None = None):
        if text is None:
            text = ''.join(tokens)
        self._text = text
        self._tokens = tokens
        property_tokens: list[PropertyToken] = self.get_elements_of_type(tokens, PropertyToken)
        self._named_properties: list[PropertyToken] | None = None
        self._positional_properties = None
        if len(property_tokens) != 0:
            all_positional = True
            any_positional = False
            for property_token in property_tokens:
                if property_token.is_positional:
                    any_positional = True
                else:
                    all_positional = False
            if all_positional:
                self._positional_properties = property_tokens
            else:
                if any_positional:
                    SelfLog.write_line("Message template is malformed: {0}", text)
                self._named_properties = property_tokens

    @staticmethod
    def get_elements_of_type(tokens: list[MessageTemplateToken], element_type):
        result: list[PropertyToken] = []
        for token in tokens:
            if isinstance(token, element_type):
                result.append(token)
        return result

    @property
    def tokens(self):
        return self._tokens

    @property
    def text(self):
        return self._text

    @property
    def named_properties(self) -> list[PropertyToken] | None:
        return self._named_properties

    @property
    def positional_properties(self) -> list[PropertyToken] | None:
        return self._positional_properties

    def render(self, properties: dict[str, LogEventPropertyValue], output: StringWriteable | None = None) -> str | None:
        if output is None:
            return self.__render_without_writer(properties=properties)
        MessageTemplateRenderer.render(self, properties, output)

    def __render_without_writer(self, properties: dict[str, LogEventPropertyValue]) -> str:
        writer = StringIOWriteable()
        self.render(properties, writer)
        result = writer.getvalue()
        writer.close()
        return result

    def __str__(self):
        return self._text
