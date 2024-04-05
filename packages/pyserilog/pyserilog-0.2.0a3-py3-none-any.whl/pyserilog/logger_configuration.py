import sys

from pyserilog.capturing.message_template_processor import MessageTemplateProcessor
from pyserilog.capturing.property_value_converter import PropertyValueConverter
from pyserilog.configuration.logger_destructuring_configuration import LoggerDestructuringConfiguration
from pyserilog.configuration.logger_filter_configuration import LoggerFilterConfiguration
from pyserilog.configuration.logger_minimum_level_configuration import LoggerMinimumLevelConfiguration
from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.ilog_event_filter import ILogEventFilter
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.level_override_map import LevelOverrideMap
from pyserilog.core.logger import Logger
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.enrichers.empty_enricher import EmptyEnricher
from pyserilog.core.enrichers.safe_aggregate_enricher import SafeAggregateEnricher
from pyserilog.core.sinks.aggregate_sink import AggregateSink
from pyserilog.core.sinks.filtering_sink import FilteringSink
from pyserilog.core.sinks.safe_aggregate_sink import SafeAggregateSink
from pyserilog.debuging import SelfLog
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.level_alias import LevelAlias
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.configuration.logger_audit_sink_configuration import LoggerAuditSinkConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration


class LoggerConfiguration:
    def __init__(self):
        self._log_event_sinks: list[ILogEventSink] = []
        self._audit_sinks: list[ILogEventSink] = []
        self._enrichers: list[ILogEventEnricher] = []
        self._filters: list[ILogEventFilter] = []
        self._additional_scalar_types: list[type] = []
        self._additional_destructuring_policies: list[IDestructuringPolicy] = []
        self._overrides: dict[str, LoggingLevelSwitch] = {}
        self._maximum_destructuring_depth = 10
        self._maximum_string_length = sys.maxsize
        self._maximum_collection_count = sys.maxsize

        self._write_to = LoggerSinkConfiguration(self, lambda s: self._log_event_sinks.append(s))
        self._enrich = LoggerEnrichmentConfiguration(self, lambda s: self._enrichers.append(s))

        self._logger_created = False
        self._minimum_level: LogEventLevel = LogEventLevel.INFORMATION
        self._level_switch: LoggingLevelSwitch | None = None

    @property
    def write_to(self) -> LoggerSinkConfiguration:
        """
        Configures the sinks that log events will be emitted to.
        """
        return self._write_to

    @property
    def audit_to(self) -> LoggerAuditSinkConfiguration:
        """
        Configures sinks for auditing, instead of regular (safe) logging. When auditing is used,
        exceptions from sinks and any intermediate filters propagate back to the caller. Most callers
        should use "write_to" instead

        Not all sinks are compatible with transactional auditing requirements (many will use asynchronous
        batching to improve write throughput and latency). Sinks need to opt-in to auditing support by
        extending "LoggerAuditSinkConfiguration", though the generic "LoggerAuditSinkConfiguration.Sink"
        method allows any sink class to be adapted for auditing.
        """

        def add_sink_function(event_sink: ILogEventSink):
            self._audit_sinks.append(event_sink)

        return LoggerAuditSinkConfiguration(self, add_sink_function=add_sink_function)

    @property
    def minimum_level(self) -> LoggerMinimumLevelConfiguration:
        def set_minimum_func(level: LogEventLevel):
            self._minimum_level = level
            self._level_switch = None

        def set_level_switch_func(level_switch: LoggingLevelSwitch):
            self._level_switch = level_switch

        def add_override_func(source: str, level_switch: LoggingLevelSwitch):
            self._overrides[source] = level_switch

        return LoggerMinimumLevelConfiguration(logger_configuration=self, set_minimum_func=set_minimum_func,
                                               set_level_switch_func=set_level_switch_func,
                                               add_override_func=add_override_func
                                               )

    @property
    def enrich(self) -> LoggerEnrichmentConfiguration:
        """
        Configures enrichment of <see cref="LogEvent"/>s. Enrichers can add, remove and
        modify the properties associated with events.
        :return:
        """
        return self._enrich

    @enrich.setter
    def enrich(self, value: LoggerEnrichmentConfiguration):
        self._enrich = value

    @property
    def filter(self) -> LoggerFilterConfiguration:
        def add_filter(log_event_filer: ILogEventFilter):
            self._filters.append(log_event_filer)

        return LoggerFilterConfiguration(self, add_filter)

    @property
    def destructure(self) -> LoggerDestructuringConfiguration:
        def set_maximum_depth_func(x: int):
            self._maximum_destructuring_depth = x

        def set_maximum_collection_count(x: int):
            self._maximum_collection_count = x

        def set_maximum_string_length(x: int):
            self._maximum_string_length = x

        def add_scalar_func(scalar_type: type):
            self._additional_scalar_types.append(scalar_type)

        return LoggerDestructuringConfiguration(
            logger_configuration=self,
            add_scalar_func=add_scalar_func,
            add_policy_func=self._additional_destructuring_policies.append,
            set_maximum_depth_func=set_maximum_depth_func,
            set_maximum_collection_count=set_maximum_collection_count,
            set_maximum_string_length=set_maximum_string_length
        )

    @property
    def read_from(self):
        from pyserilog.configuration.logger_settings_configuration import LoggerSettingsConfiguration
        return LoggerSettingsConfiguration(self)


    def create_logger(self) -> Logger:
        if self._logger_created:
            raise PermissionError("create_logger() was previously called and can only be called once.")

        self._logger_created = True

        sink = self.__get_sink()
        enricher = self.__get_enricher()
        overrider_map = self.__get_overrider_map()
        processor = self.__get_template_processor()
        exit_func = self.__exit_sinks_func

        minimum_level = LevelAlias.minimum if self._level_switch is not None else self._minimum_level
        return Logger(processor, minimum_level, self._level_switch, sink, enricher, exit_func, overrider_map)

    def __get_template_processor(self):
        propagate_exception = len(self._audit_sinks) > 0
        converter = PropertyValueConverter(self._maximum_destructuring_depth,
                                           self._maximum_string_length,
                                           self._maximum_collection_count,
                                           self._additional_scalar_types,
                                           self._additional_destructuring_policies,
                                           propagate_exception
                                           )
        processor = MessageTemplateProcessor(converter)
        return processor

    def __get_enricher(self):
        match len(self._enrichers):
            case 0:
                return EmptyEnricher()
            case 1:
                return self._enrichers[0]
            case _:
                return SafeAggregateEnricher(self._enrichers)

    def __get_overrider_map(self) -> LevelOverrideMap:
        if len(self._overrides) > 0:
            return LevelOverrideMap(self._overrides, self._minimum_level, self._level_switch)
        return None

    def __exit_sinks_func(self, exc_type, exc_val, exc_tb):
        all_handlers = []
        all_handlers.extend(self._log_event_sinks)
        all_handlers.extend(self._audit_sinks)

        for hand in all_handlers:
            try:
                if hasattr(hand, "__exit__"):
                    hand.__exit__(exc_type, exc_val, exc_tb)
            except Exception as ex:
                SelfLog.write_line("error {0} happened in exit {1} ", ex, hand)

    def __get_sink(self) -> ILogEventSink:
        sink: ILogEventSink = None
        if len(self._log_event_sinks) > 0:
            sink = SafeAggregateSink(self._log_event_sinks)

        auditing = len(self._audit_sinks) > 0
        if auditing:
            sinks = []
            if sink is not None:
                sinks.append(sink)
            sinks.extend(self._audit_sinks)
            sink = AggregateSink(sinks)

        if sink is None:
            sink = SafeAggregateSink([])

        if len(self._filters) > 0:
            sink = FilteringSink(sink, self._filters, auditing)

        return sink
