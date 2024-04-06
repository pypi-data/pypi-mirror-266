from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr893() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Assay.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Assay", string_type), ("ArcAssay", string_type), ("measurement_type", string_type), ("technology_type", string_type), ("technology_platform", string_type), ("data_files", string_type), ("materials", string_type), ("other_materials", string_type), ("samples", string_type), ("characteristic_categories", string_type), ("process_sequences", string_type), ("unit_categories", string_type), ("comments", string_type), ("filename", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Assay: str
    ArcAssay: str
    measurement_type: str
    technology_type: str
    technology_platform: str
    data_files: str
    materials: str
    other_materials: str
    samples: str
    characteristic_categories: str
    process_sequences: str
    unit_categories: str
    comments: str
    filename: str

IContext_reflection = _expr893

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Assay", Json(0, "sdo:Dataset")), ("identifier", Json(0, "sdo:identifier")), ("additionalType", Json(0, "sdo:additionalType")), ("measurementType", Json(0, "sdo:variableMeasured")), ("technologyType", Json(0, "sdo:measurementTechnique")), ("technologyPlatform", Json(0, "sdo:measurementMethod")), ("dataFiles", Json(0, "sdo:hasPart")), ("performers", Json(0, "sdo:creator")), ("processSequences", Json(0, "sdo:about")), ("comments", Json(0, "sdo:comment")), ("filename", Json(0, "sdo:url"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

