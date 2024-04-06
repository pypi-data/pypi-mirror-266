from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (try_find, FSharpList, choose, of_array, singleton, map as map_1, empty)
from ..fable_modules.fable_library.option import (default_arg, value as value_14, bind, map, default_arg_with)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.seq import is_empty
from ..fable_modules.fable_library.string_ import (replace, to_text, printf, to_fail)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import (equals, get_enumerator, dispose, IEnumerable_1)
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, IGetters, list_1 as list_1_2)
from ..fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string
from ..Core.arc_types import (ArcAssay, ArcStudy)
from ..Core.comment import Comment
from ..Core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, Person_setSourceAssayComment, Person_getSourceAssayIdentifiersFromComments, Person_removeSourceAssayComments)
from ..Core.Helper.collections_ import (ResizeArray_map, Option_fromValueWithDefault)
from ..Core.Helper.identifier import (Study_tryFileNameFromIdentifier, Study_tryIdentifierFromFileName, create_missing_identifier, Assay_fileNameFromIdentifier)
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.person import Person
from ..Core.Process.factor import Factor
from ..Core.Process.material_attribute import MaterialAttribute
from ..Core.Process.process import Process
from ..Core.Process.process_sequence import (get_protocols, get_factors, get_characteristics, get_units)
from ..Core.Process.protocol import Protocol
from ..Core.publication import Publication
from ..Core.Table.arc_table import ArcTable
from ..Core.Table.arc_tables import ArcTables
from ..Core.Table.composite_cell import CompositeCell
from .assay import (Assay_ROCrate_encoder, Assay_ROCrate_decoder, Assay_ISAJson_encoder, Assay_ISAJson_decoder)
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from .context.rocrate.isa_study_context import context_jsonvalue
from .decode import (Decode_resizeArray, Decode_objectNoAdditionalProperties)
from .encode import (try_include, try_include_seq, try_include_list, default_spaces)
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (Person_encoder, Person_decoder, Person_ROCrate_encoder, Person_ROCrate_decoder, Person_ISAJson_encoder, Person_ISAJson_decoder)
from .Process.factor import Factor_ISAJson_encoder
from .Process.material_attribute import MaterialAttribute_ISAJson_encoder
from .Process.process import (Process_ROCrate_encoder, Process_ROCrate_decoder, Process_ISAJson_encoder, Process_ISAJson_decoder)
from .Process.protocol import Protocol_ISAJson_encoder
from .Process.study_materials import encoder
from .publication import (Publication_encoder, Publication_decoder, Publication_ROCrate_encoder, Publication_ROCrate_decoder, Publication_ISAJson_encoder, Publication_ISAJson_decoder)
from .Table.arc_table import (ArcTable_encoder, ArcTable_decoder, ArcTable_encoderCompressed, ArcTable_decoderCompressed)
from .Table.compression import (decode, encode)

def Study_Helper_getAssayInformation(assays: FSharpList[ArcAssay] | None, study: ArcStudy) -> Array[ArcAssay]:
    if assays is not None:
        def f(assay_id: str, assays: Any=assays, study: Any=study) -> ArcAssay:
            def predicate(a: ArcAssay, assay_id: Any=assay_id) -> bool:
                return a.Identifier == assay_id

            return default_arg(try_find(predicate, value_14(assays)), ArcAssay.init(assay_id))

        return ResizeArray_map(f, study.RegisteredAssayIdentifiers)

    else: 
        return study.GetRegisteredAssaysOrIdentifier()



def Study_encoder(study: ArcStudy) -> Json:
    def chooser(tupled_arg: tuple[str, Json], study: Any=study) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1575(value_1: str, study: Any=study) -> Json:
        return Json(0, value_1)

    def _arrow1576(value_3: str, study: Any=study) -> Json:
        return Json(0, value_3)

    def _arrow1577(value_5: str, study: Any=study) -> Json:
        return Json(0, value_5)

    def _arrow1578(value_7: str, study: Any=study) -> Json:
        return Json(0, value_7)

    def _arrow1579(oa: Publication, study: Any=study) -> Json:
        return Publication_encoder(oa)

    def _arrow1580(person: Person, study: Any=study) -> Json:
        return Person_encoder(person)

    def _arrow1581(oa_1: OntologyAnnotation, study: Any=study) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1582(table: ArcTable, study: Any=study) -> Json:
        return ArcTable_encoder(table)

    def _arrow1583(value_9: str, study: Any=study) -> Json:
        return Json(0, value_9)

    def _arrow1584(comment: Comment, study: Any=study) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, study.Identifier)), try_include("Title", _arrow1575, study.Title), try_include("Description", _arrow1576, study.Description), try_include("SubmissionDate", _arrow1577, study.SubmissionDate), try_include("PublicReleaseDate", _arrow1578, study.PublicReleaseDate), try_include_seq("Publications", _arrow1579, study.Publications), try_include_seq("Contacts", _arrow1580, study.Contacts), try_include_seq("StudyDesignDescriptors", _arrow1581, study.StudyDesignDescriptors), try_include_seq("Tables", _arrow1582, study.Tables), try_include_seq("RegisteredAssayIdentifiers", _arrow1583, study.RegisteredAssayIdentifiers), try_include_seq("Comments", _arrow1584, study.Comments)])))


def _arrow1596(get: IGetters) -> ArcStudy:
    def _arrow1585(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow1586(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("Title", string)

    def _arrow1587(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("Description", string)

    def _arrow1588(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("SubmissionDate", string)

    def _arrow1589(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("PublicReleaseDate", string)

    def _arrow1590(__unit: None=None) -> Array[Publication] | None:
        arg_11: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("Publications", arg_11)

    def _arrow1591(__unit: None=None) -> Array[Person] | None:
        arg_13: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Contacts", arg_13)

    def _arrow1592(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_15: Decoder_1[Array[OntologyAnnotation]] = Decode_resizeArray(OntologyAnnotation_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("StudyDesignDescriptors", arg_15)

    def _arrow1593(__unit: None=None) -> Array[ArcTable] | None:
        arg_17: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("Tables", arg_17)

    def _arrow1594(__unit: None=None) -> Array[str] | None:
        arg_19: Decoder_1[Array[str]] = Decode_resizeArray(string)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("RegisteredAssayIdentifiers", arg_19)

    def _arrow1595(__unit: None=None) -> Array[Comment] | None:
        arg_21: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("Comments", arg_21)

    return ArcStudy(_arrow1585(), _arrow1586(), _arrow1587(), _arrow1588(), _arrow1589(), _arrow1590(), _arrow1591(), _arrow1592(), _arrow1593(), _arrow1594(), _arrow1595())


Study_decoder: Decoder_1[ArcStudy] = object(_arrow1596)

def Study_encoderCompressed(string_table: Any, oa_table: Any, cell_table: Any, study: ArcStudy) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1597(value_1: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Json(0, value_1)

    def _arrow1598(value_3: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Json(0, value_3)

    def _arrow1599(value_5: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Json(0, value_5)

    def _arrow1600(value_7: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Json(0, value_7)

    def _arrow1601(oa: Publication, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Publication_encoder(oa)

    def _arrow1602(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Person_encoder(person)

    def _arrow1603(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1604(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return ArcTable_encoderCompressed(string_table, oa_table, cell_table, table)

    def _arrow1605(value_9: str, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Json(0, value_9)

    def _arrow1606(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, study: Any=study) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, study.Identifier)), try_include("Title", _arrow1597, study.Title), try_include("Description", _arrow1598, study.Description), try_include("SubmissionDate", _arrow1599, study.SubmissionDate), try_include("PublicReleaseDate", _arrow1600, study.PublicReleaseDate), try_include_seq("Publications", _arrow1601, study.Publications), try_include_seq("Contacts", _arrow1602, study.Contacts), try_include_seq("StudyDesignDescriptors", _arrow1603, study.StudyDesignDescriptors), try_include_seq("Tables", _arrow1604, study.Tables), try_include_seq("RegisteredAssayIdentifiers", _arrow1605, study.RegisteredAssayIdentifiers), try_include_seq("Comments", _arrow1606, study.Comments)])))


def Study_decoderCompressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcStudy]:
    def _arrow1618(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcStudy:
        def _arrow1607(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow1608(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("Title", string)

        def _arrow1609(__unit: None=None) -> str | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("Description", string)

        def _arrow1610(__unit: None=None) -> str | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("SubmissionDate", string)

        def _arrow1611(__unit: None=None) -> str | None:
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("PublicReleaseDate", string)

        def _arrow1612(__unit: None=None) -> Array[Publication] | None:
            arg_11: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_decoder)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("Publications", arg_11)

        def _arrow1613(__unit: None=None) -> Array[Person] | None:
            arg_13: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Contacts", arg_13)

        def _arrow1614(__unit: None=None) -> Array[OntologyAnnotation] | None:
            arg_15: Decoder_1[Array[OntologyAnnotation]] = Decode_resizeArray(OntologyAnnotation_decoder)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("StudyDesignDescriptors", arg_15)

        def _arrow1615(__unit: None=None) -> Array[ArcTable] | None:
            arg_17: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoderCompressed(string_table, oa_table, cell_table))
            object_arg_8: IOptionalGetter = get.Optional
            return object_arg_8.Field("Tables", arg_17)

        def _arrow1616(__unit: None=None) -> Array[str] | None:
            arg_19: Decoder_1[Array[str]] = Decode_resizeArray(string)
            object_arg_9: IOptionalGetter = get.Optional
            return object_arg_9.Field("RegisteredAssayIdentifiers", arg_19)

        def _arrow1617(__unit: None=None) -> Array[Comment] | None:
            arg_21: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_10: IOptionalGetter = get.Optional
            return object_arg_10.Field("Comments", arg_21)

        return ArcStudy(_arrow1607(), _arrow1608(), _arrow1609(), _arrow1610(), _arrow1611(), _arrow1612(), _arrow1613(), _arrow1614(), _arrow1615(), _arrow1616(), _arrow1617())

    return object(_arrow1618)


def Study_ROCrate_genID(a: ArcStudy) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyStudy"

    else: 
        return ("#study/" + replace(match_value, " ", "_")) + ""



def Study_ROCrate_encoder(assays: FSharpList[ArcAssay] | None, s: ArcStudy) -> Json:
    file_name: str | None = Study_tryFileNameFromIdentifier(s.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(s)
    assays_1: Array[ArcAssay] = Study_Helper_getAssayInformation(assays, s)
    def chooser(tupled_arg: tuple[str, Json], assays: Any=assays, s: Any=s) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1619(value_4: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_4)

    def _arrow1620(value_6: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_6)

    def _arrow1621(value_8: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_8)

    def _arrow1622(oa: OntologyAnnotation, assays: Any=assays, s: Any=s) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa)

    def _arrow1623(value_10: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_10)

    def _arrow1624(value_12: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_12)

    def _arrow1625(oa_1: Publication, assays: Any=assays, s: Any=s) -> Json:
        return Publication_ROCrate_encoder(oa_1)

    def _arrow1626(oa_2: Person, assays: Any=assays, s: Any=s) -> Json:
        return Person_ROCrate_encoder(oa_2)

    def _arrow1628(__unit: None=None, assays: Any=assays, s: Any=s) -> Callable[[Process], Json]:
        study_name: str | None = s.Identifier
        def _arrow1627(oa_3: Process) -> Json:
            return Process_ROCrate_encoder(study_name, None, oa_3)

        return _arrow1627

    def _arrow1630(__unit: None=None, assays: Any=assays, s: Any=s) -> Callable[[ArcAssay], Json]:
        study_name_1: str | None = s.Identifier
        def _arrow1629(a_1: ArcAssay) -> Json:
            return Assay_ROCrate_encoder(study_name_1, a_1)

        return _arrow1629

    def _arrow1631(comment: Comment, assays: Any=assays, s: Any=s) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Study_ROCrate_genID(s))), ("@type", list_1_1(singleton(Json(0, "Study")))), ("additionalType", Json(0, "Study")), ("identifier", Json(0, s.Identifier)), try_include("filename", _arrow1619, file_name), try_include("title", _arrow1620, s.Title), try_include("description", _arrow1621, s.Description), try_include_seq("studyDesignDescriptors", _arrow1622, s.StudyDesignDescriptors), try_include("submissionDate", _arrow1623, s.SubmissionDate), try_include("publicReleaseDate", _arrow1624, s.PublicReleaseDate), try_include_seq("publications", _arrow1625, s.Publications), try_include_seq("people", _arrow1626, s.Contacts), try_include_list("processSequence", _arrow1628(), processes), try_include_seq("assays", _arrow1630(), assays_1), try_include_seq("comments", _arrow1631, s.Comments), ("@context", context_jsonvalue)])))


def _arrow1642(get: IGetters) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    def _arrow1632(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Study_tryIdentifierFromFileName, _arrow1632()), create_missing_identifier())
    assays: FSharpList[ArcAssay] | None
    arg_3: Decoder_1[FSharpList[ArcAssay]] = list_1_2(Assay_ROCrate_decoder)
    object_arg_1: IOptionalGetter = get.Optional
    assays = object_arg_1.Field("assays", arg_3)
    def mapping_1(arg_4: FSharpList[ArcAssay]) -> Array[str]:
        def mapping(a: ArcAssay, arg_4: Any=arg_4) -> str:
            return a.Identifier

        return list(map_1(mapping, arg_4))

    assay_identifiers: Array[str] | None = map(mapping_1, assays)
    def mapping_2(ps: FSharpList[Process]) -> Array[ArcTable]:
        return ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(ps).Tables

    def _arrow1633(__unit: None=None) -> FSharpList[Process] | None:
        arg_6: Decoder_1[FSharpList[Process]] = list_1_2(Process_ROCrate_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("processSequence", arg_6)

    tables: Array[ArcTable] | None = map(mapping_2, _arrow1633())
    def _arrow1634(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("title", string)

    def _arrow1635(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("description", string)

    def _arrow1636(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("submissionDate", string)

    def _arrow1637(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("publicReleaseDate", string)

    def _arrow1638(__unit: None=None) -> Array[Publication] | None:
        arg_16: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_ROCrate_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("publications", arg_16)

    def _arrow1639(__unit: None=None) -> Array[Person] | None:
        arg_18: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ROCrate_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("people", arg_18)

    def _arrow1640(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_20: Decoder_1[Array[OntologyAnnotation]] = Decode_resizeArray(OntologyAnnotation_ROCrate_decoderDefinedTerm)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("studyDesignDescriptors", arg_20)

    def _arrow1641(__unit: None=None) -> Array[Comment] | None:
        arg_22: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoder)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("comments", arg_22)

    return (ArcStudy(identifier, _arrow1634(), _arrow1635(), _arrow1636(), _arrow1637(), _arrow1638(), _arrow1639(), _arrow1640(), tables, assay_identifiers, _arrow1641()), default_arg(assays, empty()))


Study_ROCrate_decoder: Decoder_1[tuple[ArcStudy, FSharpList[ArcAssay]]] = object(_arrow1642)

def Study_ISAJson_encoder(assays: FSharpList[ArcAssay] | None, s: ArcStudy) -> Json:
    study: ArcStudy = s.Copy(True)
    file_name: str = Assay_fileNameFromIdentifier(study.Identifier)
    assays_1: Array[ArcAssay]
    n: Array[ArcAssay] = []
    enumerator: Any = get_enumerator(Study_Helper_getAssayInformation(assays, study))
    try: 
        while enumerator.System_Collections_IEnumerator_MoveNext():
            a: ArcAssay = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
            assay: ArcAssay = a.Copy()
            enumerator_1: Any = get_enumerator(assay.Performers)
            try: 
                while enumerator_1.System_Collections_IEnumerator_MoveNext():
                    person_1: Person = Person_setSourceAssayComment(enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current(), assay.Identifier)
                    (study.Contacts.append(person_1))

            finally: 
                dispose(enumerator_1)

            assay.Performers = []
            (n.append(assay))

    finally: 
        dispose(enumerator)

    assays_1 = n
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(study)
    protocols: FSharpList[Protocol] = get_protocols(processes)
    factors: FSharpList[Factor] = get_factors(processes)
    characteristics: FSharpList[MaterialAttribute] = get_characteristics(processes)
    units: FSharpList[OntologyAnnotation] = get_units(processes)
    def chooser(tupled_arg: tuple[str, Json], assays: Any=assays, s: Any=s) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1643(value_2: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_2)

    def _arrow1644(value_4: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_4)

    def _arrow1645(value_6: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_6)

    def _arrow1646(value_8: str, assays: Any=assays, s: Any=s) -> Json:
        return Json(0, value_8)

    def _arrow1647(oa: Publication, assays: Any=assays, s: Any=s) -> Json:
        return Publication_ISAJson_encoder(oa)

    def _arrow1648(person_2: Person, assays: Any=assays, s: Any=s) -> Json:
        return Person_ISAJson_encoder(person_2)

    def _arrow1649(oa_1: Protocol, assays: Any=assays, s: Any=s) -> Json:
        return Protocol_ISAJson_encoder(oa_1)

    def _arrow1650(ps: FSharpList[Process], assays: Any=assays, s: Any=s) -> Json:
        return encoder(ps)

    def _arrow1651(value_10: Factor, assays: Any=assays, s: Any=s) -> Json:
        return Factor_ISAJson_encoder(value_10)

    def _arrow1652(value_11: MaterialAttribute, assays: Any=assays, s: Any=s) -> Json:
        return MaterialAttribute_ISAJson_encoder(value_11)

    def _arrow1653(oa_2: Process, assays: Any=assays, s: Any=s) -> Json:
        return Process_ISAJson_encoder(oa_2)

    def _arrow1654(a_1: ArcAssay, assays: Any=assays, s: Any=s) -> Json:
        return Assay_ISAJson_encoder(a_1)

    return Json(5, choose(chooser, of_array([("filename", Json(0, file_name)), ("identifier", Json(0, study.Identifier)), try_include("title", _arrow1643, study.Title), try_include("description", _arrow1644, study.Description), try_include("submissionDate", _arrow1645, study.SubmissionDate), try_include("publicReleaseDate", _arrow1646, study.PublicReleaseDate), try_include_seq("publications", _arrow1647, study.Publications), try_include_seq("people", _arrow1648, study.Contacts), try_include_seq("studyDesignDescriptors", OntologyAnnotation_ISAJson_encoder, study.StudyDesignDescriptors), try_include_list("protocols", _arrow1649, protocols), try_include("materials", _arrow1650, Option_fromValueWithDefault(empty(), processes)), try_include_list("factors", _arrow1651, factors), try_include_list("characteristicCategories", _arrow1652, characteristics), try_include_list("unitCategories", OntologyAnnotation_ISAJson_encoder, units), try_include_list("processSequence", _arrow1653, processes), try_include_seq("assays", _arrow1654, assays_1), try_include_seq("comments", Comment_ISAJson_encoder, study.Comments)])))


Study_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "identifier", "title", "description", "submissionDate", "publicReleaseDate", "publications", "people", "studyDesignDescriptors", "protocols", "materials", "assays", "factors", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow1670(get: IGetters) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    def _arrow1655(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    def def_thunk(__unit: None=None) -> str:
        def _arrow1656(__unit: None=None) -> str | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("filename", string)

        return default_arg(bind(Study_tryIdentifierFromFileName, _arrow1656()), create_missing_identifier())

    identifier: str = default_arg_with(_arrow1655(), def_thunk)
    def mapping(arg_6: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_6)
        return a.Tables

    def _arrow1657(__unit: None=None) -> FSharpList[Process] | None:
        arg_5: Decoder_1[FSharpList[Process]] = list_1_2(Process_ISAJson_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("processSequence", arg_5)

    tables: Array[ArcTable] | None = map(mapping, _arrow1657())
    assays: FSharpList[ArcAssay] | None
    arg_8: Decoder_1[FSharpList[ArcAssay]] = list_1_2(Assay_ISAJson_decoder)
    object_arg_3: IOptionalGetter = get.Optional
    assays = object_arg_3.Field("assays", arg_8)
    persons_raw: Array[Person] | None
    arg_10: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ISAJson_decoder)
    object_arg_4: IOptionalGetter = get.Optional
    persons_raw = object_arg_4.Field("people", arg_10)
    persons: Array[Person] = []
    if persons_raw is not None:
        enumerator: Any = get_enumerator(value_14(persons_raw))
        try: 
            while enumerator.System_Collections_IEnumerator_MoveNext():
                person: Person = enumerator.System_Collections_Generic_IEnumerator_1_get_Current()
                source_assays: IEnumerable_1[str] = Person_getSourceAssayIdentifiersFromComments(person)
                with get_enumerator(source_assays) as enumerator_1:
                    while enumerator_1.System_Collections_IEnumerator_MoveNext():
                        assay_identifier: str = enumerator_1.System_Collections_Generic_IEnumerator_1_get_Current()
                        with get_enumerator(value_14(assays)) as enumerator_2:
                            while enumerator_2.System_Collections_IEnumerator_MoveNext():
                                assay: ArcAssay = enumerator_2.System_Collections_Generic_IEnumerator_1_get_Current()
                                if assay.Identifier == assay_identifier:
                                    (assay.Performers.append(person))

                person.Comments = Person_removeSourceAssayComments(person)
                if is_empty(source_assays):
                    (persons.append(person))


        finally: 
            dispose(enumerator)


    def mapping_2(arg_11: FSharpList[ArcAssay]) -> Array[str]:
        def mapping_1(a_1: ArcAssay, arg_11: Any=arg_11) -> str:
            return a_1.Identifier

        return list(map_1(mapping_1, arg_11))

    assay_identifiers: Array[str] | None = map(mapping_2, assays)
    def _arrow1663(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("title", string)

    def _arrow1664(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("description", string)

    def _arrow1665(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("submissionDate", string)

    def _arrow1666(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("publicReleaseDate", string)

    def _arrow1667(__unit: None=None) -> Array[Publication] | None:
        arg_21: Decoder_1[Array[Publication]] = Decode_resizeArray(Publication_ISAJson_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("publications", arg_21)

    def _arrow1668(__unit: None=None) -> Array[OntologyAnnotation] | None:
        arg_23: Decoder_1[Array[OntologyAnnotation]] = Decode_resizeArray(OntologyAnnotation_ISAJson_decoder)
        object_arg_10: IOptionalGetter = get.Optional
        return object_arg_10.Field("studyDesignDescriptors", arg_23)

    def _arrow1669(__unit: None=None) -> Array[Comment] | None:
        arg_25: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_11: IOptionalGetter = get.Optional
        return object_arg_11.Field("comments", arg_25)

    return (ArcStudy(identifier, _arrow1663(), _arrow1664(), _arrow1665(), _arrow1666(), _arrow1667(), None if (len(persons) == 0) else persons, _arrow1668(), tables, assay_identifiers, _arrow1669()), default_arg(assays, empty()))


Study_ISAJson_decoder: Decoder_1[tuple[ArcStudy, FSharpList[ArcAssay]]] = Decode_objectNoAdditionalProperties(Study_ISAJson_allowedFields, _arrow1670)

def ARCtrl_ArcStudy__ArcStudy_fromJsonString_Static_Z721C83C5(s: str) -> ArcStudy:
    match_value: FSharpResult_2[ArcStudy, str] = Decode_fromString(Study_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcStudy__ArcStudy_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcStudy], str]:
    def _arrow1671(obj: ArcStudy, spaces: Any=spaces) -> str:
        value: Json = Study_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1671


def ARCtrl_ArcStudy__ArcStudy_fromCompressedJsonString_Static_Z721C83C5(s: str) -> ArcStudy:
    try: 
        match_value: FSharpResult_2[ArcStudy, str] = Decode_fromString(decode(Study_decoderCompressed), s)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as e_1:
        arg_1: str = str(e_1)
        return to_fail(printf("Error. Unable to parse json string to ArcStudy: %s"))(arg_1)



def ARCtrl_ArcStudy__ArcStudy_toCompressedJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcStudy], str]:
    def _arrow1672(obj: ArcStudy, spaces: Any=spaces) -> str:
        return to_string(default_arg(spaces, 0), encode(Study_encoderCompressed, obj))

    return _arrow1672


def ARCtrl_ArcStudy__ArcStudy_toROCrateJsonString_Static_3BA23086(assays: FSharpList[ArcAssay] | None=None, spaces: int | None=None) -> Callable[[ArcStudy], str]:
    def _arrow1673(obj: ArcStudy, assays: Any=assays, spaces: Any=spaces) -> str:
        value: Json = Study_ROCrate_encoder(assays, obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1673


def ARCtrl_ArcStudy__ArcStudy_fromROCrateJsonString_Static_Z721C83C5(s: str) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    match_value: FSharpResult_2[tuple[ArcStudy, FSharpList[ArcAssay]], str] = Decode_fromString(Study_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcStudy__ArcStudy_toISAJsonString_Static_3BA23086(assays: FSharpList[ArcAssay] | None=None, spaces: int | None=None) -> Callable[[ArcStudy], str]:
    def _arrow1674(obj: ArcStudy, assays: Any=assays, spaces: Any=spaces) -> str:
        value: Json = Study_ISAJson_encoder(assays, obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1674


def ARCtrl_ArcStudy__ArcStudy_fromISAJsonString_Static_Z721C83C5(s: str) -> tuple[ArcStudy, FSharpList[ArcAssay]]:
    match_value: FSharpResult_2[tuple[ArcStudy, FSharpList[ArcAssay]], str] = Decode_fromString(Study_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



__all__ = ["Study_Helper_getAssayInformation", "Study_encoder", "Study_decoder", "Study_encoderCompressed", "Study_decoderCompressed", "Study_ROCrate_genID", "Study_ROCrate_encoder", "Study_ROCrate_decoder", "Study_ISAJson_encoder", "Study_ISAJson_allowedFields", "Study_ISAJson_decoder", "ARCtrl_ArcStudy__ArcStudy_fromJsonString_Static_Z721C83C5", "ARCtrl_ArcStudy__ArcStudy_toJsonString_Static_71136F3F", "ARCtrl_ArcStudy__ArcStudy_fromCompressedJsonString_Static_Z721C83C5", "ARCtrl_ArcStudy__ArcStudy_toCompressedJsonString_Static_71136F3F", "ARCtrl_ArcStudy__ArcStudy_toROCrateJsonString_Static_3BA23086", "ARCtrl_ArcStudy__ArcStudy_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_ArcStudy__ArcStudy_toISAJsonString_Static_3BA23086", "ARCtrl_ArcStudy__ArcStudy_fromISAJsonString_Static_Z721C83C5"]

