from pyserilog import Guard
from pyserilog.core import logging_level_switch
from pyserilog.events import log_event_level
from pyserilog.events.level_alias import LevelAlias
from pyserilog.events.log_event_level import LogEventLevel


class LevelOverrideMap:
    class LevelOverride:
        def __init__(self, context: str, level_switch: logging_level_switch):
            self._context = context
            self._level_switch = level_switch

        @property
        def context(self):
            return self._context

        @property
        def level_switch(self):
            return self._level_switch

        def __str__(self):
            return f"{{context :{self.__class__} , overrider: {self._level_switch}}}"

    def __init__(self, overrides: dict[str, logging_level_switch], default_minimum_level: LogEventLevel,
                 default_level_switch: logging_level_switch):
        Guard.against_null(overrides)

        self._default_level_switch = default_level_switch
        self._default_minimum_level = LevelAlias.minimum if default_level_switch is not None else default_minimum_level

        keys = list(overrides.keys())
        keys.sort(reverse=True)

        self._overrides: list[LevelOverrideMap.LevelOverride] = []
        for key in keys:
            self._overrides.append(LevelOverrideMap.LevelOverride(key, overrides[key]))

    def get_effective_level(self, context: str) -> tuple[log_event_level, logging_level_switch]:
        for level_override in self._overrides:
            if context.startswith(level_override.context) and (
                    len(context) == len(level_override.context) or context[len(level_override.context)] == '.'):
                return LevelAlias.minimum, level_override.level_switch

        return self._default_minimum_level, self._default_level_switch


