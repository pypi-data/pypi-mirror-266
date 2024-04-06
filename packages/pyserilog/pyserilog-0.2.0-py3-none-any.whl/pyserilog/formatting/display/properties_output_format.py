from pyserilog.core.string_writable import StringWriteable

from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.message_template import MessageTemplate
from pyserilog.events.structure_value import StructureValue
from pyserilog.formatting.json.json_value_formatter import JsonValueFormatter


class PropertiesOutputFormat:
    formatter: JsonValueFormatter = JsonValueFormatter("$type")

    @staticmethod
    def render(template: MessageTemplate, properties: dict[str, LogEventPropertyValue],
               output_template: MessageTemplate, output: StringWriteable, text_format: str | None = None):

        def contain_property(prop_key):
            return PropertiesOutputFormat.__template_contain_property_name(template, prop_key) or \
                   PropertiesOutputFormat.__template_contain_property_name(output_template, prop_key)

        if text_format is not None and "j" in text_format:
            props = list(map(lambda x: LogEventProperty(x, properties[x]),
                             filter(lambda x: not contain_property(x), properties)))
            sv = StructureValue(props)
            PropertiesOutputFormat.formatter.format(sv, output)
            return

        output.write("{ ")
        delim = ""
        for key in properties:
            if contain_property(key):
                continue
            output.write(delim)
            delim = ", "
            output.write(key)
            output.write(": ")
            properties[key].render(output, None)
        output.write(" }")

    @staticmethod
    def __template_contain_property_name(template: MessageTemplate, property_name: str):
        if template.positional_properties is not None:
            for p in template.positional_properties:
                if p.property_name == property_name:
                    return True
            return False

        if template.named_properties is not None:
            for p in template.named_properties:
                if p.property_name == property_name:
                    return True
            return False
        return False
