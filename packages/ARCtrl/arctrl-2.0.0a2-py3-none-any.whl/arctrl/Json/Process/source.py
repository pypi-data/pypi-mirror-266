from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton, of_array, FSharpList)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, list_1 as list_1_2, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.material_attribute_value import MaterialAttributeValue
from ...Core.Process.source import Source
from ...Core.uri import URIModule_toString
from ..context.rocrate.isa_source_context import context_jsonvalue
from ..decode import (Decode_uri, Decode_objectNoAdditionalProperties)
from ..encode import (try_include, try_include_list_opt, default_spaces)
from .material_attribute_value import (MaterialAttributeValue_ROCrate_encoder, MaterialAttributeValue_ROCrate_decoder, MaterialAttributeValue_ISAJson_encoder, MaterialAttributeValue_ISAJson_decoder)

def Source_ROCrate_genID(s: Source) -> str:
    match_value: str | None = s.ID
    if match_value is None:
        match_value_1: str | None = s.Name
        if match_value_1 is None:
            return "#EmptySource"

        else: 
            return "#Source_" + replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def Source_ROCrate_encoder(oa: Source) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1292(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Source_ROCrate_genID(oa))), ("@type", list_1_1(singleton(Json(0, "Source")))), try_include("name", _arrow1292, oa.Name), try_include_list_opt("characteristics", MaterialAttributeValue_ROCrate_encoder, oa.Characteristics), ("@context", context_jsonvalue)])))


def _arrow1296(get: IGetters) -> Source:
    def _arrow1293(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1294(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1295(__unit: None=None) -> FSharpList[MaterialAttributeValue] | None:
        arg_5: Decoder_1[FSharpList[MaterialAttributeValue]] = list_1_2(MaterialAttributeValue_ROCrate_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("characteristics", arg_5)

    return Source(_arrow1293(), _arrow1294(), _arrow1295())


Source_ROCrate_decoder: Decoder_1[Source] = object(_arrow1296)

def Source_ISAJson_encoder(oa: Source) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1298(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1299(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1300(oa_1: MaterialAttributeValue, oa: Any=oa) -> Json:
        return MaterialAttributeValue_ISAJson_encoder(oa_1)

    return Json(5, choose(chooser, of_array([try_include("@id", _arrow1298, oa.ID), try_include("name", _arrow1299, oa.Name), try_include_list_opt("characteristics", _arrow1300, oa.Characteristics)])))


Source_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "name", "characteristics", "@type", "@context"])

def _arrow1304(get: IGetters) -> Source:
    def _arrow1301(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1302(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1303(__unit: None=None) -> FSharpList[MaterialAttributeValue] | None:
        arg_5: Decoder_1[FSharpList[MaterialAttributeValue]] = list_1_2(MaterialAttributeValue_ISAJson_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("characteristics", arg_5)

    return Source(_arrow1301(), _arrow1302(), _arrow1303())


Source_ISAJson_decoder: Decoder_1[Source] = Decode_objectNoAdditionalProperties(Source_ISAJson_allowedFields, _arrow1304)

def ARCtrl_Process_Source__Source_fromISAJsonString_Static_Z721C83C5(s: str) -> Source:
    match_value: FSharpResult_2[Source, str] = Decode_fromString(Source_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Source__Source_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Source], str]:
    def _arrow1305(f: Source, spaces: Any=spaces) -> str:
        value: Json = Source_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1305


def ARCtrl_Process_Source__Source_fromROCrateString_Static_Z721C83C5(s: str) -> Source:
    match_value: FSharpResult_2[Source, str] = Decode_fromString(Source_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Source__Source_toROCrateString_Static_71136F3F(spaces: int | None=None) -> Callable[[Source], str]:
    def _arrow1306(f: Source, spaces: Any=spaces) -> str:
        value: Json = Source_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1306


__all__ = ["Source_ROCrate_genID", "Source_ROCrate_encoder", "Source_ROCrate_decoder", "Source_ISAJson_encoder", "Source_ISAJson_allowedFields", "Source_ISAJson_decoder", "ARCtrl_Process_Source__Source_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Source__Source_toISAJsonString_Static_71136F3F", "ARCtrl_Process_Source__Source_fromROCrateString_Static_Z721C83C5", "ARCtrl_Process_Source__Source_toROCrateString_Static_71136F3F"]

