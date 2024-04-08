from typing import Callable
from pyserilog.core.string_writable import StringWriteable


class SelfLog:
    _output: Callable[[str], None] = None

    @staticmethod
    def write_line(log_format: str, *args):
        if SelfLog._output is not None:
            res = log_format.format(*args)
            SelfLog._output(res)

    @staticmethod
    def enable(output: Callable[[str], None] | StringWriteable):
        if isinstance(output, StringWriteable):
            SelfLog._output = lambda x: SelfLog.__write_with_string_io(x, output)
        else:
            SelfLog._output = output

    @staticmethod
    def disable():
        SelfLog._output = None

    @staticmethod
    def __write_with_string_io(value: str, output: StringWriteable):
        output.write(value)
