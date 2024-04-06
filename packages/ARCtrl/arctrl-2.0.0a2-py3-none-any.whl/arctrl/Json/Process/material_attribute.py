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
from ...Core.Process.material_attribute import MaterialAttribute
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def MaterialAttribute_ISAJson_encoder(value: MaterialAttribute) -> Json:
    def chooser(tupled_arg: tuple[str, Json], value: Any=value) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    return Json(5, choose(chooser, singleton(try_include("characteristicType", OntologyAnnotation_ISAJson_encoder, value.CharacteristicType))))


def _arrow1190(get: IGetters) -> MaterialAttribute:
    def _arrow1189(__unit: None=None) -> OntologyAnnotation | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("characteristicType", OntologyAnnotation_ISAJson_decoder)

    return MaterialAttribute(None, _arrow1189())


MaterialAttribute_ISAJson_decoder: Decoder_1[MaterialAttribute] = object(_arrow1190)

def ARCtrl_Process_MaterialAttribute__MaterialAttribute_fromISAJsonString_Static_Z721C83C5(s: str) -> MaterialAttribute:
    match_value: FSharpResult_2[MaterialAttribute, str] = Decode_fromString(MaterialAttribute_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialAttribute__MaterialAttribute_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[MaterialAttribute], str]:
    def _arrow1191(v: MaterialAttribute, spaces: Any=spaces) -> str:
        value: Json = MaterialAttribute_ISAJson_encoder(v)
        return to_string(default_spaces(spaces), value)

    return _arrow1191


__all__ = ["MaterialAttribute_ISAJson_encoder", "MaterialAttribute_ISAJson_decoder", "ARCtrl_Process_MaterialAttribute__MaterialAttribute_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialAttribute__MaterialAttribute_toISAJsonString_Static_71136F3F"]

