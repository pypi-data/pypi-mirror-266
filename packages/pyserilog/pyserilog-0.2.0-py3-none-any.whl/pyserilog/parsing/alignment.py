from enum import Enum


class AlignmentDirection(Enum):
    """
    Defines the direction of the alignment.
    """
    LEFT = 0
    """
    Text will be left-aligned.
    """
    RIGHT = 1
    """
    Text will be right-aligned.
    """


class Alignment:
    """
    A structure representing the alignment settings to apply when rendering a property.
    """

    def __init__(self, direction: AlignmentDirection, width: int):
        self.__direction = direction
        self.__width = width

    @property
    def direction(self) -> AlignmentDirection:
        return self.__direction

    @property
    def width(self) -> int:
        return self.__width

    def __eq__(self, other):
        if not isinstance(other, Alignment):
            return False
        return self.__width == other.width and self.direction == other.direction
