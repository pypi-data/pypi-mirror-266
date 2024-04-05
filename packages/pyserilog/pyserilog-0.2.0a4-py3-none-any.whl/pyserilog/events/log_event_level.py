from enum import Enum;


class LogEventLevel(Enum):
    """
    Specifies the meaning and relative importance of a log event.
    """
    VERBOSE = 0,
    """
    Anything and everything you might want to know about a running block of code.
    """
    DEBUG = 1,
    """
    Internal system events that aren't necessarily observable from the outside.
    """
    INFORMATION = 2,
    """
    The lifeblood of operational intelligence - things happen.
    """
    WARNING = 3,
    """
    Service is degraded or endangered.
    """
    ERROR = 4,
    """
    Functionality is unavailable, invariants are broken or data is lost.
    """
    FATAL = 5,
    """
    If you have a pager, it goes off when one of these occurs.

    """

    def get_int(self):
        return self.value[0]

    def __gt__(self, other):
        if isinstance(other, LogEventLevel):
            return self.value > other.value

        raise Exception("Invalid Compare")

    def __ge__(self, other):
        if isinstance(other, LogEventLevel):
            return self.value >= other.value
        raise Exception("Invalid Compare")

    def __add__(self, other):
        if isinstance(other, int):
            val = other + self.get_int()
            t = self.__convert_from_int(val)
            return t
        if isinstance(other, LogEventLevel):
            val1 = other.get_int()
            val2 = self.get_int()
            return self.__convert_from_int(val1 + val2)
        raise TypeError()

    @staticmethod
    def __convert_from_int(val: int):
        for p in LogEventLevel:
            if p.value[0] == val:
                return p
        return ValueError("invalid range number")
