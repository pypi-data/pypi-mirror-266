from __future__ import annotations
from typing import Any
from ..fable_modules.fable_library.list import (FSharpList, empty)
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.seq import (iterate_indexed, append, map)
from ..fable_modules.fable_library.string_ import (to_fail, printf, to_console)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (IEnumerable_1, to_enumerable, get_enumerator, IEnumerator, ignore)
from ..fable_modules.fs_spreadsheet.fs_row import FsRow
from ..fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from ..fable_modules.fs_spreadsheet.fs_worksheet import FsWorksheet
from ..Core.arc_types import (ArcStudy, ArcAssay)
from ..Core.Helper.collections_ import (ResizeArray_choose, ResizeArray_isEmpty, ResizeArray_iter)
from ..Core.Helper.identifier import create_missing_identifier
from ..Core.Table.arc_table import ArcTable
from .AnnotationTable.arc_table import (try_from_fs_worksheet, to_fs_worksheet)
from .Metadata.sparse_table import (SparseRowModule_writeToSheet, SparseRowModule_fromValues, SparseRowModule_fromFsRow)
from .Metadata.study import (to_rows, from_rows as from_rows_1)

def ArcStudy_toMetadataSheet(study: ArcStudy, assays: FSharpList[ArcAssay] | None=None) -> FsWorksheet:
    sheet: FsWorksheet = FsWorksheet("isa_study")
    def action(row_i: int, r: IEnumerable_1[tuple[int, str]], study: Any=study, assays: Any=assays) -> None:
        SparseRowModule_writeToSheet(row_i + 1, r, sheet)

    def _arrow886(__unit: None=None, study: Any=study, assays: Any=assays) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
        source_1: IEnumerable_1[IEnumerable_1[tuple[int, str]]] = to_rows(study, assays)
        return append(to_enumerable([SparseRowModule_fromValues(to_enumerable(["STUDY"]))]), source_1)

    iterate_indexed(action, _arrow886())
    return sheet


def ArcStudy_fromMetadataSheet(sheet: FsWorksheet) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    try: 
        def _arrow887(__unit: None=None) -> tuple[ArcStudy, FSharpList[ArcAssay]] | None:
            en: IEnumerator[IEnumerable_1[tuple[int, str]]] = get_enumerator(map(SparseRowModule_fromFsRow, sheet.Rows))
            ignore(en.System_Collections_IEnumerator_MoveNext())
            return from_rows_1(2, en)[3]

        return default_arg(_arrow887(), (ArcStudy.create(create_missing_identifier()), empty()))

    except Exception as err:
        arg: str = str(err)
        return to_fail(printf("Failed while parsing metadatasheet: %s"))(arg)



def ARCtrl_ArcStudy__ArcStudy_fromFsWorkbook_Static_32154C9D(doc: FsWorkbook) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    try: 
        pattern_input: tuple[ArcStudy, FSharpList[ArcAssay]]
        match_value: FsWorksheet | None = doc.TryGetWorksheetByName("isa_study")
        if match_value is None:
            match_value_1: FsWorksheet | None = doc.TryGetWorksheetByName("Study")
            if match_value_1 is None:
                to_console(printf("Cannot retrieve metadata: Study file does not contain \"%s\" or \"%s\" sheet."))("isa_study")("Study")
                pattern_input = (ArcStudy.create(create_missing_identifier()), empty())

            else: 
                pattern_input = ArcStudy_fromMetadataSheet(match_value_1)


        else: 
            pattern_input = ArcStudy_fromMetadataSheet(match_value)

        study_metadata: ArcStudy = pattern_input[0]
        annotation_tables: Array[ArcTable] = ResizeArray_choose(try_from_fs_worksheet, doc.GetWorksheets())
        if not ResizeArray_isEmpty(annotation_tables):
            study_metadata.Tables = annotation_tables

        return (study_metadata, pattern_input[1])

    except Exception as err:
        arg_2: str = str(err)
        return to_fail(printf("Could not parse study: \n%s"))(arg_2)



def ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_353D0DB7(study: ArcStudy, assays: FSharpList[ArcAssay] | None=None) -> FsWorkbook:
    doc: FsWorkbook = FsWorkbook()
    meta_data_sheet: FsWorksheet = ArcStudy_toMetadataSheet(study, assays)
    doc.AddWorksheet(meta_data_sheet)
    def f(arg: ArcTable, study: Any=study, assays: Any=assays) -> None:
        sheet: FsWorksheet = to_fs_worksheet(arg)
        doc.AddWorksheet(sheet)

    ResizeArray_iter(f, study.Tables)
    return doc


__all__ = ["ArcStudy_toMetadataSheet", "ArcStudy_fromMetadataSheet", "ARCtrl_ArcStudy__ArcStudy_fromFsWorkbook_Static_32154C9D", "ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_353D0DB7"]

