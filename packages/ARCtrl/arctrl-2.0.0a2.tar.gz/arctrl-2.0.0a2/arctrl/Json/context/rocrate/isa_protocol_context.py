from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr938() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Protocol.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Protocol", string_type), ("ArcProtocol", string_type), ("name", string_type), ("protocol_type", string_type), ("description", string_type), ("version", string_type), ("components", string_type), ("parameters", string_type), ("uri", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Protocol: str
    ArcProtocol: str
    name: str
    protocol_type: str
    description: str
    version: str
    components: str
    parameters: str
    uri: str
    comments: str

IContext_reflection = _expr938

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("bio", Json(0, "https://bioschemas.org/")), ("Protocol", Json(0, "bio:LabProtocol")), ("name", Json(0, "sdo:name")), ("protocolType", Json(0, "bio:intendedUse")), ("description", Json(0, "sdo:description")), ("version", Json(0, "sdo:version")), ("components", Json(0, "bio:labEquipment")), ("reagents", Json(0, "bio:reagent")), ("computationalTools", Json(0, "bio:computationalTool")), ("uri", Json(0, "sdo:url")), ("comments", Json(0, "sdo:comment"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

