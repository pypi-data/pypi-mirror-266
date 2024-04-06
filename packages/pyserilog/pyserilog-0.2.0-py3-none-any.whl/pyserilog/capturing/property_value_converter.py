from typing import Iterable

from pyserilog.capturing.depth_limiter import DepthLimiter
from pyserilog.capturing.iproperty_value_converter import IPropertyValueConverter
from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.core.iscalar_conversion_policy import IScalarConversionPolicy
from pyserilog.debuging.self_log import SelfLog
from pyserilog.events.dictionary_value import DictionaryValue
from pyserilog.events.log_event_property import LogEventProperty
from pyserilog.events.log_event_property_value import LogEventPropertyValue
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.sequence_value import SequenceValue
from pyserilog.events.structure_value import StructureValue
from pyserilog.parsing.destructuring import Destructuring
from pyserilog.policies.byte_array_scalar_conversion_policy import ByteArrayScalarConversionPolicy
from pyserilog.policies.reflection_types_scalar_destructuring_policy import ReflectionTypesScalarDestructuringPolicy
from pyserilog.policies.simple_scalar_conversion_policy import SimpleScalarConversionPolicy
import pyserilog.utils as utils

built_in_scalar_types = [
    bool, int, float
    # chr,
    # str, datetime.date, decimal.Decimal
]


class PropertyValueConverter(IPropertyValueConverter):
    def __init__(self, maximum_destructuring_depth: int, maximum_string_length: int, maximum_collection_count: int,
                 additional_scalar_types: list[type], additional_destructuring_policies: list[IDestructuringPolicy],
                 propagate_exceptions: bool):
        self._maximum_string_length = maximum_string_length
        self._maximum_collection_count = maximum_collection_count
        self._propagate_exceptions = propagate_exceptions
        scalar_types = list(built_in_scalar_types)
        scalar_types.extend(additional_scalar_types)
        self._scalarConversionPolicies: list[IScalarConversionPolicy] = [
            SimpleScalarConversionPolicy(scalar_types),
            ByteArrayScalarConversionPolicy()
        ]

        self._destructuringPolicies = additional_destructuring_policies
        self._destructuringPolicies.append(ReflectionTypesScalarDestructuringPolicy())
        self._depthLimiter = DepthLimiter(maximum_destructuring_depth, self)

    def create_property(self, name: str, value, destructure_objects: bool = False) -> LogEventProperty:
        prop = self.create_property_value_check_destructuring(value, destructure_objects)
        return LogEventProperty(name, prop)

    def create_property_value_check_destructuring(self, value,
                                                  destructure_objects: bool = False) -> LogEventPropertyValue:
        return self.create_property_value_check_destructuring_and_depth(value, destructure_objects, 1)

    def create_property_value_with_destructuring(self, value: object,
                                                 destructuring: Destructuring) -> LogEventPropertyValue:
        try:
            return self.create_property_value_with_destructuring_and_depth(value, destructuring, 1)
        except Exception as ex:
            if self._propagate_exceptions:
                raise ex
            SelfLog.write_line("Exception caught while converting property value: {0}", ex)
            return ScalarValue(f"Capturing the property value threw an exception: {utils.full_name(ex)}")

    def create_property_value_check_destructuring_and_depth(self,
                                                            value, destructure_objects: bool,
                                                            depth: int) -> LogEventPropertyValue:
        destructuring = Destructuring.DESTRUCTURE if destructure_objects == True else Destructuring.DEFAULT
        return self.create_property_value_with_destructuring_and_depth(value, destructuring, depth)

    def create_property_value_with_destructuring_and_depth(self, value, destructuring: Destructuring,
                                                           depth: int) -> LogEventPropertyValue:
        if value is None:
            return ScalarValue.Null()

        if destructuring == Destructuring.STRINGIFY:
            return self.__stringify(value)

        if destructuring == Destructuring.DESTRUCTURE and isinstance(value, str):
            value = self.__truncate_if_necessary(value)

        if isinstance(value, str):
            return ScalarValue(value)

        for converter in self._scalarConversionPolicies:
            checked, res = converter.try_convert_to_scalar(value)
            if checked:
                return res

        DepthLimiter.set_current_depth(depth)

        if destructuring == Destructuring.DESTRUCTURE:
            for destructuring_policy in self._destructuringPolicies:
                checked, res = destructuring_policy.try_destructure(value, self._depthLimiter)
                if checked:
                    return res
        if isinstance(value, Iterable) or hasattr(value, '__iter__'):
            return self.__convert_iterables(value, destructuring)

        checked, res = self.__try_convert_compiler_generated_type(value, destructuring)
        if checked:
            return res
        return ScalarValue(str(value))

    def __stringify(self, value) -> ScalarValue:
        if value is None:
            return ScalarValue("")
        value_str: str = str(value)
        truncated = self.__truncate_if_necessary(value_str)
        return ScalarValue(truncated)

    def __truncate_if_necessary(self, text: str):
        if len(text) > self._maximum_string_length:
            return f"{text[0:self._maximum_string_length - 1]}…"
        return text

    def __convert_iterables(self, value, destructuring: Destructuring):
        # Only dictionaries with 'scalar' keys are permitted, as
        # more complex keys may not serialize to unique values for
        # representation in sinks. This check strengthens the expectation
        # that resulting dictionary is representable in JSON as well
        # as richer formats (e.g. XML, .NET type-aware...).
        # Only actual dictionaries are supported, as arbitrary types
        # can implement multiple IDictionary interfaces and thus introduce
        # multiple different interpretations.

        if isinstance(value, dict):
            def map_to_dictionary_elements():
                result: list = []
                count = 0
                for key in value:
                    if count >= self._maximum_collection_count:
                        break
                    count += 1
                    val = value[key]
                    key_value = self._depthLimiter.create_property_value_with_destructure(key, destructuring)
                    val_value = self._depthLimiter.create_property_value_with_destructure(val, destructuring)
                    result.append((key_value, val_value))
                return result

            elements = map_to_dictionary_elements()
            res_dict = DictionaryValue(elements)
            return res_dict

        if len(value) <= self._maximum_collection_count:
            if len(value) == 0:
                return SequenceValue.empty()
            arr = []
            for el in value:
                element_value = self._depthLimiter.create_property_value_with_destructure(el, destructuring)
                arr.append(element_value)
            return SequenceValue(arr)
        else:
            seq = self.__map_to_sequence(value, destructuring)
            return SequenceValue(seq)

    def __map_to_sequence(self, sequence: list, destructure: Destructuring):
        count = 0
        res: list[LogEventPropertyValue] = []
        for element in sequence:
            if count < self._maximum_collection_count:
                val = self._depthLimiter.create_property_value_with_destructure(element, destructure)
                res.append(val)
                count += 1
            else:
                break
        return res

    def __try_convert_compiler_generated_type(self, value, destructuring: Destructuring) \
            -> tuple[bool, LogEventPropertyValue | None]:
        if destructuring == Destructuring.DESTRUCTURE:
            type_tag = type(value).__name__
            if len(type_tag) <= 0:
                type_tag = None
            props: list[LogEventProperty] = self.__get_properties(value)
            return True, StructureValue(props, type_tag)
        return False, None

    def __get_properties(self, value) -> list[LogEventProperty]:
        res: list[LogEventProperty] = []
        public_props = list(name for name in dir(value) if not name.startswith('_'))
        for property_name in public_props:
            try:
                property_value = getattr(value, property_name)
            except Exception as ex:
                SelfLog.write_line("The property accessor {0} threw exception: {1}", property_name, ex)
                if self._propagate_exceptions:
                    raise ex
                property_value = f"The property accessor threw an exception: {type(ex).__name__}"
            prop_value = self._depthLimiter.create_property_value_with_destructure(
                property_value, Destructuring.DESTRUCTURE)
            event_prop = LogEventProperty(property_name, prop_value)
            res.append(event_prop)
        return res
