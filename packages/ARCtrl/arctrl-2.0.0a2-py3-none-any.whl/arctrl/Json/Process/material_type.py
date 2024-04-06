from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import string
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1, ErrorReason_1, IDecoderHelpers_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.material_type import MaterialType
from ..encode import default_spaces

__A_ = TypeVar("__A_")

def MaterialType_ROCrate_encoder(value: MaterialType) -> Json:
    if value.tag == 1:
        return Json(0, "Labeled Extract Name")

    else: 
        return Json(0, "Extract Name")



class ObjectExpr1187(Decoder_1[MaterialType]):
    def Decode(self, s: IDecoderHelpers_1[__A_], json: __A_) -> FSharpResult_2[MaterialType, tuple[str, ErrorReason_1[__A_]]]:
        match_value: FSharpResult_2[str, tuple[str, ErrorReason_1[__A_]]] = string.Decode(s, json)
        if match_value.tag == 1:
            return FSharpResult_2(1, match_value.fields[0])

        elif match_value.fields[0] == "Extract Name":
            return FSharpResult_2(0, MaterialType(0))

        elif match_value.fields[0] == "Labeled Extract Name":
            return FSharpResult_2(0, MaterialType(1))

        else: 
            s_1: str = match_value.fields[0]
            return FSharpResult_2(1, (("Could not parse " + s_1) + "No other value than \"Extract Name\" or \"Labeled Extract Name\" allowed for materialtype", ErrorReason_1(0, s_1, json)))



MaterialType_ROCrate_decoder: Decoder_1[MaterialType] = ObjectExpr1187()

MaterialType_ISAJson_encoder: Callable[[MaterialType], Json] = MaterialType_ROCrate_encoder

MaterialType_ISAJson_decoder: Decoder_1[MaterialType] = MaterialType_ROCrate_decoder

def ARCtrl_Process_MaterialType__MaterialType_fromISAJsonString_Static_Z721C83C5(s: str) -> MaterialType:
    match_value: FSharpResult_2[MaterialType, str] = Decode_fromString(MaterialType_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialType__MaterialType_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[MaterialType], str]:
    def _arrow1188(f: MaterialType, spaces: Any=spaces) -> str:
        value: Json = MaterialType_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1188


__all__ = ["MaterialType_ROCrate_encoder", "MaterialType_ROCrate_decoder", "MaterialType_ISAJson_encoder", "MaterialType_ISAJson_decoder", "ARCtrl_Process_MaterialType__MaterialType_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialType__MaterialType_toISAJsonString_Static_71136F3F"]

