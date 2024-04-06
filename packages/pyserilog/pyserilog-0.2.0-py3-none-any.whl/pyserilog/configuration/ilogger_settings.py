from abc import ABC, abstractclassmethod, abstractmethod

from pyserilog import LoggerConfiguration


class ILoggerSettings(ABC):

    @abstractmethod
    def configure(self, logger_configuration: LoggerConfiguration):
        pass
