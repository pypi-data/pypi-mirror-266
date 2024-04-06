from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr908() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Comment.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Comment", string_type), ("name", string_type), ("value", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Comment: str
    name: str
    value: str

IContext_reflection = _expr908

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Comment", Json(0, "sdo:Comment")), ("name", Json(0, "sdo:name")), ("value", Json(0, "sdo:text"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \r\n    \"Comment\": \"sdo:Comment\",\r\n    \"name\": \"sdo:name\",\r\n    \"value\": \"sdo:text\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

