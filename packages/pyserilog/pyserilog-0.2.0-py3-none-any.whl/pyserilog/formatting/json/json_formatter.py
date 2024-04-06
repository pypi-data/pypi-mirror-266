import decimal
from pyserilog.core.string_writable import StringWriteable

from pyserilog.guard import Guard
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.scalar_value import ScalarValue, LogEventPropertyValue
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue
from pyserilog.formatting.itext_formatter import ITextFormatter
from datetime import datetime

from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter


class JsonFormatter(ITextFormatter):

    def __init__(self, closing_delimiter: str | None = None, render_message: bool = False):
        self._close_delimiter: str = closing_delimiter if closing_delimiter is not None else '\n'
        self._render_message = render_message
        self._literal_writers = {
            int: self.__write_to_string,
            float: self.__write_to_string,
            decimal.Decimal: self.__write_to_string,
            datetime: lambda x, force_quotation, output: self.__write_datetime(x, output),
            ScalarValue: lambda x, quote, output: self.__write_literal(x.value, output, quote),
            SequenceValue: lambda x, quote, output: self.__write_sequence(x.elements, output, quote),
            DictionaryValue: lambda x, quote, output: self.__write_dictionary(x.elements, output),
            StructureValue: lambda x, quote, output: self.__write_structure(x.type_tag, x.properties, output),
        }

    def format(self, log_event, output: StringWriteable):
        from pyserilog.events.log_event import LogEvent
        log_event: LogEvent = log_event
        Guard.against_null(log_event)
        Guard.against_null(output)

        output.write("{")
        delim = JsonFormatter.Delimiter()
        self.__write_timestamp(timestamp=log_event.timestamp, delim=delim, output=output)
        if self._render_message:
            raise NotImplementedError

        if len(log_event.properties) > 0:
            self.__write_properties(props=log_event.properties, output=output)

        output.write("}")

    def __write_timestamp(self, timestamp: datetime, delim, output: StringWriteable):
        self.__write_json_property("timestamp", timestamp, delim, output)

    def __write_json_property(self, name: str, value, preceding_delimiter, output: StringWriteable):
        if preceding_delimiter.delim is not None:
            output.write(preceding_delimiter.delim)
        output.write('"')
        output.write(name)
        output.write('":')
        self.__write_literal(value, output)
        preceding_delimiter.delim = ","

    def __write_literal_value(self, value, output: StringWriteable):
        self.write_string(str(value), output)

    def __write_literal(self, value, output: StringWriteable, force_quotation: bool = False):
        if value is None:
            output.write("null")
            return

        if type(value) in self._literal_writers:
            func = self._literal_writers[type(value)]
            func(value, force_quotation, output)
            return
        self.__write_literal_value(value, output)

    @staticmethod
    def __write_to_string(number, quote: bool, output: StringWriteable):
        if quote:
            output.write('"')
        output.write(str(number))
        if quote:
            output.write('"')

    def __write_properties(self, props: dict[str, LogEventPropertyValue], output: StringWriteable):
        output.write(",\"properties\":{")
        self.__write_properties_values(props=props, output=output)
        output.write("}")

    def __write_properties_values(self, props: dict[str, LogEventPropertyValue], output: StringWriteable):
        preceding_delimiter = JsonFormatter.Delimiter()
        for property_name in props:
            property_value = props[property_name]
            self.__write_json_property(property_name, property_value, preceding_delimiter, output)

    @staticmethod
    def __write_datetime(value: datetime, output: StringWriteable):
        output.write('"')
        res = JsonValueFormatter.datetime_format(value)
        output.write(res)
        output.write('"')

    @staticmethod
    def write_string(value: str, output: StringWriteable):
        JsonValueFormatter.write_quoted_json_string(value, output)

    def __write_sequence(self, elements: list, output: StringWriteable, force_quotation: bool = False):
        output.write("[")
        delim = JsonFormatter.Delimiter()

        for value in elements:
            if delim.delim is not None:
                output.write(delim.delim)
            delim.delim = ','
            self.__write_literal(value=value, output=output, force_quotation=force_quotation)

        output.write("]")

    def __write_dictionary(self, elements: list[tuple[ScalarValue, LogEventPropertyValue]], output: StringWriteable):
        output.write("{")
        delim = JsonFormatter.Delimiter()

        for (key, value) in elements:
            if delim.delim is not None:
                output.write(delim.delim)
            delim.delim = ","
            self.__write_literal(key, output, force_quotation=True)
            output.write(":")
            self.__write_literal(value, output)

        output.write("}")

    def __write_structure(self, type_tag: str, properties: list[LogEventProperty],
                          output: StringWriteable):
        output.write("{")
        delim = JsonFormatter.Delimiter()
        if type_tag is not None:
            self.__write_json_property("_type_tag", type_tag, delim, output)
        for prop in properties:
            self.__write_json_property(prop.name, prop.value, delim, output)
        output.write("}")

    class Delimiter:
        def __init__(self):
            self._delim = None

        @property
        def delim(self):
            return self._delim

        @delim.setter
        def delim(self, value):
            self._delim = value
