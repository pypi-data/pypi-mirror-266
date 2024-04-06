from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (singleton as singleton_1, of_seq, FSharpList, is_empty, empty)
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.seq import (iterate_indexed, delay, append, singleton, map, exists, head, try_head, choose, is_empty as is_empty_1, iterate)
from ..fable_modules.fable_library.string_ import (to_fail, printf, to_console)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (IEnumerable_1, to_enumerable, get_enumerator, IEnumerator)
from ..fable_modules.fs_spreadsheet.fs_row import FsRow
from ..fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from ..fable_modules.fs_spreadsheet.fs_worksheet import FsWorksheet
from ..Core.arc_types import ArcAssay
from ..Core.comment import Remark
from ..Core.Helper.identifier import create_missing_identifier
from ..Core.person import Person
from ..Core.Table.arc_table import ArcTable
from .AnnotationTable.arc_table import (try_from_fs_worksheet, to_fs_worksheet)
from .Metadata.assays import (to_rows as to_rows_1, from_rows as from_rows_1)
from .Metadata.contacts import (to_rows as to_rows_2, from_rows as from_rows_2)
from .Metadata.sparse_table import (SparseRowModule_writeToSheet, SparseRowModule_fromValues, SparseRowModule_fromFsRow, SparseRowModule_tryGetValueAt)

def to_metadata_sheet(assay: ArcAssay) -> FsWorksheet:
    sheet: FsWorksheet = FsWorksheet("isa_assay")
    def action(row_i: int, r: IEnumerable_1[tuple[int, str]], assay: Any=assay) -> None:
        SparseRowModule_writeToSheet(row_i + 1, r, sheet)

    def _arrow884(__unit: None=None, assay: Any=assay) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
        assay_1: ArcAssay = assay
        def _arrow883(__unit: None=None) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
            def _arrow882(__unit: None=None) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
                def _arrow881(__unit: None=None) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
                    def _arrow880(__unit: None=None) -> IEnumerable_1[IEnumerable_1[tuple[int, str]]]:
                        return to_rows_2("Assay Person", of_seq(assay_1.Performers))

                    return append(singleton(SparseRowModule_fromValues(to_enumerable(["ASSAY PERFORMERS"]))), delay(_arrow880))

                return append(to_rows_1("Assay", singleton_1(assay_1)), delay(_arrow881))

            return append(singleton(SparseRowModule_fromValues(to_enumerable(["ASSAY"]))), delay(_arrow882))

        return delay(_arrow883)

    iterate_indexed(action, _arrow884())
    return sheet


def from_metadata_sheet(sheet: FsWorksheet) -> ArcAssay:
    try: 
        rows_1: IEnumerable_1[IEnumerable_1[tuple[int, str]]] = map(SparseRowModule_fromFsRow, sheet.Rows)
        def predicate(row: IEnumerable_1[tuple[int, str]]) -> bool:
            s: str = head(row)[1]
            return s.find("Assay") == 0

        pattern_input: tuple[str | None, str | None] = (("Assay", "Assay Person")) if exists(predicate, rows_1) else ((None, None))
        en: IEnumerator[IEnumerable_1[tuple[int, str]]] = get_enumerator(rows_1)
        def loop(last_line_mut: str | None, assays_mut: FSharpList[ArcAssay], contacts_mut: FSharpList[Person], line_number_mut: int) -> ArcAssay:
            while True:
                (last_line, assays, contacts, line_number) = (last_line_mut, assays_mut, contacts_mut, line_number_mut)
                (pattern_matching_result,) = (None,)
                if last_line is not None:
                    def _arrow885(__unit: None=None, last_line: Any=last_line, assays: Any=assays, contacts: Any=contacts, line_number: Any=line_number) -> bool:
                        k: str = last_line
                        return True if (k == "ASSAY") else (k == "ASSAY METADATA")

                    if _arrow885():
                        pattern_matching_result = 0

                    elif last_line == "ASSAY PERFORMERS":
                        pattern_matching_result = 1

                    else: 
                        pattern_matching_result = 2


                else: 
                    pattern_matching_result = 2

                if pattern_matching_result == 0:
                    pattern_input_1: tuple[str | None, int, FSharpList[Remark], FSharpList[ArcAssay]] = from_rows_1(pattern_input[0], line_number + 1, en)
                    last_line_mut = pattern_input_1[0]
                    assays_mut = pattern_input_1[3]
                    contacts_mut = contacts
                    line_number_mut = pattern_input_1[1]
                    continue

                elif pattern_matching_result == 1:
                    pattern_input_2: tuple[str | None, int, FSharpList[Remark], FSharpList[Person]] = from_rows_2(pattern_input[1], line_number + 1, en)
                    last_line_mut = pattern_input_2[0]
                    assays_mut = assays
                    contacts_mut = pattern_input_2[3]
                    line_number_mut = pattern_input_2[1]
                    continue

                elif pattern_matching_result == 2:
                    (pattern_matching_result_1, assays_2, contacts_2) = (None, None, None)
                    if is_empty(assays):
                        if is_empty(contacts):
                            pattern_matching_result_1 = 0

                        else: 
                            pattern_matching_result_1 = 1
                            assays_2 = assays
                            contacts_2 = contacts


                    else: 
                        pattern_matching_result_1 = 1
                        assays_2 = assays
                        contacts_2 = contacts

                    if pattern_matching_result_1 == 0:
                        return ArcAssay.create(create_missing_identifier())

                    elif pattern_matching_result_1 == 1:
                        performers: Array[Person] = list(contacts_2)
                        assay: ArcAssay = default_arg(try_head(assays_2), ArcAssay.create(create_missing_identifier()))
                        return ArcAssay.set_performers(performers, assay)


                break

        if en.System_Collections_IEnumerator_MoveNext():
            return loop(SparseRowModule_tryGetValueAt(0, en.System_Collections_Generic_IEnumerator_1_get_Current()), empty(), empty(), 1)

        else: 
            raise Exception("empty assay metadata sheet")


    except Exception as err:
        arg: str = str(err)
        return to_fail(printf("Failed while parsing metadatasheet: %s"))(arg)



def from_fs_workbook(doc: FsWorkbook) -> ArcAssay:
    try: 
        assay_meta_data: ArcAssay
        match_value: FsWorksheet | None = doc.TryGetWorksheetByName("isa_assay")
        if match_value is None:
            match_value_1: FsWorksheet | None = doc.TryGetWorksheetByName("Assay")
            if match_value_1 is None:
                to_console(printf("Cannot retrieve metadata: Assay file does not contain \"%s\" or \"%s\" sheet."))("isa_assay")("Assay")
                assay_meta_data = ArcAssay.create(create_missing_identifier())

            else: 
                assay_meta_data = from_metadata_sheet(match_value_1)


        else: 
            assay_meta_data = from_metadata_sheet(match_value)

        annotation_tables: IEnumerable_1[ArcTable] = choose(try_from_fs_worksheet, doc.GetWorksheets())
        if not is_empty_1(annotation_tables):
            assay_meta_data.Tables = list(annotation_tables)

        return assay_meta_data

    except Exception as err:
        arg_2: str = str(err)
        return to_fail(printf("Could not parse assay: \n%s"))(arg_2)



def to_fs_workbook(assay: ArcAssay) -> FsWorkbook:
    doc: FsWorkbook = FsWorkbook()
    meta_data_sheet: FsWorksheet = to_metadata_sheet(assay)
    doc.AddWorksheet(meta_data_sheet)
    def action(arg: ArcTable, assay: Any=assay) -> None:
        sheet: FsWorksheet = to_fs_worksheet(arg)
        doc.AddWorksheet(sheet)

    iterate(action, assay.Tables)
    return doc


__all__ = ["to_metadata_sheet", "from_metadata_sheet", "from_fs_workbook", "to_fs_workbook"]

