from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr931() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.OntologyAnnotation.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("OntologyAnnotation", string_type), ("annotation_value", string_type), ("term_source", string_type), ("term_accession", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    OntologyAnnotation: str
    annotation_value: str
    term_source: str
    term_accession: str
    comments: str

IContext_reflection = _expr931

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("OntologyAnnotation", Json(0, "sdo:DefinedTerm")), ("annotationValue", Json(0, "sdo:name")), ("termSource", Json(0, "sdo:inDefinedTermSet")), ("termAccession", Json(0, "sdo:termCode")), ("comments", Json(0, "sdo:disambiguatingDescription"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

