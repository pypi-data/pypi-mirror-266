from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr935() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Person.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Person", string_type), ("first_name", string_type), ("last_name", string_type), ("mid_initials", string_type), ("email", string_type), ("address", string_type), ("phone", string_type), ("fax", string_type), ("comments", string_type), ("roles", string_type), ("affiliation", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Person: str
    first_name: str
    last_name: str
    mid_initials: str
    email: str
    address: str
    phone: str
    fax: str
    comments: str
    roles: str
    affiliation: str

IContext_reflection = _expr935

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Person", Json(0, "sdo:Person")), ("orcid", Json(0, "sdo:identifier")), ("firstName", Json(0, "sdo:givenName")), ("lastName", Json(0, "sdo:familyName")), ("midInitials", Json(0, "sdo:additionalName")), ("email", Json(0, "sdo:email")), ("address", Json(0, "sdo:address")), ("phone", Json(0, "sdo:telephone")), ("fax", Json(0, "sdo:faxNumber")), ("comments", Json(0, "sdo:disambiguatingDescription")), ("roles", Json(0, "sdo:jobTitle")), ("affiliation", Json(0, "sdo:affiliation"))]))

context_minimal_json_value: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Person", Json(0, "sdo:Person")), ("name", Json(0, "sdo:name"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"Person\": \"sdo:Person\",\r\n    \"firstName\": \"sdo:givenName\",\r\n    \"lastName\": \"sdo:familyName\",\r\n    \"midInitials\": \"sdo:additionalName\",\r\n    \"email\": \"sdo:email\",\r\n    \"address\": \"sdo:address\",\r\n    \"phone\": \"sdo:telephone\",\r\n    \"fax\": \"sdo:faxNumber\",\r\n    \"comments\": \"sdo:disambiguatingDescription\",\r\n    \"roles\": \"sdo:jobTitle\",\r\n    \"affiliation\": \"sdo:affiliation\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_minimal_json_value", "context_str"]

