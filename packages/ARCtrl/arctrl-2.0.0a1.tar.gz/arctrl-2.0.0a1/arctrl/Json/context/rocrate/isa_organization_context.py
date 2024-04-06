from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr934() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Organization.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Organization", string_type), ("name", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Organization: str
    name: str

IContext_reflection = _expr934

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Organization", Json(0, "sdo:Organization")), ("name", Json(0, "sdo:name"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"Organization\": \"sdo:Organization\",\r\n    \r\n    \"name\": \"sdo:name\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

