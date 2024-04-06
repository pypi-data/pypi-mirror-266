from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr941() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Sample.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Sample", string_type), ("ArcSample", string_type), ("name", string_type), ("characteristics", string_type), ("factor_values", string_type), ("derives_from", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Sample: str
    ArcSample: str
    name: str
    characteristics: str
    factor_values: str
    derives_from: str

IContext_reflection = _expr941

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("bio", Json(0, "https://bioschemas.org/")), ("Sample", Json(0, "bio:Sample")), ("name", Json(0, "sdo:name")), ("additionalProperties", Json(0, "bio:additionalProperty"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

