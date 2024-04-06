from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr936() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Process.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Process", string_type), ("ArcProcess", string_type), ("name", string_type), ("executes_protocol", string_type), ("performer", string_type), ("date", string_type), ("previous_process", string_type), ("next_process", string_type), ("input", string_type), ("output", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Process: str
    ArcProcess: str
    name: str
    executes_protocol: str
    performer: str
    date: str
    previous_process: str
    next_process: str
    input: str
    output: str
    comments: str

IContext_reflection = _expr936

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("bio", Json(0, "https://bioschemas.org/")), ("Process", Json(0, "bio:LabProcess")), ("name", Json(0, "sdo:name")), ("executesProtocol", Json(0, "bio:executesLabProtocol")), ("parameterValues", Json(0, "bio:parameterValue")), ("performer", Json(0, "sdo:agent")), ("date", Json(0, "sdo:endTime")), ("inputs", Json(0, "sdo:object")), ("outputs", Json(0, "sdo:result")), ("comments", Json(0, "sdo:disambiguatingDescription"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

