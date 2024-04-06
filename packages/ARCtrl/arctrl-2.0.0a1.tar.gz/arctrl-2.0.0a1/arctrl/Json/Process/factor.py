from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.comment import Comment
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.factor import Factor
from ..comment import (Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from ..decode import Decode_resizeArray
from ..encode import (try_include, try_include_seq, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def Factor_ISAJson_encoder(value: Factor) -> Json:
    def chooser(tupled_arg: tuple[str, Json], value: Any=value) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1126(value_1: str, value: Any=value) -> Json:
        return Json(0, value_1)

    return Json(5, choose(chooser, of_array([try_include("factorName", _arrow1126, value.Name), try_include("factorType", OntologyAnnotation_ISAJson_encoder, value.FactorType), try_include_seq("comments", Comment_ISAJson_encoder, default_arg(value.Comments, []))])))


def _arrow1134(get: IGetters) -> Factor:
    def _arrow1130(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("factorName", string)

    def _arrow1131(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("factorType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1133(__unit: None=None) -> Array[Comment] | None:
        arg_5: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("comments", arg_5)

    return Factor(_arrow1130(), _arrow1131(), _arrow1133())


Factor_ISAJson_decoder: Decoder_1[Factor] = object(_arrow1134)

def ARCtrl_Process_Factor__Factor_fromISAJsonString_Static_Z721C83C5(s: str) -> Factor:
    match_value: FSharpResult_2[Factor, str] = Decode_fromString(Factor_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Factor__Factor_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Factor], str]:
    def _arrow1142(f: Factor, spaces: Any=spaces) -> str:
        value: Json = Factor_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1142


__all__ = ["Factor_ISAJson_encoder", "Factor_ISAJson_decoder", "ARCtrl_Process_Factor__Factor_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Factor__Factor_toISAJsonString_Static_71136F3F"]

