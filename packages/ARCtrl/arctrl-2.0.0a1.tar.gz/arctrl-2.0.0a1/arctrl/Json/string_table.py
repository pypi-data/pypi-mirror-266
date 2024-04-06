from __future__ import annotations
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.array_ import (fill, map)
from ..fable_modules.fable_library.map_util import add_to_dict
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.seq import iterate
from ..fable_modules.fable_library.types import Array
from ..fable_modules.thoth_json_core.decode import (array as array_1, string, int_1)
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1, ErrorReason_1, IDecoderHelpers_1)
from ..Core.Helper.collections_ import Dictionary_tryFind

__A_ = TypeVar("__A_")

def array_from_map(otm: Any) -> Array[str]:
    a: Array[str] = fill([0] * len(otm), 0, len(otm), "")
    def action(kv: Any, otm: Any=otm) -> None:
        a[kv[1]] = kv[0]

    iterate(action, otm)
    return a


def encoder(ot: Array[str]) -> Json:
    def _arrow954(value: str, ot: Any=ot) -> Json:
        return Json(0, value)

    return Json(6, map(_arrow954, ot, None))


decoder: Decoder_1[Array[str]] = array_1(string)

def encode_string(otm: Any, s: str) -> Json:
    match_value: int | None = Dictionary_tryFind(s, otm)
    if match_value is None:
        i_1: int = len(otm) or 0
        add_to_dict(otm, s, i_1)
        return Json(7, int(i_1+0x100000000 if i_1 < 0 else i_1))

    else: 
        i: int = match_value or 0
        return Json(7, int(i+0x100000000 if i < 0 else i))



def decode_string(ot: Array[str]) -> Decoder_1[str]:
    class ObjectExpr955(Decoder_1[str]):
        def Decode(self, s: IDecoderHelpers_1[__A_], json: __A_, ot: Any=ot) -> FSharpResult_2[str, tuple[str, ErrorReason_1[__A_]]]:
            match_value: FSharpResult_2[int, tuple[str, ErrorReason_1[__A_]]] = int_1.Decode(s, json)
            return FSharpResult_2(1, match_value.fields[0]) if (match_value.tag == 1) else FSharpResult_2(0, ot[match_value.fields[0]])

    return ObjectExpr955()


__all__ = ["array_from_map", "encoder", "decoder", "encode_string", "decode_string"]

