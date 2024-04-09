from pyserilog.core.string_writable import StringWriteable

from pyserilog.parsing.alignment import Alignment
from pyserilog.parsing.destructuring import Destructuring
from pyserilog.parsing.message_template_token import MessageTemplateToken


class PropertyTokenBase(MessageTemplateToken):

    def __init__(self, property_name: str, raw_text: str, text_format: str = None,
                 text_alignment: Alignment = None, destructuring: Destructuring = Destructuring.DEFAULT,
                 start_index: int = -1):
        super().__init__(start_index)
        self._property_name = property_name
        self._raw_text = raw_text
        self._destructuring = destructuring
        self._text_alignment = text_alignment
        self._text_format = text_format

        self._position = None
        if property_name.isdigit() and int(property_name) >= 0:
            self._position = int(property_name)

    @property
    def length(self) -> int:
        return len(self._raw_text)

    @property
    def property_name(self) -> str:
        return self._property_name

    @property
    def is_positional(self) -> bool:
        return self._position is not None

    @property
    def destructuring(self) -> Destructuring:
        return self._destructuring

    @property
    def format(self):
        return self._text_format

    @property
    def alignment(self) -> Alignment | None:
        return self._text_alignment

    @property
    def raw_text(self):
        return self._raw_text

    def render(self, properties: dict, writer: StringWriteable):
        pass

    def try_get_positional_value(self) -> tuple[bool, int]:
        if self._position is None:
            return False, 0
        return True, self._position

    def __eq__(self, other):
        if not isinstance(other, PropertyToken):
            return False
        return other._destructuring == self._destructuring and other.format == self.format and \
               other._property_name == self._property_name and other._raw_text == self._raw_text

    def __hash__(self):
        return hash(self._property_name)

    def __str__(self):
        return self.raw_text


class PropertyToken(PropertyTokenBase):
    __metaclass__ = PropertyTokenBase
