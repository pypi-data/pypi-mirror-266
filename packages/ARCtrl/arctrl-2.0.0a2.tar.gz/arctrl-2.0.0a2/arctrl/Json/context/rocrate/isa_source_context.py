from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr942() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Source.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Source", string_type), ("ArcSource", string_type), ("identifier", string_type), ("characteristics", string_type), ("name", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Source: str
    ArcSource: str
    identifier: str
    characteristics: str
    name: str

IContext_reflection = _expr942

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("bio", Json(0, "https://bioschemas.org/")), ("Source", Json(0, "bio:Sample")), ("name", Json(0, "sdo:name")), ("characteristics", Json(0, "bio:additionalProperty"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"Source\": \"sdo:Thing\",\r\n    \"ArcSource\": \"arc:ARC#ARC_00000071\",\r\n\r\n    \"identifier\": \"sdo:identifier\",\r\n\r\n    \"name\": \"arc:ARC#ARC_00000019\",\r\n    \"characteristics\": \"arc:ARC#ARC_00000080\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

