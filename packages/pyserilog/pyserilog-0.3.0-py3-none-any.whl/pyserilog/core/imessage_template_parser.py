from abc import ABC, abstractmethod

from pyserilog.events import message_template


class IMessageTemplateParser(ABC):

    @abstractmethod
    def parse(self, message_template: str) -> message_template:
        pass
