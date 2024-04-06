import string
from builtins import staticmethod
from pyserilog.core.string_writable import StringIOWriteable

from pyserilog.guard import Guard
from pyserilog.core.imessage_template_parser import IMessageTemplateParser
from pyserilog.events.message_template import MessageTemplate
from pyserilog.parsing.alignment import Alignment, AlignmentDirection
from pyserilog.parsing.destructuring import Destructuring
from pyserilog.parsing.message_template_token import MessageTemplateToken
from pyserilog.parsing.property_token import PropertyToken
from pyserilog.parsing.text_token import TextToken


class MessageTemplateParser(IMessageTemplateParser):

    def parse(self, message_template: str) -> MessageTemplate:
        Guard.against_null(message_template)
        tokens = self.__tokenize(message_template)
        return MessageTemplate(tokens, message_template)

    @staticmethod
    def __tokenize(message_template: str) -> list[MessageTemplateToken]:
        result: list[MessageTemplateToken] = []
        if len(message_template) == 0:
            result.append(TextToken("", 0))
            return result
        next_index = 0
        while True:
            before_text = next_index
            tt, next_index = MessageTemplateParser.__parse_text_token(next_index, message_template)
            if next_index > before_text:
                result.append(tt)
            if next_index == len(message_template):
                break
            before_pop = next_index
            pt, next_index = MessageTemplateParser.__parse_property_token(next_index, message_template)
            if before_pop < next_index:
                result.append(pt)
            if next_index == len(message_template):
                break
        return result

    @staticmethod
    def __parse_text_token(start_at: int, message_template: str) -> tuple[TextToken, int]:
        first = start_at
        accum = StringIOWriteable()

        while True:
            nc = message_template[start_at]
            if nc == '{':
                if start_at + 1 < len(message_template) and message_template[start_at + 1] == '{':
                    accum.write(nc)
                    start_at += 1
                else:
                    break
            else:
                accum.write(nc)
                if nc == '}':
                    if start_at + 1 < len(message_template) and message_template[start_at + 1] == '}':
                        start_at += 1
            start_at += 1
            if start_at >= len(message_template):
                break
        next_step = start_at
        result = str(accum)
        token = TextToken(result, first)
        return token, next_step

    @staticmethod
    def __parse_property_token(start_at: int, message_template: str) -> tuple[MessageTemplateToken, int]:
        first = start_at
        start_at += 1
        while start_at < len(message_template) and \
                MessageTemplateParser.__is_valid_in_property_tag(message_template[start_at]):
            start_at += 1

        if start_at == len(message_template) or message_template[start_at] != '}':
            next_value = start_at
            token = TextToken(message_template[first: next_value], first)
            return token, next_value
        next_value = start_at + 1
        raw_text = message_template[first: next_value]
        tag_content = raw_text[1: 1 + (next_value - (first + 2))]
        if len(tag_content) == 0:
            return TextToken(raw_text, first), next_value
        checked, property_name_and_destructuring, tag_content_format, tag_content_alignment = \
            MessageTemplateParser.__try_split_tag_content(tag_content)
        if not checked:
            return TextToken(raw_text, first), next_value
        property_name = property_name_and_destructuring
        destructuring = Destructuring.DEFAULT
        if len(property_name) > 0:
            checked, destructuring = MessageTemplateParser.__try_get_destructuring_hint(property_name[0])
            if checked:
                property_name = property_name[1:]
        if len(property_name) == 0:
            return TextToken(raw_text, first), next_value
        for char in property_name:
            if not MessageTemplateParser.__is_valid_in_property_name(char):
                return TextToken(raw_text, first), next_value
        if tag_content_format is not None:
            for char in tag_content_format:
                if not MessageTemplateParser.__is_valid_in_format(char):
                    return TextToken(raw_text, first), next_value
        text_alignment: Alignment = None
        if tag_content_alignment is not None:
            for char in tag_content_alignment:
                if not MessageTemplateParser.__is_valid_in_alignment(char):
                    return TextToken(raw_text, first), next_value

            def last_index_of(text: str, sub: str):
                try:
                    return text.rindex(sub)
                except ValueError:
                    return -1

            last_dash = last_index_of(tag_content_alignment, '-')
            if last_dash > 0:
                return TextToken(raw_text, first), next_value

            width: str = tag_content_alignment if last_dash == -1 else tag_content_alignment[1:]
            if not width.isdigit() or int(width) == 0:
                return TextToken(raw_text, first), next_value
            width: int = int(width)

            direction = AlignmentDirection.RIGHT if last_dash == -1 else AlignmentDirection.LEFT
            text_alignment = Alignment(direction, width)
        return PropertyToken(property_name, raw_text, tag_content_format, text_alignment, destructuring,
                             first), next_value

    @staticmethod
    def __try_split_tag_content(tag_content: str) -> tuple[bool, str, str, str]:
        property_name_and_destructuring = None
        tag_content_format = None
        tag_content_alignment = None

        def index_of(text: str, sub: str):
            try:
                return text.index(sub)
            except ValueError:
                return -1

        format_delim = index_of(tag_content, ':')
        alignment_delim = index_of(tag_content, ',')
        if format_delim == -1 and alignment_delim == -1:
            return True, tag_content, None, None
        if alignment_delim == -1 or (format_delim != -1 and alignment_delim > format_delim):
            property_name_and_destructuring = tag_content[:format_delim]
            tag_content_format = None if format_delim == len(tag_content) - 1 else tag_content[format_delim + 1:]
            tag_content_alignment = None
            return True, property_name_and_destructuring, tag_content_format, tag_content_alignment
        property_name_and_destructuring = tag_content[:alignment_delim]
        if format_delim == -1:
            if alignment_delim == len(tag_content) - 1:
                tag_content_alignment = None
                tag_content_format = None
                return False, property_name_and_destructuring, tag_content_format, tag_content_alignment
            tag_content_format = None
            tag_content_alignment = tag_content[alignment_delim + 1:]
            return True, property_name_and_destructuring, tag_content_format, tag_content_alignment
        if alignment_delim == format_delim - 1:
            return False, property_name_and_destructuring, tag_content_format, tag_content_alignment

        tag_content_alignment = tag_content[alignment_delim + 1: format_delim ]
        if format_delim == len(tag_content) - 1:
            tag_content_format = None
        else:
            tag_content_format = tag_content[format_delim + 1:]
        return True, property_name_and_destructuring, tag_content_format, tag_content_alignment

    @staticmethod
    def __is_valid_in_property_tag(ch: str) -> bool:
        return MessageTemplateParser.__is_valid_in_destructuring_hint(ch) or \
               MessageTemplateParser.__is_valid_in_property_name(ch) or \
               MessageTemplateParser.__is_valid_in_format(ch) or \
               ch == ':'

    @staticmethod
    def __is_valid_in_destructuring_hint(ch: str) -> bool:
        return ch == '@' or ch == '$'

    @staticmethod
    def __is_valid_in_property_name(ch: str) -> bool:
        return ch == '_' or ch.isalpha() or ch.isdigit()

    @staticmethod
    def __is_valid_in_format(ch: str) -> bool:
        return ch != '}' and ch != '$' \
               and (ch.isalpha() or ch.isdigit() or ch in string.punctuation or ch == ' ' or ch == '+')

    @staticmethod
    def __is_valid_in_alignment(ch: str):
        return ch.isdigit() or ch == '-'

    @staticmethod
    def __try_get_destructuring_hint(ch: str) -> tuple[bool, Destructuring]:
        match ch:
            case '@':
                return True, Destructuring.DESTRUCTURE
            case '$':
                return True, Destructuring.STRINGIFY
            case _:
                return False, Destructuring.DEFAULT
