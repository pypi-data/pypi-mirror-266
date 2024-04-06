from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.protocol_parameter import ProtocolParameter
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def ProtocolParameter_ISAJson_encoder(value: ProtocolParameter) -> Json:
    def chooser(tupled_arg: tuple[str, Json], value: Any=value) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    return Json(5, choose(chooser, singleton(try_include("parameterName", OntologyAnnotation_ISAJson_encoder, value.ParameterName))))


def _arrow1185(get: IGetters) -> ProtocolParameter:
    def _arrow1184(__unit: None=None) -> OntologyAnnotation | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("parameterName", OntologyAnnotation_ISAJson_decoder)

    return ProtocolParameter(None, _arrow1184())


ProtocolParameter_ISAJson_decoder: Decoder_1[ProtocolParameter] = object(_arrow1185)

def ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5(s: str) -> ProtocolParameter:
    match_value: FSharpResult_2[ProtocolParameter, str] = Decode_fromString(ProtocolParameter_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProtocolParameter], str]:
    def _arrow1186(v: ProtocolParameter, spaces: Any=spaces) -> str:
        value: Json = ProtocolParameter_ISAJson_encoder(v)
        return to_string(default_spaces(spaces), value)

    return _arrow1186


__all__ = ["ProtocolParameter_ISAJson_encoder", "ProtocolParameter_ISAJson_decoder", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F"]

