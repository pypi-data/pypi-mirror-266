from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.seq import (to_list, delay, append, singleton, is_empty, map, empty, iterate)
from ...fable_modules.fable_library.util import (IEnumerable_1, ignore)
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, seq as seq_1, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.encode import seq
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..Cells.fs_cell import FsCell
from ..fs_row import FsRow
from ..fs_worksheet import FsWorksheet
from ..Tables.fs_table import FsTable
from .row import (encode as encode_2, decode as decode_2)
from .table import (encode as encode_1, decode as decode_1)

def encode(sheet: FsWorksheet) -> Json:
    sheet.RescanRows()
    def _arrow230(__unit: None=None, sheet: Any=sheet) -> IEnumerable_1[tuple[str, Json]]:
        def _arrow229(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
            def _arrow228(__unit: None=None) -> IEnumerable_1[tuple[str, Json]]:
                return singleton(("rows", seq(map(encode_2, sheet.Rows))))

            return append(singleton(("tables", seq(map(encode_1, sheet.Tables)))) if (not is_empty(sheet.Tables)) else empty(), delay(_arrow228))

        return append(singleton(("name", Json(0, sheet.Name))), delay(_arrow229))

    return Json(5, to_list(delay(_arrow230)))


def _arrow231(builder: IGetters) -> FsWorksheet:
    n: str
    object_arg: IRequiredGetter = builder.Required
    n = object_arg.Field("name", string)
    ts: IEnumerable_1[FsTable] | None
    arg_3: Decoder_1[IEnumerable_1[FsTable]] = seq_1(decode_1)
    object_arg_1: IOptionalGetter = builder.Optional
    ts = object_arg_1.Field("tables", arg_3)
    rs: IEnumerable_1[tuple[int, IEnumerable_1[FsCell]]]
    arg_5: Decoder_1[IEnumerable_1[tuple[int, IEnumerable_1[FsCell]]]] = seq_1(decode_2)
    object_arg_2: IRequiredGetter = builder.Required
    rs = object_arg_2.Field("rows", arg_5)
    sheet: FsWorksheet = FsWorksheet(n)
    def action_1(tupled_arg: tuple[int, IEnumerable_1[FsCell]]) -> None:
        r: FsRow = sheet.Row(tupled_arg[0])
        def action(cell: FsCell, tupled_arg: Any=tupled_arg) -> None:
            c: FsCell = r.Item(cell.ColumnNumber)
            c.Value = cell.Value
            c.DataType = cell.DataType

        iterate(action, tupled_arg[1])

    iterate(action_1, rs)
    if ts is None:
        pass

    else: 
        def action_2(t: FsTable) -> None:
            ignore(sheet.AddTable(t))

        iterate(action_2, ts)

    return sheet


decode: Decoder_1[FsWorksheet] = object(_arrow231)

__all__ = ["encode", "decode"]

