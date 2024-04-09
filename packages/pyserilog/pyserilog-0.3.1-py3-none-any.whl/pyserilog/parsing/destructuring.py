from enum import Enum


class Destructuring(Enum):
    """
    Instructs the logger on how to store information about provided parameters.
    """
    DEFAULT = 0
    """
    Convert known types and objects to scalars, arrays to sequences.
    """
    STRINGIFY = 1
    """
    Convert all types to scalar strings. Prefix name with '$'.
    """
    DESTRUCTURE = 2
    """
    Convert known types to scalars, destructure objects and collections 
    into sequences and structures. Prefix name with '@'.
    """