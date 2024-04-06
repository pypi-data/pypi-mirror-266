from __future__ import annotations
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("additionalType", Json(0, "sdo:additionalType")), ("category", Json(0, "sdo:name")), ("categoryCode", Json(0, "sdo:propertyID")), ("value", Json(0, "sdo:value")), ("valueCode", Json(0, "sdo:valueReference")), ("unit", Json(0, "sdo:unitText")), ("unitCode", Json(0, "sdo:unitCode")), ("comments", Json(0, "sdo:disambiguatingDescription"))]))

__all__ = ["context_jsonvalue"]

