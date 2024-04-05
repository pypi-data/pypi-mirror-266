from abc import ABC, abstractmethod


class ILogEventPropertyFactory(ABC):

    @abstractmethod
    def create_property(self, name : str , value, destructure_objects : bool = False):
        """
        Construct a :ref <see cref="LogEventProperty"/> with the specified name and value.
        :param name: The name of the property.
        :param value:The value of the property.
        :param destructure_objects: If 'True', and the value is a non-primitive, non-array type,
        then the value will be converted to a structure; otherwise, unknown types will
        be converted to scalars, which are generally stored as strings.
        :return: Created "LogEventProperty" instance.
        """
        pass
