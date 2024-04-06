from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr922() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Material.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Material", string_type), ("ArcMaterial", string_type), ("type", string_type), ("name", string_type), ("characteristics", string_type), ("derives_from", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Material: str
    ArcMaterial: str
    type: str
    name: str
    characteristics: str
    derives_from: str

IContext_reflection = _expr922

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("bio", Json(0, "https://bioschemas.org/")), ("Material", Json(0, "bio:Sample")), ("type", Json(0, "sdo:disambiguatingDescription")), ("name", Json(0, "sdo:name")), ("characteristics", Json(0, "bio:additionalProperty"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"ArcMaterial\": \"arc:ARC#ARC_00000108\",\r\n    \"Material\": \"sdo:Thing\",\r\n\r\n    \"type\": \"arc:ARC#ARC_00000085\",\r\n    \"name\": \"arc:ARC#ARC_00000019\",\r\n    \"characteristics\": \"arc:ARC#ARC_00000080\",\r\n    \"derivesFrom\": \"arc:ARC#ARC_00000082\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

