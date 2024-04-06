from __future__ import annotations
from dataclasses import dataclass
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.reflection import (TypeInfo, array_type, record_type)
from ...fable_modules.fable_library.seq import (to_array, delay, collect, singleton, empty, fold)
from ...fable_modules.fable_library.types import (Array, Record)
from ...fable_modules.fable_library.util import IEnumerable_1
from ..ontology_annotation import OntologyAnnotation
from .composite_cell import (CompositeCell, CompositeCell_reflection)
from .composite_header import (CompositeHeader, CompositeHeader_reflection)

def _expr383() -> TypeInfo:
    return record_type("ARCtrl.CompositeColumn", [], CompositeColumn, lambda: [("Header", CompositeHeader_reflection()), ("Cells", array_type(CompositeCell_reflection()))])


@dataclass(eq = False, repr = False, slots = True)
class CompositeColumn(Record):
    Header: CompositeHeader
    Cells: Array[CompositeCell]
    @staticmethod
    def create(header: CompositeHeader, cells: Array[CompositeCell] | None=None) -> CompositeColumn:
        return CompositeColumn(header, default_arg(cells, []))

    def Validate(self, raise_exception: bool | None=None) -> bool:
        this: CompositeColumn = self
        raise_exeption: bool = default_arg(raise_exception, False)
        header: CompositeHeader = this.Header
        cells: Array[CompositeCell] = this.Cells
        if len(cells) == 0:
            return True

        elif (True if cells[0].is_term else cells[0].is_unitized) if header.IsTermColumn else False:
            return True

        elif cells[0].is_free_text if (not header.IsTermColumn) else False:
            return True

        else: 
            if raise_exeption:
                raise Exception(((("Invalid combination of header `" + str(header)) + "` and cells `") + str(cells[0])) + "`")

            return False


    def TryGetColumnUnits(self, __unit: None=None) -> Array[OntologyAnnotation] | None:
        this: CompositeColumn = self
        def _arrow382(__unit: None=None) -> IEnumerable_1[OntologyAnnotation]:
            def _arrow381(cell: CompositeCell) -> IEnumerable_1[OntologyAnnotation]:
                return singleton(cell.AsUnitized[1]) if cell.is_unitized else empty()

            return collect(_arrow381, this.Cells)

        arr: Array[OntologyAnnotation] = to_array(delay(_arrow382))
        return None if (len(arr) == 0) else arr

    def GetDefaultEmptyCell(self, __unit: None=None) -> CompositeCell:
        this: CompositeColumn = self
        if not this.Header.IsTermColumn:
            return CompositeCell.empty_free_text()

        else: 
            pattern_input: tuple[int, int]
            arg: tuple[int, int] = (0, 0)
            def folder(tupled_arg: tuple[int, int], cell: CompositeCell) -> tuple[int, int]:
                units: int = tupled_arg[0] or 0
                terms: int = tupled_arg[1] or 0
                if cell.is_unitized:
                    return (units + 1, terms)

                else: 
                    return (units, terms + 1)


            pattern_input = fold(folder, (arg[0], arg[1]), this.Cells)
            return CompositeCell.empty_term() if (pattern_input[1] >= pattern_input[0]) else CompositeCell.empty_unitized()



CompositeColumn_reflection = _expr383

__all__ = ["CompositeColumn_reflection"]

