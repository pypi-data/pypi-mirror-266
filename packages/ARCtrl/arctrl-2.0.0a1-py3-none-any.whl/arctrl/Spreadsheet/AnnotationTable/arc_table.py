from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.list import (reverse, map, FSharpList, fold, singleton, cons, is_empty, head, tail, empty, to_array, collect, sort_by, of_array, length, iterate_indexed)
from ...fable_modules.fable_library.map_util import add_to_dict
from ...fable_modules.fable_library.reflection import enum_type
from ...fable_modules.fable_library.seq import (try_find, to_list, map as map_1)
from ...fable_modules.fable_library.string_ import (to_fail, printf)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import (IEnumerable_1, compare_primitives)
from ...fable_modules.fs_spreadsheet.Cells.fs_cell import FsCell
from ...fable_modules.fs_spreadsheet.Cells.fs_cells_collection import Dictionary_tryGet
from ...fable_modules.fs_spreadsheet.fs_address import (FsAddress__ctor_Z37302880, FsAddress)
from ...fable_modules.fs_spreadsheet.fs_column import FsColumn
from ...fable_modules.fs_spreadsheet.fs_worksheet import FsWorksheet
from ...fable_modules.fs_spreadsheet.Ranges.fs_range_address import FsRangeAddress__ctor_7E77A4A0
from ...fable_modules.fs_spreadsheet.Ranges.fs_range_base import FsRangeBase__Cell_Z3407A44B
from ...fable_modules.fs_spreadsheet.Tables.fs_table import FsTable
from ...Core.Helper.regex import try_parse_reference_column_header
from ...Core.Table.arc_table import ArcTable
from ...Core.Table.composite_column import CompositeColumn
from ...Core.Table.composite_header import CompositeHeader
from .composite_column import (from_fs_columns, fix_deprecated_ioheader, to_fs_columns)

__A = TypeVar("__A")

def Aux_List_groupWhen(f: Callable[[__A], bool], list_1: FSharpList[__A]) -> FSharpList[FSharpList[__A]]:
    def mapping(list_3: FSharpList[__A], f: Any=f, list_1: Any=list_1) -> FSharpList[__A]:
        return reverse(list_3)

    def folder(acc: FSharpList[FSharpList[__A]], e: __A, f: Any=f, list_1: Any=list_1) -> FSharpList[FSharpList[__A]]:
        matchValue: bool = f(e)
        if matchValue:
            return cons(singleton(e), acc)

        elif not is_empty(acc):
            return cons(cons(e, head(acc)), tail(acc))

        else: 
            return singleton(singleton(e))


    return reverse(map(mapping, fold(folder, empty(), list_1)))


def classify_header_order(header: CompositeHeader) -> enum_type("ARCtrl.Spreadsheet.ArcTable.ColumnOrder", int, [("InputClass", 1.0), ("ProtocolClass", 2.0), ("ParamsClass", 3.0), ("OutputClass", 4.0)]):
    if ((((((header.tag == 4) or (header.tag == 5)) or (header.tag == 6)) or (header.tag == 7)) or (header.tag == 8)) or (header.tag == 9)) or (header.tag == 10):
        return 2

    elif ((((header.tag == 0) or (header.tag == 1)) or (header.tag == 2)) or (header.tag == 3)) or (header.tag == 13):
        return 3

    elif header.tag == 12:
        return 4

    else: 
        return 1



def classify_column_order(column: CompositeColumn) -> enum_type("ARCtrl.Spreadsheet.ArcTable.ColumnOrder", int, [("InputClass", 1.0), ("ProtocolClass", 2.0), ("ParamsClass", 3.0), ("OutputClass", 4.0)]):
    return classify_header_order(column.Header)


def group_columns_by_header(columns: FSharpList[FsColumn]) -> FSharpList[FSharpList[FsColumn]]:
    def f(c: FsColumn, columns: Any=columns) -> bool:
        v: str = c.Item(1).ValueAsString()
        if try_parse_reference_column_header(v) is None:
            return not (v.find("Unit") == 0)

        else: 
            return False


    return Aux_List_groupWhen(f, columns)


def try_annotation_table(sheet: FsWorksheet) -> FsTable | None:
    def predicate(t: FsTable, sheet: Any=sheet) -> bool:
        return t.Name.find("annotationTable") == 0

    return try_find(predicate, sheet.Tables)


def compose_columns(columns: IEnumerable_1[FsColumn]) -> Array[CompositeColumn]:
    def _arrow876(columns_2: FSharpList[FsColumn], columns: Any=columns) -> CompositeColumn:
        return from_fs_columns(columns_2)

    return to_array(map(_arrow876, group_columns_by_header(to_list(columns))))


def try_from_fs_worksheet(sheet: FsWorksheet) -> ArcTable | None:
    try: 
        match_value: FsTable | None = try_annotation_table(sheet)
        if match_value is None:
            return None

        else: 
            t: FsTable = match_value
            composite_columns: Array[CompositeColumn] = compose_columns(map_1(fix_deprecated_ioheader, t.GetColumns(sheet.CellCollection)))
            return ArcTable.add_columns(composite_columns, None, True)(ArcTable.init(sheet.Name))


    except Exception as err:
        arg: str = sheet.Name
        arg_1: str = str(err)
        return to_fail(printf("Could not parse table with name \"%s\":\n%s"))(arg)(arg_1)



def to_fs_worksheet(table: ArcTable) -> FsWorksheet:
    string_count: Any = dict([])
    ws: FsWorksheet = FsWorksheet(table.Name)
    if len(table.Columns) == 0:
        return ws

    else: 
        def _arrow877(column_1: CompositeColumn, table: Any=table) -> FSharpList[FSharpList[FsCell]]:
            return to_fs_columns(column_1)

        def _arrow878(column: CompositeColumn, table: Any=table) -> enum_type("ARCtrl.Spreadsheet.ArcTable.ColumnOrder", int, [("InputClass", 1.0), ("ProtocolClass", 2.0), ("ParamsClass", 3.0), ("OutputClass", 4.0)]):
            return classify_column_order(column)

        class ObjectExpr879:
            @property
            def Compare(self) -> Callable[[enum_type("ARCtrl.Spreadsheet.ArcTable.ColumnOrder", int, [("InputClass", 1.0), ("ProtocolClass", 2.0), ("ParamsClass", 3.0), ("OutputClass", 4.0)]), enum_type("ARCtrl.Spreadsheet.ArcTable.ColumnOrder", int, [("InputClass", 1.0), ("ProtocolClass", 2.0), ("ParamsClass", 3.0), ("OutputClass", 4.0)])], int]:
                return compare_primitives

        columns: FSharpList[FSharpList[FsCell]] = collect(_arrow877, sort_by(_arrow878, of_array(table.Columns), ObjectExpr879()))
        max_row: int = length(head(columns)) or 0
        max_col: int = length(columns) or 0
        fs_table: FsTable = ws.Table("annotationTable", FsRangeAddress__ctor_7E77A4A0(FsAddress__ctor_Z37302880(1, 1), FsAddress__ctor_Z37302880(max_row, max_col)))
        def action_1(col_i: int, col: FSharpList[FsCell], table: Any=table) -> None:
            def action(row_i: int, cell: FsCell, col_i: Any=col_i, col: Any=col) -> None:
                value: str
                v: str = cell.ValueAsString()
                if row_i == 0:
                    match_value: str | None = Dictionary_tryGet(v, string_count)
                    if match_value is None:
                        add_to_dict(string_count, cell.ValueAsString(), "")
                        value = v

                    else: 
                        spaces: str = match_value
                        string_count[v] = spaces + " "
                        value = (v + " ") + spaces


                else: 
                    value = v

                address: FsAddress = FsAddress__ctor_Z37302880(row_i + 1, col_i + 1)
                FsRangeBase__Cell_Z3407A44B(fs_table, address, ws.CellCollection).SetValueAs(value)

            iterate_indexed(action, col)

        iterate_indexed(action_1, columns)
        return ws



__all__ = ["Aux_List_groupWhen", "classify_header_order", "classify_column_order", "group_columns_by_header", "try_annotation_table", "compose_columns", "try_from_fs_worksheet", "to_fs_worksheet"]

