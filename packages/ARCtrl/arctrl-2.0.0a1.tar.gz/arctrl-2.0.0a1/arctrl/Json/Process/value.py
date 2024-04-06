from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import of_array
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import (one_of, map, int_1, float_1, string)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.value import Value
from ..encode import default_spaces
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def Value_ISAJson_encoder(value: Value) -> Json:
    if value.tag == 1:
        return Json(7, int(value.fields[0]+0x100000000 if value.fields[0] < 0 else value.fields[0]))

    elif value.tag == 3:
        return Json(0, value.fields[0])

    elif value.tag == 0:
        return OntologyAnnotation_ISAJson_encoder(value.fields[0])

    else: 
        return Json(2, value.fields[0])



def _arrow1036(Item: int) -> Value:
    return Value(1, Item)


def _arrow1037(Item_1: float) -> Value:
    return Value(2, Item_1)


def _arrow1038(Item_2: OntologyAnnotation) -> Value:
    return Value(0, Item_2)


def _arrow1039(Item_3: str) -> Value:
    return Value(3, Item_3)


Value_ISAJson_decoder: Decoder_1[Value] = one_of(of_array([map(_arrow1036, int_1), map(_arrow1037, float_1), map(_arrow1038, OntologyAnnotation_ISAJson_decoder), map(_arrow1039, string)]))

def ARCtrl_Process_Value__Value_fromISAJsonString_Static_Z721C83C5(s: str) -> Value:
    match_value: FSharpResult_2[Value, str] = Decode_fromString(Value_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Value__Value_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Value], str]:
    def _arrow1040(v: Value, spaces: Any=spaces) -> str:
        value: Json = Value_ISAJson_encoder(v)
        return to_string(default_spaces(spaces), value)

    return _arrow1040


__all__ = ["Value_ISAJson_encoder", "Value_ISAJson_decoder", "ARCtrl_Process_Value__Value_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Value__Value_toISAJsonString_Static_71136F3F"]

