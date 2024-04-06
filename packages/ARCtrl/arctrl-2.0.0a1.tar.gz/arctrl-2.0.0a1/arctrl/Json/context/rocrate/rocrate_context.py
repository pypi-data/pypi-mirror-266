from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr945() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.ROCrate.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("CreativeWork", string_type), ("about", string_type), ("conforms_to", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    CreativeWork: str
    about: str
    conforms_to: str

IContext_reflection = _expr945

conforms_to_jsonvalue: Json = Json(5, to_enumerable([("@id", Json(0, "https://w3id.org/ro/crate/1.1"))]))

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("arc", Json(0, "http://purl.org/nfdi4plants/ontology/")), ("CreativeWork", Json(0, "sdo:CreativeWork")), ("about", Json(0, "sdo:about")), ("conformsTo", Json(0, "sdo:conformsTo"))]))

__all__ = ["IContext_reflection", "conforms_to_jsonvalue", "context_jsonvalue"]

