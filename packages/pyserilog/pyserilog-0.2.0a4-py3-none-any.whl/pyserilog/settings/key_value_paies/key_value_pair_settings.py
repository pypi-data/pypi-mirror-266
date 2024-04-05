import importlib
from ctypes import FormatError
from types import ModuleType
from typing import Callable

from pyserilog import LoggerConfiguration, Guard
from pyserilog.configuration.ilogger_settings import ILoggerSettings
from pyserilog.configuration.logger_audit_sink_configuration import LoggerAuditSinkConfiguration
from pyserilog.configuration.logger_destructuring_configuration import LoggerDestructuringConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.configuration.logger_filter_configuration import LoggerFilterConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.debuging import SelfLog
from pyserilog.events.log_event_level import LogEventLevel
import re

from pyserilog.settings.key_value_paies.callable_configuration_method_finder import CallableConfigurationMethodFinder, \
    MethodInfo
from pyserilog.settings.key_value_paies.setting_value_conversions import SettingValueConversions


class KeyValuePairSettings(ILoggerSettings):
    USING_DIRECTIVE = "using"
    LEVEL_SWITCH_DIRECTIVE = "level-switch"
    AUDIT_TO_DIRECTIVE = "audit-to"
    WRITE_TO_DIRECTIVE = "write-to"
    MINIMUM_LEVEL_DIRECTIVE = "minimum-level"
    MINIMUM_LEVEL_CONTROLLED_BY_DIRECTIVE = "minimum-level:controlled-by"
    ENRICH_WITH_DIRECTIVE = "enrich"
    ENRICH_WITH_PROPERTY_DIRECTIVE = "enrich:with-property"
    FILTER_DIRECTIVE = "filter"
    DESTRUCTURE_DIRECTIVE = "destructure"

    USING_DIRECTIVE_FULL_FORM_PREFIX = "using:"
    ENRICH_WITH_PROPERTY_DIRECTIVE_PREFIX = "enrich:with-property:"
    MINIMUM_LEVEL_OVERRIDE_DIRECTIVE_PREFIX = "minimum-level:override:"

    CALLABLE_DIRECTIVE_REGEX = '^(?P<directive>audit-to|write-to|enrich|filter|destructure):(?P<method>[A-Za-z0-9_]*)' \
                               '(\\.(?P<argument>[A-Za-z0-9_]*)){0,1}'
    LEVEL_SWITCH_DECLARATION_DIRECTIVE_REGEX = "^level-switch:(?P<switch_name>.*)"
    LEVEL_SWITCH_NAME_REGEX = '^\\$[A-Za-z]+[A-Za-z0-9]*$'

    _supportedDirectives = [
        USING_DIRECTIVE,
        LEVEL_SWITCH_DIRECTIVE,
        AUDIT_TO_DIRECTIVE,
        WRITE_TO_DIRECTIVE,
        MINIMUM_LEVEL_DIRECTIVE,
        MINIMUM_LEVEL_CONTROLLED_BY_DIRECTIVE,
        ENRICH_WITH_PROPERTY_DIRECTIVE,
        ENRICH_WITH_DIRECTIVE,
        FILTER_DIRECTIVE,
        DESTRUCTURE_DIRECTIVE
    ]

    callable_directive_receiver_types: dict[str, type] = {
        "audit-to": LoggerAuditSinkConfiguration,
        "write-to": LoggerSinkConfiguration,
        "enrich": LoggerEnrichmentConfiguration,
        "filter": LoggerFilterConfiguration,
        "destructure": LoggerDestructuringConfiguration
    }
    callable_directive_receivers: dict[type, Callable[[LoggerConfiguration], object]] = {
        LoggerAuditSinkConfiguration: lambda lc: lc.audit_to,
        LoggerSinkConfiguration: lambda lc: lc.write_to,
        LoggerEnrichmentConfiguration: lambda lc: lc.enrich,
        LoggerFilterConfiguration: lambda lc: lc.filter,
        LoggerDestructuringConfiguration: lambda lc: lc.destructure,
    }

    def __init__(self, settings: dict[str, str]):
        self._settings = settings

    def configure(self, logger_configuration: LoggerConfiguration):
        Guard.against_null(logger_configuration)

        directives = {k: v for k, v in self._settings.items() if
                      any(filter(lambda x: k.startswith(x), self._supportedDirectives))}

        declared_level_switches = self.__parse_named_level_switch_declaration_directives(directives)

        if self.MINIMUM_LEVEL_DIRECTIVE in directives:
            minimum_level_directive = directives[self.MINIMUM_LEVEL_DIRECTIVE]
            if minimum_level_directive in LogEventLevel._member_names_:
                min_level = LogEventLevel[minimum_level_directive]
                logger_configuration.minimum_level.level_is(min_level)

        self.__config_minimum_level_controlled_by(directives, logger_configuration, declared_level_switches)
        self.__config_enrich_with_property(directives, logger_configuration)
        self.__config_minimum_level_with_override_prefix(directives, logger_configuration, declared_level_switches)
        self.__config_callable_methods(directives, logger_configuration, declared_level_switches)
        pass

    def __config_enrich_with_property(self, directives: dict[str, str], logger_configuration: LoggerConfiguration):
        def check_enrich_property_with_name(key_enrich: str):
            start_with = key_enrich.startswith(self.ENRICH_WITH_PROPERTY_DIRECTIVE_PREFIX)
            return start_with and len(key_enrich) > len(self.ENRICH_WITH_PROPERTY_DIRECTIVE_PREFIX)

        for key in filter(check_enrich_property_with_name, directives):
            name = key[len(self.ENRICH_WITH_PROPERTY_DIRECTIVE_PREFIX):]
            value = directives[key]
            logger_configuration.enrich.with_property(name, value)

    def __config_minimum_level_with_override_prefix(self, directives: dict[str, str],
                                                    logger_configuration: LoggerConfiguration, declared_level_switches):
        def is_contain(level_key: str):
            start_with = level_key.startswith(self.MINIMUM_LEVEL_OVERRIDE_DIRECTIVE_PREFIX)
            return start_with and len(level_key) > len(self.MINIMUM_LEVEL_OVERRIDE_DIRECTIVE_PREFIX)

        for key in filter(is_contain, directives):
            package_prefix = key[len(self.MINIMUM_LEVEL_OVERRIDE_DIRECTIVE_PREFIX):]
            value = directives[key]
            if value in LogEventLevel._member_names_:
                level = LogEventLevel[value]
            else:
                level = self.__look_up_switch_by_name(value, declared_level_switches)
            logger_configuration.minimum_level.override(package_prefix, level)

    def __config_callable_methods(self, directives: dict[str, str], logger_configuration: LoggerConfiguration,
                                  declared_level_switches):
        res = []

        for key in directives:
            match = re.match(self.CALLABLE_DIRECTIVE_REGEX, key)
            if match:
                received_type = self.callable_directive_receiver_types[match.group("directive")]
                method = match.group("method")
                argument = match.group("argument")
                call = KeyValuePairSettings.ConfigurationMethodCall(method, argument, directives[key])
                call_res = KeyValuePairSettings.CallableResult(received_type, call)
                res.append(call_res)
        if not any(res):
            return

        modules = self.__load_configuration_modules(directives)
        receiver_types = set(list(map(lambda x: x.receiver_type, res)))
        for receiver_type in receiver_types:
            methods = CallableConfigurationMethodFinder.find_configuration_methods(modules, receiver_type)
            method_names = set(
                map(lambda x: x.call.method_name, filter(lambda x: x.receiver_type == receiver_type, res)))
            for method_name in method_names:
                target: MethodInfo = self.__select_configuration_method(methods, method_name)
                if target is None:
                    SelfLog.write_line('Setting "{0}" could not be matched to an implementation in any of the loaded '
                                       'assemblies. To use settings from additional assemblies, specify them with the'
                                       ' "serilog:import" key.')
                else:
                    kwargs = KeyValuePairSettings.__get_method_args(method_name, receiver_type, res, target,
                                                                    declared_level_switches)
                    obj = self.callable_directive_receivers[receiver_type](logger_configuration)
                    kwargs[target.args.args[0]] = obj
                    target.func(**kwargs)

    @staticmethod
    def __get_method_args(method_name: str, receiver_type: type, callable_results, target: MethodInfo,
                          declared_level_switches):
        callable_results: list[KeyValuePairSettings.CallableResult] = callable_results
        res: list[KeyValuePairSettings.CallableResult] = list(
            filter(lambda x: x.call.method_name == method_name and x.receiver_type == receiver_type, callable_results)
        )

        kwargs = {}
        for receiver in res:
            arg_name = receiver.call.argument_name
            arg_type = target.args.annotations[arg_name]
            arg_value = KeyValuePairSettings.__convert_or_lookup_by_name(receiver.call.value, arg_type,
                                                                         declared_level_switches)
            kwargs[arg_name] = arg_value
        return kwargs

    @staticmethod
    def __convert_or_lookup_by_name(value_or_switch_name: str, klass_type: type,
                                    declared_switches: dict[str, LoggingLevelSwitch]):
        if issubclass(klass_type, LoggingLevelSwitch):
            return KeyValuePairSettings.__look_up_switch_by_name(value_or_switch_name, declared_switches)
        return SettingValueConversions.convert_to_type(value_or_switch_name, klass_type)

    def __load_configuration_modules(self, directives: dict[str, str]) -> list[ModuleType]:
        modules = set()

        def func(x: str):
            return x == self.USING_DIRECTIVE or x.startswith(self.USING_DIRECTIVE_FULL_FORM_PREFIX)

        for import_directive in filter(func, directives):
            value: str = directives[import_directive]
            if len(value.strip()) == 0:
                raise ValueError(
                    "A zero-length or whitespace module name was supplied to a serilog:import configuration statement.")
            module = importlib.import_module(value)
            modules.add(module)
        return list(modules)

    def __config_minimum_level_controlled_by(self, directives: dict[str, str],
                                             logger_configuration: LoggerConfiguration,
                                             declared_level_switches: dict[str, LoggingLevelSwitch]):
        if self.MINIMUM_LEVEL_CONTROLLED_BY_DIRECTIVE in directives:
            switch_name = directives[self.MINIMUM_LEVEL_CONTROLLED_BY_DIRECTIVE]
            global_minimum_level_switch = self.__look_up_switch_by_name(switch_name, declared_level_switches)
            logger_configuration.minimum_level.controlled_by(global_minimum_level_switch)

    @staticmethod
    def __select_configuration_method(candidate_methods: list[MethodInfo], name: str):

        def is_valid(x: MethodInfo):
            return x.method_name == name

        result = list(filter(lambda x: x.method_name == name, candidate_methods))
        if len(result) > 0:
            return result[0]

    @staticmethod
    def __parse_named_level_switch_declaration_directives(directives: dict[str, str]):
        res = re.compile(KeyValuePairSettings.LEVEL_SWITCH_DECLARATION_DIRECTIVE_REGEX)

        switches = []
        for key in directives:
            match = res.match(key)
            if match:
                switch_name = match.group("switch_name")
                initial_switch_level = directives[key]
                switches.append((switch_name, initial_switch_level))
        named_switches: dict[str, LoggingLevelSwitch] = {}
        for switch_name, initial_switch_level in switches:
            if not KeyValuePairSettings.is_valid_switch_name(switch_name):
                raise ValueError(f'"{switch_name}" is not a valid name for a Level Switch declaration. '
                                 f'Level switch must be declared with a \'$\' sign, like "level-switch:$switchName"')

            if initial_switch_level == "":
                named_switches[switch_name] = LoggingLevelSwitch()
            else:
                initial_level = LogEventLevel[initial_switch_level]
                named_switches[switch_name] = LoggingLevelSwitch(initial_level)
        return named_switches

    @staticmethod
    def __look_up_switch_by_name(switch_name: str,
                                 declared_level_switches: dict[str, LoggingLevelSwitch]) -> LoggingLevelSwitch:
        if switch_name in declared_level_switches:
            return declared_level_switches[switch_name]
        raise ValueError(f'No LoggingLevelSwitch has been declared with name "{switch_name}\".'
                         f' You might be missing a key "{KeyValuePairSettings.LEVEL_SWITCH_DIRECTIVE}:{switch_name}"')

    @staticmethod
    def is_valid_switch_name(inp: str):
        res = re.search(KeyValuePairSettings.LEVEL_SWITCH_NAME_REGEX, inp)
        return True if res else False

    class CallableResult(object):
        def __init__(self, receiver_type: type, call):
            self.receiver_type = receiver_type
            self.call: KeyValuePairSettings.ConfigurationMethodCall = call

    class ConfigurationMethodCall:
        def __init__(self, method_name: str, argument_name: str, value: str):
            self.method_name = method_name
            self.argument_name = argument_name
            self.value = value
