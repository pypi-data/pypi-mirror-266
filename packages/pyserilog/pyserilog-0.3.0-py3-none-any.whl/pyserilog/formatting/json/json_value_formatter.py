import decimal
import math
from datetime import timedelta, datetime, date

from pyserilog.core.string_writable import StringIOWriteable, StringWriteable
from pyserilog.events.log_event_property import LogEventProperty

from pyserilog.guard import Guard
from pyserilog.data.log_event_property_value_visitor import LogEventPropertyValueVisitor
from pyserilog.events import log_event_property
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue


class JsonValueFormatter(LogEventPropertyValueVisitor[StringWriteable, bool]):
    def __init__(self, type_tag_name: str | None = "_typeTag"):
        self._type_tag_name = type_tag_name

    def format(self, value: LogEventPropertyValue, output: StringWriteable):
        self.visit(output, value)

    def _visit_scalar_value(self, state: StringWriteable, value: ScalarValue) -> bool:
        Guard.against_null(value)
        self._format_literal_value(value.value, state)
        return False

    def _visit_sequence_value(self, output: StringWriteable, sequence: SequenceValue) -> bool:
        Guard.against_null(sequence)

        output.write("[")
        for element in sequence.elements[:-1]:
            self.visit(output, element)
            output.write(",")
        if len(sequence.elements) > 0:
            self.visit(output, sequence.elements[-1])
        output.write("]")
        return False

    def _visit_structure_value(self, state: StringWriteable, structure: StructureValue) -> bool:
        Guard.against_null(structure)

        def write_property(event_property: LogEventProperty):
            self.write_quoted_json_string(value=event_property.name, output=state)
            state.write(":")
            self.visit(state=state, value=event_property.value)

        state.write("{")
        if len(structure.properties) > 0:
            write_property(structure.properties[0])

        for prop in structure.properties[1:]:
            state.write(",")
            write_property(prop)

        if self._type_tag_name is not None and structure.type_tag is not None:
            if len(structure.properties) > 0:
                state.write(",")
            self.write_quoted_json_string(value=self._type_tag_name, output=state)
            state.write(":")
            self.write_quoted_json_string(value=structure.type_tag, output=state)

        state.write("}")
        return False

    def _visit_dictionary_value(self, state: StringWriteable, dictionary: DictionaryValue) -> bool:
        Guard.against_null(dictionary)

        state.write("{")
        delim = None
        for (element_key, element_value) in dictionary.elements:

            if delim is not None:
                state.write(delim)
            delim = ","
            val = str(element_key) if element_key is not None else "null"
            self.write_quoted_json_string(value=val, output=state)
            state.write(":")
            self.visit(state=state, value=element_value)
        state.write("}")
        return False

    def _format_literal_value(self, value, output: StringWriteable):
        if value is None:
            self._format_null_value(output)
            return

        if isinstance(value, str):
            self._format_string_value(output, value)
            return

        if isinstance(value, bool):
            data = 'true' if value else 'false'
            output.write(data)
            return

        if isinstance(value, int) or isinstance(value, float):
            self._format_number_value(value=value, output=output)
            return

        if isinstance(value, timedelta):
            data = self.td_format(value)
            self._format_string_value(output=output, value=data)
            return
        if isinstance(value, datetime):
            res = self.datetime_format(value)
            self._format_string_value(output=output, value=res)
            return

        if isinstance(value, decimal.Decimal):
            res = "{0:f}".format(value)
            output.write(res)
            return
        self._format_literal_object_value(value, output)

    @staticmethod
    def _format_null_value(output: StringWriteable):
        output.write("null")

    @staticmethod
    def _format_string_value(output: StringWriteable, value: str):
        JsonValueFormatter.write_quoted_json_string(value, output)

    @staticmethod
    def write_quoted_json_string(value: str, output: StringWriteable):
        output.write('"')

        clean_segment_start = 0
        any_escaped = False

        for i in range(len(value)):
            ch = value[i]
            if ord(ch) < 32 or ch == '\\' or ch == '"':
                any_escaped = True

                output.write(value[clean_segment_start: i])

                clean_segment_start = i + 1

                match ch:
                    case '"':
                        output.write('\\\"')
                    case '\\':
                        output.write('\\\\')
                    case '\n':
                        output.write('\\n')
                    case '\r':
                        output.write('\\r')
                    case '\f':
                        output.write('\\f')
                    case '\t':
                        output.write('\\t')
                    case _:
                        output.write('\\u')
                        output.write(format(ord(ch), "04X"))

        if any_escaped:
            output.write(value[clean_segment_start:])
        else:
            output.write(value)
        output.write('\"')

    def _format_literal_object_value(self, value, output: StringWriteable):
        Guard.against_null(value)

        res = str(value)
        string_value = "" if res is None else res
        self._format_string_value(output, string_value)

    def _format_number_value(self, value, output: StringWriteable):
        if math.isnan(value):
            self._format_string_value(output=output, value="NaN")
        elif math.isinf(value):
            if value > 0:
                self._format_string_value(output=output, value="Infinity")
            else:
                self._format_string_value(output=output, value="-Infinity")
        else:
            output.write(str(value))
        return

    @staticmethod
    def datetime_format(datetime_object: datetime):
        res = datetime_object.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        if datetime_object.tzinfo is not None:
            res = f"{res[:-2]}:{res[-2:]}"
        return res

    @staticmethod
    def td_format(td_object: timedelta):
        is_negative = False
        seconds = int(td_object.total_seconds())
        if seconds < 0:
            is_negative = True
            seconds = seconds * -1
        periods = [
            ('day', 60 * 60 * 24),
            ('hour', 60 * 60),
            ('minute', 60),
            ('second', 1)
        ]

        writer = StringIOWriteable()
        if is_negative:
            writer.write("-")
        for i in range(4):
            (period_name, period_seconds) = periods[i]
            if i == 0 and period_seconds > seconds:
                continue
            period_value, seconds = divmod(seconds, period_seconds)
            if i == 0:
                writer.write(str(period_value))
            else:
                writer.write(format(period_value, "02d"))

            if i == 0:
                writer.write(".")
            elif i != 3:
                writer.write(":")

        res = writer.getvalue()
        writer.close()
        return res
