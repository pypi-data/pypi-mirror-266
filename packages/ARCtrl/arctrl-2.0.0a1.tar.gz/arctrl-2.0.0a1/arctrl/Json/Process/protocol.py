from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton, of_array, empty, FSharpList, append)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, list_1 as list_1_2, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.comment import Comment
from ...Core.Helper.collections_ import Option_fromValueWithDefault
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.component import Component
from ...Core.Process.protocol import Protocol
from ...Core.Process.protocol_parameter import ProtocolParameter
from ..comment import (Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from ..context.rocrate.isa_protocol_context import context_jsonvalue
from ..decode import Decode_uri
from ..encode import (try_include, try_include_list_opt, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .component import (Component_ROCrate_encoder, Component_ROCrate_decoder, Component_ISAJson_encoder, Component_ISAJson_decoder)
from .protocol_parameter import (ProtocolParameter_ISAJson_encoder, ProtocolParameter_ISAJson_decoder)

def Protocol_ROCrate_genID(study_name: str | None, assay_name: str | None, process_name: str | None, p: Protocol) -> str:
    match_value: str | None = p.Uri
    if match_value is None:
        match_value_1: str | None = p.Name
        if match_value_1 is None:
            (pattern_matching_result, an, pn, sn, pn_1, sn_1, pn_2) = (None, None, None, None, None, None, None)
            if study_name is None:
                if assay_name is None:
                    if process_name is not None:
                        pattern_matching_result = 2
                        pn_2 = process_name

                    else: 
                        pattern_matching_result = 3


                else: 
                    pattern_matching_result = 3


            elif assay_name is None:
                if process_name is not None:
                    pattern_matching_result = 1
                    pn_1 = process_name
                    sn_1 = study_name

                else: 
                    pattern_matching_result = 3


            elif process_name is not None:
                pattern_matching_result = 0
                an = assay_name
                pn = process_name
                sn = study_name

            else: 
                pattern_matching_result = 3

            if pattern_matching_result == 0:
                return (((("#Protocol_" + replace(sn, " ", "_")) + "_") + replace(an, " ", "_")) + "_") + replace(pn, " ", "_")

            elif pattern_matching_result == 1:
                return (("#Protocol_" + replace(sn_1, " ", "_")) + "_") + replace(pn_1, " ", "_")

            elif pattern_matching_result == 2:
                return "#Protocol_" + replace(pn_2, " ", "_")

            elif pattern_matching_result == 3:
                return "#EmptyProtocol"


        else: 
            return "#Protocol_" + replace(match_value_1, " ", "_")


    else: 
        return match_value



def Protocol_ROCrate_encoder(study_name: str | None, assay_name: str | None, process_name: str | None, oa: Protocol) -> Json:
    def chooser(tupled_arg: tuple[str, Json], study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1209(value_2: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1210(oa_1: OntologyAnnotation, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1211(value_4: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1212(value_6: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_6)

    def _arrow1213(value_8: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_8)

    def _arrow1214(comment: Comment, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Protocol_ROCrate_genID(study_name, assay_name, process_name, oa))), ("@type", list_1_1(singleton(Json(0, "Protocol")))), try_include("name", _arrow1209, oa.Name), try_include("protocolType", _arrow1210, oa.ProtocolType), try_include("description", _arrow1211, oa.Description), try_include("uri", _arrow1212, oa.Uri), try_include("version", _arrow1213, oa.Version), try_include_list_opt("components", Component_ROCrate_encoder, oa.Components), try_include_list_opt("comments", _arrow1214, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow1226(get: IGetters) -> Protocol:
    def _arrow1218(__unit: None=None) -> FSharpList[Component]:
        list_4: FSharpList[Component]
        def _arrow1215(__unit: None=None) -> FSharpList[Component] | None:
            arg_1: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("components", arg_1)

        list_2: FSharpList[Component] = default_arg(_arrow1215(), empty())
        def _arrow1216(__unit: None=None) -> FSharpList[Component] | None:
            arg_3: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("reagents", arg_3)

        list_4 = append(default_arg(_arrow1216(), empty()), list_2)
        def _arrow1217(__unit: None=None) -> FSharpList[Component] | None:
            arg_5: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("computationalTools", arg_5)

        return append(default_arg(_arrow1217(), empty()), list_4)

    components: FSharpList[Component] | None = Option_fromValueWithDefault(empty(), _arrow1218())
    def _arrow1219(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("@id", Decode_uri)

    def _arrow1220(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("name", string)

    def _arrow1221(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("protocolType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1222(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("description", string)

    def _arrow1223(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("uri", Decode_uri)

    def _arrow1224(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("version", string)

    def _arrow1225(__unit: None=None) -> FSharpList[Comment] | None:
        arg_19: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ROCrate_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return Protocol(_arrow1219(), _arrow1220(), _arrow1221(), _arrow1222(), _arrow1223(), _arrow1224(), None, components, _arrow1225())


Protocol_ROCrate_decoder: Decoder_1[Protocol] = object(_arrow1226)

def Protocol_ISAJson_encoder(oa: Protocol) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1228(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1229(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1230(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1231(value_6: str, oa: Any=oa) -> Json:
        return Json(0, value_6)

    def _arrow1232(value_8: str, oa: Any=oa) -> Json:
        return Json(0, value_8)

    def _arrow1233(value_10: ProtocolParameter, oa: Any=oa) -> Json:
        return ProtocolParameter_ISAJson_encoder(value_10)

    def _arrow1234(c: Component, oa: Any=oa) -> Json:
        return Component_ISAJson_encoder(c)

    return Json(5, choose(chooser, of_array([try_include("@id", _arrow1228, oa.ID), try_include("name", _arrow1229, oa.Name), try_include("protocolType", OntologyAnnotation_ISAJson_encoder, oa.ProtocolType), try_include("description", _arrow1230, oa.Description), try_include("uri", _arrow1231, oa.Uri), try_include("version", _arrow1232, oa.Version), try_include_list_opt("parameters", _arrow1233, oa.Parameters), try_include_list_opt("components", _arrow1234, oa.Components), try_include_list_opt("comments", Comment_ISAJson_encoder, oa.Comments)])))


def _arrow1244(get: IGetters) -> Protocol:
    def _arrow1235(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1236(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1237(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("protocolType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1238(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow1239(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("uri", Decode_uri)

    def _arrow1240(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("version", string)

    def _arrow1241(__unit: None=None) -> FSharpList[ProtocolParameter] | None:
        arg_13: Decoder_1[FSharpList[ProtocolParameter]] = list_1_2(ProtocolParameter_ISAJson_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("parameters", arg_13)

    def _arrow1242(__unit: None=None) -> FSharpList[Component] | None:
        arg_15: Decoder_1[FSharpList[Component]] = list_1_2(Component_ISAJson_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("components", arg_15)

    def _arrow1243(__unit: None=None) -> FSharpList[Comment] | None:
        arg_17: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ISAJson_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_17)

    return Protocol(_arrow1235(), _arrow1236(), _arrow1237(), _arrow1238(), _arrow1239(), _arrow1240(), _arrow1241(), _arrow1242(), _arrow1243())


Protocol_ISAJson_decoder: Decoder_1[Protocol] = object(_arrow1244)

def ARCtrl_Process_Protocol__Protocol_fromISAJsonString_Static_Z721C83C5(s: str) -> Protocol:
    match_value: FSharpResult_2[Protocol, str] = Decode_fromString(Protocol_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Protocol__Protocol_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Protocol], str]:
    def _arrow1245(f: Protocol, spaces: Any=spaces) -> str:
        value: Json = Protocol_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1245


def ARCtrl_Process_Protocol__Protocol_fromROCrateString_Static_Z721C83C5(s: str) -> Protocol:
    match_value: FSharpResult_2[Protocol, str] = Decode_fromString(Protocol_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Protocol__Protocol_toROCrateString_Static(study_name: str | None=None, assay_name: str | None=None, process_name: str | None=None, spaces: int | None=None) -> Callable[[Protocol], str]:
    def _arrow1246(f: Protocol, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, spaces: Any=spaces) -> str:
        value: Json = Protocol_ROCrate_encoder(study_name, assay_name, process_name, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1246


__all__ = ["Protocol_ROCrate_genID", "Protocol_ROCrate_encoder", "Protocol_ROCrate_decoder", "Protocol_ISAJson_encoder", "Protocol_ISAJson_decoder", "ARCtrl_Process_Protocol__Protocol_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Protocol__Protocol_toISAJsonString_Static_71136F3F", "ARCtrl_Process_Protocol__Protocol_fromROCrateString_Static_Z721C83C5", "ARCtrl_Process_Protocol__Protocol_toROCrateString_Static"]

