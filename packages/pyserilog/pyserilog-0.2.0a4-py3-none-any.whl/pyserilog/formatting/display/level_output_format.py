from pyserilog.events.level_alias import LevelAlias
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.rendering.casing import Casing


class LevelOutputFormat:
    _titleCaseLevelMap = [
        ["V", "Vb", "Vrb", "Verb", "Verbo", "Verbos", "Verbose"],
        ["D", "De", "Dbg", "Dbug", "Debug"],
        ["I", "In", "Inf", "Info", "Infor", "Inform", "Informa", "Informat", "Informati", "Informatio", "Information"],
        ["W", "Wn", "Wrn", "Warn", "Warni", "Warnin", "Warning"],
        ["E", "Er", "Err", "Eror", "Error"],
        ["F", "Fa", "Ftl", "Fatl", "Fatal"]
    ]

    _lowerCaseLevelMap = [
        ["v", "vb", "vrb", "verb", "verbo", "verbos", "verbose"],
        ["d", "de", "dbg", "dbug", "debug"],
        ["i", "in", "inf", "info", "infor", "inform", "informa", "informat", "informati", "informatio", "information"],
        ["w", "wn", "wrn", "warn", "warni", "warnin", "warning"],
        ["e", "er", "err", "eror", "error"],
        ["f", "fa", "ftl", "fatl", "fatal"]
    ]

    _upperCaseLevelMap = [
        ["V", "VB", "VRB", "VERB", "VERBO", "VERBOS", "VERBOSE"],
        ["D", "DE", "DBG", "DBUG", "DEBUG"],
        ["I", "IN", "INF", "INFO", "INFOR", "INFORM", "INFORMA", "INFORMAT", "INFORMATI", "INFORMATIO", "INFORMATION"],
        ["W", "WN", "WRN", "WARN", "WARNI", "WARNIN", "WARNING"],
        ["E", "ER", "ERR", "EROR", "ERROR"],
        ["F", "FA", "FTL", "FATL", "FATAL"]
    ]

    @staticmethod
    def get_level_moniker(value: LogEventLevel, text_format: str | None = None):
        if value.get_int() < LevelAlias.minimum.get_int() or value.get_int() > LevelAlias.maximum.get_int():
            return Casing.format(str(value), text_format)

        if text_format is None or len(text_format) != 2 and len(text_format) != 3:
            val = LevelOutputFormat.__get_level_moniker_from_list(LevelOutputFormat._titleCaseLevelMap, value)
            return Casing.format(val, text_format)

        width = int(text_format[1:])
        if width < 1:
            return ""

        match text_format[0]:
            case "w":
                return LevelOutputFormat.__get_level_moniker_from_list(LevelOutputFormat._lowerCaseLevelMap, value,
                                                                       width)
            case "u":
                return LevelOutputFormat.__get_level_moniker_from_list(LevelOutputFormat._upperCaseLevelMap, value,
                                                                       width)
            case "t":
                return LevelOutputFormat.__get_level_moniker_from_list(LevelOutputFormat._titleCaseLevelMap, value,
                                                                       width)
            case _:
                val = LevelOutputFormat.__get_level_moniker_from_list(LevelOutputFormat._titleCaseLevelMap, value)
                return Casing.format(val, text_format)

    @staticmethod
    def __get_level_moniker_from_list(case_level_map: list[list[str]], level: LogEventLevel, width: int = None):
        case_level = case_level_map[level.get_int()]
        index = len(case_level)
        if width is not None and width < index:
            index = width

        return case_level[index-1]
