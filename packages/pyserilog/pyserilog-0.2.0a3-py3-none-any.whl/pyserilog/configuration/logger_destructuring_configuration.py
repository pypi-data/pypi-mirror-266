from typing import Callable

import pyserilog.logger_configuration as logConf
from pyserilog.guard import Guard, NoneError
from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.policies.projected_destructuring_policy import ProjectedDestructuringPolicy


class LoggerDestructuringConfiguration:
    """
    Controls template parameter destructuring configuration.
    """

    def __init__(self, logger_configuration, add_scalar_func: Callable[[type], None],
                 add_policy_func: Callable[[IDestructuringPolicy], None],
                 set_maximum_depth_func: Callable[[int], None], set_maximum_string_length: Callable[[int], None],
                 set_maximum_collection_count: Callable[[int], None]
                 ):
        self._logger_configuration = Guard.against_null(logger_configuration)
        self._add_scalar_func: Callable[[type], None] = Guard.against_null(add_scalar_func)
        self._add_policy_func: Callable[[IDestructuringPolicy], None] = Guard.against_null(add_policy_func)
        self._set_maximum_depth_func: Callable[[int], None] = Guard.against_null(set_maximum_depth_func)
        self._set_maximum_string_length: Callable[[int], None] = Guard.against_null(set_maximum_string_length)
        self._set_maximum_collection_count: Callable[[int], None] = Guard.against_null(set_maximum_collection_count)

    def as_scalar(self, scalar_type: type):
        """
        Treat objects of the specified type as scalar values, i.e., don't
        break them down into properties even when destructuring complex types.
        :param scalar_type: Type to treat as scalar.
        :return: Configuration object allowing method chaining.
        """
        Guard.against_null(scalar_type)

        self._add_scalar_func(scalar_type)
        return self._logger_configuration

    def with_policies(self, *destructuring_policies):
        """
        When destructuring objects, transform instances with the provided policies.
        :param destructuring_policies: Policies to apply when destructuring.
        :return: Configuration object allowing method chaining.
        """

        for destructuring_policy in destructuring_policies:
            if destructuring_policy is None:
                return NoneError("None policy is not allowed.")
            if isinstance(destructuring_policy, IDestructuringPolicy):
                self._add_policy_func(destructuring_policy)
            else:
                raise ValueError("type of policies should be IDestructuringPolicy")

        return self._logger_configuration

    def by_transforming(self, value_type: type, transformation_func: Callable):
        """
        When destructuring objects, transform instances of the specified type with the provided function.
        :param value_type:
        :param transformation_func:
        :return:
        """
        Guard.against_null(transformation_func)

        policy = ProjectedDestructuringPolicy(can_apply_func=lambda x: x == value_type,
                                              projection_func=lambda o: transformation_func(o))
        return self.with_policies(policy)

    def to_maximum_depth(self, maximum_destructuring_depth: int):
        """
        When destructuring objects, depth will be limited to 10 property traversals deep to
        guard against ballooning space when recursive/cyclic structures are accidentally passed. To
        change this limit pass a new maximum depth.
        :param maximum_destructuring_depth: The maximum depth to use.
        :return: Configuration object allowing method chaining.
        """
        if maximum_destructuring_depth < 0:
            raise ValueError("Maximum destructuring depth must be positive.")

        self._set_maximum_depth_func(maximum_destructuring_depth)
        return self._logger_configuration

    def to_maximum_string_length(self, maximum_string_length: int):
        """
        When destructuring objects, string values can be restricted to specified length
        thus avoiding bloating payload. Limit is applied to each value separately,
        sum of length of strings can exceed limit.
        :param maximum_string_length: The maximum string length.
        :return: Configuration object allowing method chaining.
        """
        if maximum_string_length < 2:
            raise ValueError("Maximum string length must be at least two.")

        self._set_maximum_string_length(maximum_string_length)
        return self._logger_configuration

    def to_maximum_collection_count(self, maximum_collection_count: int):
        """
        When destructuring objects, collections be restricted to specified count
        thus avoiding bloating payload. Limit is applied to each collection separately,
        sum of length of collection can exceed limit.
        Applies limit to all "list" including dictionaries.
        :param maximum_collection_count:
        :return: Configuration object allowing method chaining.
        """
        if maximum_collection_count < 1:
            raise ValueError("Maximum collection length must be at least one.")
        self._set_maximum_collection_count(maximum_collection_count)
        return self._logger_configuration
