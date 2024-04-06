from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (choose, of_array, FSharpList, singleton, empty)
from ..fable_modules.fable_library.option import (default_arg, map, bind)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.string_ import (replace, to_text, printf, to_fail)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import equals
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, IGetters, list_1 as list_1_2, map as map_1)
from ..fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string
from ..Core.arc_types import ArcAssay
from ..Core.comment import Comment
from ..Core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, JsonTypes_composeTechnologyPlatform, JsonTypes_decomposeTechnologyPlatform)
from ..Core.Helper.collections_ import Option_fromValueWithDefault
from ..Core.Helper.identifier import (Assay_fileNameFromIdentifier, create_missing_identifier, Assay_tryIdentifierFromFileName)
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.person import Person
from ..Core.Process.data import Data
from ..Core.Process.material_attribute import MaterialAttribute
from ..Core.Process.process import Process
from ..Core.Process.process_sequence import (get_data, get_characteristics, get_units)
from ..Core.Table.arc_table import ArcTable
from ..Core.Table.arc_tables import ArcTables
from ..Core.Table.composite_cell import CompositeCell
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from .context.rocrate.isa_assay_context import context_jsonvalue
from .decode import (Decode_resizeArray, Decode_objectNoAdditionalProperties)
from .encode import (try_include, try_include_seq, try_include_list, default_spaces)
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderPropertyValue, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderPropertyValue, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (Person_encoder, Person_decoder, Person_ROCrate_encoder, Person_ROCrate_decoder)
from .Process.assay_materials import encoder
from .Process.data import (Data_ROCrate_encoder, Data_ISAJson_encoder)
from .Process.material_attribute import MaterialAttribute_ISAJson_encoder
from .Process.process import (Process_ROCrate_encoder, Process_ROCrate_decoder, Process_ISAJson_encoder, Process_ISAJson_decoder)
from .Table.arc_table import (ArcTable_encoder, ArcTable_decoder, ArcTable_encoderCompressed, ArcTable_decoderCompressed)
from .Table.compression import (decode, encode)

def Assay_encoder(assay: ArcAssay) -> Json:
    def chooser(tupled_arg: tuple[str, Json], assay: Any=assay) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1515(oa: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa)

    def _arrow1516(oa_1: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1517(oa_2: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow1518(table: ArcTable, assay: Any=assay) -> Json:
        return ArcTable_encoder(table)

    def _arrow1519(person: Person, assay: Any=assay) -> Json:
        return Person_encoder(person)

    def _arrow1520(comment: Comment, assay: Any=assay) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, assay.Identifier)), try_include("MeasurementType", _arrow1515, assay.MeasurementType), try_include("TechnologyType", _arrow1516, assay.TechnologyType), try_include("TechnologyPlatform", _arrow1517, assay.TechnologyPlatform), try_include_seq("Tables", _arrow1518, assay.Tables), try_include_seq("Performers", _arrow1519, assay.Performers), try_include_seq("Comments", _arrow1520, assay.Comments)])))


def _arrow1528(get: IGetters) -> ArcAssay:
    def _arrow1521(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow1522(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow1523(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow1524(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow1525(__unit: None=None) -> Array[ArcTable] | None:
        arg_9: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoder)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("Tables", arg_9)

    def _arrow1526(__unit: None=None) -> Array[Person] | None:
        arg_11: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("Performers", arg_11)

    def _arrow1527(__unit: None=None) -> Array[Comment] | None:
        arg_13: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Comments", arg_13)

    return ArcAssay.create(_arrow1521(), _arrow1522(), _arrow1523(), _arrow1524(), _arrow1525(), _arrow1526(), _arrow1527())


Assay_decoder: Decoder_1[ArcAssay] = object(_arrow1528)

def Assay_encoderCompressed(string_table: Any, oa_table: Any, cell_table: Any, assay: ArcAssay) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1529(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa)

    def _arrow1530(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1531(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow1532(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return ArcTable_encoderCompressed(string_table, oa_table, cell_table, table)

    def _arrow1533(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return Person_encoder(person)

    def _arrow1534(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, assay.Identifier)), try_include("MeasurementType", _arrow1529, assay.MeasurementType), try_include("TechnologyType", _arrow1530, assay.TechnologyType), try_include("TechnologyPlatform", _arrow1531, assay.TechnologyPlatform), try_include_seq("Tables", _arrow1532, assay.Tables), try_include_seq("Performers", _arrow1533, assay.Performers), try_include_seq("Comments", _arrow1534, assay.Comments)])))


def Assay_decoderCompressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcAssay]:
    def _arrow1542(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcAssay:
        def _arrow1535(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow1536(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow1537(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow1538(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow1539(__unit: None=None) -> Array[ArcTable] | None:
            arg_9: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoderCompressed(string_table, oa_table, cell_table))
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("Tables", arg_9)

        def _arrow1540(__unit: None=None) -> Array[Person] | None:
            arg_11: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("Performers", arg_11)

        def _arrow1541(__unit: None=None) -> Array[Comment] | None:
            arg_13: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Comments", arg_13)

        return ArcAssay.create(_arrow1535(), _arrow1536(), _arrow1537(), _arrow1538(), _arrow1539(), _arrow1540(), _arrow1541())

    return object(_arrow1542)


def Assay_ROCrate_genID(a: ArcAssay) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyAssay"

    else: 
        return ("#assay/" + replace(match_value, " ", "_")) + ""



def Assay_ROCrate_encoder(study_name: str | None, a: ArcAssay) -> Json:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    def chooser(tupled_arg: tuple[str, Json], study_name: Any=study_name, a: Any=a) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1543(oa: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderPropertyValue(oa)

    def _arrow1544(oa_1: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1545(oa_2: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_2)

    def _arrow1546(oa_3: Person, study_name: Any=study_name, a: Any=a) -> Json:
        return Person_ROCrate_encoder(oa_3)

    def _arrow1547(oa_4: Data, study_name: Any=study_name, a: Any=a) -> Json:
        return Data_ROCrate_encoder(oa_4)

    def _arrow1549(__unit: None=None, study_name: Any=study_name, a: Any=a) -> Callable[[Process], Json]:
        assay_name: str | None = a.Identifier
        def _arrow1548(oa_5: Process) -> Json:
            return Process_ROCrate_encoder(study_name, assay_name, oa_5)

        return _arrow1548

    def _arrow1550(comment: Comment, study_name: Any=study_name, a: Any=a) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Assay_ROCrate_genID(a))), ("@type", list_1_1(singleton(Json(0, "Assay")))), ("additionalType", Json(0, "Assay")), ("identifier", Json(0, a.Identifier)), ("filename", Json(0, file_name)), try_include("measurementType", _arrow1543, a.MeasurementType), try_include("technologyType", _arrow1544, a.TechnologyType), try_include("technologyPlatform", _arrow1545, a.TechnologyPlatform), try_include_seq("performers", _arrow1546, a.Performers), try_include_list("dataFiles", _arrow1547, data_files), try_include_list("processSequence", _arrow1549(), processes), try_include_seq("comments", _arrow1550, a.Comments), ("@context", context_jsonvalue)])))


def _arrow1558(get: IGetters) -> ArcAssay:
    def _arrow1551(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    identifier: str = default_arg(_arrow1551(), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow1552(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(Process_ROCrate_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow1552())
    def _arrow1553(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("measurementType", OntologyAnnotation_ROCrate_decoderPropertyValue)

    def _arrow1554(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("technologyType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1555(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyPlatform", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1556(__unit: None=None) -> Array[Person] | None:
        arg_12: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ROCrate_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("performers", arg_12)

    def _arrow1557(__unit: None=None) -> Array[Comment] | None:
        arg_14: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("comments", arg_14)

    return ArcAssay(identifier, _arrow1553(), _arrow1554(), _arrow1555(), tables, _arrow1556(), _arrow1557())


Assay_ROCrate_decoder: Decoder_1[ArcAssay] = object(_arrow1558)

def Assay_ISAJson_encoder(a: ArcAssay) -> Json:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    characteristics: FSharpList[MaterialAttribute] = get_characteristics(processes)
    units: FSharpList[OntologyAnnotation] = get_units(processes)
    def chooser(tupled_arg: tuple[str, Json], a: Any=a) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1559(value_1: str, a: Any=a) -> Json:
        return Json(0, value_1)

    def mapping(tp: OntologyAnnotation, a: Any=a) -> str:
        return JsonTypes_composeTechnologyPlatform(tp)

    def _arrow1560(oa: Data, a: Any=a) -> Json:
        return Data_ISAJson_encoder(oa)

    def _arrow1561(ps: FSharpList[Process], a: Any=a) -> Json:
        return encoder(ps)

    def _arrow1562(value_3: MaterialAttribute, a: Any=a) -> Json:
        return MaterialAttribute_ISAJson_encoder(value_3)

    def _arrow1563(oa_1: Process, a: Any=a) -> Json:
        return Process_ISAJson_encoder(oa_1)

    return Json(5, choose(chooser, of_array([("filename", Json(0, file_name)), try_include("measurementType", OntologyAnnotation_ISAJson_encoder, a.MeasurementType), try_include("technologyType", OntologyAnnotation_ISAJson_encoder, a.TechnologyType), try_include("technologyPlatform", _arrow1559, map(mapping, a.TechnologyPlatform)), try_include_list("dataFiles", _arrow1560, data_files), try_include("materials", _arrow1561, Option_fromValueWithDefault(empty(), processes)), try_include_list("characteristicCategories", _arrow1562, characteristics), try_include_list("unitCategories", OntologyAnnotation_ISAJson_encoder, units), try_include_list("processSequence", _arrow1563, processes), try_include_seq("comments", Comment_ISAJson_encoder, a.Comments)])))


Assay_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "measurementType", "technologyType", "technologyPlatform", "dataFiles", "materials", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow1570(get: IGetters) -> ArcAssay:
    def _arrow1564(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Assay_tryIdentifierFromFileName, _arrow1564()), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow1565(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(Process_ISAJson_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow1565())
    def _arrow1566(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("measurementType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1567(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("technologyType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1568(__unit: None=None) -> OntologyAnnotation | None:
        arg_10: Decoder_1[OntologyAnnotation] = map_1(JsonTypes_decomposeTechnologyPlatform, string)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyPlatform", arg_10)

    def _arrow1569(__unit: None=None) -> Array[Comment] | None:
        arg_12: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("comments", arg_12)

    return ArcAssay(identifier, _arrow1566(), _arrow1567(), _arrow1568(), tables, None, _arrow1569())


Assay_ISAJson_decoder: Decoder_1[ArcAssay] = Decode_objectNoAdditionalProperties(Assay_ISAJson_allowedFields, _arrow1570)

def ARCtrl_ArcAssay__ArcAssay_fromJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcAssay__ArcAssay_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1571(obj: ArcAssay, spaces: Any=spaces) -> str:
        value: Json = Assay_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1571


def ARCtrl_ArcAssay__ArcAssay_fromCompressedJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    try: 
        match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(decode(Assay_decoderCompressed), s)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as e_1:
        arg_1: str = str(e_1)
        return to_fail(printf("Error. Unable to parse json string to ArcStudy: %s"))(arg_1)



def ARCtrl_ArcAssay__ArcAssay_toCompressedJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1572(obj: ArcAssay, spaces: Any=spaces) -> str:
        return to_string(default_arg(spaces, 0), encode(Assay_encoderCompressed, obj))

    return _arrow1572


def ARCtrl_ArcAssay__ArcAssay_fromROCrateJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcAssay__ArcAssay_toROCrateJsonString_Static_5CABCA47(study_name: str | None=None, spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1573(obj: ArcAssay, study_name: Any=study_name, spaces: Any=spaces) -> str:
        value: Json = Assay_ROCrate_encoder(study_name, obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1573


def ARCtrl_ArcAssay__ArcAssay_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1574(obj: ArcAssay, spaces: Any=spaces) -> str:
        value: Json = Assay_ISAJson_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1574


def ARCtrl_ArcAssay__ArcAssay_fromISAJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



__all__ = ["Assay_encoder", "Assay_decoder", "Assay_encoderCompressed", "Assay_decoderCompressed", "Assay_ROCrate_genID", "Assay_ROCrate_encoder", "Assay_ROCrate_decoder", "Assay_ISAJson_encoder", "Assay_ISAJson_allowedFields", "Assay_ISAJson_decoder", "ARCtrl_ArcAssay__ArcAssay_fromJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toJsonString_Static_71136F3F", "ARCtrl_ArcAssay__ArcAssay_fromCompressedJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toCompressedJsonString_Static_71136F3F", "ARCtrl_ArcAssay__ArcAssay_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toROCrateJsonString_Static_5CABCA47", "ARCtrl_ArcAssay__ArcAssay_toISAJsonString_Static_71136F3F", "ARCtrl_ArcAssay__ArcAssay_fromISAJsonString_Static_Z721C83C5"]

