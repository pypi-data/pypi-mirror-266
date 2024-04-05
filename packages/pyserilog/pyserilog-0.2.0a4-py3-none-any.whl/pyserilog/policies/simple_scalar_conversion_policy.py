from pyserilog.core.iscalar_conversion_policy import IScalarConversionPolicy
from pyserilog.events.scalar_value import ScalarValue


class SimpleScalarConversionPolicy(IScalarConversionPolicy):
    def __init__(self, scalar_types: list):
        self._scalar_type = set(scalar_types)

    def try_convert_to_scalar(self, value) -> tuple[bool, ScalarValue | None]:
        if type(value) in self._scalar_type:
            return True, ScalarValue(value)
        return False, None