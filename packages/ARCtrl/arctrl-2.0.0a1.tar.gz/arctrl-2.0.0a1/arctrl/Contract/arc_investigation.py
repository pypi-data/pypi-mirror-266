from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.array_ import equals_with
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from ..Core.arc_types import ArcInvestigation
from ..FileSystem.path import combine_many
from ..Spreadsheet.arc_investigation import (to_light_fs_workbook, to_fs_workbook, from_fs_workbook)
from .contract import (Contract, DTOType, DTO)

def _007CInvestigationPath_007C__007C(input: Array[str]) -> str | None:
    (pattern_matching_result,) = (None,)
    def _arrow1785(x: str, y: str, input: Any=input) -> bool:
        return x == y

    if (len(input) == 1) if (not equals_with(_arrow1785, input, None)) else False:
        if input[0] == "isa.investigation.xlsx":
            pattern_matching_result = 0

        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return combine_many(input)

    elif pattern_matching_result == 1:
        return None



def ARCtrl_ArcInvestigation__ArcInvestigation_ToCreateContract_6FCE9E49(this: ArcInvestigation, is_light: bool | None=None) -> Contract:
    def _arrow1786(investigation: ArcInvestigation, this: Any=this, is_light: Any=is_light) -> FsWorkbook:
        return to_light_fs_workbook(investigation)

    def _arrow1787(investigation_1: ArcInvestigation, this: Any=this, is_light: Any=is_light) -> FsWorkbook:
        return to_fs_workbook(investigation_1)

    converter: Callable[[ArcInvestigation], FsWorkbook] = _arrow1786 if default_arg(is_light, True) else _arrow1787
    return Contract.create_create("isa.investigation.xlsx", DTOType(2), DTO(0, converter(this)))


def ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract_6FCE9E49(this: ArcInvestigation, is_light: bool | None=None) -> Contract:
    def _arrow1788(investigation: ArcInvestigation, this: Any=this, is_light: Any=is_light) -> FsWorkbook:
        return to_light_fs_workbook(investigation)

    def _arrow1789(investigation_1: ArcInvestigation, this: Any=this, is_light: Any=is_light) -> FsWorkbook:
        return to_fs_workbook(investigation_1)

    converter: Callable[[ArcInvestigation], FsWorkbook] = _arrow1788 if default_arg(is_light, True) else _arrow1789
    return Contract.create_update("isa.investigation.xlsx", DTOType(2), DTO(0, converter(this)))


def ARCtrl_ArcInvestigation__ArcInvestigation_toCreateContract_Static_23B73268(inv: ArcInvestigation, is_light: bool | None=None) -> Contract:
    return ARCtrl_ArcInvestigation__ArcInvestigation_ToCreateContract_6FCE9E49(inv, is_light)


def ARCtrl_ArcInvestigation__ArcInvestigation_toUpdateContract_Static_23B73268(inv: ArcInvestigation, is_light: bool | None=None) -> Contract:
    return ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract_6FCE9E49(inv, is_light)


def ARCtrl_ArcInvestigation__ArcInvestigation_tryFromReadContract_Static_7570923F(c: Contract) -> ArcInvestigation | None:
    (pattern_matching_result, fsworkbook) = (None, None)
    if c.Operation == "READ":
        if c.DTOType is not None:
            if c.DTOType.tag == 2:
                if c.DTO is not None:
                    if c.DTO.tag == 0:
                        pattern_matching_result = 0
                        fsworkbook = c.DTO.fields[0]

                    else: 
                        pattern_matching_result = 1


                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1


        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return from_fs_workbook(fsworkbook)

    elif pattern_matching_result == 1:
        return None



__all__ = ["_007CInvestigationPath_007C__007C", "ARCtrl_ArcInvestigation__ArcInvestigation_ToCreateContract_6FCE9E49", "ARCtrl_ArcInvestigation__ArcInvestigation_ToUpdateContract_6FCE9E49", "ARCtrl_ArcInvestigation__ArcInvestigation_toCreateContract_Static_23B73268", "ARCtrl_ArcInvestigation__ArcInvestigation_toUpdateContract_Static_23B73268", "ARCtrl_ArcInvestigation__ArcInvestigation_tryFromReadContract_Static_7570923F"]

