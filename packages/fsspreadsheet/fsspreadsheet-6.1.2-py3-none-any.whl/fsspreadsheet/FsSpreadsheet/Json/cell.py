from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.util import to_enumerable
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, int_1, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..Cells.fs_cell import (FsCell, DataType)
from ..fs_address import FsAddress__ctor_Z37302880
from .value import (encode as encode_1, decode as decode_1)

def encode(cell: FsCell) -> Json:
    def _arrow218(__unit: None=None, cell: Any=cell) -> Json:
        value_1: int = cell.ColumnNumber or 0
        return Json(7, int(value_1+0x100000000 if value_1 < 0 else value_1))

    return Json(5, to_enumerable([("column", _arrow218()), ("value", encode_1(cell.Value))]))


def decode(row_number: int) -> Decoder_1[FsCell]:
    def _arrow220(builder: IGetters, row_number: Any=row_number) -> FsCell:
        pattern_input: tuple[Any, DataType]
        object_arg: IRequiredGetter = builder.Required
        pattern_input = object_arg.Field("value", decode_1)
        def _arrow219(__unit: None=None) -> int:
            object_arg_1: IRequiredGetter = builder.Required
            return object_arg_1.Field("column", int_1)

        return FsCell(pattern_input[0], pattern_input[1], FsAddress__ctor_Z37302880(row_number, _arrow219()))

    return object(_arrow220)


__all__ = ["encode", "decode"]

