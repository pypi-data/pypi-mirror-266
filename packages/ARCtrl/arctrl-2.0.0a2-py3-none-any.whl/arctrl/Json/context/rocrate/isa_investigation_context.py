from __future__ import annotations
from dataclasses import dataclass
from ....fable_modules.fable_library.reflection import (TypeInfo, string_type, record_type)
from ....fable_modules.fable_library.types import Record
from ....fable_modules.fable_library.util import to_enumerable
from ....fable_modules.thoth_json_core.types import Json

def _expr913() -> TypeInfo:
    return record_type("ARCtrl.Json.ROCrateContext.Investigation.IContext", [], IContext, lambda: [("sdo", string_type), ("arc", string_type), ("Investigation", string_type), ("identifier", string_type), ("title", string_type), ("description", string_type), ("submission_date", string_type), ("public_release_date", string_type), ("publications", string_type), ("people", string_type), ("studies", string_type), ("ontology_source_references", string_type), ("comments", string_type), ("publications_003F", string_type), ("filename", string_type)])


@dataclass(eq = False, repr = False, slots = True)
class IContext(Record):
    sdo: str
    arc: str
    Investigation: str
    identifier: str
    title: str
    description: str
    submission_date: str
    public_release_date: str
    publications: str
    people: str
    studies: str
    ontology_source_references: str
    comments: str
    publications_003F: str
    filename: str

IContext_reflection = _expr913

context_jsonvalue: Json = Json(5, to_enumerable([("sdo", Json(0, "http://schema.org/")), ("Investigation", Json(0, "sdo:Dataset")), ("identifier", Json(0, "sdo:identifier")), ("title", Json(0, "sdo:headline")), ("additionalType", Json(0, "sdo:additionalType")), ("description", Json(0, "sdo:description")), ("submissionDate", Json(0, "sdo:dateCreated")), ("publicReleaseDate", Json(0, "sdo:datePublished")), ("publications", Json(0, "sdo:citation")), ("people", Json(0, "sdo:creator")), ("studies", Json(0, "sdo:hasPart")), ("ontologySourceReferences", Json(0, "sdo:mentions")), ("comments", Json(0, "sdo:comment")), ("filename", Json(0, "sdo:alternateName"))]))

context_str: str = "\r\n{\r\n  \"@context\": {\r\n    \"sdo\": \"http://schema.org/\",\r\n    \"arc\": \"http://purl.org/nfdi4plants/ontology/\",\r\n\r\n    \"Investigation\": \"sdo:Dataset\",\r\n\r\n    \"identifier\" : \"sdo:identifier\",\r\n    \"title\": \"sdo:headline\",\r\n    \"description\": \"sdo:description\",\r\n    \"submissionDate\": \"sdo:dateCreated\",\r\n    \"publicReleaseDate\": \"sdo:datePublished\",\r\n    \"publications\": \"sdo:citation\",\r\n    \"people\": \"sdo:creator\",\r\n    \"studies\": \"sdo:hasPart\",\r\n    \"ontologySourceReferences\": \"sdo:mentions\",\r\n    \"comments\": \"sdo:disambiguatingDescription\",\r\n\r\n    \"publications?\": \"sdo:subjectOf?\",\r\n    \"filename\": \"sdo:alternateName\"\r\n  }\r\n}\r\n    "

__all__ = ["IContext_reflection", "context_jsonvalue", "context_str"]

