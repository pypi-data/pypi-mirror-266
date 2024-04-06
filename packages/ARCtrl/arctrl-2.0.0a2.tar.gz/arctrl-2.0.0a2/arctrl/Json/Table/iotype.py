from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.types import to_string
from ...fable_modules.thoth_json_core.decode import (and_then, succeed, string)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string as to_string_1
from ...Core.Table.composite_header import IOType
from ..encode import default_spaces

def IOType_encoder(io: IOType) -> Json:
    return Json(0, to_string(io))


def cb(s: str) -> Decoder_1[IOType]:
    return succeed(IOType.of_string(s))


IOType_decoder: Decoder_1[IOType] = and_then(cb, string)

def ARCtrl_IOType__IOType_fromJsonString_Static_Z721C83C5(s: str) -> IOType:
    match_value: FSharpResult_2[IOType, str] = Decode_fromString(IOType_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_IOType__IOType_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[IOType], str]:
    def _arrow1428(obj: IOType, spaces: Any=spaces) -> str:
        value: Json = IOType_encoder(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1428


def ARCtrl_IOType__IOType_ToJsonString_71136F3F(this: IOType, spaces: int | None=None) -> str:
    return ARCtrl_IOType__IOType_toJsonString_Static_71136F3F(spaces)(this)


__all__ = ["IOType_encoder", "IOType_decoder", "ARCtrl_IOType__IOType_fromJsonString_Static_Z721C83C5", "ARCtrl_IOType__IOType_toJsonString_Static_71136F3F", "ARCtrl_IOType__IOType_ToJsonString_71136F3F"]

