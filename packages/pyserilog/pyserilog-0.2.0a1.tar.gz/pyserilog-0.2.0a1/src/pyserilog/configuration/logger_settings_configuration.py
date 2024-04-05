from pyserilog import LoggerConfiguration, Guard
from pyserilog.configuration.ilogger_settings import ILoggerSettings
from pyserilog.settings.key_value_paies.key_value_pair_settings import KeyValuePairSettings


class LoggerSettingsConfiguration:

    def __init__(self, logger_configuration):
        self._logger_configuration = logger_configuration

    def settings(self, settings: ILoggerSettings) -> LoggerConfiguration:
        Guard.against_null(settings)

        settings.configure(self._logger_configuration)
        return self._logger_configuration

    def key_value_pairs(self, settings: list[tuple[str, str]] | dict) -> LoggerConfiguration:
        Guard.against_null(settings)

        unique_settings = {}
        if isinstance(settings, list):
            for (key, value) in settings:
                unique_settings[key] = value
        elif isinstance(settings, dict):
            for key in settings:
                unique_settings[key] = settings[key]

        return self.__key_value_pairs(unique_settings)

    def __key_value_pairs(self, settings: dict):
        return self.settings(KeyValuePairSettings(settings))
