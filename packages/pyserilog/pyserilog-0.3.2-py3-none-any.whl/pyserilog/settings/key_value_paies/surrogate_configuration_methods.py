import types
from typing import Callable

from pyserilog import LoggerConfiguration
from pyserilog.configuration.logger_destructuring_configuration import LoggerDestructuringConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.configuration.logger_filter_configuration import LoggerFilterConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.configuration.logger_audit_sink_configuration import LoggerAuditSinkConfiguration
from pyserilog.core.ilog_event_filter import ILogEventFilter
from pyserilog.core.idestructuring_policy import IDestructuringPolicy
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.sinks.secondary_logger_sink import SecondaryLoggerSink
from pyserilog.events.level_alias import LevelAlias
from pyserilog.events.log_event_level import LogEventLevel


class WriteToSurrogateConfigurationMethods:
    @staticmethod
    def sink(logger_sink_configuration: LoggerSinkConfiguration, sink: ILogEventSink,
             restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
             level_switch: LoggingLevelSwitch = None) -> LoggerConfiguration:
        return logger_sink_configuration.sink(sink, restricted_to_minimum_level, level_switch)

    @staticmethod
    def logger(logger_sink_configuration: LoggerSinkConfiguration,
               configure_logger: Callable[[LoggerConfiguration], types.NoneType],
               restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
               level_switch: LoggingLevelSwitch = None) -> LoggerConfiguration:
        configure = LoggerConfiguration().minimum_level.level_is(LevelAlias.minimum)
        configure_logger(configure)
        sub_logger = configure.create_logger()

        secondary_sink = SecondaryLoggerSink(sub_logger, attempt_dispose=True)
        return logger_sink_configuration.sink(secondary_sink, restricted_to_minimum_level, level_switch)


class AuditToSurrogateConfigurationMethods:
    @staticmethod
    def sink(audit_sink_configuration: LoggerAuditSinkConfiguration, sink: ILogEventSink,
             restricted_to_minimum_level: LogEventLevel = LevelAlias.minimum,
             level_switch: LoggingLevelSwitch = None) -> LoggerConfiguration:
        return audit_sink_configuration.sink(sink, restricted_to_minimum_level, level_switch)


class EnrichSurrogateConfigurationMethods:
    @staticmethod
    def with_enrich(logger_enrichment_configuration: LoggerEnrichmentConfiguration,
                    enricher: ILogEventEnricher) -> LoggerConfiguration:
        return logger_enrichment_configuration.with_enrichers(enricher)

    # @staticmethod
    # def from_log_context(logger_enrichment_configuration: LoggerEnrichmentConfiguration):
    #     logger_enrichment_configuration.with_enrichers(LogContextEnricher)


class DestructuringSurrogateConfigurationMethods:

    @staticmethod
    def with_destructure(logger_destructuring_configuration: LoggerDestructuringConfiguration,
                         policy: IDestructuringPolicy) -> LoggerConfiguration:
        return logger_destructuring_configuration.with_policies(policy)

    @staticmethod
    def as_scalar(logger_destructuring_configuration: LoggerDestructuringConfiguration, scalar_type: type):
        return logger_destructuring_configuration.as_scalar(scalar_type)

    @staticmethod
    def to_maximum_depth(logger_destructuring_configuration: LoggerDestructuringConfiguration,
                         maximum_destructuring_depth: int):
        return logger_destructuring_configuration.to_maximum_depth(maximum_destructuring_depth)

    @staticmethod
    def to_maximum_collection_count(logger_destructuring_configuration: LoggerDestructuringConfiguration,
                                    maximum_collection_count: int):
        return logger_destructuring_configuration.to_maximum_collection_count(maximum_collection_count)

    @staticmethod
    def to_maximum_string_length(logger_destructuring_configuration: LoggerDestructuringConfiguration,
                                 maximum_string_length: int):
        return logger_destructuring_configuration.to_maximum_string_length(maximum_string_length)


class FilterSurrogateConfigurationMethods:

    @staticmethod
    def with_filter(logger_filter_configuration: LoggerFilterConfiguration, event_filter: ILogEventFilter):
        return logger_filter_configuration.with_filter(event_filter)


class SurrogateConfigurationMethods:
    write_to: list[staticmethod] = [
        WriteToSurrogateConfigurationMethods.sink,
        WriteToSurrogateConfigurationMethods.logger
    ]
    audit_to: list[staticmethod] = [
        AuditToSurrogateConfigurationMethods.sink
    ]
    enrich: list[staticmethod] = [
        EnrichSurrogateConfigurationMethods.with_enrich
    ]
    destructure: list[staticmethod] = [
        DestructuringSurrogateConfigurationMethods.with_destructure,
        DestructuringSurrogateConfigurationMethods.as_scalar,
        DestructuringSurrogateConfigurationMethods.to_maximum_depth,
        DestructuringSurrogateConfigurationMethods.to_maximum_collection_count,
        DestructuringSurrogateConfigurationMethods.to_maximum_string_length
    ]
    filter_to: list[staticmethod] = [
        FilterSurrogateConfigurationMethods.with_filter
    ]
