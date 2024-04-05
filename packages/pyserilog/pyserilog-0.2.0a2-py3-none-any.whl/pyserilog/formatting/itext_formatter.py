from abc import ABC, abstractmethod

from pyserilog.core.string_writable import StringWriteable


class ITextFormatter(ABC):

    @abstractmethod
    def format(self, log_event, output: StringWriteable):
        pass
