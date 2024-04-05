from typing import TypeVar, Generic, Mapping, MappingView

from pyserilog.guard import Guard
from pyserilog.data.log_event_property_value_visitor import LogEventPropertyValueVisitor, TResult
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue

TState = TypeVar('TState')


class LogEventPropertyValueRewriter(LogEventPropertyValueVisitor[Generic[TState], LogEventPropertyValue]):
    def _visit_scalar_value(self, state: TState, value: ScalarValue) -> LogEventPropertyValue:
        Guard.against_null(value)
        return value

    def _visit_sequence_value(self, state: TState, sequence: SequenceValue) -> LogEventPropertyValue:
        Guard.against_null(sequence)
        for i in range(len(sequence.elements)):
            original: LogEventPropertyValue = sequence.elements[i]
            if not original == self.visit(state, original):
                consts: list[LogEventPropertyValue] = []
                for j in range(i):
                    consts.append(sequence.elements[j])

                for k in range(i, len(sequence.elements)):
                    vp = self.visit(state, sequence.elements[k])
                    consts.append(vp)
                return SequenceValue(consts)
        return sequence

    def _visit_structure_value(self, state: TState, structure: StructureValue) -> LogEventPropertyValue:
        Guard.against_null(structure)

        for i in range(len(structure.properties)):
            original: LogEventProperty = structure.properties[i]
            if not original.value == self.visit(state, original.value):
                properties: list[LogEventProperty] = []
                for j in range(i):
                    properties.append(structure.properties[j])

                for k in range(i, len(structure.properties)):
                    prop = structure.properties[k]
                    event_property = LogEventProperty(prop.name, self.visit(state, prop.value))
                    properties.append(event_property)
                return StructureValue(properties)
        return structure

    def _visit_dictionary_value(self, state: TState, dictionary: DictionaryValue) -> LogEventPropertyValue:
        Guard.against_null(dictionary)

        for (key, value) in dictionary.elements:
            if value != self.visit(state, value):
                elements = []
                for element in dictionary.elements:
                    visited = self.visit(state, element[1])
                    res = tuple([element[0], visited])
                    elements.append(res)
                return DictionaryValue(elements)
        return dictionary

    def _visit_unsupported_value(self, state: TState, value: DictionaryValue) -> TResult:
        return value
