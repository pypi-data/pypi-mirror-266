from pyserilog.core.iscalar_conversion_policy import IScalarConversionPolicy
from pyserilog.events.scalar_value import ScalarValue


class ByteArrayScalarConversionPolicy(IScalarConversionPolicy):
    maximum_byte_array_length: int = 1024

    def try_convert_to_scalar(self, value) -> tuple[bool, ScalarValue | None]:
        if isinstance(value, bytearray) or \
                (isinstance(value, list) and len(value) > 0 and isinstance(value[0], bytes)):
            value = b''.join(value)

        if not isinstance(value, bytes):
            return False, None

        if len(value) > self.maximum_byte_array_length:
            start : str = value[0:16].hex().upper()
            hex_str = f"{start}… ({len(value)} bytes)"
        else:
            hex_str = value.hex()
        return True, ScalarValue(hex_str)
