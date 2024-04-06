from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (of_array, choose)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.string_ import (replace, to_text, printf)
from ..fable_modules.fable_library.types import (to_string, Array)
from ..fable_modules.fable_library.util import (int32_to_string, equals)
from ..fable_modules.thoth_json_core.decode import (one_of, map, int_1, float_1, string, object, IOptionalGetter, IGetters)
from ..fable_modules.thoth_json_core.types import (Decoder_1, Json)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string as to_string_1
from ..Core.comment import Comment
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.uri import URIModule_toString
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoderDisambiguatingDescription, Comment_ROCrate_decoderDisambiguatingDescription)
from .context.rocrate.isa_ontology_annotation_context import context_jsonvalue
from .context.rocrate.property_value_context import context_jsonvalue as context_jsonvalue_1
from .decode import Decode_resizeArray
from .encode import (try_include, try_include_seq, default_spaces)
from .string_table import (encode_string, decode_string)

AnnotationValue_decoder: Decoder_1[str] = one_of(of_array([map(int32_to_string, int_1), map(to_string, float_1), string]))

def OntologyAnnotation_encoder(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow971(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow972(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow973(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow974(comment: Comment, oa: Any=oa) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([try_include("annotationValue", _arrow971, oa.Name), try_include("termSource", _arrow972, oa.TermSourceREF), try_include("termAccession", _arrow973, oa.TermAccessionNumber), try_include_seq("comments", _arrow974, oa.Comments)])))


def _arrow979(get: IGetters) -> OntologyAnnotation:
    def _arrow975(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow976(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow977(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow978(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow975(), _arrow976(), _arrow977(), _arrow978())


OntologyAnnotation_decoder: Decoder_1[OntologyAnnotation] = object(_arrow979)

def OntologyAnnotation_compressedEncoder(string_table: Any, oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow981(s: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s)

    def _arrow982(s_1: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s_1)

    def _arrow983(s_2: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s_2)

    def _arrow984(comment: Comment, string_table: Any=string_table, oa: Any=oa) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([try_include("a", _arrow981, oa.Name), try_include("ts", _arrow982, oa.TermSourceREF), try_include("ta", _arrow983, oa.TermAccessionNumber), try_include_seq("comments", _arrow984, oa.Comments)])))


def OntologyAnnotation_compressedDecoder(string_table: Array[str]) -> Decoder_1[OntologyAnnotation]:
    def _arrow989(get: IGetters, string_table: Any=string_table) -> OntologyAnnotation:
        def _arrow985(__unit: None=None) -> str | None:
            arg_1: Decoder_1[str] = decode_string(string_table)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("a", arg_1)

        def _arrow986(__unit: None=None) -> str | None:
            arg_3: Decoder_1[str] = decode_string(string_table)
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("ts", arg_3)

        def _arrow987(__unit: None=None) -> str | None:
            arg_5: Decoder_1[str] = decode_string(string_table)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("ta", arg_5)

        def _arrow988(__unit: None=None) -> Array[Comment] | None:
            arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("comments", arg_7)

        return OntologyAnnotation(_arrow985(), _arrow986(), _arrow987(), _arrow988())

    return object(_arrow989)


def OntologyAnnotation_ROCrate_genID(o: OntologyAnnotation) -> str:
    match_value: str | None = o.TermAccessionNumber
    if match_value is None:
        match_value_1: str | None = o.TermSourceREF
        if match_value_1 is None:
            match_value_2: str | None = o.Name
            if match_value_2 is None:
                return "#DummyOntologyAnnotation"

            else: 
                return "#UserTerm_" + replace(match_value_2, " ", "_")


        else: 
            return "#" + replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def OntologyAnnotation_ROCrate_encoderDefinedTerm(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow990(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow991(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow992(value_6: str, oa: Any=oa) -> Json:
        return Json(0, value_6)

    def _arrow993(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoderDisambiguatingDescription(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, OntologyAnnotation_ROCrate_genID(oa))), ("@type", Json(0, "OntologyAnnotation")), try_include("annotationValue", _arrow990, oa.Name), try_include("termSource", _arrow991, oa.TermSourceREF), try_include("termAccession", _arrow992, oa.TermAccessionNumber), try_include_seq("comments", _arrow993, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow998(get: IGetters) -> OntologyAnnotation:
    def _arrow994(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow995(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow996(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow997(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoderDisambiguatingDescription)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow994(), _arrow995(), _arrow996(), _arrow997())


OntologyAnnotation_ROCrate_decoderDefinedTerm: Decoder_1[OntologyAnnotation] = object(_arrow998)

def OntologyAnnotation_ROCrate_encoderPropertyValue(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow999(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1000(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1001(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoderDisambiguatingDescription(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, OntologyAnnotation_ROCrate_genID(oa))), ("@type", Json(0, "PropertyValue")), try_include("category", _arrow999, oa.Name), try_include("categoryCode", _arrow1000, oa.TermAccessionNumber), try_include_seq("comments", _arrow1001, oa.Comments), ("@context", context_jsonvalue_1)])))


def _arrow1005(get: IGetters) -> OntologyAnnotation:
    def _arrow1002(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("category", string)

    def _arrow1003(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("categoryCode", string)

    def _arrow1004(__unit: None=None) -> Array[Comment] | None:
        arg_5: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoderDisambiguatingDescription)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("comments", arg_5)

    return OntologyAnnotation.create(_arrow1002(), None, _arrow1003(), _arrow1004())


OntologyAnnotation_ROCrate_decoderPropertyValue: Decoder_1[OntologyAnnotation] = object(_arrow1005)

OntologyAnnotation_ISAJson_encoder: Callable[[OntologyAnnotation], Json] = OntologyAnnotation_encoder

OntologyAnnotation_ISAJson_decoder: Decoder_1[OntologyAnnotation] = OntologyAnnotation_decoder

def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_OntologyAnnotation__OntologyAnnotation_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1006(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_encoder(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1006


def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromROCrateJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_ROCrate_decoderDefinedTerm, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_OntologyAnnotation__OntologyAnnotation_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1007(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_ROCrate_encoderDefinedTerm(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1007


def ARCtrl_OntologyAnnotation__OntologyAnnotation_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1008(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_ISAJson_encoder(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1008


def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromISAJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



__all__ = ["AnnotationValue_decoder", "OntologyAnnotation_encoder", "OntologyAnnotation_decoder", "OntologyAnnotation_compressedEncoder", "OntologyAnnotation_compressedDecoder", "OntologyAnnotation_ROCrate_genID", "OntologyAnnotation_ROCrate_encoderDefinedTerm", "OntologyAnnotation_ROCrate_decoderDefinedTerm", "OntologyAnnotation_ROCrate_encoderPropertyValue", "OntologyAnnotation_ROCrate_decoderPropertyValue", "OntologyAnnotation_ISAJson_encoder", "OntologyAnnotation_ISAJson_decoder", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromJsonString_Static_Z721C83C5", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toROCrateJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toISAJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromISAJsonString_Static_Z721C83C5"]

