from __future__ import annotations
from .fable_modules.fable_library.list import (FSharpList, of_seq)
from .fable_modules.fable_library.option import map
from .fable_modules.fable_library.reflection import (TypeInfo, class_type)
from .fable_modules.fable_library.types import Array
from .fable_modules.fs_spreadsheet.fs_workbook import FsWorkbook
from .Core.arc_types import (ArcAssay, ArcStudy, ArcInvestigation)
from .Spreadsheet.arc_assay import (from_fs_workbook, to_fs_workbook)
from .Spreadsheet.arc_investigation import (from_fs_workbook as from_fs_workbook_1, to_fs_workbook as to_fs_workbook_1, to_light_fs_workbook)
from .Spreadsheet.arc_study import (ARCtrl_ArcStudy__ArcStudy_fromFsWorkbook_Static_32154C9D, ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_353D0DB7)

def _expr1814() -> TypeInfo:
    return class_type("ARCtrl.XlsxHelper.AssayXlsx", None, XlsxHelper_AssayXlsx)


class XlsxHelper_AssayXlsx:
    def __init__(self, __unit: None=None) -> None:
        pass

    def from_fs_workbook(self, fswb: FsWorkbook) -> ArcAssay:
        return from_fs_workbook(fswb)

    def to_fs_workbook(self, assay: ArcAssay) -> FsWorkbook:
        return to_fs_workbook(assay)


XlsxHelper_AssayXlsx_reflection = _expr1814

def XlsxHelper_AssayXlsx__ctor(__unit: None=None) -> XlsxHelper_AssayXlsx:
    return XlsxHelper_AssayXlsx(__unit)


def _expr1815() -> TypeInfo:
    return class_type("ARCtrl.XlsxHelper.StudyXlsx", None, XlsxHelper_StudyXlsx)


class XlsxHelper_StudyXlsx:
    def __init__(self, __unit: None=None) -> None:
        pass

    def from_fs_workbook(self, fswb: FsWorkbook) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
        return ARCtrl_ArcStudy__ArcStudy_fromFsWorkbook_Static_32154C9D(fswb)

    def to_fs_workbook(self, study: ArcStudy, assays: Array[ArcAssay] | None=None) -> FsWorkbook:
        return ARCtrl_ArcStudy__ArcStudy_toFsWorkbook_Static_353D0DB7(study, map(of_seq, assays))


XlsxHelper_StudyXlsx_reflection = _expr1815

def XlsxHelper_StudyXlsx__ctor(__unit: None=None) -> XlsxHelper_StudyXlsx:
    return XlsxHelper_StudyXlsx(__unit)


def _expr1816() -> TypeInfo:
    return class_type("ARCtrl.XlsxHelper.InvestigationXlsx", None, XlsxHelper_InvestigationXlsx)


class XlsxHelper_InvestigationXlsx:
    def __init__(self, __unit: None=None) -> None:
        pass

    def from_fs_workbook(self, fswb: FsWorkbook) -> ArcInvestigation:
        return from_fs_workbook_1(fswb)

    def to_fs_workbook(self, investigation: ArcInvestigation) -> FsWorkbook:
        return to_fs_workbook_1(investigation)

    def to_light_fs_workbook(self, investigation: ArcInvestigation) -> FsWorkbook:
        return to_light_fs_workbook(investigation)


XlsxHelper_InvestigationXlsx_reflection = _expr1816

def XlsxHelper_InvestigationXlsx__ctor(__unit: None=None) -> XlsxHelper_InvestigationXlsx:
    return XlsxHelper_InvestigationXlsx(__unit)


def _expr1817() -> TypeInfo:
    return class_type("ARCtrl.XlsxController", None, XlsxController)


class XlsxController:
    @staticmethod
    def Assay() -> XlsxHelper_AssayXlsx:
        return XlsxHelper_AssayXlsx()

    @staticmethod
    def Study() -> XlsxHelper_StudyXlsx:
        return XlsxHelper_StudyXlsx()

    @staticmethod
    def Investigation() -> XlsxHelper_InvestigationXlsx:
        return XlsxHelper_InvestigationXlsx()


XlsxController_reflection = _expr1817

__all__ = ["XlsxHelper_AssayXlsx_reflection", "XlsxHelper_StudyXlsx_reflection", "XlsxHelper_InvestigationXlsx_reflection", "XlsxController_reflection"]

