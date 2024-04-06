from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr943() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Study.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Study", string_type), ("ArcStudy", string_type), ("identifier", string_type), ("title", string_type), ("description", string_type), ("submission_date", string_type), ("public_release_date", string_type), ("publications", string_type), ("people", string_type), ("assays", string_type), ("filename", string_type), ("comments", string_type), ("protocols", string_type), ("materials", string_type), ("other_materials", string_type), ("sources", string_type), ("samples", string_type), ("process_sequence", string_type), ("factors", string_type), ("characteristic_categories", string_type), ("unit_categories", string_type), ("study_design_descriptors", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Study: str
    ArcStudy: str
    identifier: str
    title: str
    description: str
    submission_date: str
    public_release_date: str
    publications: str
    people: str
    assays: str
    filename: str
    comments: str
    protocols: str
    materials: str
    other_materials: str
    sources: str
    samples: str
    process_sequence: str
    factors: str
    characteristic_categories: str
    unit_categories: str
    study_design_descriptors: str

IContext_reflection = _expr943

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Study", Json(0, "sdo:Dataset")), ("identifier", Json(0, "sdo:identifier")), ("title", Json(0, "sdo:headline")), ("additionalType", Json(0, "sdo:additionalType")), ("description", Json(0, "sdo:description")), ("submissionDate", Json(0, "sdo:dateCreated")), ("publicReleaseDate", Json(0, "sdo:datePublished")), ("publications", Json(0, "sdo:citation")), ("people", Json(0, "sdo:creator")), ("assays", Json(0, "sdo:hasPart")), ("filename", Json(0, "sdo:alternateName")), ("comments", Json(0, "sdo:comment")), ("processSequence", Json(0, "sdo:about")), ("studyDesignDescriptors", Json(0, "arc:ARC#ARC_00000037"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

