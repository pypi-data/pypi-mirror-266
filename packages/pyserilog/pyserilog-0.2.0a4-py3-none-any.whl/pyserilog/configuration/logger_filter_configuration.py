from typing import Callable

from pyserilog.guard import Guard
from pyserilog.core.ilog_event_filter import ILogEventFilter
from pyserilog.core.filter.delegate_filter import DelegateFilter
from pyserilog.events.log_event import LogEvent


class LoggerFilterConfiguration:

    def __init__(self, logger_configuration, add_filter: Callable[[ILogEventFilter], None]):
        self._logger_configuration = Guard.against_null(logger_configuration)
        self._add_filter: Callable[[ILogEventFilter], None] = Guard.against_null(add_filter)

    def with_filter(self, *filters):
        """
        Filter out log events from the stream based on the provided filter.
        :param filters: The filters to apply.
        :return: Configuration object allowing method chaining.
        """
        for log_event_filer in filters:
            if log_event_filer is None:
                raise ValueError("Null filter is not allowed.")
            self._add_filter(log_event_filer)
        return self._logger_configuration

    def by_excluding(self, exclusion_predicate: Callable[[LogEvent], bool]):

        def is_enable_func(log_level: LogEvent):
            res = not exclusion_predicate(log_level)
            return res

        return self.with_filter(DelegateFilter(is_enable_func=is_enable_func))

    def by_including_only(self, inclusion_predicate: Callable[[LogEvent], bool]):
        return self.with_filter(DelegateFilter(inclusion_predicate))
