from abc import ABC, abstractmethod

from pyserilog.events.scalar_value import ScalarValue


class IScalarConversionPolicy(ABC):
    @abstractmethod
    def try_convert_to_scalar(self, value) -> tuple[bool, ScalarValue | None]:
        pass
