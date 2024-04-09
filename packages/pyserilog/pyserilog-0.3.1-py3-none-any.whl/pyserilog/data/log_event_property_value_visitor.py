from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pyserilog.guard import Guard
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue

TState = TypeVar('TState')
TResult = TypeVar('TResult')


class LogEventPropertyValueVisitor(ABC, Generic[TState, TResult]):

    def visit(self, state: TState, value: LogEventPropertyValue) -> TResult:
        Guard.against_null(value)

        if isinstance(value, ScalarValue):
            return self._visit_scalar_value(state, value)
        if isinstance(value, SequenceValue):
            return self._visit_sequence_value(state, value)
        if isinstance(value, StructureValue):
            return self._visit_structure_value(state, value)
        if isinstance(value, DictionaryValue):
            return self._visit_dictionary_value(state, value)
        return self._visit_unsupported_value(state, value)

    @abstractmethod
    def _visit_scalar_value(self, state: TState, value: ScalarValue) -> TResult:
        pass

    @abstractmethod
    def _visit_sequence_value(self, state: TState, value: SequenceValue) -> TResult:
        pass

    @abstractmethod
    def _visit_structure_value(self, state: TState, value: StructureValue) -> TResult:
        pass

    @abstractmethod
    def _visit_dictionary_value(self, state: TState, value: DictionaryValue) -> TResult:
        pass

    def _visit_unsupported_value(self, state: TState, value: DictionaryValue) -> TResult:
        Guard.against_null(value)
        raise Exception(f"The value {value} is not of a type supported by this visitor.")
