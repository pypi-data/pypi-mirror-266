import enum
import typing
from typing import Callable, get_args
from datetime import date, time, datetime
import pydoc as pydoc
import inspect

from pyserilog.debuging import SelfLog


class SettingValueConversions:
    __converters: dict[type, Callable[[str], object]] = {
        int: lambda x: None if x is None or x == "" else int(x),
        float: lambda x: None if x is None or x == "" else float(x),
        str: lambda x: x,
        time: lambda x: time.fromisoformat(x),
        date: lambda x: date.fromisoformat(x),
        datetime: lambda x: datetime.fromisoformat(x),
        type: lambda x: pydoc.locate(x)
    }

    @staticmethod
    def convert_to_type(value: str, klass_type: type):
        if klass_type in SettingValueConversions.__converters:
            converter = SettingValueConversions.__converters[klass_type]
            return converter(value)

        if issubclass(klass_type, enum.Enum):
            return klass_type.__members__[value]
        elif issubclass(klass_type, list) or typing.get_origin(klass_type) is list:
            items = value.split(',')
            res = []
            if len(value) == 0:
                return res
            element_type = get_args(klass_type)[0]
            for item in items:
                converted_item = SettingValueConversions.convert_to_type(item, element_type)
                res.append(converted_item)
            return res

        if value is not None and value != "":
            t: type = pydoc.locate(value)
            if t is not None:
                ins = t()
                return ins
        return value
