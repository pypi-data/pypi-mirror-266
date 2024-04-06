from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.reflection import (TypeInfo, string_type, union_type)
from ...fable_modules.fable_library.types import (Array, Union)
from ..ontology_annotation import (OntologyAnnotation, OntologyAnnotation_reflection)

def _expr380() -> TypeInfo:
    return union_type("ARCtrl.CompositeCell", [], CompositeCell, lambda: [[("Item", OntologyAnnotation_reflection())], [("Item", string_type)], [("Item1", string_type), ("Item2", OntologyAnnotation_reflection())]])


class CompositeCell(Union):
    def __init__(self, tag: int, *fields: Any) -> None:
        super().__init__()
        self.tag: int = tag or 0
        self.fields: Array[Any] = list(fields)

    @staticmethod
    def cases() -> list[str]:
        return ["Term", "FreeText", "Unitized"]

    @property
    def is_unitized(self, __unit: None=None) -> bool:
        this: CompositeCell = self
        return True if (this.tag == 2) else False

    @property
    def is_term(self, __unit: None=None) -> bool:
        this: CompositeCell = self
        return True if (this.tag == 0) else False

    @property
    def is_free_text(self, __unit: None=None) -> bool:
        this: CompositeCell = self
        return True if (this.tag == 1) else False

    def GetEmptyCell(self, __unit: None=None) -> CompositeCell:
        this: CompositeCell = self
        if this.tag == 2:
            return CompositeCell.empty_unitized()

        elif this.tag == 1:
            return CompositeCell.empty_free_text()

        else: 
            return CompositeCell.empty_term()


    def GetContent(self, __unit: None=None) -> Array[str]:
        this: CompositeCell = self
        if this.tag == 0:
            oa: OntologyAnnotation = this.fields[0]
            return [oa.NameText, default_arg(oa.TermSourceREF, ""), default_arg(oa.TermAccessionNumber, "")]

        elif this.tag == 2:
            oa_1: OntologyAnnotation = this.fields[1]
            return [this.fields[0], oa_1.NameText, default_arg(oa_1.TermSourceREF, ""), default_arg(oa_1.TermAccessionNumber, "")]

        else: 
            return [this.fields[0]]


    def ToUnitizedCell(self, __unit: None=None) -> CompositeCell:
        this: CompositeCell = self
        if this.tag == 1:
            return CompositeCell(2, "", OntologyAnnotation.create(this.fields[0]))

        elif this.tag == 0:
            return CompositeCell(2, "", this.fields[0])

        else: 
            return this


    def ToTermCell(self, __unit: None=None) -> CompositeCell:
        this: CompositeCell = self
        if this.tag == 2:
            return CompositeCell(0, this.fields[1])

        elif this.tag == 1:
            return CompositeCell(0, OntologyAnnotation.create(this.fields[0]))

        else: 
            return this


    def ToFreeTextCell(self, __unit: None=None) -> CompositeCell:
        this: CompositeCell = self
        if this.tag == 0:
            return CompositeCell(1, this.fields[0].NameText)

        elif this.tag == 2:
            return CompositeCell(1, this.fields[1].NameText)

        else: 
            return this


    @property
    def AsUnitized(self, __unit: None=None) -> tuple[str, OntologyAnnotation]:
        this: CompositeCell = self
        if this.tag == 2:
            return (this.fields[0], this.fields[1])

        else: 
            raise Exception("Not a Unitized cell.")


    @property
    def AsTerm(self, __unit: None=None) -> OntologyAnnotation:
        this: CompositeCell = self
        if this.tag == 0:
            return this.fields[0]

        else: 
            raise Exception("Not a Swate TermCell.")


    @property
    def AsFreeText(self, __unit: None=None) -> str:
        this: CompositeCell = self
        if this.tag == 1:
            return this.fields[0]

        else: 
            raise Exception("Not a Swate TermCell.")


    @staticmethod
    def create_term(oa: OntologyAnnotation) -> CompositeCell:
        return CompositeCell(0, oa)

    @staticmethod
    def create_term_from_string(name: str | None=None, tsr: str | None=None, tan: str | None=None) -> CompositeCell:
        return CompositeCell(0, OntologyAnnotation.create(name, tsr, tan))

    @staticmethod
    def create_unitized(value: str, oa: OntologyAnnotation | None=None) -> CompositeCell:
        return CompositeCell(2, value, default_arg(oa, OntologyAnnotation()))

    @staticmethod
    def create_unitized_from_string(value: str, name: str | None=None, tsr: str | None=None, tan: str | None=None) -> CompositeCell:
        tupled_arg: tuple[str, OntologyAnnotation] = (value, OntologyAnnotation.create(name, tsr, tan))
        return CompositeCell(2, tupled_arg[0], tupled_arg[1])

    @staticmethod
    def create_free_text(value: str) -> CompositeCell:
        return CompositeCell(1, value)

    @staticmethod
    def empty_term() -> CompositeCell:
        return CompositeCell(0, OntologyAnnotation())

    @staticmethod
    def empty_free_text() -> CompositeCell:
        return CompositeCell(1, "")

    @staticmethod
    def empty_unitized() -> CompositeCell:
        return CompositeCell(2, "", OntologyAnnotation())

    def UpdateWithOA(self, oa: OntologyAnnotation) -> CompositeCell:
        this: CompositeCell = self
        if this.tag == 2:
            return CompositeCell.create_unitized(this.fields[0], oa)

        elif this.tag == 1:
            return CompositeCell.create_free_text(oa.NameText)

        else: 
            return CompositeCell.create_term(oa)


    @staticmethod
    def update_with_oa(oa: OntologyAnnotation, cell: CompositeCell) -> CompositeCell:
        return cell.UpdateWithOA(oa)

    def __str__(self, __unit: None=None) -> str:
        this: CompositeCell = self
        if this.tag == 1:
            return this.fields[0]

        elif this.tag == 2:
            return ((("" + this.fields[0]) + " ") + this.fields[1].NameText) + ""

        else: 
            return ("" + this.fields[0].NameText) + ""


    @staticmethod
    def term(oa: OntologyAnnotation) -> CompositeCell:
        return CompositeCell(0, oa)

    @staticmethod
    def free_text(s: str) -> CompositeCell:
        return CompositeCell(1, s)

    @staticmethod
    def unitized(v: str, oa: OntologyAnnotation) -> CompositeCell:
        return CompositeCell(2, v, oa)


CompositeCell_reflection = _expr380

__all__ = ["CompositeCell_reflection"]

