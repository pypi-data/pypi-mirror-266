from typing import Callable

import pytest

from pyserilog.core.enrichers.conditional_enricher import ConditionalEnricher
from support.collecting_enricher import CollectingEnricher
from test_dummies import *
from dummy_wrapping_sink import DummyWrappingSink
from pyserilog.logger_configuration import LoggerConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.core.constants import Constants
from pyserilog.core.ilog_event_property_value_factory import ILogEventPropertyValueFactory
from pyserilog.core.ilog_event_sink import ILogEventSink
from pyserilog.core.logger import Logger
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.core.filter.delegate_filter import DelegateFilter
from pyserilog.events.log_event import LogEvent
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.events.scalar_value import ScalarValue
from pyserilog.events.structure_value import StructureValue
from pyserilog.policies.ProjectedDestructuringPolicy import ProjectedDestructuringPolicy
from support.collecting_sink import CollectingSink
from support.delegating_enricher import DelegatingEnricher
from support.some import Some
from support.delegating_sink import DelegatingSink
from support.string_sink import StringSink


class AB:
    def __init__(self):
        self._a: int = 0
        self._b: int = 0

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self._a = value

    @property
    def b(self):
        return self._b

    @b.setter
    def b(self, value):
        self._b = value


def log_and_get_as_string(x, config_func: Callable[[LoggerConfiguration], LoggerConfiguration],
                          destructuring_symbol: str = ""):
    evt = {'res': None}

    def write_func(log_event: LogEvent):
        evt['res'] = log_event

    log_conf = LoggerConfiguration() \
        .write_to.sink(DelegatingSink(write_func))
    log_conf = config_func(log_conf)
    log = log_conf.create_logger()

    log.information(f"{{{destructuring_symbol}X}}", x)

    assert evt['res'] is not None
    res = evt['res']
    assert isinstance(res, LogEvent)
    return str(res.properties["X"])


class ToStringOfLength:

    def __init__(self, to_string_of_length: int):
        self._to_string_of_length = to_string_of_length

    def __str__(self):
        return "#" * self._to_string_of_length


class Expando(object):
    pass


class Value:
    pass


class DisposableSink(ILogEventSink):
    def __init__(self):
        self.is_disposed = False

    def emit(self, log_event: LogEvent):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_disposed = True


class TestLoggerConfiguration:
    class DisposableSink(ILogEventSink):

        def __init__(self):
            self._is_disposed = False

        @property
        def is_disposed(self):
            return self._is_disposed

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._is_disposed = True

        def emit(self, log_event: LogEvent):
            pass

    def test_disposable_sinks_are_disposed_along_with_root_logger(self):
        sink = TestLoggerConfiguration.DisposableSink()
        with LoggerConfiguration() \
                .write_to \
                .sink(sink) \
                .create_logger():
            # Do nothing
            assert True

        assert sink.is_disposed

    def test_disposable_sinks_are_not_disposed_along_with_contextual_loggers(self):
        sink = DisposableSink()
        with LoggerConfiguration() \
                .write_to.sink(sink) \
                .create_logger() \
                .for_context(TestLoggerConfiguration):
            pass

        assert not sink.is_disposed

    def test_a_filter_prevents_matched_events_from_passing_to_the_sink(self):
        excluded = Some.information_event()
        included = Some.information_event()

        delegate_filter = DelegateFilter(lambda e: e.message_template != excluded.message_template)
        events = []
        sink = DelegatingSink(events.append)
        logger = LoggerConfiguration() \
            .write_to.sink(sink) \
            .filter.with_filter(delegate_filter) \
            .create_logger()
        logger.write_event(included)
        logger.write_event(excluded)

        assert len(events) == 1
        assert included in events

    def test_specifying_that_a_type_is_scalar_causes_it_to_be_logged_as_scalar_even_when_destructuring(self):
        events = []
        sink = DelegatingSink(events.append)

        with LoggerConfiguration() \
                .write_to.sink(sink) \
                .destructure.as_scalar(AB) \
                .create_logger() as logger:
            logger.information("{@AB}", AB())

            assert len(events) == 1
            ev: LogEvent = events[0]
            prop = ev.properties["AB"]
            assert isinstance(prop, ScalarValue)

    def test_destructuring_system_type_gives_scalar_by_default(self):
        events: list[LogEvent] = []
        sink = DelegatingSink(events.append)

        logger = LoggerConfiguration() \
            .write_to.sink(sink) \
            .create_logger()

        this_type = TestLoggerConfiguration
        logger.information("{@this_type}", this_type)

        ev: LogEvent = events[0]
        prop = ev.properties["this_type"]

        assert isinstance(prop, ScalarValue)
        assert this_type == prop.value

    def test_destructuring_is_possible_for_system_type_derived_properties(self):
        events: list[LogEvent] = []
        sink = DelegatingSink(events.append)

        def can_apply_func(input_typ: type):
            return issubclass(type, input_typ)

        def projection_func(input_typ: type):
            return input_typ.__name__

        policy = ProjectedDestructuringPolicy(can_apply_func=can_apply_func, projection_func=projection_func)
        logger = LoggerConfiguration() \
            .destructure \
            .with_policies(policy) \
            .write_to.sink(sink) \
            .create_logger()

        this_type = TestLoggerConfiguration
        logger.information("{@this_type}", this_type)

        ev = events[0]
        prop = ev.properties["this_type"]
        assert isinstance(prop, ScalarValue)
        assert this_type.__name__ == prop.value

    def test_transformations_are_applied_to_event_properties(self):
        events: list[LogEvent] = []
        sink = DelegatingSink(events.append)

        class TestC:
            def __init__(self, value):
                self._c_property = value

            @property
            def c_property(self):
                return self._c_property

            @c_property.setter
            def c_property(self, value):
                self._c_property = value

        def create_test(k):
            return TestC(k)

        logger = LoggerConfiguration() \
            .write_to.sink(sink) \
            .destructure \
            .by_transforming(AB, create_test) \
            .create_logger()

        logger.information("{@AB}", AB())

        ev = events[0]
        prop = ev.properties["AB"]

        assert isinstance(prop, StructureValue)
        sv = prop.properties[0]
        assert "c_property" == sv.name

    def test_writing_to_a_logger_writes_to_sub_logger(self):
        event_received = {'res': False}

        def configure_logger_function(l: LoggerConfiguration):
            def set_val(k):
                event_received['res'] = True

            l.write_to.sink(DelegatingSink(set_val))

        logger = LoggerConfiguration() \
            .write_to \
            .logger(configure_logger_function) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert event_received['res']

    def test_sub_logger_restricts_filter(self):
        event_received = {'res': False}

        def configure_logger_function(l: LoggerConfiguration):
            def set_val(k):
                event_received['res'] = True

            log: LoggerConfiguration = l.minimum_level.fatal()
            log.write_to.sink(DelegatingSink(set_val))

        logger = LoggerConfiguration() \
            .write_to.logger(configure_logger_function) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert not event_received['res']

    def test_enrichers_execute_in_configuration_order(self):
        prop = Some.log_event_property()
        enriched_property_seen = {'res': False}

        def first(log_event: LogEvent, factory: ILogEventPropertyValueFactory):
            t = factory
            log_event.add_property_if_absent(prop)

        def second(log_event: LogEvent, factory: ILogEventPropertyValueFactory):
            t = factory
            enriched_property_seen['res'] = prop.name in log_event.properties

        logger_conf: LoggerConfiguration = LoggerConfiguration().write_to.sink(StringSink())
        logger_conf: LoggerConfiguration = logger_conf.enrich.with_enrichers(DelegatingEnricher(first))
        logger: Logger = logger_conf.enrich.with_enrichers(DelegatingEnricher(second)).create_logger()

        logger.write_event(Some.information_event())

        assert enriched_property_seen['res']

    def test_maximum_destructuring_depth_default_is_effective(self):
        x = Expando()
        x.lvl1 = Expando()
        x.lvl1.lvl2 = Expando()
        x.lvl1.lvl2.lvl3 = Expando()
        x.lvl1.lvl2.lvl3.lvl4 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6.lvl7 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6.lvl7.lvl8 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6.lvl7.lvl8.lvl9 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6.lvl7.lvl8.lvl9.lvl10 = Expando()
        x.lvl1.lvl2.lvl3.lvl4.lvl5.lvl6.lvl7.lvl8.lvl9.lvl10 = "lvl11"

        xs = log_and_get_as_string(x, lambda conf: conf, "@")

        assert "lvl10" in xs
        assert "lvl11" not in xs

    def test_maximum_destructuring_depth_is_effective(self):
        x = Expando()
        x.a_filed = Expando()
        x.a_filed.b_filed = Expando()
        x.a_filed.b_filed.c_filed = Expando()
        x.a_filed.b_filed.c_filed.d_field = Expando()
        x.a_filed.b_filed.c_filed.d_field = "f"

        def config_func(conf: LoggerConfiguration):
            return conf.destructure.to_maximum_depth(3)

        xs = log_and_get_as_string(x, config_func, "@")

        assert "c_filed" in xs
        assert "d_filed" not in xs

    def test_maximum_string_length_throws_for_limit_lower_than2(self):
        with pytest.raises(ValueError) as ex:
            LoggerConfiguration().destructure.to_maximum_string_length(1)

    def test_maximum_string_length_not_effective_for_string(self):
        x = "ABCD"
        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(3))

        assert "\"ABCD\"" == limited_text

    def test_maximum_string_length_effective_for_captured_string(self):
        x = "ABCD"

        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(3), "@")

        assert "\"AB…\"" == limited_text

    def test_maximum_string_length_effective_for_stringified_string(self):
        x = "ABCD"

        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(3), "$")

        assert "\"AB…\"" == limited_text

    @pytest.mark.parametrize("text,text_after,limit", [("1234", "12…", 3), ("123", "123", 3)])
    def test_maximum_string_length_effective_for_captured_object(self, text: str, text_after: str, limit: int):
        x = Expando()
        x.too_long_text = text

        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(limit), "@")

        assert text_after in limited_text

    def test_maximum_string_length_effective_for_stringified_object(self):
        x = ToStringOfLength(4)

        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(3), "$")
        assert "##…" in limited_text

    def test_maximum_string_length_not_effective_for_object(self):
        x = ToStringOfLength(4)

        limited_text = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_string_length(3))

        assert "####" in limited_text

    def test_maximum_string_collection_throws_for_limit_lower_than1(self):
        with pytest.raises(ValueError) as ve:
            LoggerConfiguration().destructure.to_maximum_collection_count(0)

    def test_maximum_collection_count_not_effective_for_array_as_long_as_limit(self):
        x = [1, 2, 3]

        limited_collection = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_collection_count(3))

        assert "3" in limited_collection

    def test_maximum_collection_count_effective_for_array_than_limit(self):
        x = [1, 2, 3, 4]

        limited_collection = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_collection_count(3))

        assert "3" in limited_collection
        assert "4" not in limited_collection

    def test_maximum_collection_count_effective_for_dictionary_with_more_keys_than_limit(self):
        x = {
            "1": 1,
            "2": 2,
            "3": 3
        }

        limited_collection = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_collection_count(2))

        assert "2" in limited_collection
        assert "3" not in limited_collection

    def test_maximum_collection_count_not_effective_for_dictionary_with_as_many_keys_as_limit(self):
        x = {
            "1": 1,
            "2": 2,
        }

        limited_collection = log_and_get_as_string(x, lambda conf: conf.destructure.to_maximum_collection_count(2))

        assert "2" in limited_collection

    def test_dynamically_switching_sink_restricts_output(self):
        events_received = {'res': 0}
        level_switch = LoggingLevelSwitch()

        def write_func(log_event: LogEvent):
            events_received['res'] += 1

        logger = LoggerConfiguration() \
            .write_to.sink(DelegatingSink(write_func), level_switch=level_switch) \
            .create_logger()

        logger.write_event(Some.information_event())
        level_switch.minimum_level = LogEventLevel.WARNING
        logger.write_event(Some.information_event())
        level_switch.minimum_level = LogEventLevel.VERBOSE
        logger.write_event(Some.information_event())

        assert 2 == events_received['res']

    def test_level_switch_takes_precedence_over_minimum_level(self):
        sink = CollectingSink()

        logger = LoggerConfiguration() \
            .write_to.sink(sink, LogEventLevel.FATAL, LoggingLevelSwitch()) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert len(sink.events) == 1

    def test_last_minimum_level_configuration_wins(self):
        sink = CollectingSink()

        logger_conf: LoggerConfiguration = LoggerConfiguration() \
            .minimum_level.controlled_by(LoggingLevelSwitch(LogEventLevel.FATAL))
        logger_conf: LoggerConfiguration = logger_conf.minimum_level.debug()
        logger: Logger = logger_conf.write_to.sink(sink) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert len(sink.events) == 1

    def test_higher_minimum_level_overrides_are_propagated(self):
        sink = CollectingSink()

        logger_conf: LoggerConfiguration = LoggerConfiguration() \
            .minimum_level.debug()
        logger_conf: LoggerConfiguration = logger_conf.minimum_level.override("Microsoft", LogEventLevel.FATAL)
        logger: Logger = logger_conf.write_to.sink(sink).create_logger()

        logger.write_event(Some.information_event())
        logger.for_context(Constants.SOURCE_CONTEXT_PROPERTY_NAME, "Microsoft.AspNet.Something") \
            .write_event(Some.information_event())
        logger.for_context(TestLoggerConfiguration).write_event(Some.information_event())

        assert 2 == len(sink.events)

    def test_lower_minimum_level_overrides_are_propagated(self):
        sink = CollectingSink()

        logger: Logger = LoggerConfiguration() \
            .minimum_level.error() \
            .minimum_level.override("Microsoft", LogEventLevel.DEBUG) \
            .write_to.sink(sink) \
            .create_logger()

        logger.write_event(Some.information_event())
        logger.for_context(Constants.SOURCE_CONTEXT_PROPERTY_NAME, "Microsoft.AspNet.Something") \
            .write_event(Some.information_event())
        logger.for_context(TestLoggerConfiguration) \
            .write_event(Some.information_event())

        assert 1 == len(sink.events)

    def test_exceptions_thrown_by_sinks_are_not_propagated(self):
        def func(x):
            raise Exception("Boom!")

        logger = LoggerConfiguration() \
            .write_to.sink(DelegatingSink(func)) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert True, "No exception reached the caller"

    def test_exceptions_thrown_by_sinks_are_not_propagated_even_when_auditing_is_present(self):
        def func(x):
            raise Exception("Boom!")

        logger = LoggerConfiguration() \
            .audit_to.sink(CollectingSink()) \
            .write_to.sink(DelegatingSink(func)) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert True, "No exception reached the caller"

    def test_exceptions_thrown_by_filters_are_not_propagated(self):
        def func(x):
            raise Exception("Boom!")

        logger = LoggerConfiguration() \
            .filter.by_excluding(func) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert True, "No exception reached the caller"

    def test_exceptions_thrown_by_destructuring_policies_are_not_propagated(self):
        def func(x):
            raise Exception("Boom!")

        logger = LoggerConfiguration() \
            .write_to.sink(CollectingSink()) \
            .destructure.by_transforming(Value, func) \
            .create_logger()

        logger.information("{@Value}", Value())

        assert True, "No exception reached the caller"

    def test_wrapping_decorates_the_configured_sink(self):
        DummyWrappingSink.reset()
        sink = CollectingSink()
        logger_conf = DummyLoggerConfigurationExtensions.dummy(LoggerConfiguration().write_to, lambda w: w.sink(sink))
        logger = logger_conf.create_logger()

        evt = Some.information_event()
        logger.write_event(evt)

        em: list = DummyWrappingSink.emitted()
        assert evt == em[0]
        assert evt == sink.single_event

    def test_wrapping_does_not_permit_enrichment(self):
        sink = CollectingSink()
        property_name = Some.string()
        logger = LoggerConfiguration().write_to.dummy(lambda w: w.sink(sink) \
                                                      .enrich.with_property(property_name, 1)) \
            .create_logger()

        evt = Some.information_event()
        logger.write_event(evt)

        assert evt == sink.single_event
        assert property_name not in evt.properties

    def test_wrapping_is_applied_when_chaining(self):
        DummyWrappingSink.reset()
        sink1 = CollectingSink()
        sink2 = CollectingSink()
        logger = LoggerConfiguration().write_to.dummy(lambda w: w.sink(sink1).write_to.sink(sink2)) \
            .create_logger()

        evt = Some.information_event()
        logger.write_event(evt)

        assert evt == DummyWrappingSink.emitted()[0]
        assert evt == sink1.single_event
        assert evt == sink2.single_event

    def test_wrapping_is_applied_when_calling_multiple_times(self):
        DummyWrappingSink.reset()
        sink1 = CollectingSink()
        sink2 = CollectingSink()

        def func(w: LoggerSinkConfiguration):
            w.sink(sink1)
            w.sink(sink2)

        logger = LoggerConfiguration().write_to.dummy(func) \
            .create_logger()

        evt = Some.information_event()
        logger.write_event(evt)

        assert evt == DummyWrappingSink.emitted()[0]
        assert evt == sink1.single_event
        assert evt == sink2.single_event

    def test_wrapping_sink_respects_log_event_level_setting(self):
        DummyWrappingSink.reset()
        sink = CollectingSink()
        logger = LoggerConfiguration() \
            .write_to.dummy_wrap(lambda w: w.sink(sink), LogEventLevel.ERROR, None) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert len(DummyWrappingSink.emitted()) == 0
        assert 0 == len(sink.events)

    def test_wrapping_sink_respects_level_switch_setting(self):
        DummyWrappingSink.reset()
        sink = CollectingSink()
        logger = LoggerConfiguration() \
            .write_to.dummy_wrap(
            lambda w: w.sink(sink), LogEventLevel.VERBOSE,
            LoggingLevelSwitch(LogEventLevel.ERROR)) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert len(DummyWrappingSink.emitted()) == 0
        assert len(sink.events) == 0

    def test_wrapping_sink_receives_events_when_level_is_appropriate(self):
        DummyWrappingSink.reset()
        sink = CollectingSink()
        logger = LoggerConfiguration() \
            .write_to.dummy_wrap(
            lambda w: w.sink(sink), LogEventLevel.ERROR,
            LoggingLevelSwitch(LogEventLevel.VERBOSE)) \
            .create_logger()

        logger.write_event(Some.information_event())

        assert len(DummyWrappingSink.emitted()) > 0
        assert len(sink.events) > 0

    def test_conditional_sinks_receive_events_matching_condition(self):
        matching = CollectingSink()
        logger = LoggerConfiguration() \
            .write_to.conditional(
            lambda le: le.level == LogEventLevel.WARNING,
            lambda w: w.sink(matching)) \
            .create_logger()

        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        evt = matching.single_event
        assert LogEventLevel.WARNING == evt.level

    def test_enrichers_can_be_wrapped(self):
        enricher = CollectingEnricher()

        configuration = LoggerConfiguration()
        LoggerEnrichmentConfiguration.wrap(
            configuration.enrich,
            lambda e: ConditionalEnricher(e, lambda le: le.level == LogEventLevel.WARNING),
            lambda enrich: enrich.with_enrichers(enricher))

        logger = configuration.create_logger()
        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        assert len(enricher.events) == 1
        evt = enricher.events[0]
        assert LogEventLevel.WARNING == evt.level

    def testConditionalEnrichersCheckConditions(self):
        enricher = CollectingEnricher()

        logger = LoggerConfiguration() \
            .enrich.when(lambda le: le.level == LogEventLevel.WARNING, lambda enrich: enrich.with_enrichers(enricher)) \
            .create_logger()

        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        assert 1 == len(enricher.events)
        evt = enricher.events[0]
        assert LogEventLevel.WARNING == evt.level

    def test_leveled_enrichers_check_levels(self):
        enricher = CollectingEnricher()

        logger = LoggerConfiguration() \
            .enrich.at_level(LogEventLevel.WARNING, lambda enrich: enrich.with_enrichers(enricher)) \
            .create_logger()

        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        assert 2 == len(enricher.events)
        assert 0 == len(list(filter(lambda x: not x.level >= LogEventLevel.WARNING, enricher.events)))

    def test_leveled_enrichers_check_level_switch(self):
        enricher = CollectingEnricher()
        level_switch = LoggingLevelSwitch(LogEventLevel.WARNING)

        logger = LoggerConfiguration() \
            .enrich.at_level(level_switch, lambda enrich: enrich.with_enrichers(enricher)) \
            .create_logger()

        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        assert 2 == len(enricher.events)
        assert 0 == len(list(filter(lambda x: not x.level >= LogEventLevel.WARNING, enricher.events)))

        enricher.events.clear()
        level_switch.minimum_level = LogEventLevel.ERROR

        logger.information("Information")
        logger.warning("Warning")
        logger.error("Error")

        assert 1 == len(enricher.events)
        error = enricher.events[0]
        assert error.level == LogEventLevel.ERROR
