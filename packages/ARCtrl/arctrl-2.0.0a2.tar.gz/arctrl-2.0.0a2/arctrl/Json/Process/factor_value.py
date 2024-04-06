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
from ...Core.Process.factor import Factor
from ...Core.Process.factor_value import (FactorValue, FactorValue_createAsPV)
from ...Core.Process.value import Value
from ..decode import Decode_uri
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .factor import (Factor_ISAJson_encoder, Factor_ISAJson_decoder)
from .property_value import (encoder, decoder as decoder_1)
from .value import (Value_ISAJson_encoder, Value_ISAJson_decoder)

FactorValue_ROCrate_encoder: Callable[[FactorValue], Json] = encoder

FactorValue_ROCrate_decoder: Decoder_1[FactorValue] = decoder_1(FactorValue_createAsPV)

def FactorValue_ISAJson_encoder(fv: FactorValue) -> Json:
    def chooser(tupled_arg: tuple[str, Json], fv: Any=fv) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1175(value: str, fv: Any=fv) -> Json:
        return Json(0, value)

    def _arrow1176(value_2: Factor, fv: Any=fv) -> Json:
        return Factor_ISAJson_encoder(value_2)

    def _arrow1177(value_3: Value, fv: Any=fv) -> Json:
        return Value_ISAJson_encoder(value_3)

    return Json(5, choose(chooser, of_array([try_include("@id", _arrow1175, fv.ID), try_include("category", _arrow1176, fv.Category), try_include("value", _arrow1177, fv.Value), try_include("unit", OntologyAnnotation_ISAJson_encoder, fv.Unit)])))


def _arrow1182(get: IGetters) -> FactorValue:
    def _arrow1178(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1179(__unit: None=None) -> Factor | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("category", Factor_ISAJson_decoder)

    def _arrow1180(__unit: None=None) -> Value | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("value", Value_ISAJson_decoder)

    def _arrow1181(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("unit", OntologyAnnotation_ISAJson_decoder)

    return FactorValue(_arrow1178(), _arrow1179(), _arrow1180(), _arrow1181())


FactorValue_ISAJson_decoder: Decoder_1[FactorValue] = object(_arrow1182)

def ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5(s: str) -> FactorValue:
    match_value: FSharpResult_2[FactorValue, str] = Decode_fromString(FactorValue_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[FactorValue], str]:
    def _arrow1183(f: FactorValue, spaces: Any=spaces) -> str:
        value: Json = FactorValue_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1183


__all__ = ["FactorValue_ROCrate_encoder", "FactorValue_ROCrate_decoder", "FactorValue_ISAJson_encoder", "FactorValue_ISAJson_decoder", "ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_71136F3F"]

