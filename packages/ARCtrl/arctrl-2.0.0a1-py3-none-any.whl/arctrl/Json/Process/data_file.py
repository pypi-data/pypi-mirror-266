from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import string
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1, ErrorReason_1, IDecoderHelpers_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.data_file import DataFile
from ..encode import default_spaces

__A_ = TypeVar("__A_")

def DataFile_ROCrate_encoder(value: DataFile) -> Json:
    if value.tag == 1:
        return Json(0, "Derived Data File")

    elif value.tag == 2:
        return Json(0, "Image File")

    else: 
        return Json(0, "Raw Data File")



class ObjectExpr1260(Decoder_1[DataFile]):
    def Decode(self, s: IDecoderHelpers_1[__A_], json: __A_) -> FSharpResult_2[DataFile, tuple[str, ErrorReason_1[__A_]]]:
        match_value: FSharpResult_2[str, tuple[str, ErrorReason_1[__A_]]] = string.Decode(s, json)
        if match_value.tag == 1:
            return FSharpResult_2(1, match_value.fields[0])

        elif match_value.fields[0] == "Raw Data File":
            return FSharpResult_2(0, DataFile(0))

        elif match_value.fields[0] == "Derived Data File":
            return FSharpResult_2(0, DataFile(1))

        elif match_value.fields[0] == "Image File":
            return FSharpResult_2(0, DataFile(2))

        else: 
            s_1: str = match_value.fields[0]
            return FSharpResult_2(1, (("Could not parse " + s_1) + ".", ErrorReason_1(0, s_1, json)))



DataFile_ROCrate_decoder: Decoder_1[DataFile] = ObjectExpr1260()

DataFile_ISAJson_encoder: Callable[[DataFile], Json] = DataFile_ROCrate_encoder

DataFile_ISAJson_decoder: Decoder_1[DataFile] = DataFile_ROCrate_decoder

def ARCtrl_Process_DataFile__DataFile_fromISAJsonString_Static_Z721C83C5(s: str) -> DataFile:
    match_value: FSharpResult_2[DataFile, str] = Decode_fromString(DataFile_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_DataFile__DataFile_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[DataFile], str]:
    def _arrow1266(f: DataFile, spaces: Any=spaces) -> str:
        value: Json = DataFile_ISAJson_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1266


def ARCtrl_Process_DataFile__DataFile_fromROCrateJsonString_Static_Z721C83C5(s: str) -> DataFile:
    match_value: FSharpResult_2[DataFile, str] = Decode_fromString(DataFile_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_DataFile__DataFile_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[DataFile], str]:
    def _arrow1270(f: DataFile, spaces: Any=spaces) -> str:
        value: Json = DataFile_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1270


__all__ = ["DataFile_ROCrate_encoder", "DataFile_ROCrate_decoder", "DataFile_ISAJson_encoder", "DataFile_ISAJson_decoder", "ARCtrl_Process_DataFile__DataFile_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_DataFile__DataFile_toISAJsonString_Static_71136F3F", "ARCtrl_Process_DataFile__DataFile_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_DataFile__DataFile_toROCrateJsonString_Static_71136F3F"]

