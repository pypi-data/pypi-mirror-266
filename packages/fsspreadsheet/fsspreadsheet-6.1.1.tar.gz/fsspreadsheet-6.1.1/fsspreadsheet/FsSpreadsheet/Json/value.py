from __future__ import annotations
from abc import abstractmethod
from datetime import datetime
from typing import (Any, Protocol)
from ...fable_modules.fable_library.date import (to_universal_time, to_string)
from ...fable_modules.fable_library.list import of_array
from ...fable_modules.thoth_json_core.decode import (map, datetime_local, one_of, bool_1, int_1, float_1, string)
from ...fable_modules.thoth_json_core.types import (Decoder_1, Json)
from ..Cells.fs_cell import DataType

class DateTimeStatic(Protocol):
    @abstractmethod
    def from_time_stamp(self, timestamp: float) -> Any:
        ...


def PyTime_toUniversalTimePy(dt: Any) -> Any:
    timestamp: float = to_universal_time(dt).timestamp()
    return datetime.fromtimestamp(timestamp=timestamp)


Decode_datetime: Decoder_1[Any] = map(PyTime_toUniversalTimePy, datetime_local)

def encode(value: Any=None) -> Json:
    if str(type(value)) == "<class \'str\'>":
        return Json(0, value)

    elif str(type(value)) == "<class \'float\'>":
        return Json(2, value)

    elif str(type(value)) == "<class \'int\'>":
        return Json(7, int(value+0x100000000 if value < 0 else value))

    elif str(type(value)) == "<class \'bool\'>":
        return Json(4, value)

    elif isinstance(value, datetime):
        return Json(0, to_string(value, "O", {}).split("+")[0])

    else: 
        return Json(3)



def ctor(b: bool) -> tuple[Any, DataType]:
    return (b, DataType(1))


def ctor_1(i: int) -> tuple[Any, DataType]:
    return (i, DataType(2))


def ctor_2(f: float) -> tuple[Any, DataType]:
    return (f, DataType(2))


def ctor_3(d_3: Any) -> tuple[Any, DataType]:
    return (d_3, DataType(3))


def ctor_4(s: str) -> tuple[Any, DataType]:
    return (s, DataType(0))


decode: Decoder_1[tuple[Any, DataType]] = one_of(of_array([map(ctor, bool_1), map(ctor_1, int_1), map(ctor_2, float_1), map(ctor_3, Decode_datetime), map(ctor_4, string)]))

__all__ = ["PyTime_toUniversalTimePy", "Decode_datetime", "encode", "decode"]

