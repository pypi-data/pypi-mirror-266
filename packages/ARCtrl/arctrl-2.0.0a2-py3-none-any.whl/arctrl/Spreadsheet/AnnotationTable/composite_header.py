from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (map, FSharpList, is_empty, head, tail, singleton)
from ...fable_modules.fable_library.seq import (to_list, delay, append, singleton as singleton_1, empty)
from ...fable_modules.fable_library.string_ import (to_fail, printf)
from ...fable_modules.fable_library.types import to_string
from ...fable_modules.fable_library.util import IEnumerable_1
from ...fable_modules.fs_spreadsheet.Cells.fs_cell import FsCell
from ...Core.Helper.regex import (ActivePatterns__007CTSRColumnHeader_007C__007C, ActivePatterns__007CTANColumnHeader_007C__007C, ActivePatterns__007CUnitColumnHeader_007C__007C, try_parse_parameter_column_header, try_parse_factor_column_header, try_parse_characteristic_column_header, try_parse_component_column_header, ActivePatterns__007CInputColumnHeader_007C__007C, ActivePatterns__007COutputColumnHeader_007C__007C)
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.composite_header import (CompositeHeader, IOType)

def ActivePattern_mergeIDInfo(id_space1: str, local_id1: str, id_space2: str, local_id2: str) -> dict[str, Any]:
    if id_space1 != id_space2:
        to_fail(printf("TermSourceRef %s and %s do not match"))(id_space1)(id_space2)

    if local_id1 != local_id2:
        to_fail(printf("LocalID %s and %s do not match"))(local_id1)(local_id2)

    return {
        "TermAccessionNumber": ((("" + id_space1) + ":") + local_id1) + "",
        "TermSourceRef": id_space1
    }


def ActivePattern__007CTerm_007C__007C(category_parser: Callable[[str], str | None], f: Callable[[OntologyAnnotation], CompositeHeader], cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def _007CAC_007C__007C(s: str, category_parser: Any=category_parser, f: Any=f, cells: Any=cells) -> str | None:
        return category_parser(s)

    def mapping(c: FsCell, category_parser: Any=category_parser, f: Any=f, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result, name) = (None, None)
    if not is_empty(cell_values):
        active_pattern_result: str | None = _007CAC_007C__007C(head(cell_values))
        if active_pattern_result is not None:
            if is_empty(tail(cell_values)):
                pattern_matching_result = 0
                name = active_pattern_result

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return f(OntologyAnnotation.create(name))

    elif pattern_matching_result == 1:
        (pattern_matching_result_1, name_1, term1, term2) = (None, None, None, None)
        if not is_empty(cell_values):
            active_pattern_result_1: str | None = _007CAC_007C__007C(head(cell_values))
            if active_pattern_result_1 is not None:
                if not is_empty(tail(cell_values)):
                    active_pattern_result_2: dict[str, Any] | None = ActivePatterns__007CTSRColumnHeader_007C__007C(head(tail(cell_values)))
                    if active_pattern_result_2 is not None:
                        if not is_empty(tail(tail(cell_values))):
                            active_pattern_result_3: dict[str, Any] | None = ActivePatterns__007CTANColumnHeader_007C__007C(head(tail(tail(cell_values))))
                            if active_pattern_result_3 is not None:
                                if not is_empty(tail(tail(tail(cell_values)))):
                                    active_pattern_result_4: dict[str, Any] | None = ActivePatterns__007CTANColumnHeader_007C__007C(head(tail(tail(tail(cell_values)))))
                                    if active_pattern_result_4 is not None:
                                        if is_empty(tail(tail(tail(tail(cell_values))))):
                                            active_pattern_result_5: dict[str, Any] | None = ActivePatterns__007CTSRColumnHeader_007C__007C(head(tail(tail(cell_values))))
                                            if active_pattern_result_5 is not None:
                                                if ActivePatterns__007CUnitColumnHeader_007C__007C(head(tail(cell_values))) is not None:
                                                    pattern_matching_result_1 = 0
                                                    name_1 = active_pattern_result_1
                                                    term1 = active_pattern_result_5
                                                    term2 = active_pattern_result_4

                                                else: 
                                                    pattern_matching_result_1 = 1


                                            else: 
                                                pattern_matching_result_1 = 1


                                        else: 
                                            pattern_matching_result_1 = 1


                                    else: 
                                        pattern_matching_result_1 = 1


                                else: 
                                    pattern_matching_result_1 = 0
                                    name_1 = active_pattern_result_1
                                    term1 = active_pattern_result_2
                                    term2 = active_pattern_result_3


                            else: 
                                active_pattern_result_7: dict[str, Any] | None = ActivePatterns__007CTSRColumnHeader_007C__007C(head(tail(tail(cell_values))))
                                if active_pattern_result_7 is not None:
                                    if not is_empty(tail(tail(tail(cell_values)))):
                                        active_pattern_result_8: dict[str, Any] | None = ActivePatterns__007CTANColumnHeader_007C__007C(head(tail(tail(tail(cell_values)))))
                                        if active_pattern_result_8 is not None:
                                            if is_empty(tail(tail(tail(tail(cell_values))))):
                                                if ActivePatterns__007CUnitColumnHeader_007C__007C(head(tail(cell_values))) is not None:
                                                    pattern_matching_result_1 = 0
                                                    name_1 = active_pattern_result_1
                                                    term1 = active_pattern_result_7
                                                    term2 = active_pattern_result_8

                                                else: 
                                                    pattern_matching_result_1 = 1


                                            else: 
                                                pattern_matching_result_1 = 1


                                        else: 
                                            pattern_matching_result_1 = 1


                                    else: 
                                        pattern_matching_result_1 = 1


                                else: 
                                    pattern_matching_result_1 = 1



                        else: 
                            pattern_matching_result_1 = 1


                    elif ActivePatterns__007CUnitColumnHeader_007C__007C(head(tail(cell_values))) is not None:
                        if not is_empty(tail(tail(cell_values))):
                            active_pattern_result_11: dict[str, Any] | None = ActivePatterns__007CTSRColumnHeader_007C__007C(head(tail(tail(cell_values))))
                            if active_pattern_result_11 is not None:
                                if not is_empty(tail(tail(tail(cell_values)))):
                                    active_pattern_result_12: dict[str, Any] | None = ActivePatterns__007CTANColumnHeader_007C__007C(head(tail(tail(tail(cell_values)))))
                                    if active_pattern_result_12 is not None:
                                        if is_empty(tail(tail(tail(tail(cell_values))))):
                                            pattern_matching_result_1 = 0
                                            name_1 = active_pattern_result_1
                                            term1 = active_pattern_result_11
                                            term2 = active_pattern_result_12

                                        else: 
                                            pattern_matching_result_1 = 1


                                    else: 
                                        pattern_matching_result_1 = 1


                                else: 
                                    pattern_matching_result_1 = 1


                            else: 
                                pattern_matching_result_1 = 1


                        else: 
                            pattern_matching_result_1 = 1


                    else: 
                        pattern_matching_result_1 = 1


                else: 
                    pattern_matching_result_1 = 1


            else: 
                pattern_matching_result_1 = 1


        else: 
            pattern_matching_result_1 = 1

        if pattern_matching_result_1 == 0:
            term: dict[str, Any] = ActivePattern_mergeIDInfo(term1["IDSpace"], term1["LocalID"], term2["IDSpace"], term2["LocalID"])
            return f(OntologyAnnotation.create(name_1, term["TermSourceRef"], term["TermAccessionNumber"]))

        elif pattern_matching_result_1 == 1:
            return None




def ActivePattern__007CParameter_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def _arrow832(input: str, cells: Any=cells) -> str | None:
        return try_parse_parameter_column_header(input)

    def _arrow833(Item: OntologyAnnotation, cells: Any=cells) -> CompositeHeader:
        return CompositeHeader(3, Item)

    active_pattern_result: CompositeHeader | None = ActivePattern__007CTerm_007C__007C(_arrow832, _arrow833, cells)
    if active_pattern_result is not None:
        r: CompositeHeader = active_pattern_result
        return r

    else: 
        return None



def ActivePattern__007CFactor_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def _arrow834(input: str, cells: Any=cells) -> str | None:
        return try_parse_factor_column_header(input)

    def _arrow835(Item: OntologyAnnotation, cells: Any=cells) -> CompositeHeader:
        return CompositeHeader(2, Item)

    active_pattern_result: CompositeHeader | None = ActivePattern__007CTerm_007C__007C(_arrow834, _arrow835, cells)
    if active_pattern_result is not None:
        r: CompositeHeader = active_pattern_result
        return r

    else: 
        return None



def ActivePattern__007CCharacteristic_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def _arrow836(input: str, cells: Any=cells) -> str | None:
        return try_parse_characteristic_column_header(input)

    def _arrow837(Item: OntologyAnnotation, cells: Any=cells) -> CompositeHeader:
        return CompositeHeader(1, Item)

    active_pattern_result: CompositeHeader | None = ActivePattern__007CTerm_007C__007C(_arrow836, _arrow837, cells)
    if active_pattern_result is not None:
        r: CompositeHeader = active_pattern_result
        return r

    else: 
        return None



def ActivePattern__007CComponent_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def _arrow838(input: str, cells: Any=cells) -> str | None:
        return try_parse_component_column_header(input)

    def _arrow839(Item: OntologyAnnotation, cells: Any=cells) -> CompositeHeader:
        return CompositeHeader(0, Item)

    active_pattern_result: CompositeHeader | None = ActivePattern__007CTerm_007C__007C(_arrow838, _arrow839, cells)
    if active_pattern_result is not None:
        r: CompositeHeader = active_pattern_result
        return r

    else: 
        return None



def ActivePattern__007CInput_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def mapping(c: FsCell, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result, io_type) = (None, None)
    if not is_empty(cell_values):
        active_pattern_result: str | None = ActivePatterns__007CInputColumnHeader_007C__007C(head(cell_values))
        if active_pattern_result is not None:
            if is_empty(tail(cell_values)):
                pattern_matching_result = 0
                io_type = active_pattern_result

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return CompositeHeader(11, IOType.of_string(io_type))

    elif pattern_matching_result == 1:
        return None



def ActivePattern__007COutput_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def mapping(c: FsCell, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result, io_type) = (None, None)
    if not is_empty(cell_values):
        active_pattern_result: str | None = ActivePatterns__007COutputColumnHeader_007C__007C(head(cell_values))
        if active_pattern_result is not None:
            if is_empty(tail(cell_values)):
                pattern_matching_result = 0
                io_type = active_pattern_result

            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return CompositeHeader(12, IOType.of_string(io_type))

    elif pattern_matching_result == 1:
        return None



def ActivePattern__007CProtocolHeader_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def mapping(c: FsCell, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result,) = (None,)
    if not is_empty(cell_values):
        if head(cell_values) == "Protocol Type":
            pattern_matching_result = 0

        elif head(cell_values) == "Protocol REF":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 1

            else: 
                pattern_matching_result = 7


        elif head(cell_values) == "Protocol Description":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 2

            else: 
                pattern_matching_result = 7


        elif head(cell_values) == "Protocol Uri":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 3

            else: 
                pattern_matching_result = 7


        elif head(cell_values) == "Protocol Version":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 4

            else: 
                pattern_matching_result = 7


        elif head(cell_values) == "Performer":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 5

            else: 
                pattern_matching_result = 7


        elif head(cell_values) == "Date":
            if is_empty(tail(cell_values)):
                pattern_matching_result = 6

            else: 
                pattern_matching_result = 7


        else: 
            pattern_matching_result = 7


    else: 
        pattern_matching_result = 7

    if pattern_matching_result == 0:
        return CompositeHeader(4)

    elif pattern_matching_result == 1:
        return CompositeHeader(8)

    elif pattern_matching_result == 2:
        return CompositeHeader(5)

    elif pattern_matching_result == 3:
        return CompositeHeader(6)

    elif pattern_matching_result == 4:
        return CompositeHeader(7)

    elif pattern_matching_result == 5:
        return CompositeHeader(9)

    elif pattern_matching_result == 6:
        return CompositeHeader(10)

    elif pattern_matching_result == 7:
        return None



def ActivePattern__007CFreeText_007C__007C(cells: FSharpList[FsCell]) -> CompositeHeader | None:
    def mapping(c: FsCell, cells: Any=cells) -> str:
        return c.ValueAsString()

    cell_values: FSharpList[str] = map(mapping, cells)
    (pattern_matching_result, text) = (None, None)
    if not is_empty(cell_values):
        if is_empty(tail(cell_values)):
            pattern_matching_result = 0
            text = head(cell_values)

        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return CompositeHeader(13, text)

    elif pattern_matching_result == 1:
        return None



def from_fs_cells(cells: FSharpList[FsCell]) -> CompositeHeader:
    active_pattern_result: CompositeHeader | None = ActivePattern__007CParameter_007C__007C(cells)
    if active_pattern_result is not None:
        p: CompositeHeader = active_pattern_result
        return p

    else: 
        active_pattern_result_1: CompositeHeader | None = ActivePattern__007CFactor_007C__007C(cells)
        if active_pattern_result_1 is not None:
            f: CompositeHeader = active_pattern_result_1
            return f

        else: 
            active_pattern_result_2: CompositeHeader | None = ActivePattern__007CCharacteristic_007C__007C(cells)
            if active_pattern_result_2 is not None:
                c: CompositeHeader = active_pattern_result_2
                return c

            else: 
                active_pattern_result_3: CompositeHeader | None = ActivePattern__007CComponent_007C__007C(cells)
                if active_pattern_result_3 is not None:
                    c_1: CompositeHeader = active_pattern_result_3
                    return c_1

                else: 
                    active_pattern_result_4: CompositeHeader | None = ActivePattern__007CInput_007C__007C(cells)
                    if active_pattern_result_4 is not None:
                        i: CompositeHeader = active_pattern_result_4
                        return i

                    else: 
                        active_pattern_result_5: CompositeHeader | None = ActivePattern__007COutput_007C__007C(cells)
                        if active_pattern_result_5 is not None:
                            o: CompositeHeader = active_pattern_result_5
                            return o

                        else: 
                            active_pattern_result_6: CompositeHeader | None = ActivePattern__007CProtocolHeader_007C__007C(cells)
                            if active_pattern_result_6 is not None:
                                ph: CompositeHeader = active_pattern_result_6
                                return ph

                            else: 
                                active_pattern_result_7: CompositeHeader | None = ActivePattern__007CFreeText_007C__007C(cells)
                                if active_pattern_result_7 is not None:
                                    ft: CompositeHeader = active_pattern_result_7
                                    return ft

                                else: 
                                    return to_fail(printf("Could not parse header group %O"))(cells)










def to_fs_cells(has_unit: bool, header: CompositeHeader) -> FSharpList[FsCell]:
    if header.IsSingleColumn:
        return singleton(FsCell(to_string(header)))

    elif header.IsTermColumn:
        def _arrow843(__unit: None=None, has_unit: Any=has_unit, header: Any=header) -> IEnumerable_1[FsCell]:
            def _arrow842(__unit: None=None) -> IEnumerable_1[FsCell]:
                def _arrow841(__unit: None=None) -> IEnumerable_1[FsCell]:
                    def _arrow840(__unit: None=None) -> IEnumerable_1[FsCell]:
                        return singleton_1(FsCell(("Term Accession Number (" + header.GetColumnAccessionShort) + ")"))

                    return append(singleton_1(FsCell(("Term Source REF (" + header.GetColumnAccessionShort) + ")")), delay(_arrow840))

                return append(singleton_1(FsCell("Unit")) if has_unit else empty(), delay(_arrow841))

            return append(singleton_1(FsCell(to_string(header))), delay(_arrow842))

        return to_list(delay(_arrow843))

    else: 
        return to_fail(printf("header %O is neither single nor term column"))(header)



__all__ = ["ActivePattern_mergeIDInfo", "ActivePattern__007CTerm_007C__007C", "ActivePattern__007CParameter_007C__007C", "ActivePattern__007CFactor_007C__007C", "ActivePattern__007CCharacteristic_007C__007C", "ActivePattern__007CComponent_007C__007C", "ActivePattern__007CInput_007C__007C", "ActivePattern__007COutput_007C__007C", "ActivePattern__007CProtocolHeader_007C__007C", "ActivePattern__007CFreeText_007C__007C", "from_fs_cells", "to_fs_cells"]

