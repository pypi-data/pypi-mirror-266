from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.material_attribute import MaterialAttribute
from ...Core.Process.material_attribute_value import (MaterialAttributeValue, MaterialAttributeValue_createAsPV)
from ...Core.Process.value import Value
from ..decode import Decode_uri
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .material_attribute import (MaterialAttribute_ISAJson_encoder, MaterialAttribute_ISAJson_decoder)
from .property_value import (encoder, decoder as decoder_1)
from .value import (Value_ISAJson_encoder, Value_ISAJson_decoder)

MaterialAttributeValue_ROCrate_encoder: Callable[[MaterialAttributeValue], Json] = encoder

MaterialAttributeValue_ROCrate_decoder: Decoder_1[MaterialAttributeValue] = decoder_1(MaterialAttributeValue_createAsPV)

def MaterialAttributeValue_ISAJson_encoder(oa: MaterialAttributeValue) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1199(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1200(value_2: MaterialAttribute, oa: Any=oa) -> Json:
        return MaterialAttribute_ISAJson_encoder(value_2)

    def _arrow1201(value_3: Value, oa: Any=oa) -> Json:
        return Value_ISAJson_encoder(value_3)

    return Json(5, choose(chooser, of_array([try_include("@id", _arrow1199, oa.ID), try_include("category", _arrow1200, oa.Category), try_include("value", _arrow1201, oa.Value), try_include("unit", OntologyAnnotation_ISAJson_encoder, oa.Unit)])))


def _arrow1206(get: IGetters) -> MaterialAttributeValue:
    def _arrow1202(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1203(__unit: None=None) -> MaterialAttribute | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("category", MaterialAttribute_ISAJson_decoder)

    def _arrow1204(__unit: None=None) -> Value | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("value", Value_ISAJson_decoder)

    def _arrow1205(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("unit", OntologyAnnotation_ISAJson_decoder)

    return MaterialAttributeValue(_arrow1202(), _arrow1203(), _arrow1204(), _arrow1205())


MaterialAttributeValue_ISAJson_decoder: Decoder_1[MaterialAttributeValue] = object(_arrow1206)

def ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_fromISAJsonString_Static_Z721C83C5(s: str) -> MaterialAttributeValue:
    match_value: FSharpResult_2[MaterialAttributeValue, str] = Decode_fromString(MaterialAttributeValue_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[MaterialAttributeValue], str]:
    def _arrow1207(f: MaterialAttributeValue, spaces: Any=spaces) -> str:
        value: Json = MaterialAttributeValue_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1207


def ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_fromROCrateJsonString_Static_Z721C83C5(s: str) -> MaterialAttributeValue:
    match_value: FSharpResult_2[MaterialAttributeValue, str] = Decode_fromString(MaterialAttributeValue_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[MaterialAttributeValue], str]:
    def _arrow1208(f: MaterialAttributeValue, spaces: Any=spaces) -> str:
        value: Json = MaterialAttributeValue_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1208


__all__ = ["MaterialAttributeValue_ROCrate_encoder", "MaterialAttributeValue_ROCrate_decoder", "MaterialAttributeValue_ISAJson_encoder", "MaterialAttributeValue_ISAJson_decoder", "ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_toISAJsonString_Static_71136F3F", "ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialAttributeValue__MaterialAttributeValue_toROCrateJsonString_Static_71136F3F"]

