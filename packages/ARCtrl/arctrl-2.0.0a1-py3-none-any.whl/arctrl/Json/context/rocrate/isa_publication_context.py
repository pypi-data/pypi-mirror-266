from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr940() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Publication.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Publication", string_type), ("pub_med_id", string_type), ("doi", string_type), ("title", string_type), ("status", string_type), ("author_list", string_type), ("comments", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Publication: str
    pub_med_id: str
    doi: str
    title: str
    status: str
    author_list: str
    comments: str

IContext_reflection = _expr940

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Publication", Json(0, "sdo:ScholarlyArticle")), ("pubMedID", Json(0, "sdo:url")), ("doi", Json(0, "sdo:sameAs")), ("title", Json(0, "sdo:headline")), ("status", Json(0, "sdo:creativeWorkStatus")), ("authorList", Json(0, "sdo:author")), ("comments", Json(0, "sdo:disambiguatingDescription"))]))

__all__ = ["IContext_reflection", "context_jsonvalue"]

