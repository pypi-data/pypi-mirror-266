from typing import Callable

from pyserilog.guard import Guard

from pyserilog.core.ilog_event_enricher import ILogEventEnricher
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.enrichers.conditional_enricher import ConditionalEnricher
from pyserilog.core.enrichers.property_enricher import PropertyEnricher
from pyserilog.core.enrichers.safe_aggregate_enricher import SafeAggregateEnricher
from pyserilog.debuging import SelfLog
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel


class LoggerEnrichmentConfiguration:
    def __init__(self, logger_configuration, add_enricher_function: Callable[[ILogEventEnricher], None]):
        self._logger_configuration = Guard.against_null(logger_configuration)
        self._add_enricher_function = Guard.against_null(add_enricher_function)

    def with_enrichers(self, *enrichers):
        for log_event_enricher in enrichers:
            Guard.against_null(value=log_event_enricher)

            if isinstance(log_event_enricher, ILogEventEnricher):
                self._add_enricher_function(log_event_enricher)
            else:
                raise TypeError(f"enrichers should be type of ILogEventEnricher , error for {log_event_enricher}")
        return self._logger_configuration

    def with_property(self, name: str, value, destructure_objects: bool = False):
        enricher = PropertyEnricher(name, value, destructure_objects)
        return self.with_enrichers(enricher)

    def when(self, condition: Callable[[LogEvent], bool], configure_enricher: Callable):
        Guard.against_null(condition)
        Guard.against_null(configure_enricher)

        return self.wrap(self, lambda e: ConditionalEnricher(e, condition), configure_enricher)

    def at_level(self, level_switch: LoggingLevelSwitch | LogEventLevel, configure_enricher: Callable):
        Guard.against_null(configure_enricher)

        lev: LoggingLevelSwitch = level_switch
        if isinstance(lev, LogEventLevel):
            lev = LoggingLevelSwitch(lev)
        return self.wrap(self, lambda e: ConditionalEnricher(e, lambda le: le.level >= lev.minimum_level),
                         configure_enricher)

    @staticmethod
    def wrap(logger_enrichment_configuration, wrap_enricher: Callable[[ILogEventEnricher], ILogEventEnricher],
             configure_wrapped_enricher: Callable):
        Guard.against_null(logger_enrichment_configuration)
        Guard.against_null(wrap_enricher)
        Guard.against_null(configure_wrapped_enricher)

        enrichers_to_wrap = []
        from pyserilog.logger_configuration import LoggerConfiguration
        capturing_configuration = LoggerConfiguration()
        capturing_logger_enrichment_configuration = LoggerEnrichmentConfiguration(capturing_configuration,
                                                                                  enrichers_to_wrap.append)

        capturing_configuration.enrich = capturing_logger_enrichment_configuration

        configure_wrapped_enricher(capturing_logger_enrichment_configuration)

        if len(enrichers_to_wrap) == 0:
            return logger_enrichment_configuration._logger_configuration

        enclosed = enrichers_to_wrap[0] if len(enrichers_to_wrap) == 0 else SafeAggregateEnricher(enrichers_to_wrap)

        wrapped_enricher = wrap_enricher(enclosed)

        if not hasattr(wrapped_enricher, "__exit__"):
            SelfLog.write_line("Wrapping enricher {0} does not implement IDisposable; to ensure " + \
                               "wrapped enrichers are properly disposed, wrappers should dispose " + \
                               "their wrapped contents", wrapped_enricher)

        return logger_enrichment_configuration.with_enrichers(wrapped_enricher)
