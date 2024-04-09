from abc import ABC, abstractmethod
from pyserilog.core.string_writable import StringIOWriteable,StringWriteable
from typing import Callable


class LogEventPropertyValue(ABC):

    @abstractmethod
    def render(self, output: StringWriteable, text_format: str | None = None, formatter: Callable[[object], str] = None):
        pass

    def __str__(self) -> str:
        string_writer = StringIOWriteable()
        self.render(string_writer)
        res = string_writer.getvalue()
        string_writer.close()
        return res
