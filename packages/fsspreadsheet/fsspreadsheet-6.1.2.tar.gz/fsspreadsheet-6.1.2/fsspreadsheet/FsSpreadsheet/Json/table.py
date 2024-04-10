from __future__ import annotations
from ...fable_modules.fable_library.util import to_enumerable
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..Ranges.fs_range_address import (FsRangeAddress__get_Range, FsRangeAddress__ctor_Z721C83C5)
from ..Ranges.fs_range_base import FsRangeBase__get_RangeAddress
from ..Tables.fs_table import FsTable

def encode(sheet: FsTable) -> Json:
    return Json(5, to_enumerable([("name", Json(0, sheet.Name)), ("range", Json(0, FsRangeAddress__get_Range(FsRangeBase__get_RangeAddress(sheet))))]))


def _arrow226(builder: IGetters) -> FsTable:
    def _arrow224(__unit: None=None) -> str:
        object_arg: IRequiredGetter = builder.Required
        return object_arg.Field("name", string)

    def _arrow225(__unit: None=None) -> str:
        object_arg_1: IRequiredGetter = builder.Required
        return object_arg_1.Field("range", string)

    return FsTable(_arrow224(), FsRangeAddress__ctor_Z721C83C5(_arrow225()))


decode: Decoder_1[FsTable] = object(_arrow226)

__all__ = ["encode", "decode"]

