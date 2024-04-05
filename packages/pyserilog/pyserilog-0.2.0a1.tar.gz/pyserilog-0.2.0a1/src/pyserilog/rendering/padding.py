from pyserilog.core.string_writable import StringWriteable

from pyserilog.parsing.alignment import Alignment, AlignmentDirection


class Padding:

    @staticmethod
    def apply(output: StringWriteable, value: str, text_alignment: Alignment | None):
        if text_alignment is None or len(value) >= text_alignment.width:
            output.write(value)
            return

        pad: int = text_alignment.width - len(value)
        if text_alignment.direction == AlignmentDirection.LEFT:
            output.write(value)
        output.write(' ' * pad)
        if text_alignment.direction == AlignmentDirection.RIGHT:
            output.write(value)
