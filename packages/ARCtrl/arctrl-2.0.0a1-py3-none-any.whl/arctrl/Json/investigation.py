from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (choose, of_array, unzip, FSharpList, empty)
from ..fable_modules.fable_library.option import default_arg
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.seq import (concat, map)
from ..fable_modules.fable_library.seq2 import distinct_by
from ..fable_modules.fable_library.string_ import (to_text, printf, to_fail)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (equals, string_hash)
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, IGetters, list_1 as list_1_1)
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string
from ..Core.arc_types import (ArcAssay, ArcStudy, ArcInvestigation)
from ..Core.comment import Comment
from ..Core.Helper.identifier import create_missing_identifier
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.ontology_source_reference import OntologySourceReference
from ..Core.person import Person
from ..Core.publication import Publication
from ..Core.Table.composite_cell import CompositeCell
from .assay import (Assay_encoder, Assay_decoder, Assay_encoderCompressed, Assay_decoderCompressed)
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from .context.rocrate.isa_investigation_context import context_jsonvalue
from .context.rocrate.rocrate_context import (conforms_to_jsonvalue, context_jsonvalue as context_jsonvalue_1)
from .decode import (Decode_resizeArray, Decode_objectNoAdditionalProperties)
from .encode import (try_include, try_include_seq, default_spaces)
from .ontology_source_reference import (OntologySourceReference_encoder, OntologySourceReference_decoder, OntologySourceReference_ROCrate_encoder, OntologySourceReference_ROCrate_decoder, OntologySourceReference_ISAJson_encoder, OntologySourceReference_ISAJson_decoder)
from .person import (Person_encoder, Person_decoder, Person_ROCrate_encoder, Person_ROCrate_decoder, Person_ISAJson_encoder, Person_ISAJson_decoder)
from .publication import (Publication_encoder, Publication_decoder, Publication_ROCrate_encoder, Publication_ROCrate_decoder, Publication_ISAJson_encoder, Publication_ISAJson_decoder)
from .study import (Study_encoder, Study_decoder, Study_encoderCompressed, Study_decoderCompressed, Study_ROCrate_encoder, Study_ROCrate_decoder, Study_ISAJson_encoder, Study_ISAJson_decoder)
from .Table.compression import (decode, encode)

def Investigation_encoder(inv: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], inv: Any=inv) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1684(value_1: str, inv: Any=inv) -> Json:
        return Json(0, value_1)

    def _arrow1685(value_3: str, inv: Any=inv) -> Json:
        return Json(0, value_3)

    def _arrow1686(value_5: str, inv: Any=inv) -> Json:
        return Json(0, value_5)

    def _arrow1687(value_7: str, inv: Any=inv) -> Json:
        return Json(0, value_7)

    def _arrow1688(osr: OntologySourceReference, inv: Any=inv) -> Json:
        return OntologySourceReference_encoder(osr)

    def _arrow1689(oa: Publication, inv: Any=inv) -> Json:
        return Publication_encoder(oa)

    def _arrow1690(person: Person, inv: Any=inv) -> Json:
        return Person_encoder(person)

    def _arrow1691(assay: ArcAssay, inv: Any=inv) -> Json:
        return Assay_encoder(assay)

    def _arrow1692(study: ArcStudy, inv: Any=inv) -> Json:
        return Study_encoder(study)

    def _arrow1693(value_9: str, inv: Any=inv) -> Json:
        return Json(0, value_9)

    def _arrow1694(comment: Comment, inv: Any=inv) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, inv.Identifier)), try_include("Title", _arrow1684, inv.Title), try_include("Description", _arrow1685, inv.Description), try_include("SubmissionDate", _arrow1686, inv.SubmissionDate), try_include("PublicReleaseDate", _arrow1687, inv.PublicReleaseDate), try_include_seq("OntologySourceReferences", _arrow1688, inv.OntologySourceReferences), try_include_seq("Publications", _arrow1689, inv.Publications), try_include_seq("Contacts", _arrow1690, inv.Contacts), try_include_seq("Assays", _arrow1691, inv.Assays), try_include_seq("Studies", _arrow1692, inv.Studies), try_include_seq("RegisteredStudyIdentifiers", _arrow1693, inv.RegisteredStudyIdentifiers), try_include_seq("Comments", _arrow1694, inv.Comments)])))


def _arrow1707(get: IGetters) -> ArcInvestigation:
    def _arrow1695(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow1696(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow1697(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow1698(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("SubmissionDate", string)

    def _arrow1699(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("PublicReleaseDate", string)

    def _arrow1700(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_11: Decoder_1[Array[OntologySourceReference]] = Decode_resizeArray(OntologySourceReference_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("OntologySourceReferences", arg_11)

    def _arrow1701(__unit: None=None) -> Array[Publication] | None:
        arg_13: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Publications", arg_13)

    def _arrow1702(__unit: None=None) -> Array[Person] | None:
        arg_15: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("Contacts", arg_15)

    def _arrow1703(__unit: None=None) -> Array[ArcAssay] | None:
        arg_17: Decoder_1[Array[ArcAssay]] = Decode_resizeArray(Assay_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Assays", arg_17)

    def _arrow1704(__unit: None=None) -> Array[ArcStudy] | None:
        arg_19: Decoder_1[Array[ArcStudy]] = Decode_resizeArray(Study_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("Studies", arg_19)

    def _arrow1705(__unit: None=None) -> Array[str] | None:
        arg_21: Decoder_1[Array[str]] = Decode_resizeArray(string)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("RegisteredStudyIdentifiers", arg_21)

    def _arrow1706(__unit: None=None) -> Array[Comment] | None:
        arg_23: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("Comments", arg_23)

    return ArcInvestigation(_arrow1695(), _arrow1696(), _arrow1697(), _arrow1698(), _arrow1699(), _arrow1700(), _arrow1701(), _arrow1702(), _arrow1703(), _arrow1704(), _arrow1705(), _arrow1706())


Investigation_decoder: Decoder_1[ArcInvestigation] = object(_arrow1707)

def Investigation_encoderCompressed(string_table: Any, oa_table: Any, cell_table: Any, inv: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1708(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Json(0, value_1)

    def _arrow1709(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Json(0, value_3)

    def _arrow1710(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Json(0, value_5)

    def _arrow1711(value_7: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Json(0, value_7)

    def _arrow1712(osr: OntologySourceReference, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return OntologySourceReference_encoder(osr)

    def _arrow1713(oa: Publication, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Publication_encoder(oa)

    def _arrow1714(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Person_encoder(person)

    def _arrow1715(assay: ArcAssay, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Assay_encoderCompressed(string_table, oa_table, cell_table, assay)

    def _arrow1716(study: ArcStudy, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Study_encoderCompressed(string_table, oa_table, cell_table, study)

    def _arrow1717(value_9: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Json(0, value_9)

    def _arrow1718(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, inv: Any=inv) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, inv.Identifier)), try_include("Title", _arrow1708, inv.Title), try_include("Description", _arrow1709, inv.Description), try_include("SubmissionDate", _arrow1710, inv.SubmissionDate), try_include("PublicReleaseDate", _arrow1711, inv.PublicReleaseDate), try_include_seq("OntologySourceReferences", _arrow1712, inv.OntologySourceReferences), try_include_seq("Publications", _arrow1713, inv.Publications), try_include_seq("Contacts", _arrow1714, inv.Contacts), try_include_seq("Assays", _arrow1715, inv.Assays), try_include_seq("Studies", _arrow1716, inv.Studies), try_include_seq("RegisteredStudyIdentifiers", _arrow1717, inv.RegisteredStudyIdentifiers), try_include_seq("Comments", _arrow1718, inv.Comments)])))


def Investigation_decoderCompressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcInvestigation]:
    def _arrow1731(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcInvestigation:
        def _arrow1719(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow1720(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow1721(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow1722(__unit: None=None) -> str | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("SubmissionDate", string)

        def _arrow1723(__unit: None=None) -> str | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("PublicReleaseDate", string)

        def _arrow1724(__unit: None=None) -> Array[OntologySourceReference] | None:
            arg_11: Decoder_1[Array[OntologySourceReference]] = Decode_resizeArray(OntologySourceReference_decoder)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("OntologySourceReferences", arg_11)

        def _arrow1725(__unit: None=None) -> Array[Publication] | None:
            arg_13: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_decoder)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Publications", arg_13)

        def _arrow1726(__unit: None=None) -> Array[Person] | None:
            arg_15: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("Contacts", arg_15)

        def _arrow1727(__unit: None=None) -> Array[ArcAssay] | None:
            arg_17: Decoder_1[Array[ArcAssay]] = Decode_resizeArray(Assay_decoderCompressed(string_table, oa_table, cell_table))
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Assays", arg_17)

        def _arrow1728(__unit: None=None) -> Array[ArcStudy] | None:
            arg_19: Decoder_1[Array[ArcStudy]] = Decode_resizeArray(Study_decoderCompressed(string_table, oa_table, cell_table))
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("Studies", arg_19)

        def _arrow1729(__unit: None=None) -> Array[str] | None:
            arg_21: Decoder_1[Array[str]] = Decode_resizeArray(string)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("RegisteredStudyIdentifiers", arg_21)

        def _arrow1730(__unit: None=None) -> Array[Comment] | None:
            arg_23: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_11: IOptionalGetter = get.Optional
            return object_arg_11.Field("Comments", arg_23)

        return ArcInvestigation(_arrow1719(), _arrow1720(), _arrow1721(), _arrow1722(), _arrow1723(), _arrow1724(), _arrow1725(), _arrow1726(), _arrow1727(), _arrow1728(), _arrow1729(), _arrow1730())

    return object(_arrow1731)


def Investigation_ROCrate_genID(i: ArcInvestigation) -> str:
    return "./"


def Investigation_ROCrate_encoder(oa: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1732(value_5: str, oa: Any=oa) -> Json:
        return Json(0, value_5)

    def _arrow1733(value_7: str, oa: Any=oa) -> Json:
        return Json(0, value_7)

    def _arrow1734(value_9: str, oa: Any=oa) -> Json:
        return Json(0, value_9)

    def _arrow1735(value_11: str, oa: Any=oa) -> Json:
        return Json(0, value_11)

    def _arrow1736(osr: OntologySourceReference, oa: Any=oa) -> Json:
        return OntologySourceReference_ROCrate_encoder(osr)

    def _arrow1737(oa_1: Publication, oa: Any=oa) -> Json:
        return Publication_ROCrate_encoder(oa_1)

    def _arrow1738(oa_2: Person, oa: Any=oa) -> Json:
        return Person_ROCrate_encoder(oa_2)

    def _arrow1739(s: ArcStudy, oa: Any=oa) -> Json:
        return Study_ROCrate_encoder(None, s)

    def _arrow1740(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Investigation_ROCrate_genID(oa))), ("@type", Json(0, "Investigation")), ("additionalType", Json(0, "Investigation")), ("identifier", Json(0, oa.Identifier)), ("filename", Json(0, ArcInvestigation.FileName())), try_include("title", _arrow1732, oa.Title), try_include("description", _arrow1733, oa.Description), try_include("submissionDate", _arrow1734, oa.SubmissionDate), try_include("publicReleaseDate", _arrow1735, oa.PublicReleaseDate), try_include_seq("ontologySourceReferences", _arrow1736, oa.OntologySourceReferences), try_include_seq("publications", _arrow1737, oa.Publications), try_include_seq("people", _arrow1738, oa.Contacts), try_include_seq("studies", _arrow1739, oa.Studies), try_include_seq("comments", _arrow1740, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow1752(get: IGetters) -> ArcInvestigation:
    identifier: str
    match_value: str | None
    object_arg: IOptionalGetter = get.Optional
    match_value = object_arg.Field("identifier", string)
    identifier = create_missing_identifier() if (match_value is None) else match_value
    def _arrow1741(__unit: None=None) -> FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]] | None:
        arg_3: Decoder_1[FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]]] = list_1_1(Study_ROCrate_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("studies", arg_3)

    pattern_input: tuple[FSharpList[ArcStudy], FSharpList[FSharpList[ArcAssay]]] = unzip(default_arg(_arrow1741(), empty()))
    studies_raw: FSharpList[ArcStudy] = pattern_input[0]
    def projection(a: ArcAssay) -> str:
        return a.Identifier

    class ObjectExpr1743:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1742(x: str, y: str) -> bool:
                return x == y

            return _arrow1742

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    assays: Array[ArcAssay] = list(distinct_by(projection, concat(pattern_input[1]), ObjectExpr1743()))
    studies: Array[ArcStudy] = list(studies_raw)
    def mapping(a_1: ArcStudy) -> str:
        return a_1.Identifier

    study_identifiers: Array[str] = list(map(mapping, studies_raw))
    def _arrow1744(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow1745(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow1746(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("submissionDate", string)

    def _arrow1747(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("publicReleaseDate", string)

    def _arrow1748(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_13: Decoder_1[Array[OntologySourceReference]] = Decode_resizeArray(OntologySourceReference_ROCrate_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("ontologySourceReferences", arg_13)

    def _arrow1749(__unit: None=None) -> Array[Publication] | None:
        arg_15: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_ROCrate_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_15)

    def _arrow1750(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ROCrate_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_17)

    def _arrow1751(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return ArcInvestigation(identifier, _arrow1744(), _arrow1745(), _arrow1746(), _arrow1747(), _arrow1748(), _arrow1749(), _arrow1750(), assays, studies, study_identifiers, _arrow1751())


Investigation_ROCrate_decoder: Decoder_1[ArcInvestigation] = object(_arrow1752)

def Investigation_ROCrate_encodeRoCrate(oa: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1754(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1755(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1756(oa_1: ArcInvestigation, oa: Any=oa) -> Json:
        return Investigation_ROCrate_encoder(oa_1)

    return Json(5, choose(chooser, of_array([try_include("@type", _arrow1754, "CreativeWork"), try_include("@id", _arrow1755, "ro-crate-metadata.json"), try_include("about", _arrow1756, oa), ("conformsTo", conforms_to_jsonvalue), ("@context", context_jsonvalue_1)])))


Investigation_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "identifier", "title", "description", "submissionDate", "publicReleaseDate", "ontologySourceReferences", "publications", "people", "studies", "comments", "@type", "@context"])

def Investigation_ISAJson_encoder(inv: ArcInvestigation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], inv: Any=inv) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1757(value_2: str, inv: Any=inv) -> Json:
        return Json(0, value_2)

    def _arrow1758(value_4: str, inv: Any=inv) -> Json:
        return Json(0, value_4)

    def _arrow1759(value_6: str, inv: Any=inv) -> Json:
        return Json(0, value_6)

    def _arrow1760(value_8: str, inv: Any=inv) -> Json:
        return Json(0, value_8)

    def _arrow1761(oa: Publication, inv: Any=inv) -> Json:
        return Publication_ISAJson_encoder(oa)

    def _arrow1762(person: Person, inv: Any=inv) -> Json:
        return Person_ISAJson_encoder(person)

    def _arrow1763(s: ArcStudy, inv: Any=inv) -> Json:
        return Study_ISAJson_encoder(None, s)

    return Json(5, choose(chooser, of_array([("filename", Json(0, ArcInvestigation.FileName())), ("identifier", Json(0, inv.Identifier)), try_include("title", _arrow1757, inv.Title), try_include("description", _arrow1758, inv.Description), try_include("submissionDate", _arrow1759, inv.SubmissionDate), try_include("publicReleaseDate", _arrow1760, inv.PublicReleaseDate), try_include_seq("ontologySourceReferences", OntologySourceReference_ISAJson_encoder, inv.OntologySourceReferences), try_include_seq("publications", _arrow1761, inv.Publications), try_include_seq("people", _arrow1762, inv.Contacts), try_include_seq("studies", _arrow1763, inv.Studies), try_include_seq("comments", Comment_ISAJson_encoder, inv.Comments)])))


def _arrow1775(get: IGetters) -> ArcInvestigation:
    identifer: str
    match_value: str | None
    object_arg: IOptionalGetter = get.Optional
    match_value = object_arg.Field("identifier", string)
    identifer = create_missing_identifier() if (match_value is None) else match_value
    def _arrow1764(__unit: None=None) -> FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]] | None:
        arg_3: Decoder_1[FSharpList[tuple[ArcStudy, FSharpList[ArcAssay]]]] = list_1_1(Study_ISAJson_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("studies", arg_3)

    pattern_input: tuple[FSharpList[ArcStudy], FSharpList[FSharpList[ArcAssay]]] = unzip(default_arg(_arrow1764(), empty()))
    studies_raw: FSharpList[ArcStudy] = pattern_input[0]
    def projection(a: ArcAssay) -> str:
        return a.Identifier

    class ObjectExpr1766:
        @property
        def Equals(self) -> Callable[[str, str], bool]:
            def _arrow1765(x: str, y: str) -> bool:
                return x == y

            return _arrow1765

        @property
        def GetHashCode(self) -> Callable[[str], int]:
            return string_hash

    assays: Array[ArcAssay] = list(distinct_by(projection, concat(pattern_input[1]), ObjectExpr1766()))
    studies: Array[ArcStudy] = list(studies_raw)
    def mapping(a_1: ArcStudy) -> str:
        return a_1.Identifier

    study_identifiers: Array[str] = list(map(mapping, studies_raw))
    def _arrow1767(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("title", string)

    def _arrow1768(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow1769(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("submissionDate", string)

    def _arrow1770(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("publicReleaseDate", string)

    def _arrow1771(__unit: None=None) -> Array[OntologySourceReference] | None:
        arg_13: Decoder_1[Array[OntologySourceReference]] = Decode_resizeArray(OntologySourceReference_ISAJson_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("ontologySourceReferences", arg_13)

    def _arrow1772(__unit: None=None) -> Array[Publication] | None:
        arg_15: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_ISAJson_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_15)

    def _arrow1773(__unit: None=None) -> Array[Person] | None:
        arg_17: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ISAJson_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_17)

    def _arrow1774(__unit: None=None) -> Array[Comment] | None:
        arg_19: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return ArcInvestigation(identifer, _arrow1767(), _arrow1768(), _arrow1769(), _arrow1770(), _arrow1771(), _arrow1772(), _arrow1773(), assays, studies, study_identifiers, _arrow1774())


Investigation_ISAJson_decoder: Decoder_1[ArcInvestigation] = Decode_objectNoAdditionalProperties(Investigation_ISAJson_allowedFields, _arrow1775)

def ARCtrl_ArcInvestigation__ArcInvestigation_fromJsonString_Static_Z721C83C5(s: str) -> ArcInvestigation:
    match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(Investigation_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcInvestigation__ArcInvestigation_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcInvestigation], str]:
    def _arrow1776(obj: ArcInvestigation, spaces: Any=spaces) -> str:
        value: Json = Investigation_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1776


def ARCtrl_ArcInvestigation__ArcInvestigation_fromCompressedJsonString_Static_Z721C83C5(s: str) -> ArcInvestigation:
    try: 
        match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(decode(Investigation_decoderCompressed), s)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as e_1:
        arg_1: str = str(e_1)
        return to_fail(printf("Error. Unable to parse json string to ArcStudy: %s"))(arg_1)



def ARCtrl_ArcInvestigation__ArcInvestigation_toCompressedJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcInvestigation], str]:
    def _arrow1777(obj: ArcInvestigation, spaces: Any=spaces) -> str:
        return to_string(default_arg(spaces, 0), encode(Investigation_encoderCompressed, obj))

    return _arrow1777


def ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateJsonString_Static_Z721C83C5(s: str) -> ArcInvestigation:
    match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(Investigation_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcInvestigation__ArcInvestigation_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcInvestigation], str]:
    def _arrow1778(obj: ArcInvestigation, spaces: Any=spaces) -> str:
        value: Json = Investigation_ROCrate_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1778


def ARCtrl_ArcInvestigation__ArcInvestigation_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcInvestigation], str]:
    def _arrow1779(obj: ArcInvestigation, spaces: Any=spaces) -> str:
        value: Json = Investigation_ISAJson_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1779


def ARCtrl_ArcInvestigation__ArcInvestigation_fromISAJsonString_Static_Z721C83C5(s: str) -> ArcInvestigation:
    match_value: FSharpResult_2[ArcInvestigation, str] = Decode_fromString(Investigation_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



__all__ = ["Investigation_encoder", "Investigation_decoder", "Investigation_encoderCompressed", "Investigation_decoderCompressed", "Investigation_ROCrate_genID", "Investigation_ROCrate_encoder", "Investigation_ROCrate_decoder", "Investigation_ROCrate_encodeRoCrate", "Investigation_ISAJson_allowedFields", "Investigation_ISAJson_encoder", "Investigation_ISAJson_decoder", "ARCtrl_ArcInvestigation__ArcInvestigation_fromJsonString_Static_Z721C83C5", "ARCtrl_ArcInvestigation__ArcInvestigation_toJsonString_Static_71136F3F", "ARCtrl_ArcInvestigation__ArcInvestigation_fromCompressedJsonString_Static_Z721C83C5", "ARCtrl_ArcInvestigation__ArcInvestigation_toCompressedJsonString_Static_71136F3F", "ARCtrl_ArcInvestigation__ArcInvestigation_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_ArcInvestigation__ArcInvestigation_toROCrateJsonString_Static_71136F3F", "ARCtrl_ArcInvestigation__ArcInvestigation_toISAJsonString_Static_71136F3F", "ARCtrl_ArcInvestigation__ArcInvestigation_fromISAJsonString_Static_Z721C83C5"]

