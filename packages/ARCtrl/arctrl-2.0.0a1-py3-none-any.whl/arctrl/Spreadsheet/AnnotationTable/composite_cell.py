from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.list import (map, FSharpList, is_empty, tail, head, of_array, singleton)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.string_ import (to_fail, printf)
from ...fable_modules.fs_spreadsheet.Cells.fs_cell import FsCell
from ...Core.Table.composite_cell import CompositeCell

def from_fs_cells(cells: FSharpList[FsCell]) -> CompositeCell:
    def mapping(c: FsCell, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result, v, v1, v2, v3, v1_1, v2_1, v3_1, v4) = (None, None, None, None, None, None, None, None, None)
    if not is_empty(cell_values):
        if not is_empty(tail(cell_values)):
            if not is_empty(tail(tail(cell_values))):
                if not is_empty(tail(tail(tail(cell_values)))):
                    if is_empty(tail(tail(tail(tail(cell_values))))):
                        pattern_matching_result = 2
                        v1_1 = head(cell_values)
                        v2_1 = head(tail(cell_values))
                        v3_1 = head(tail(tail(cell_values)))
                        v4 = head(tail(tail(tail(cell_values))))

                    else: 
                        pattern_matching_result = 3


                else: 
                    pattern_matching_result = 1
                    v1 = head(cell_values)
                    v2 = head(tail(cell_values))
                    v3 = head(tail(tail(cell_values)))


            else: 
                pattern_matching_result = 3


        else: 
            pattern_matching_result = 0
            v = head(cell_values)


    else: 
        pattern_matching_result = 3

    if pattern_matching_result == 0:
        return CompositeCell.create_free_text(v)

    elif pattern_matching_result == 1:
        return CompositeCell.create_term_from_string(v1, v2, v3)

    elif pattern_matching_result == 2:
        return CompositeCell.create_unitized_from_string(v1_1, v2_1, v3_1, v4)

    elif pattern_matching_result == 3:
        return to_fail(printf("Dafuq"))



def to_fs_cells(is_term: bool, has_unit: bool, cell: CompositeCell) -> FSharpList[FsCell]:
    if cell.tag == 0:
        if has_unit:
            return of_array([FsCell(cell.fields[0].NameText), FsCell(""), FsCell(default_arg(cell.fields[0].TermSourceREF, "")), FsCell(cell.fields[0].TermAccessionOntobeeUrl)])

        else: 
            return of_array([FsCell(cell.fields[0].NameText), FsCell(default_arg(cell.fields[0].TermSourceREF, "")), FsCell(cell.fields[0].TermAccessionOntobeeUrl)])


    elif cell.tag == 2:
        return of_array([FsCell(cell.fields[0]), FsCell(cell.fields[1].NameText), FsCell(default_arg(cell.fields[1].TermSourceREF, "")), FsCell(cell.fields[1].TermAccessionOntobeeUrl)])

    elif has_unit:
        return of_array([FsCell(cell.fields[0]), FsCell(""), FsCell(""), FsCell("")])

    elif is_term:
        return of_array([FsCell(cell.fields[0]), FsCell(""), FsCell("")])

    else: 
        return singleton(FsCell(cell.fields[0]))



__all__ = ["from_fs_cells", "to_fs_cells"]

